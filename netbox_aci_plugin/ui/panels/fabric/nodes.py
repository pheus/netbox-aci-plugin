# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the fabric ACI Node model."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

from ....choices import NodeRoleChoices

__all__ = (
    "ACINodeInfrastructurePanel",
    "ACINodePanel",
    "ACINodeSwitchProfilesPanel",
)


class ACINodePanel(panels.ObjectAttributesPanel):
    """Identity attribute panel for the ACI Node detail view."""

    title = _("ACI Node")

    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_pod = attrs.RelatedObjectAttr("aci_pod", linkify=True, label=_("ACI Pod"))
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    node_id = attrs.NumericAttr("node_id", label=_("Node ID"))
    node_object = attrs.GenericForeignKeyAttr(
        "node_object", linkify=True, label=_("Node")
    )
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACINodeInfrastructurePanel(panels.ObjectAttributesPanel):
    """Role, type, and VPC pairing attribute panel for an ACI Node."""

    title = _("Infrastructure")

    role = attrs.ChoiceAttr("role", label=_("Role"))
    node_type = attrs.ChoiceAttr("node_type", label=_("Type"))
    tep_ip_address = attrs.RelatedObjectAttr(
        "tep_ip_address", linkify=True, label=_("TEP IP Address")
    )
    vpc_protection_group = attrs.TemplatedAttr(
        "vpc_protection_group",
        template_name="netbox_aci_plugin/attrs/vpc_protection_group.html",
        label=_("ACI VPC Protection Group"),
    )


class ACINodeSwitchProfilesPanel(panels.ObjectsTablePanel):
    """Covering ACI Leaf Switch Profiles card for the ACI Node detail view.

    Routes through the Profile list view so the rows honour object
    permissions, which an attribute row cannot.

    The card carries no Add action: coverage is resolved from node
    blocks, so the object a user would create here is a block.
    """

    title = _("ACI Leaf Switch Profiles")

    def __init__(self, **kwargs) -> None:
        super().__init__(
            "netbox_aci_plugin.ACILeafSwitchProfile",
            filters={"covering_aci_node_id": lambda ctx: ctx["object"].pk},
            exclude_columns=["aci_fabric", "name_alias", "nb_tenant"],
            **kwargs,
        )

    def should_render(self, context) -> bool:
        """Hide the card on Nodes whose role no Profile can cover."""
        return (
            super().should_render(context)
            and context["object"].role == NodeRoleChoices.ROLE_LEAF
        )
