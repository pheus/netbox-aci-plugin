# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Models for ACI access-policy Leaf Interface Profiles."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ...constants import (
    LEAF_PORT_BLOCK_MODULE_MAX,
    LEAF_PORT_BLOCK_MODULE_MIN,
    NODE_INTERFACE_PORT_MAX,
    NODE_INTERFACE_PORT_MIN,
)
from ..base import ACIFabricBaseModel

if TYPE_CHECKING:
    from core.models import ObjectChange

    from ..fabric.fabrics import ACIFabric


class ACILeafInterfaceProfile(ACIFabricBaseModel):
    """ACI Leaf Interface Profile (infraAccPortP) scoped to a fabric.

    Groups the selectors that select the leaf ports a policy group
    applies to.
    """

    aci_fabric = models.ForeignKey(
        to="netbox_aci_plugin.ACIFabric",
        on_delete=models.PROTECT,
        related_name="aci_leaf_interface_profiles",
        verbose_name=_("ACI Fabric"),
    )

    clone_fields: tuple = ACIFabricBaseModel.clone_fields + ("aci_fabric",)
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIFabric",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_fabric", "name"),
                name="%(app_label)s_%(class)s_uniq_name_per_fabric",
            ),
        ]
        default_related_name: str = "aci_leaf_interface_profiles"
        ordering: tuple = ("aci_fabric", "name")
        verbose_name: str = _("ACI Leaf Interface Profile")

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        errors = {}

        # A Selector checks its Policy Group only on its own save
        if self.pk and self.aci_fabric_id:
            stored_fabric_id = (
                ACILeafInterfaceProfile.objects.filter(pk=self.pk)
                .values_list("aci_fabric_id", flat=True)
                .first()
            )
            if stored_fabric_id is not None and stored_fabric_id != self.aci_fabric_id:
                offending = sorted(
                    self.aci_leaf_interface_selectors.filter(
                        aci_leaf_interface_policy_group__isnull=False
                    )
                    .exclude(
                        aci_leaf_interface_policy_group__aci_fabric=self.aci_fabric_id
                    )
                    .values_list("name", flat=True)
                )
                if offending:
                    errors.setdefault("aci_fabric", []).append(
                        _(
                            "The assigned ACI Fabric differs from the ACI "
                            "Fabric of the ACI Leaf Interface Policy Groups "
                            "assigned to existing ACI Leaf Interface "
                            "Selectors: {offending}."
                        ).format(offending=", ".join(offending))
                    )

        # The Binding cannot see a Fabric change made on this object
        if (
            self.pk
            and self.aci_fabric_id
            and self.aci_leaf_switch_profile_bindings.exclude(
                aci_leaf_switch_profile__aci_fabric=self.aci_fabric_id
            ).exists()
        ):
            errors.setdefault("aci_fabric", []).append(
                _(
                    "The assigned ACI Fabric differs from the ACI Fabric of "
                    "the ACI Leaf Switch Profiles bound to this ACI Leaf "
                    "Interface Profile."
                )
            )

        if errors:
            raise ValidationError(errors)

    @property
    def parent_object(self) -> ACIFabric:
        """Return the parent object of the instance."""
        return self.aci_fabric


class ACILeafInterfaceSelector(ACIFabricBaseModel):
    """ACI Leaf Interface Selector (infraHPortS) within an interface profile.

    Names leaf ports through its port blocks and optionally assigns
    them an interface policy group. Only the range selector type is
    modeled.
    """

    aci_leaf_interface_profile = models.ForeignKey(
        to="netbox_aci_plugin.ACILeafInterfaceProfile",
        on_delete=models.CASCADE,
        related_name="aci_leaf_interface_selectors",
        verbose_name=_("ACI Leaf Interface Profile"),
    )
    aci_leaf_interface_policy_group = models.ForeignKey(
        to="netbox_aci_plugin.ACILeafInterfacePolicyGroup",
        on_delete=models.PROTECT,
        related_name="aci_leaf_interface_selectors",
        verbose_name=_("ACI Leaf Interface Policy Group"),
        blank=True,
        null=True,
    )

    clone_fields: tuple = ACIFabricBaseModel.clone_fields + (
        "aci_leaf_interface_profile",
        "aci_leaf_interface_policy_group",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACILeafInterfaceProfile",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_leaf_interface_profile", "name"),
                name="%(app_label)s_%(class)s_uniq_name",
            ),
        ]
        default_related_name: str = "aci_leaf_interface_selectors"
        ordering: tuple = ("aci_leaf_interface_profile", "name")
        verbose_name: str = _("ACI Leaf Interface Selector")

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        errors = {}

        if (
            self.aci_leaf_interface_profile_id
            and self.aci_leaf_interface_policy_group_id
            and self.aci_leaf_interface_policy_group.aci_fabric
            != self.aci_leaf_interface_profile.aci_fabric
        ):
            errors.setdefault("aci_leaf_interface_policy_group", []).append(
                _(
                    "The assigned ACI Leaf Interface Policy Group must belong "
                    "to the same ACI Fabric as the ACI Leaf Interface Profile."
                )
            )

        if errors:
            raise ValidationError(errors)

    def to_objectchange(self, action) -> ObjectChange:
        """Return an ObjectChange for the change made to an instance."""
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.aci_leaf_interface_profile
        return objectchange

    @property
    def aci_fabric(self) -> ACIFabric:
        """Return the ACIFabric of the related ACILeafInterfaceProfile."""
        return self.aci_leaf_interface_profile.aci_fabric

    @property
    def parent_object(self) -> ACILeafInterfaceProfile:
        """Return the parent object of the instance."""
        return self.aci_leaf_interface_profile


