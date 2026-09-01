# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the tenant ACI Bridge Domain models."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = (
    "ACIBridgeDomainAdditionalSettingsPanel",
    "ACIBridgeDomainEndpointLearningPanel",
    "ACIBridgeDomainForwardingMethodPanel",
    "ACIBridgeDomainL3OutBindingPanel",
    "ACIBridgeDomainMulticastPanel",
    "ACIBridgeDomainPanel",
    "ACIBridgeDomainRoutingPanel",
    "ACIBridgeDomainSubnetControlPanel",
    "ACIBridgeDomainSubnetEndpointLearningPanel",
    "ACIBridgeDomainSubnetIPv6Panel",
    "ACIBridgeDomainSubnetPanel",
    "ACIBridgeDomainSubnetScopePanel",
)


class ACIBridgeDomainPanel(panels.ObjectAttributesPanel):
    """Identity attribute panel for the ACI Bridge Domain detail view."""

    title = _("ACI Bridge Domain")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    aci_vrf = attrs.RelatedObjectAttr("aci_vrf", linkify=True, label=_("ACI VRF"))
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACIBridgeDomainRoutingPanel(panels.ObjectAttributesPanel):
    """Routing attribute panel for the ACI Bridge Domain detail view."""

    title = _("Routing Settings")

    unicast_routing_enabled = attrs.BooleanAttr(
        "unicast_routing_enabled", label=_("Unicast Routing enabled")
    )
    advertise_host_routes_enabled = attrs.BooleanAttr(
        "advertise_host_routes_enabled", label=_("Advertise Host Routes enabled")
    )
    ep_move_detection_enabled = attrs.BooleanAttr(
        "ep_move_detection_enabled", label=_("Endpoint Move Detection enabled")
    )
    mac_address = attrs.TextAttr("mac_address", label=_("MAC Address"))
    virtual_mac_address = attrs.TextAttr(
        "virtual_mac_address", label=_("Virtual MAC Address")
    )


class ACIBridgeDomainForwardingMethodPanel(panels.ObjectAttributesPanel):
    """Forwarding method panel for the ACI Bridge Domain detail view."""

    title = _("Forwarding Method Settings")

    arp_flooding_enabled = attrs.BooleanAttr(
        "arp_flooding_enabled", label=_("ARP Flooding enabled")
    )
    unknown_unicast = attrs.ChoiceAttr("unknown_unicast", label=_("Unknown Unicast"))
    unknown_ipv4_multicast = attrs.ChoiceAttr(
        "unknown_ipv4_multicast", label=_("Unknown IPv4 Multicast")
    )
    unknown_ipv6_multicast = attrs.ChoiceAttr(
        "unknown_ipv6_multicast", label=_("Unknown IPv6 Multicast")
    )
    multi_destination_flooding = attrs.ChoiceAttr(
        "multi_destination_flooding", label=_("Multi Destination Flooding")
    )


class ACIBridgeDomainEndpointLearningPanel(panels.ObjectAttributesPanel):
    """Endpoint learning panel for the ACI Bridge Domain detail view."""

    title = _("Endpoint Learning Settings")

    ip_data_plane_learning_enabled = attrs.BooleanAttr(
        "ip_data_plane_learning_enabled", label=_("IP Data Plane Learning enabled")
    )
    limit_ip_learn_enabled = attrs.BooleanAttr(
        "limit_ip_learn_enabled", label=_("Limit IP Learn to Subnet enabled")
    )
    clear_remote_mac_enabled = attrs.BooleanAttr(
        "clear_remote_mac_enabled", label=_("Clear Remote MAC Entries enabled")
    )


