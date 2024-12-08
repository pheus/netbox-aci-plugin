# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ipam.api.serializers import IPAddressSerializer, VRFSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer

from ..models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup
from ..models.tenant_contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from ..models.tenant_contracts import (
    ACIContract,
    ACIContractSubject,
    ACIContractSubjectFilter,
)
from ..models.tenant_networks import (
    ACIVRF,
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)
from ..models.tenants import ACITenant


class ACITenantSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Tenant model."""

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
            "name_alias",
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
            "name_alias",
            "description",
            "nb_tenant",
        )


class ACIAppProfileSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Application Profile model."""

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
            "name_alias",
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
            "name_alias",
            "description",
            "aci_tenant",
            "nb_tenant",
        )


class ACIVRFSerializer(NetBoxModelSerializer):
    """Serializer for the ACI VRF model."""

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
            "name_alias",
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
            "name_alias",
            "description",
            "aci_tenant",
            "nb_tenant",
            "nb_vrf",
        )


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
        view_name=(
            "plugins-api:netbox_aci_plugin-api:acibridgedomainsubnet-detail"
        )
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


class ACIEndpointGroupSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Endpoint Group model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:aciendpointgroup-detail"
    )
    aci_app_profile = ACIAppProfileSerializer(nested=True, required=True)
    aci_bridge_domain = ACIBridgeDomainSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIEndpointGroup
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_app_profile",
            "aci_bridge_domain",
            "nb_tenant",
            "description",
            "admin_shutdown",
            "custom_qos_policy_name",
            "flood_in_encap_enabled",
            "intra_epg_isolation_enabled",
            "qos_class",
            "preferred_group_member_enabled",
            "proxy_arp_enabled",
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
            "aci_app_profile",
            "aci_bridge_domain",
            "nb_tenant",
        )


class ACIContractFilterSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Contract Filter model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acicontractfilter-detail"
    )
    aci_tenant = ACITenantSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIContractFilter
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
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
            "name_alias",
            "description",
            "aci_tenant",
            "nb_tenant",
        )


class ACIContractFilterEntrySerializer(NetBoxModelSerializer):
    """Serializer for the ACI Contract Filter Entry model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:"
        "acicontractfilterentry-detail"
    )
    aci_contract_filter = ACIContractFilterSerializer(
        nested=True, required=True
    )

    class Meta:
        model = ACIContractFilterEntry
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_contract_filter",
            "arp_opc",
            "destination_from_port",
            "destination_to_port",
            "ether_type",
            "icmp_v4_type",
            "icmp_v6_type",
            "ip_protocol",
            "match_dscp",
            "match_only_fragments_enabled",
            "source_from_port",
            "source_to_port",
            "stateful_enabled",
            "tcp_rules",
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
            "aci_contract_filter",
        )


class ACIContractSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Contract model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acicontract-detail"
    )
    aci_tenant = ACITenantSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIContract
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "nb_tenant",
            "qos_class",
            "scope",
            "target_dscp",
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
            "nb_tenant",
            "scope",
        )


class ACIContractSubjectSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Contract Subject model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acicontractsubject-detail"
    )
    aci_contract = ACIContractSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIContractSubject
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_contract",
            "nb_tenant",
            "apply_both_directions_enabled",
            "qos_class",
            "qos_class_cons_to_prov",
            "qos_class_prov_to_cons",
            "reverse_filter_ports_enabled",
            "service_graph_name",
            "service_graph_name_cons_to_prov",
            "service_graph_name_prov_to_cons",
            "target_dscp",
            "target_dscp_cons_to_prov",
            "target_dscp_prov_to_cons",
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
            "aci_contract",
            "nb_tenant",
        )


class ACIContractSubjectFilterSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Contract Subject Filter model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:"
        "acicontractsubjectfilter-detail"
    )
    aci_contract_filter = ACIContractFilterSerializer(
        nested=True, required=True
    )
    aci_contract_subject = ACIContractSubjectSerializer(
        nested=True, required=True
    )

    class Meta:
        model = ACIContractSubjectFilter
        fields: tuple = (
            "id",
            "url",
            "display",
            "aci_contract_filter",
            "aci_contract_subject",
            "action",
            "apply_direction",
            "log_enabled",
            "policy_compression_enabled",
            "priority",
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
            "aci_contract_filter",
            "aci_contract_subject",
            "action",
        )
