# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the tenant ACI Endpoint Group models."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = (
    "ACIEndpointGroupForwardingPanel",
    "ACIEndpointGroupPanel",
    "ACIEndpointGroupPolicyEnforcementPanel",
    "ACIEndpointGroupQoSPanel",
    "ACIUSegEndpointGroupForwardingPanel",
    "ACIUSegEndpointGroupPanel",
    "ACIUSegEndpointGroupPolicyEnforcementPanel",
    "ACIUSegEndpointGroupQoSPanel",
    "ACIUSegNetworkAttributeAssignmentPanel",
    "ACIUSegNetworkAttributeEPGSubnetPanel",
    "ACIUSegNetworkAttributePanel",
)


class ACIEndpointGroupPanel(panels.ObjectAttributesPanel):
    """Identity attribute panel for the ACI Endpoint Group detail view."""

    title = _("ACI Endpoint Group")
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
    aci_bridge_domain = attrs.RelatedObjectAttr(
        "aci_bridge_domain", linkify=True, label=_("ACI Bridge Domain")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACIEndpointGroupPolicyEnforcementPanel(panels.ObjectAttributesPanel):
    """Policy enforcement panel for the ACI Endpoint Group detail view."""

    title = _("Policy Enforcement Settings")

    preferred_group_member_enabled = attrs.BooleanAttr(
        "preferred_group_member_enabled", label=_("Preferred Group Member enabled")
    )
    intra_epg_isolation_enabled = attrs.BooleanAttr(
        "intra_epg_isolation_enabled", label=_("Intra-EPG Isolation enabled")
    )


class ACIEndpointGroupForwardingPanel(panels.ObjectAttributesPanel):
    """Endpoint forwarding panel for the ACI Endpoint Group detail view."""

    title = _("Endpoint Forwarding Settings")

    flood_in_encap_enabled = attrs.BooleanAttr(
        "flood_in_encap_enabled", label=_("Flood in Encapsulation enabled")
    )
    proxy_arp_enabled = attrs.BooleanAttr(
        "proxy_arp_enabled", label=_("Proxy ARP enabled")
    )


class ACIEndpointGroupQoSPanel(panels.ObjectAttributesPanel):
    """QoS attribute panel for the ACI Endpoint Group detail view."""

    title = _("Quality of Service (QoS) Settings")

    qos_class = attrs.ChoiceAttr("qos_class", label=_("QoS Class"))
    custom_qos_policy_name = attrs.TextAttr(
        "custom_qos_policy_name", label=_("Custom QoS Policy")
    )


class ACIUSegEndpointGroupPanel(panels.ObjectAttributesPanel):
    """Identity attribute panel for the ACI uSeg Endpoint Group detail view."""

    title = _("ACI uSeg Endpoint Group")
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
    aci_bridge_domain = attrs.RelatedObjectAttr(
        "aci_bridge_domain", linkify=True, label=_("ACI Bridge Domain")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACIUSegEndpointGroupPolicyEnforcementPanel(panels.ObjectAttributesPanel):
    """Policy enforcement attribute panel for the ACI uSeg EPG detail view."""

    title = _("Policy Enforcement Settings")

    preferred_group_member_enabled = attrs.BooleanAttr(
        "preferred_group_member_enabled", label=_("Preferred Group Member enabled")
    )
    intra_epg_isolation_enabled = attrs.BooleanAttr(
        "intra_epg_isolation_enabled", label=_("Intra-EPG Isolation enabled")
    )


class ACIUSegEndpointGroupForwardingPanel(panels.ObjectAttributesPanel):
    """Endpoint forwarding panel for the ACI uSeg EPG detail view.

    ACIUSegEndpointGroup has no proxy_arp_enabled field.
    """

    title = _("Endpoint Forwarding Settings")

    flood_in_encap_enabled = attrs.BooleanAttr(
        "flood_in_encap_enabled", label=_("Flood in Encapsulation enabled")
    )


class ACIUSegEndpointGroupQoSPanel(panels.ObjectAttributesPanel):
    """QoS attribute panel for the ACI uSeg Endpoint Group detail view."""

    title = _("Quality of Service (QoS) Settings")

    qos_class = attrs.ChoiceAttr("qos_class", label=_("QoS Class"))
    custom_qos_policy_name = attrs.TextAttr(
        "custom_qos_policy_name", label=_("Custom QoS Policy")
    )


class ACIUSegNetworkAttributePanel(panels.ObjectAttributesPanel):
    """Identity panel for the ACI uSeg Network Attribute detail view."""

    title = _("ACI uSeg Network Attribute")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    aci_app_profile = attrs.RelatedObjectAttr(
        "aci_app_profile", linkify=True, label=_("ACI Application Profile")
    )
    aci_useg_endpoint_group = attrs.RelatedObjectAttr(
        "aci_useg_endpoint_group", linkify=True, label=_("ACI uSeg Endpoint Group")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    type = attrs.ChoiceAttr("type", label=_("Type"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACIUSegNetworkAttributeEPGSubnetPanel(panels.ObjectAttributesPanel):
    """EPG subnet panel for the ACI uSeg Network Attribute detail view."""

    title = _("EPG Subnet Settings")

    use_epg_subnet = attrs.BooleanAttr("use_epg_subnet", label=_("Use EPG Subnet"))


class ACIUSegNetworkAttributeAssignmentPanel(panels.ObjectAttributesPanel):
    """Attribute assignment panel for the ACI uSeg Network Attribute view."""

    title = _("Attribute Assignment")

    attr_object = attrs.GenericForeignKeyAttr(
        "attr_object", linkify=True, label=_("Attribute Object")
    )
