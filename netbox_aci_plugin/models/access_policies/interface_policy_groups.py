# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Model for ACI Leaf Interface Policy Groups."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ...choices import LeafInterfacePolicyGroupTypeChoices
from ..base import ACIFabricBaseModel

if TYPE_CHECKING:
    from ..fabric.fabrics import ACIFabric


class ACILeafInterfacePolicyGroup(ACIFabricBaseModel):
    """ACI Leaf Interface Policy Group.

    Represents an access, port channel, or virtual port channel
    Interface Policy Group. The type determines the APIC class:
    access maps to infraAccPortGrp, port channel and virtual port
    channel map to infraAccBndlGrp with the link aggregation type
    derived from the type.
    """

    aci_fabric = models.ForeignKey(
        to="netbox_aci_plugin.ACIFabric",
        on_delete=models.PROTECT,
        related_name="aci_leaf_interface_policy_groups",
        verbose_name=_("ACI Fabric"),
    )
    group_type = models.CharField(
        verbose_name=_("type"),
        max_length=16,
        choices=LeafInterfacePolicyGroupTypeChoices,
        help_text=_(
            "Type of the Interface Policy Group. The type cannot be "
            "changed after creation."
        ),
    )
    aci_aaep = models.ForeignKey(
        to="netbox_aci_plugin.ACIAttachableAccessEntityProfile",
        on_delete=models.SET_NULL,
        related_name="aci_leaf_interface_policy_groups",
        verbose_name=_("ACI AAEP"),
        blank=True,
        null=True,
        help_text=_(
            "Attachable Access Entity Profile associated with the "
            "Policy Group. Required for a deployable access path."
        ),
    )

    clone_fields: tuple = ACIFabricBaseModel.clone_fields + (
        "aci_fabric",
        "group_type",
        "aci_aaep",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIFabric",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_fabric", "name"),
                condition=models.Q(group_type="access"),
                name="%(app_label)s_%(class)s_uniq_access_name",
                violation_error_message=_(
                    "An Access Interface Policy Group with this name "
                    "already exists in the ACI Fabric."
                ),
            ),
            models.UniqueConstraint(
                fields=("aci_fabric", "name"),
                condition=models.Q(group_type__in=("pc", "vpc")),
                name="%(app_label)s_%(class)s_uniq_bundle_name",
                violation_error_message=_(
                    "A Port Channel or Virtual Port Channel Interface "
                    "Policy Group with this name already exists in the "
                    "ACI Fabric."
                ),
            ),
        ]
        default_related_name: str = "aci_leaf_interface_policy_groups"
        ordering: tuple = ("aci_fabric", "name")
        verbose_name: str = _("ACI Leaf Interface Policy Group")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return f"{self.name} ({self.get_group_type_display()})"

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        errors = {}

        if (
            self.aci_aaep_id
            and self.aci_fabric_id
            and self.aci_aaep.aci_fabric_id != self.aci_fabric_id
        ):
            errors.setdefault("aci_aaep", []).append(
                _(
                    "The ACI AAEP must belong to the same ACI Fabric as "
                    "the Policy Group."
                )
            )

        stored_group_type = self._get_stored_group_type()
        if stored_group_type is not None and stored_group_type != self.group_type:
            errors.setdefault("group_type", []).append(
                _("The type cannot be changed after creation.")
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        """Save the current instance, refusing a type change."""
        # update_fields may be a one-shot iterable, so materialize it first
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            update_fields = set(update_fields)
            kwargs["update_fields"] = update_fields

        # The type decides the APIC namespace and the link aggregation
        # type, so a direct save must not bypass the clean() guard
        type_will_be_saved = update_fields is None or "group_type" in update_fields

        if type_will_be_saved:
            stored_group_type = self._get_stored_group_type()
            if stored_group_type is not None and stored_group_type != self.group_type:
                raise ValidationError([_("The type cannot be changed after creation.")])

        super().save(*args, **kwargs)

    @property
    def parent_object(self) -> ACIFabric:
        """Return the parent object of the instance."""
        return self.aci_fabric

    @property
    def lag_type(self) -> str | None:
        """Return the APIC link aggregation type for the group type."""
        if self.group_type == LeafInterfacePolicyGroupTypeChoices.TYPE_PC:
            return "link"
        if self.group_type == LeafInterfacePolicyGroupTypeChoices.TYPE_VPC:
            return "node"
        return None

    @property
    def apic_namespace(self) -> str | None:
        """Return the APIC name namespace of the policy group."""
        if self.group_type == LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS:
            return "access"
        if self.group_type in {
            LeafInterfacePolicyGroupTypeChoices.TYPE_PC,
            LeafInterfacePolicyGroupTypeChoices.TYPE_VPC,
        }:
            return "bundle"
        return None

    def get_group_type_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return LeafInterfacePolicyGroupTypeChoices.colors.get(self.group_type)

    def _get_stored_group_type(self) -> str | None:
        """Return the stored group type, or None when there is no row.

        Shared by clean() and save() so the two cannot drift apart. A
        missing row degrades to None rather than raising, leaving the
        immutability check to pass on an instance with nothing stored.
        """
        if not self.pk:
            return None
        return (
            ACILeafInterfacePolicyGroup.objects.filter(pk=self.pk)
            .values_list("group_type", flat=True)
            .first()
        )