class ACILeafPortBlock(ACIFabricBaseModel):
    """ACI Leaf Port Block (infraPortBlk) within an interface selector.

    A contiguous module and port range covered by its selector. APIC
    treats the block as the cartesian product of the two ranges.
    """

    aci_leaf_interface_selector = models.ForeignKey(
        to="netbox_aci_plugin.ACILeafInterfaceSelector",
        on_delete=models.CASCADE,
        related_name="aci_leaf_port_blocks",
        verbose_name=_("ACI Leaf Interface Selector"),
    )
    module_from = models.PositiveSmallIntegerField(
        verbose_name=_("module (from)"),
        validators=[
            MinValueValidator(LEAF_PORT_BLOCK_MODULE_MIN),
            MaxValueValidator(LEAF_PORT_BLOCK_MODULE_MAX),
        ],
    )
    module_to = models.PositiveSmallIntegerField(
        verbose_name=_("module (to)"),
        validators=[
            MinValueValidator(LEAF_PORT_BLOCK_MODULE_MIN),
            MaxValueValidator(LEAF_PORT_BLOCK_MODULE_MAX),
        ],
    )
    port_from = models.PositiveSmallIntegerField(
        verbose_name=_("port (from)"),
        validators=[
            MinValueValidator(NODE_INTERFACE_PORT_MIN),
            MaxValueValidator(NODE_INTERFACE_PORT_MAX),
        ],
    )
    port_to = models.PositiveSmallIntegerField(
        verbose_name=_("port (to)"),
        validators=[
            MinValueValidator(NODE_INTERFACE_PORT_MIN),
            MaxValueValidator(NODE_INTERFACE_PORT_MAX),
        ],
    )

    clone_fields: tuple = ACIFabricBaseModel.clone_fields + (
        "aci_leaf_interface_selector",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACILeafInterfaceSelector",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_leaf_interface_selector", "name"),
                name="%(app_label)s_%(class)s_uniq_name_per_selector",
            ),
        ]
        default_related_name: str = "aci_leaf_port_blocks"
        ordering: tuple = ("aci_leaf_interface_selector", "module_from", "port_from")
        verbose_name: str = _("ACI Leaf Port Block")

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        errors = {}

        if (
            self.module_from is not None
            and self.module_to is not None
            and self.module_from > self.module_to
        ):
            errors.setdefault("module_to", []).append(
                _("The starting module must not be greater than the ending module.")
            )

        if (
            self.port_from is not None
            and self.port_to is not None
            and self.port_from > self.port_to
        ):
            errors.setdefault("port_to", []).append(
                _("The starting port must not be greater than the ending port.")
            )

        if errors:
            raise ValidationError(errors)

    def to_objectchange(self, action) -> ObjectChange:
        """Return an ObjectChange for the change made to an instance."""
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.aci_leaf_interface_selector
        return objectchange

    @property
    def aci_fabric(self) -> ACIFabric:
        """Return the ACIFabric of the related ACILeafInterfaceSelector."""
        return self.aci_leaf_interface_selector.aci_fabric

    @property
    def parent_object(self) -> ACILeafInterfaceSelector:
        """Return the parent object of the instance."""
        return self.aci_leaf_interface_selector
