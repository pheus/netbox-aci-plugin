# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ipam.api.serializers import VRFSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer

from ..models.tenant_app_profiles import ACIAppProfile
from ..models.tenant_networks import ACIVRF, ACIBridgeDomain
from ..models.tenants import ACITenant


class ACITenantSerializer(NetBoxModelSerializer):
    """Serializer for ACI Tenant model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acitenant-detail"
    )
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACITenant
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "alias",
            "description",
            "nb_tenant",
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
            "alias",
            "description",
            "nb_tenant",
        )


class ACIAppProfileSerializer(NetBoxModelSerializer):
    """Serializer for ACI Application Profile model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:aciappprofile-detail"
    )
    aci_tenant = ACITenantSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIAppProfile
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "alias",
            "description",
            "aci_tenant",
            "nb_tenant",
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
            "alias",
            "description",
            "aci_tenant",
            "nb_tenant",
        )


class ACIVRFSerializer(NetBoxModelSerializer):
    """Serializer for ACI VRF model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acivrf-detail"
    )
    aci_tenant = ACITenantSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    nb_vrf = VRFSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIVRF
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "alias",
            "description",
            "aci_tenant",
            "nb_tenant",
            "nb_vrf",
            "bd_enforcement_enabled",
            "dns_labels",
            "ip_data_plane_learning_enabled",
            "pc_enforcement_direction",
            "pc_enforcement_preference",
            "pim_ipv4_enabled",
            "pim_ipv6_enabled",
            "preferred_group_enabled",
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
            "alias",
            "description",
            "aci_tenant",
            "nb_tenant",
            "nb_vrf",
        )


class ACIBridgeDomainSerializer(NetBoxModelSerializer):
    """Serializer for ACI Bridge Domain model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acibridgedomain-detail"
    )
    aci_vrf = ACIVRFSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIBridgeDomain
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "alias",
            "description",
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
            "alias",
            "description",
            "aci_vrf",
            "nb_tenant",
        )
