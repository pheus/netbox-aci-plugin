# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns

from ...models.tenant.bridge_domains import (
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)

BRIDGEDOMAIN_SUBNETS = """
{% for bd_subnet in value.all %}
    <a href="{% url 'plugins:netbox_aci_plugin:acibridgedomainsubnet' pk=bd_subnet.pk %}">
        {{ bd_subnet.gateway_ip_address }}
    </a>{% if not forloop.last %}<br />{% endif %}
{% endfor %}
"""


class ACIBridgeDomainTable(NetBoxTable):
    """NetBox table for the ACI Bridge Domain model."""

    name = tables.Column(
        verbose_name=_("Bridge Domain"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    aci_tenant = tables.Column(
        linkify=True,
    )
    aci_vrf = tables.Column(
        linkify=True,
    )
    nb_tenant = tables.Column(
        linkify=True,
    )
    advertise_host_routes_enabled = columns.BooleanColumn(
        verbose_name=_("Advertise host routes")
    )
    arp_flooding_enabled = columns.BooleanColumn(verbose_name=_("ARP flooding"))
    clear_remote_mac_enabled = columns.BooleanColumn(verbose_name=_("Clear remote MAC"))
    dhcp_labels = columns.ArrayColumn()
    ep_move_detection_enabled = columns.BooleanColumn(verbose_name=_("EP move detect"))
    ip_data_plane_learning_enabled = columns.BooleanColumn(
        verbose_name=_("DP learning"),
    )
    limit_ip_learn_enabled = columns.BooleanColumn(
        verbose_name=_("Limit IP learn"),
    )
    multi_destination_flooding = columns.ChoiceFieldColumn(
        verbose_name=_("Multi dest flooding"),
    )
    pim_ipv4_enabled = columns.BooleanColumn(
        verbose_name=_("PIM IPv4"),
    )
    pim_ipv6_enabled = columns.BooleanColumn(
        verbose_name=_("PIM IPv6"),
    )
    unicast_routing_enabled = columns.BooleanColumn(
        verbose_name=_("Unicast routing"),
    )
    unknown_ipv4_multicast = columns.ChoiceFieldColumn(
        verbose_name=_("Unknown IPv4 multicast"),
    )
    unknown_ipv6_multicast = columns.ChoiceFieldColumn(
        verbose_name=_("Unknown IPv6 multicast"),
    )
    unknown_unicast = columns.ChoiceFieldColumn(
        verbose_name=_("Unknown unicast"),
    )
    aci_bridge_domain_subnets = columns.TemplateColumn(
        verbose_name=_("BD Subnets"),
        orderable=False,
        template_code=BRIDGEDOMAIN_SUBNETS,
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIBridgeDomain
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "aci_tenant",
            "aci_vrf",
            "nb_tenant",
            "description",
            "advertise_host_routes_enabled",
            "arp_flooding_enabled",
            "clear_remote_mac_enabled",
            "dhcp_labels",
            "ep_move_detection_enabled",
            "igmp_interface_policy_name",
            "igmp_snooping_policy_name",
            "ip_data_plane_learning_enabled",
            "limit_ip_learn_enabled",
            "mac_address",
            "multi_destination_flooding",
            "pim_ipv4_enabled",
            "pim_ipv4_destination_filter",
            "pim_ipv4_source_filter",
            "pim_ipv6_enabled",
            "unicast_routing_enabled",
            "unknown_ipv4_multicast",
            "unknown_ipv6_multicast",
            "unknown_unicast",
            "virtual_mac_address",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "aci_vrf",
            "nb_tenant",
            "description",
            "unicast_routing_enabled",
            "tags",
        )


class ACIBridgeDomainSubnetTable(NetBoxTable):
    """NetBox table for the ACI Bridge Domain Subnet model."""

    name = tables.Column(
        verbose_name=_("Subnet Name"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    gateway_ip_address = tables.Column(
        verbose_name=_("Gateway IP"),
        linkify=True,
    )
    aci_tenant = tables.Column(
        verbose_name=_("ACI Tenant"),
        linkify=True,
    )
    aci_vrf = tables.Column(
        verbose_name=_("ACI VRF"),
        linkify=True,
    )
    aci_bridge_domain = tables.Column(
        linkify=True,
    )
    nb_tenant = tables.Column(
        linkify=True,
    )
    advertised_externally_enabled = columns.BooleanColumn(
        verbose_name=_("Advertised externally")
    )
    igmp_querier_enabled = columns.BooleanColumn(verbose_name=_("IGMP querier"))
    ip_data_plane_learning_enabled = columns.BooleanColumn(
        verbose_name=_("DP learning"),
    )
    no_default_gateway = columns.BooleanColumn(
        verbose_name=_("No default GW"),
    )
    nd_ra_enabled = columns.BooleanColumn(
        verbose_name=_("ND RA"),
    )
    preferred_ip_address_enabled = columns.BooleanColumn(
        verbose_name=_("Preferred"),
    )
    shared_enabled = columns.BooleanColumn(
        verbose_name=_("Shared"),
    )
    virtual_ip_enabled = columns.BooleanColumn(
        verbose_name=_("VIP"),
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIBridgeDomainSubnet
        fields: tuple = (
            "pk",
            "id",
            "name",
            "gateway_ip_address",
            "name_alias",
            "aci_tenant",
            "aci_vrf",
            "aci_bridge_domain",
            "nb_tenant",
            "description",
            "advertised_externally_enabled",
            "igmp_querier_enabled",
            "ip_data_plane_learning_enabled",
            "no_default_gateway",
            "nd_ra_enabled",
            "nd_ra_prefix_policy_name",
            "preferred_ip_address_enabled",
            "shared_enabled",
            "virtual_ip_enabled",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "gateway_ip_address",
            "name_alias",
            "aci_tenant",
            "aci_bridge_domain",
            "nb_tenant",
            "description",
            "advertised_externally_enabled",
            "preferred_ip_address_enabled",
            "shared_enabled",
            "tags",
        )


class ACIBridgeDomainSubnetReducedTable(NetBoxTable):
    """Reduced NetBox table for the ACI Bridge Domain Subnet model."""

    name = tables.Column(
        verbose_name=_("Subnet Name"),
        linkify=True,
    )
    gateway_ip_address = tables.Column(
        verbose_name=_("Gateway IP"),
        linkify=True,
    )

    class Meta(NetBoxTable.Meta):
        model = ACIBridgeDomainSubnet
        fields: tuple = (
            "pk",
            "id",
            "name",
            "gateway_ip_address",
        )
        default_columns: tuple = (
            "name",
            "gateway_ip_address",
        )
