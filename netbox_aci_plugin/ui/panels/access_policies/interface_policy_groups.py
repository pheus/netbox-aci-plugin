# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the ACI Leaf Interface Policy Group model."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = ("ACILeafInterfacePolicyGroupPanel",)


class ACILeafInterfacePolicyGroupPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Leaf Interface Policy Group detail view."""

    title = _("ACI Leaf Interface Policy Group")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    group_type = attrs.ChoiceAttr("group_type", label=_("Type"))
    aci_aaep = attrs.RelatedObjectAttr("aci_aaep", linkify=True, label=_("ACI AAEP"))
    lag_type = attrs.TextAttr("lag_type", label=_("LAG Type"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )
