# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the tenant ACI Endpoint Group binding models."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = (
    "ACIEndpointGroupAAEPBindingPanel",
    "ACIEndpointGroupDomainBindingPanel",
)


class ACIEndpointGroupDomainBindingPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Endpoint Group Domain Binding detail view.

    The only dual-GFK card in the plugin: the EPG side and the domain
    side are each their own GenericForeignKey.
    """

    title = _("ACI Endpoint Group Domain Binding")
    aci_epg_object = attrs.GenericForeignKeyAttr(
        "aci_epg_object", linkify=True, label=_("ACI EPG Object")
    )
    aci_domain_object = attrs.GenericForeignKeyAttr(
        "aci_domain_object", linkify=True, label=_("ACI Domain Object")
    )
    deployment_immediacy = attrs.ChoiceAttr(
        "deployment_immediacy", label=_("Deployment Immediacy")
    )
    resolution_immediacy = attrs.ChoiceAttr(
        "resolution_immediacy", label=_("Resolution Immediacy")
    )


class ACIEndpointGroupAAEPBindingPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Endpoint Group AAEP Binding detail view."""

    title = _("ACI Endpoint Group AAEP Binding")
    aci_endpoint_group = attrs.RelatedObjectAttr(
        "aci_endpoint_group", linkify=True, label=_("ACI Endpoint Group")
    )
    aci_aaep = attrs.RelatedObjectAttr("aci_aaep", linkify=True, label=_("ACI AAEP"))
    mode = attrs.ChoiceAttr("mode", label=_("Mode"))
    deployment_immediacy = attrs.ChoiceAttr(
        "deployment_immediacy", label=_("Deployment Immediacy")
    )
    nb_vlan = attrs.RelatedObjectAttr("nb_vlan", linkify=True, label=_("NetBox VLAN"))
    encap_vlan_id = attrs.NumericAttr("encap_vlan_id", label=_("Encap VLAN ID"))
    effective_encap_vlan_id = attrs.NumericAttr(
        "effective_encap_vlan_id", label=_("Effective Encap VLAN ID")
    )
    primary_nb_vlan = attrs.RelatedObjectAttr(
        "primary_nb_vlan", linkify=True, label=_("Primary NetBox VLAN")
    )
    primary_encap_vlan_id = attrs.NumericAttr(
        "primary_encap_vlan_id", label=_("Primary Encap VLAN ID")
    )
    effective_primary_encap_vlan_id = attrs.NumericAttr(
        "effective_primary_encap_vlan_id",
        label=_("Effective Primary Encap VLAN ID"),
    )
