# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the tenant ACI Endpoint Security Group models."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = (
    "ACIEndpointSecurityGroupPanel",
    "ACIEndpointSecurityGroupPolicyEnforcementPanel",
    "ACIEsgEndpointGroupSelectorAssignmentPanel",
    "ACIEsgEndpointGroupSelectorPanel",
    "ACIEsgEndpointSelectorAssignmentPanel",
    "ACIEsgEndpointSelectorPanel",
)


class ACIEndpointSecurityGroupPanel(panels.ObjectAttributesPanel):
    """Identity panel for the ACI Endpoint Security Group detail view."""

    title = _("ACI Endpoint Security Group")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    aci_app_profile = attrs.RelatedObjectAttr(
        "aci_app_profile", linkify=True, label=_("ACI Application Profile")
    )
    aci_vrf = attrs.RelatedObjectAttr("aci_vrf", linkify=True, label=_("ACI VRF"))
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACIEndpointSecurityGroupPolicyEnforcementPanel(panels.ObjectAttributesPanel):
    """Policy enforcement attribute panel for the ACI ESG detail view."""

    title = _("Policy Enforcement Settings")

    preferred_group_member_enabled = attrs.BooleanAttr(
        "preferred_group_member_enabled", label=_("Preferred Group Member enabled")
    )
    intra_esg_isolation_enabled = attrs.BooleanAttr(
        "intra_esg_isolation_enabled", label=_("Intra-ESG Isolation enabled")
    )


class ACIEsgEndpointGroupSelectorPanel(panels.ObjectAttributesPanel):
    """Identity panel for the ACI ESG Endpoint Group Selector detail view."""

    title = _("ACI ESG Endpoint Group Selector")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    aci_app_profile = attrs.RelatedObjectAttr(
        "aci_app_profile", linkify=True, label=_("ACI Application Profile")
    )
    aci_endpoint_security_group = attrs.RelatedObjectAttr(
        "aci_endpoint_security_group",
        linkify=True,
        label=_("ACI Endpoint Security Group"),
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACIEsgEndpointGroupSelectorAssignmentPanel(panels.ObjectAttributesPanel):
    """EPG assignment attribute panel for the ACI ESG EPG Selector detail view.

    The retired template used the selected object's content type name as
    the third row's label, which no static ObjectAttribute label can
    express (ObjectAttributesPanel always renders a fixed label per
    declared attribute). A TemplatedAttr renders the type as a muted
    sub-line under the linked value instead, preserving both pieces of
    information the original row carried.
    """

    title = _("Endpoint Group (EPG) Assignment")

    aci_tenant = attrs.RelatedObjectAttr(
        "aci_epg_object.aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    aci_app_profile = attrs.RelatedObjectAttr(
        "aci_epg_object.aci_app_profile",
        linkify=True,
        label=_("ACI Application Profile"),
    )
    aci_epg_object = attrs.TemplatedAttr(
        "aci_epg_object",
        template_name="netbox_aci_plugin/attrs/esg_endpoint_group_selector.html",
        label=_("Endpoint Group"),
    )


class ACIEsgEndpointSelectorPanel(panels.ObjectAttributesPanel):
    """Identity panel for the ACI ESG Endpoint Selector detail view."""

    title = _("ACI ESG Endpoint Selector")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    aci_app_profile = attrs.RelatedObjectAttr(
        "aci_app_profile", linkify=True, label=_("ACI Application Profile")
    )
    aci_endpoint_security_group = attrs.RelatedObjectAttr(
        "aci_endpoint_security_group",
        linkify=True,
        label=_("ACI Endpoint Security Group"),
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACIEsgEndpointSelectorAssignmentPanel(panels.ObjectAttributesPanel):
    """Endpoint assignment panel for the ACI ESG EP Selector detail view."""

    title = _("Endpoint Assignment")

    ep_object = attrs.GenericForeignKeyAttr(
        "ep_object", linkify=True, label=_("Endpoint Object")
    )
