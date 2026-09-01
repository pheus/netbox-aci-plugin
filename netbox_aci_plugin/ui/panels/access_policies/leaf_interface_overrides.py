# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the ACI Leaf Interface Override model."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = ("ACILeafInterfaceOverridePanel",)


class ACILeafInterfaceOverridePanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Leaf Interface Override detail view."""

    title = _("ACI Leaf Interface Override")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_node_interface = attrs.RelatedObjectAttr(
        "aci_node_interface", linkify=True, label=_("ACI Node Interface")
    )
    aci_leaf_interface_policy_group = attrs.RelatedObjectAttr(
        "aci_leaf_interface_policy_group",
        linkify=True,
        label=_("ACI Leaf Interface Policy Group"),
    )
    description = attrs.TextAttr("description", label=_("Description"))
