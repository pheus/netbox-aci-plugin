# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Model for ACI VPC Explicit Protection Groups."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Greatest, Least
from django.utils.translation import gettext_lazy as _

from ...choices import NodeRoleChoices
from ...constants import VPC_LOGICAL_PAIR_ID_MAX, VPC_LOGICAL_PAIR_ID_MIN
from ..base import ACIFabricBaseModel

if TYPE_CHECKING:
    from ..fabric.fabrics import ACIFabric
    from ..fabric.pods import ACIPod


class ACIVPCProtectionGroup(ACIFabricBaseModel):
    """ACI VPC Explicit Protection Group (fabricExplicitGEp).

    Pairs two Leaf Nodes into a virtual port channel domain with a
    logical pair ID. Virtual port channel access paths require the
    two leaves of the path to form exactly one Protection Group.

    Notes:
        Cisco recommends pairing Leaf Nodes of compatible hardware
        generations. The plugin does not enforce that, since the
        supported combinations change per platform release.
    """

    aci_fabric = models.ForeignKey(
        to="netbox_aci_plugin.ACIFabric",
        on_delete=models.PROTECT,
        related_name="aci_vpc_protection_groups",
        verbose_name=_("ACI Fabric"),
    )
    logical_pair_id = models.PositiveSmallIntegerField(
        verbose_name=_("logical pair ID"),
        validators=[
            MinValueValidator(VPC_LOGICAL_PAIR_ID_MIN),
            MaxValueValidator(VPC_LOGICAL_PAIR_ID_MAX),
        ],
        help_text=_(
            "Identifier of the virtual port channel domain formed by "
            "the node pair (1-1000)."
        ),
    )
    aci_node_a = models.ForeignKey(
        to="netbox_aci_plugin.ACINode",
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("ACI Node A"),
        help_text=_("First ACI Leaf Node of the Protection Group."),
    )
    aci_node_b = models.ForeignKey(
        to="netbox_aci_plugin.ACINode",
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("ACI Node B"),
        help_text=_("Second ACI Leaf Node of the Protection Group."),
    )

    clone_fields: tuple = ACIFabricBaseModel.clone_fields + ("aci_fabric",)
    prerequisite_models: tuple = (
        "netbox_aci_plugin.ACIFabric",
        "netbox_aci_plugin.ACINode",
    )

    class Meta:
        constraints: list[models.BaseConstraint] = [
            models.UniqueConstraint(
                fields=("aci_fabric", "name"),
                name="%(app_label)s_%(class)s_uniq_name",
                violation_error_message=_(
                    "A VPC Protection Group with this name already exists "
                    "in the ACI Fabric."
                ),
            ),
            models.UniqueConstraint(
                fields=("aci_fabric", "logical_pair_id"),
                name="%(app_label)s_%(class)s_uniq_pair_id",
                violation_error_message=_(
                    "A VPC Protection Group with this logical pair ID "
                    "already exists in the ACI Fabric."
                ),
            ),
            models.UniqueConstraint(
                Least("aci_node_a", "aci_node_b"),
                Greatest("aci_node_a", "aci_node_b"),
                name="%(app_label)s_%(class)s_uniq_pair",
                violation_error_message=_(
                    "This pair of ACI Nodes is already assigned to "
                    "another VPC Protection Group."
                ),
            ),
            models.CheckConstraint(
                condition=~models.Q(aci_node_a=models.F("aci_node_b")),
                name="%(app_label)s_%(class)s_distinct_nodes",
            ),
        ]
        default_related_name: str = "aci_vpc_protection_groups"
        ordering: tuple = ("aci_fabric", "logical_pair_id")
        verbose_name: str = _("ACI VPC Protection Group")

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        errors = {}

        if (
            self.aci_node_a_id
            and self.aci_node_b_id
            and self.aci_node_a_id == self.aci_node_b_id
        ):
            errors.setdefault("aci_node_b", []).append(
                _("ACI Node A and ACI Node B must be different nodes.")
            )

        # Read stored Node state, not the supplied instances: an in-memory
        # edit must not decide these checks. A missing row skips them,
        # leaving the unknown ID to the foreign key's own validation
        stored_nodes: dict[int, dict] = {}
        if self.aci_node_a_id or self.aci_node_b_id:
            node_model = apps.get_model("netbox_aci_plugin", "ACINode")
            stored_nodes = {
                row["pk"]: row
                for row in node_model.objects.filter(
                    pk__in=(self.aci_node_a_id, self.aci_node_b_id)
                ).values("pk", "role", "aci_pod_id", "_aci_fabric_id")
            }
        stored_node_a = stored_nodes.get(self.aci_node_a_id)
        stored_node_b = stored_nodes.get(self.aci_node_b_id)

        if stored_node_a and stored_node_a["role"] != NodeRoleChoices.ROLE_LEAF:
            errors.setdefault("aci_node_a", []).append(
                _("ACI Node A must have the Leaf role.")
            )
        if stored_node_b and stored_node_b["role"] != NodeRoleChoices.ROLE_LEAF:
            errors.setdefault("aci_node_b", []).append(
                _("ACI Node B must have the Leaf role.")
            )

        if (
            stored_node_a
            and self.aci_fabric_id
            and stored_node_a["_aci_fabric_id"] != self.aci_fabric_id
        ):
            errors.setdefault("aci_node_a", []).append(
                _(
                    "ACI Node A must belong to the same ACI Fabric as the "
                    "Protection Group."
                )
            )
        if (
            stored_node_b
            and self.aci_fabric_id
            and stored_node_b["_aci_fabric_id"] != self.aci_fabric_id
        ):
            errors.setdefault("aci_node_b", []).append(
                _(
                    "ACI Node B must belong to the same ACI Fabric as the "
                    "Protection Group."
                )
            )

        if (
            stored_node_a
            and stored_node_b
            and stored_node_a["aci_pod_id"] != stored_node_b["aci_pod_id"]
        ):
            errors.setdefault("aci_node_b", []).append(
                _("ACI Node A and ACI Node B must belong to the same ACI Pod.")
            )

        # Node membership exclusivity has no database equivalent: it spans
        # an unordered pair across two foreign key columns
        if self.aci_node_a_id:
            conflict = (
                ACIVPCProtectionGroup.objects.filter(
                    models.Q(aci_node_a_id=self.aci_node_a_id)
                    | models.Q(aci_node_b_id=self.aci_node_a_id)
                )
                .exclude(pk=self.pk)
                .exists()
            )
            if conflict:
                errors.setdefault("aci_node_a", []).append(
                    _(
                        "This ACI Node is already a member of another VPC "
                        "Protection Group."
                    )
                )
        if self.aci_node_b_id:
            conflict = (
                ACIVPCProtectionGroup.objects.filter(
                    models.Q(aci_node_a_id=self.aci_node_b_id)
                    | models.Q(aci_node_b_id=self.aci_node_b_id)
                )
                .exclude(pk=self.pk)
                .exists()
            )
            if conflict:
                errors.setdefault("aci_node_b", []).append(
                    _(
                        "This ACI Node is already a member of another VPC "
                        "Protection Group."
                    )
                )

        if errors:
            raise ValidationError(errors)

    @property
    def aci_pod(self) -> ACIPod:
        """Return the ACIPod instance of the related ACI nodes."""
        return self.aci_node_a.aci_pod

    @property
    def parent_object(self) -> ACIFabric:
        """Return the parent object of the instance."""
        return self.aci_fabric

    @property
    def ordered_nodes(self) -> tuple:
        """Return the node pair ordered by ACI node ID."""
        return tuple(
            sorted(
                (self.aci_node_a, self.aci_node_b),
                key=lambda node: node.node_id,
            )
        )
