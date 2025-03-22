# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer

from ....models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
)
from .app_profiles import ACIAppProfileSerializer
from .bridge_domains import ACIBridgeDomainSerializer


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


class ACIUSegEndpointGroupSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Endpoint Group model."""

    url = serializers.HyperlinkedIdentityField(
        view_name=(
            "plugins-api:netbox_aci_plugin-api:aciusegendpointgroup-detail"
        )
    )
    aci_app_profile = ACIAppProfileSerializer(nested=True, required=True)
    aci_bridge_domain = ACIBridgeDomainSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIUSegEndpointGroup
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
            "match_operator",
            "qos_class",
            "preferred_group_member_enabled",
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
