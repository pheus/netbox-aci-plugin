# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the access-policy AAEP models."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = (
    "ACIAAEPDomainBindingPanel",
    "ACIAttachableAccessEntityProfilePanel",
)


class ACIAttachableAccessEntityProfilePanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Attachable Access Entity Profile view."""

    title = _("ACI Attachable Access Entity Profile")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    infra_vlan = attrs.BooleanAttr("infra_vlan", label=_("Infrastructure VLAN"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACIAAEPDomainBindingPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI AAEP Domain Binding detail view."""

    title = _("ACI AAEP Domain Binding")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_aaep = attrs.RelatedObjectAttr("aci_aaep", linkify=True, label=_("ACI AAEP"))
    aci_domain_object = attrs.GenericForeignKeyAttr(
        "aci_domain_object", linkify=True, label=_("ACI Domain Object")
    )
