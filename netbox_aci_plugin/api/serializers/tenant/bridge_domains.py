# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ipam.api.serializers import IPAddressSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer

from ....models.tenant.bridge_domains import (
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)
from .tenants import ACITenantSerializer
from .vrfs import ACIVRFSerializer


class ACIBridgeDomainSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Bridge Domain model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acibridgedomain-detail"
    )
    aci_tenant = ACITenantSerializer(nested=True, required=True)
    aci_vrf = ACIVRFSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    mac_address = serializers.CharField(
        required=False, default=None, allow_blank=True, allow_null=True
    )
    virtual_mac_address = serializers.CharField(
        required=False, default=None, allow_blank=True, allow_null=True
    )

    class Meta:
        model = ACIBridgeDomain
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "aci_vrf",
            "nb_tenant",
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
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "aci_vrf",
            "nb_tenant",
        )


class ACIBridgeDomainSubnetSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Bridge Domain Subnet model."""

    url = serializers.HyperlinkedIdentityField(
        view_name=("plugins-api:netbox_aci_plugin-api:acibridgedomainsubnet-detail")
    )
    aci_bridge_domain = ACIBridgeDomainSerializer(nested=True, required=True)
    gateway_ip_address = IPAddressSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIBridgeDomainSubnet
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_bridge_domain",
            "gateway_ip_address",
            "nb_tenant",
            "advertised_externally_enabled",
            "igmp_querier_enabled",
            "ip_data_plane_learning_enabled",
            "no_default_gateway",
            "nd_ra_enabled",
            "nd_ra_prefix_policy_name",
            "preferred_ip_address_enabled",
            "shared_enabled",
            "virtual_ip_enabled",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "gateway_ip_address",
            "aci_bridge_domain",
            "nb_tenant",
        )
