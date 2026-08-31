# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the ACI Leaf Switch Profile models."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = (
    "ACILeafNodeBlockPanel",
    "ACILeafNodeBlockRangePanel",
    "ACILeafSelectorPanel",
    "ACILeafSwitchProfileInterfaceBindingPanel",
    "ACILeafSwitchProfilePanel",
)


class ACILeafSwitchProfilePanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Leaf Switch Profile detail view."""

    title = _("ACI Leaf Switch Profile")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )
    selector_count = attrs.NumericAttr("selector_count", label=_("Selectors"))


class ACILeafSelectorPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Leaf Selector detail view."""

    title = _("ACI Leaf Selector")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_leaf_switch_profile = attrs.RelatedObjectAttr(
        "aci_leaf_switch_profile", linkify=True, label=_("ACI Leaf Switch Profile")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )
    node_block_count = attrs.NumericAttr("node_block_count", label=_("Node Blocks"))


class ACILeafNodeBlockPanel(panels.ObjectAttributesPanel):
    """Identity attribute panel for the ACI Leaf Node Block detail view."""

    title = _("ACI Leaf Node Block")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_leaf_switch_profile = attrs.RelatedObjectAttr(
        "aci_leaf_selector.aci_leaf_switch_profile",
        linkify=True,
        label=_("ACI Leaf Switch Profile"),
    )
    aci_leaf_selector = attrs.RelatedObjectAttr(
        "aci_leaf_selector", linkify=True, label=_("ACI Leaf Selector")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACILeafNodeBlockRangePanel(panels.ObjectAttributesPanel):
    """Node ID range attribute panel for an ACI Leaf Node Block."""

    title = _("Node ID Range")

    node_id_from = attrs.NumericAttr("node_id_from", label=_("Node ID (from)"))
    node_id_to = attrs.NumericAttr("node_id_to", label=_("Node ID (to)"))


class ACILeafSwitchProfileInterfaceBindingPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Leaf Switch Profile Interface Binding."""

    title = _("ACI Leaf Switch Profile Interface Binding")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_leaf_switch_profile = attrs.RelatedObjectAttr(
        "aci_leaf_switch_profile", linkify=True, label=_("ACI Leaf Switch Profile")
    )
    aci_leaf_interface_profile = attrs.RelatedObjectAttr(
        "aci_leaf_interface_profile",
        linkify=True,
        label=_("ACI Leaf Interface Profile"),
    )
