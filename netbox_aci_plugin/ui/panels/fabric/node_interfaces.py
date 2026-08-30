# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the fabric ACI Node Interface model."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

from ...actions import ACIObjectLinkAction

__all__ = ("ACINodeInterfaceOverridePanel", "ACINodeInterfacePanel")


class ACINodeInterfacePanel(panels.ObjectAttributesPanel):
    """Identity attribute panel for the ACI Node Interface detail view.

    ACINodeInterface has no name_alias field.
    """

    title = _("ACI Node Interface")

    aci_node = attrs.RelatedObjectAttr("aci_node", linkify=True, label=_("ACI Node"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_interface = attrs.RelatedObjectAttr(
        "nb_interface", linkify=True, label=_("NetBox Interface")
    )
    module = attrs.NumericAttr("module", label=_("Module"))
    port = attrs.NumericAttr("port", label=_("Port"))
    sub_port = attrs.NumericAttr("sub_port_display", label=_("Sub Port"))
    interface_token = attrs.TextAttr("interface_token", label=_("Interface Token"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACINodeInterfaceOverridePanel(panels.ObjectAttributesPanel):
    """Leaf Interface Override attribute panel, with its Add/Edit/Delete triad.

    Stock actions cannot express the triad: the Add link needs to hide
    once an Override exists, Edit and Delete need the opposite, and all
    three need a permission check on the Override model rather than the
    port. ACIObjectLinkAction adds a condition callable for exactly this.
    """

    title = _("Leaf Interface Override")
    actions = [
        ACIObjectLinkAction(
            "plugins:netbox_aci_plugin:acileafinterfaceoverride_add",
            condition=lambda ctx: ctx["object"].leaf_interface_override is None,
            permissions=["netbox_aci_plugin.add_acileafinterfaceoverride"],
            label=_("Add an Override"),
            button_icon="plus-thick",
            url_params={
                "aci_fabric": lambda ctx: ctx["object"].aci_node.aci_pod.aci_fabric_id,
                "aci_pod": lambda ctx: ctx["object"].aci_node.aci_pod_id,
                "aci_node": lambda ctx: ctx["object"].aci_node_id,
                "aci_node_interface": lambda ctx: ctx["object"].pk,
            },
        ),
        ACIObjectLinkAction(
            "plugins:netbox_aci_plugin:acileafinterfaceoverride_edit",
            condition=lambda ctx: ctx["object"].leaf_interface_override is not None,
            permissions=["netbox_aci_plugin.change_acileafinterfaceoverride"],
            label=_("Edit"),
            button_class="warning",
            button_icon="pencil",
            view_kwargs={"pk": lambda ctx: ctx["object"].leaf_interface_override.pk},
        ),
        ACIObjectLinkAction(
            "plugins:netbox_aci_plugin:acileafinterfaceoverride_delete",
            condition=lambda ctx: ctx["object"].leaf_interface_override is not None,
            permissions=["netbox_aci_plugin.delete_acileafinterfaceoverride"],
            label=_("Delete"),
            button_class="danger",
            button_icon="trash-can-outline",
            view_kwargs={"pk": lambda ctx: ctx["object"].leaf_interface_override.pk},
        ),
    ]

    aci_leaf_interface_override = attrs.RelatedObjectAttr(
        "leaf_interface_override", linkify=True, label=_("Leaf Interface Override")
    )
    aci_leaf_interface_policy_group = attrs.RelatedObjectAttr(
        "leaf_interface_override.aci_leaf_interface_policy_group",
        linkify=True,
        label=_("Leaf Interface Policy Group"),
    )
