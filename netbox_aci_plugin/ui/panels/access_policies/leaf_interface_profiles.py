# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the ACI Leaf Interface Profile models."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = (
    "ACILeafInterfaceProfilePanel",
    "ACILeafInterfaceSelectorPanel",
    "ACILeafPortBlockPanel",
    "ACILeafPortBlockRangePanel",
)


class ACILeafInterfaceProfilePanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Leaf Interface Profile detail view."""

    title = _("ACI Leaf Interface Profile")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )
    selector_count = attrs.NumericAttr("selector_count", label=_("Selectors"))


class ACILeafInterfaceSelectorPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Leaf Interface Selector detail view."""

    title = _("ACI Leaf Interface Selector")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_leaf_interface_profile = attrs.RelatedObjectAttr(
        "aci_leaf_interface_profile",
        linkify=True,
        label=_("ACI Leaf Interface Profile"),
    )
    aci_leaf_interface_policy_group = attrs.RelatedObjectAttr(
        "aci_leaf_interface_policy_group",
        linkify=True,
        label=_("ACI Leaf Interface Policy Group"),
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )
    port_block_count = attrs.NumericAttr("port_block_count", label=_("Port Blocks"))


class ACILeafPortBlockPanel(panels.ObjectAttributesPanel):
    """Identity attribute panel for the ACI Leaf Port Block detail view."""

    title = _("ACI Leaf Port Block")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_leaf_interface_profile = attrs.RelatedObjectAttr(
        "aci_leaf_interface_selector.aci_leaf_interface_profile",
        linkify=True,
        label=_("ACI Leaf Interface Profile"),
    )
    aci_leaf_interface_selector = attrs.RelatedObjectAttr(
        "aci_leaf_interface_selector",
        linkify=True,
        label=_("ACI Leaf Interface Selector"),
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACILeafPortBlockRangePanel(panels.ObjectAttributesPanel):
    """Module and port range attribute panel for an ACI Leaf Port Block."""

    title = _("Module and Port Ranges")

    module_from = attrs.NumericAttr("module_from", label=_("Module (from)"))
    module_to = attrs.NumericAttr("module_to", label=_("Module (to)"))
    port_from = attrs.NumericAttr("port_from", label=_("Port (from)"))
    port_to = attrs.NumericAttr("port_to", label=_("Port (to)"))
