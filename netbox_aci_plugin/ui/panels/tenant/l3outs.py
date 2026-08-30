# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the tenant ACI L3Out models."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = (
    "ACIExternalEndpointGroupPanel",
    "ACIExternalEndpointGroupPolicyPanel",
    "ACIExternalSubnetPanel",
    "ACIExternalSubnetRouteSummarizationPanel",
    "ACIExternalSubnetScopePanel",
    "ACIL3OutPanel",
    "ACIL3OutPolicyPanel",
    "ACIL3OutPolicyReferencesPanel",
    "ACIL3OutProtocolsPanel",
)


class ACIL3OutPanel(panels.ObjectAttributesPanel):
    """Identity attribute panel for the ACI L3Out detail view."""

    title = _("ACI L3Out")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    aci_vrf = attrs.RelatedObjectAttr("aci_vrf", linkify=True, label=_("ACI VRF"))
    aci_routed_domain = attrs.RelatedObjectAttr(
        "aci_routed_domain", linkify=True, label=_("ACI Routed Domain")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACIL3OutPolicyPanel(panels.ObjectAttributesPanel):
    """Policy attribute panel for the ACI L3Out detail view."""

    title = _("Policy")

    target_dscp = attrs.ChoiceAttr("target_dscp", label=_("Target DSCP"))
    import_route_control_enforcement_enabled = attrs.BooleanAttr(
        "import_route_control_enforcement_enabled",
        label=_("Import Route Control Enforcement"),
    )
    export_route_control_enforcement_enabled = attrs.BooleanAttr(
        "export_route_control_enforcement_enabled",
        label=_("Export Route Control Enforcement"),
    )


class ACIL3OutProtocolsPanel(panels.ObjectAttributesPanel):
    """Protocols attribute panel for the ACI L3Out detail view."""

    title = _("Protocols")

    bgp_enabled = attrs.BooleanAttr("bgp_enabled", label=_("BGP"))
    ospf_enabled = attrs.BooleanAttr("ospf_enabled", label=_("OSPF"))
    eigrp_enabled = attrs.BooleanAttr("eigrp_enabled", label=_("EIGRP"))
    l3_multicast_ipv4_enabled = attrs.BooleanAttr(
        "l3_multicast_ipv4_enabled", label=_("L3 Multicast IPv4")
    )
    l3_multicast_ipv6_enabled = attrs.BooleanAttr(
        "l3_multicast_ipv6_enabled", label=_("L3 Multicast IPv6")
    )


class ACIL3OutPolicyReferencesPanel(panels.ObjectAttributesPanel):
    """Policy references attribute panel for the ACI L3Out detail view."""

    title = _("Policy References")

    custom_qos_policy_name = attrs.TextAttr(
        "custom_qos_policy_name", label=_("Custom QoS Policy")
    )
    bfd_policy_name = attrs.TextAttr("bfd_policy_name", label=_("BFD Policy"))
    pim_policy_name = attrs.TextAttr("pim_policy_name", label=_("PIM Policy"))
    igmp_interface_policy_name = attrs.TextAttr(
        "igmp_interface_policy_name", label=_("IGMP Interface Policy")
    )
    ospf_external_policy_name = attrs.TextAttr(
        "ospf_external_policy_name", label=_("OSPF External Policy")
    )
    eigrp_interface_policy_name = attrs.TextAttr(
        "eigrp_interface_policy_name", label=_("EIGRP Interface Policy")
    )
    interleak_route_map_name = attrs.TextAttr(
        "interleak_route_map_name", label=_("Interleak Route Map")
    )
    ingress_data_plane_policing_policy_name = attrs.TextAttr(
        "ingress_data_plane_policing_policy_name",
        label=_("Ingress Data Plane Policing"),
    )
    egress_data_plane_policing_policy_name = attrs.TextAttr(
        "egress_data_plane_policing_policy_name",
        label=_("Egress Data Plane Policing"),
    )


class ACIExternalEndpointGroupPanel(panels.ObjectAttributesPanel):
    """Identity attribute panel for the ACI External EPG detail view."""

    title = _("ACI External EPG")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    aci_vrf = attrs.RelatedObjectAttr("aci_vrf", linkify=True, label=_("ACI VRF"))
    aci_l3out = attrs.RelatedObjectAttr("aci_l3out", linkify=True, label=_("ACI L3Out"))
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACIExternalEndpointGroupPolicyPanel(panels.ObjectAttributesPanel):
    """Policy attribute panel for the ACI External EPG detail view."""

    title = _("Policy")

    preferred_group_member_enabled = attrs.BooleanAttr(
        "preferred_group_member_enabled", label=_("Preferred Group Member")
    )
    target_dscp = attrs.ChoiceAttr("target_dscp", label=_("Target DSCP"))
    qos_class = attrs.ChoiceAttr("qos_class", label=_("QoS Class"))


class ACIExternalSubnetPanel(panels.ObjectAttributesPanel):
    """Identity attribute panel for the ACI External Subnet detail view."""

    title = _("ACI External Subnet")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    aci_l3out = attrs.RelatedObjectAttr("aci_l3out", linkify=True, label=_("ACI L3Out"))
    aci_external_endpoint_group = attrs.RelatedObjectAttr(
        "aci_external_endpoint_group",
        linkify=True,
        label=_("ACI External EPG"),
    )
    matched_prefix = attrs.TextAttr("matched_prefix", label=_("Matched Prefix"))
    nb_prefix = attrs.RelatedObjectAttr(
        "nb_prefix", linkify=True, label=_("NetBox Prefix")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACIExternalSubnetScopePanel(panels.ObjectAttributesPanel):
    """Subnet scope attribute panel for the ACI External Subnet detail view."""

    title = _("Subnet Scope")

    import_route_control_enabled = attrs.BooleanAttr(
        "import_route_control_enabled", label=_("Import Route Control")
    )
    export_route_control_enabled = attrs.BooleanAttr(
        "export_route_control_enabled", label=_("Export Route Control")
    )
    shared_route_control_enabled = attrs.BooleanAttr(
        "shared_route_control_enabled", label=_("Shared Route Control")
    )
    import_security_enabled = attrs.BooleanAttr(
        "import_security_enabled", label=_("Import Security")
    )
    shared_security_enabled = attrs.BooleanAttr(
        "shared_security_enabled", label=_("Shared Security")
    )
    aggregate_import_route_control_enabled = attrs.BooleanAttr(
        "aggregate_import_route_control_enabled",
        label=_("Aggregate Import Route Control"),
    )
    aggregate_export_route_control_enabled = attrs.BooleanAttr(
        "aggregate_export_route_control_enabled",
        label=_("Aggregate Export Route Control"),
    )
    aggregate_shared_route_control_enabled = attrs.BooleanAttr(
        "aggregate_shared_route_control_enabled",
        label=_("Aggregate Shared Route Control"),
    )


class ACIExternalSubnetRouteSummarizationPanel(panels.ObjectAttributesPanel):
    """Route summarization panel for the ACI External Subnet detail view."""

    title = _("Route Summarization")

    bgp_route_summarization_enabled = attrs.BooleanAttr(
        "bgp_route_summarization_enabled", label=_("BGP Route Summarization")
    )
    bgp_route_summarization_policy_name = attrs.TextAttr(
        "bgp_route_summarization_policy_name", label=_("BGP Policy")
    )
    ospf_route_summarization_enabled = attrs.BooleanAttr(
        "ospf_route_summarization_enabled", label=_("OSPF Route Summarization")
    )
    ospf_route_summarization_policy_name = attrs.TextAttr(
        "ospf_route_summarization_policy_name", label=_("OSPF Policy")
    )
    eigrp_route_summarization_enabled = attrs.BooleanAttr(
        "eigrp_route_summarization_enabled", label=_("EIGRP Route Summarization")
    )