class ACIBridgeDomainMulticastPanel(panels.ObjectAttributesPanel):
    """Multicast attribute panel for the ACI Bridge Domain detail view."""

    title = _("Multicast Settings")

    pim_ipv4_enabled = attrs.BooleanAttr(
        "pim_ipv4_enabled", label=_("PIM (Multicast) IPv4")
    )
    pim_ipv6_enabled = attrs.BooleanAttr(
        "pim_ipv6_enabled", label=_("PIM (Multicast) IPv6")
    )
    igmp_interface_policy_name = attrs.TextAttr(
        "igmp_interface_policy_name", label=_("IGMP Interface Policy")
    )
    igmp_snooping_policy_name = attrs.TextAttr(
        "igmp_snooping_policy_name", label=_("IGMP Snooping Policy")
    )
    pim_ipv4_source_filter = attrs.TextAttr(
        "pim_ipv4_source_filter", label=_("PIM IPv4 Source Filter")
    )
    pim_ipv4_destination_filter = attrs.TextAttr(
        "pim_ipv4_destination_filter", label=_("PIM IPv4 Destination Filter")
    )


class ACIBridgeDomainAdditionalSettingsPanel(panels.ObjectAttributesPanel):
    """Additional settings panel for the ACI Bridge Domain detail view."""

    title = _("Additional Settings")

    dhcp_labels = attrs.ArrayAttr("dhcp_labels", label=_("DHCP Labels"))


class ACIBridgeDomainSubnetPanel(panels.ObjectAttributesPanel):
    """Identity panel for the ACI Bridge Domain Subnet detail view."""

    title = _("ACI Bridge Domain Subnet")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_tenant", linkify=True, label=_("ACI Tenant")
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
    preferred_ip_address_enabled = attrs.BooleanAttr(
        "preferred_ip_address_enabled", label=_("Preferred IP address enabled")
    )
    virtual_ip_enabled = attrs.BooleanAttr(
        "virtual_ip_enabled", label=_("Virtual IP enabled")
    )


class ACIBridgeDomainSubnetScopePanel(panels.ObjectAttributesPanel):
    """Scope attribute panel for the ACI Bridge Domain Subnet detail view."""

    title = _("Scope Settings")

    advertised_externally_enabled = attrs.BooleanAttr(
        "advertised_externally_enabled", label=_("Advertised externally enabled")
    )
    shared_enabled = attrs.BooleanAttr("shared_enabled", label=_("Shared enabled"))


class ACIBridgeDomainSubnetControlPanel(panels.ObjectAttributesPanel):
    """Subnet control panel for the ACI Bridge Domain Subnet detail view."""

    title = _("Subnet Control Settings")

    igmp_querier_enabled = attrs.BooleanAttr(
        "igmp_querier_enabled", label=_("IGMP Querier enabled")
    )
    no_default_gateway = attrs.BooleanAttr(
        "no_default_gateway", label=_("No Default SVI Gateway")
    )


class ACIBridgeDomainSubnetEndpointLearningPanel(panels.ObjectAttributesPanel):
    """Endpoint learning attribute panel for the ACI BD Subnet detail view."""

    title = _("Endpoint Learning Settings")

    ip_data_plane_learning_enabled = attrs.BooleanAttr(
        "ip_data_plane_learning_enabled", label=_("IP Data Plane Learning enabled")
    )


class ACIBridgeDomainSubnetIPv6Panel(panels.ObjectAttributesPanel):
    """IPv6 attribute panel for the ACI Bridge Domain Subnet detail view."""

    title = _("IPv6 Settings")

    nd_ra_enabled = attrs.BooleanAttr("nd_ra_enabled", label=_("ND RA enabled"))
    nd_ra_prefix_policy_name = attrs.TextAttr(
        "nd_ra_prefix_policy_name", label=_("ND RA Prefix Policy")
    )


class ACIBridgeDomainL3OutBindingPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Bridge Domain L3Out Binding detail view."""

    title = _("ACI Bridge Domain L3Out Binding")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    aci_vrf = attrs.RelatedObjectAttr("aci_vrf", linkify=True, label=_("ACI VRF"))
    aci_bridge_domain = attrs.RelatedObjectAttr(
        "aci_bridge_domain", linkify=True, label=_("ACI Bridge Domain")
    )
    aci_l3out = attrs.RelatedObjectAttr("aci_l3out", linkify=True, label=_("ACI L3Out"))
