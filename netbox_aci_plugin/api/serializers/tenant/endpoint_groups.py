# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer
from utilities.api import get_serializer_for_model

from ....constants import USEG_NETWORK_ATTRIBUTES_MODELS
from ....models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
    ACIUSegNetworkAttribute,
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
        view_name=("plugins-api:netbox_aci_plugin-api:aciusegendpointgroup-detail")
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


class ACIUSegNetworkAttributeSerializer(NetBoxModelSerializer):
    """Serializer for the ACI uSeg Network Attribute model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:aciusegnetworkattribute-detail"
    )
    aci_useg_endpoint_group = ACIUSegEndpointGroupSerializer(nested=True, required=True)
    attr_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(USEG_NETWORK_ATTRIBUTES_MODELS),
        required=False,
        default=None,
        allow_null=True,
    )
    attr_object_id = serializers.IntegerField(
        required=False,
        default=None,
        allow_null=True,
    )
    attr_object = serializers.SerializerMethodField(read_only=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIUSegNetworkAttribute
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_useg_endpoint_group",
            "attr_object_type",
            "attr_object_id",
            "attr_object",
            "nb_tenant",
            "use_epg_subnet",
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
            "aci_useg_endpoint_group",
            "attr_object_type",
            "attr_object_id",
            "attr_object",
            "use_epg_subnet",
        )

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_attr_object(self, obj):
        """Return the attribute object as nested JSON."""
        if obj.attr_object_id is None:
            return None
        serializer = get_serializer_for_model(obj.attr_object)
        context = {"request": self.context["request"]}
        return serializer(obj.attr_object, nested=True, context=context).data
