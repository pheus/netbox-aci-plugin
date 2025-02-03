# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer

from ...models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup
from .tenant_networks import ACIBridgeDomainSerializer
from .tenants import ACITenantSerializer


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
