# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Models for ACI access-policy Leaf Interface Overrides."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel

from ...choices import LeafInterfacePolicyGroupTypeChoices
from ...constants import ACI_DESC_MAX_LEN
from ...validators import ACIPolicyDescriptionValidator

if TYPE_CHECKING:
    from core.models import ObjectChange

    from ..fabric.fabrics import ACIFabric
    from ..fabric.node_interfaces import ACINodeInterface


class ACILeafInterfaceOverride(NetBoxModel):
    """ACI Leaf Interface Override (infraHPathS) for one Leaf port.

    Replaces the policy group inherited from the interface profile and
    selector tree. The APIC path selector and its path attachment are
    modelled as one object, since one override per port covers the
    operational case.
    """

    aci_node_interface = models.OneToOneField(
        to="netbox_aci_plugin.ACINodeInterface",
        on_delete=models.CASCADE,
        related_name="aci_leaf_interface_override",
        verbose_name=_("ACI Node Interface"),
    )
    aci_leaf_interface_policy_group = models.ForeignKey(
        to="netbox_aci_plugin.ACILeafInterfacePolicyGroup",
        on_delete=models.PROTECT,
        related_name="aci_leaf_interface_overrides",
        verbose_name=_("ACI Leaf Interface Policy Group"),
    )
    description = models.CharField(
        verbose_name=_("description"),
        max_length=ACI_DESC_MAX_LEN,
        blank=True,
        validators=[ACIPolicyDescriptionValidator],
    )
    comments = models.TextField(
        verbose_name=_("comments"),
        blank=True,
    )

    clone_fields: tuple = ("aci_leaf_interface_policy_group",)
    prerequisite_models: tuple = (
        "netbox_aci_plugin.ACINodeInterface",
        "netbox_aci_plugin.ACILeafInterfacePolicyGroup",
    )

    class Meta:
        default_related_name: str = "aci_leaf_interface_overrides"
        ordering: tuple = ("aci_node_interface",)
        verbose_name: str = _("ACI Leaf Interface Override")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return f"{self.aci_node_interface} - {self.aci_leaf_interface_policy_group}"

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        errors = {}

        if (
            self.aci_node_interface_id
            and self.aci_leaf_interface_policy_group_id
            and self.aci_leaf_interface_policy_group.aci_fabric_id
            != self.aci_node_interface.aci_node._aci_fabric_id  # noqa: SLF001
        ):
            errors.setdefault("aci_leaf_interface_policy_group", []).append(
                _(
                    "The assigned ACI Leaf Interface Policy Group must "
                    "belong to the same ACI Fabric as the ACI Node "
                    "Interface."
                )
            )

        # Bundle-group overrides are deferred scope, not a MIM restriction
        if (
            self.aci_leaf_interface_policy_group_id
            and self.aci_leaf_interface_policy_group.group_type
            != LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS
        ):
            errors.setdefault("aci_leaf_interface_policy_group", []).append(
                _(
                    "Only an Access ACI Leaf Interface Policy Group can be "
                    "assigned to a single Leaf port."
                )
            )

        if errors:
            raise ValidationError(errors)

    def to_objectchange(self, action) -> ObjectChange:
        """Return an ObjectChange for the change made to an instance."""
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.aci_node_interface
        return objectchange

    @property
    def aci_fabric(self) -> ACIFabric:
        """Return the ACIFabric of the related ACI Node Interface."""
        return self.aci_node_interface.aci_fabric

    @property
    def parent_object(self) -> ACINodeInterface:
        """Return the parent object of the instance."""
        return self.aci_node_interface

    @property
    def apic_name(self) -> str:
        """Return the deterministic APIC name of the path selector.

        Built from the coordinates, not the database key, so generated
        policy is stable. The interface token's slashes are not legal
        in an APIC name.
        """
        interface: ACINodeInterface = self.aci_node_interface
        parts: list[int] = [
            interface.aci_node.node_id,
            interface.module,
            interface.port,
        ]
        if interface.sub_port:
            parts.append(interface.sub_port)
        return "override-" + "-".join(str(part) for part in parts)
