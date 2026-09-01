# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the access-policy domain models."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = (
    "ACIPhysicalDomainPanel",
    "ACIRoutedDomainPanel",
)


class ACIPhysicalDomainPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Physical Domain detail view."""

    title = _("ACI Physical Domain")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_vlan_pool = attrs.RelatedObjectAttr(
        "aci_vlan_pool", linkify=True, label=_("VLAN Pool")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    security_domains = attrs.ArrayAttr("security_domains", label=_("Security Domains"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACIRoutedDomainPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Routed Domain detail view."""

    title = _("ACI Routed Domain")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_vlan_pool = attrs.RelatedObjectAttr(
        "aci_vlan_pool", linkify=True, label=_("VLAN Pool")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    security_domains = attrs.ArrayAttr("security_domains", label=_("Security Domains"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )
