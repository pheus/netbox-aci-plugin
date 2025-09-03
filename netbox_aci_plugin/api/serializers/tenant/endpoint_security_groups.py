# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer
from utilities.api import get_serializer_for_model

from ....constants import (
    ESG_ENDPOINT_GROUP_SELECTORS_MODELS,
    ESG_ENDPOINT_SELECTORS_MODELS,
)
from ....models.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroup,
    ACIEsgEndpointGroupSelector,
    ACIEsgEndpointSelector,
)
from .app_profiles import ACIAppProfileSerializer
from .vrfs import ACIVRFSerializer


class ACIEndpointSecurityGroupSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Endpoint Security Group model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:aciendpointsecuritygroup-detail"
    )
    aci_app_profile = ACIAppProfileSerializer(nested=True, required=True)
    aci_vrf = ACIVRFSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIEndpointSecurityGroup
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_app_profile",
            "aci_vrf",
            "nb_tenant",
            "admin_shutdown",
            "intra_esg_isolation_enabled",
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
            "aci_vrf",
            "nb_tenant",
        )


class ACIEsgEndpointGroupSelectorSerializer(NetBoxModelSerializer):
    """Serializer for the ACI ESG Endpoint Group (EPG) Selector model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:aciesgendpointgroupselector-detail"
    )
    aci_endpoint_security_group = ACIEndpointSecurityGroupSerializer(
        nested=True, required=True
    )
    aci_epg_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(ESG_ENDPOINT_GROUP_SELECTORS_MODELS),
        required=False,
        default=None,
        allow_null=True,
    )
    aci_epg_object_id = serializers.IntegerField(
        required=False,
        default=None,
        allow_null=True,
    )
    aci_epg_object = serializers.SerializerMethodField(read_only=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIEsgEndpointGroupSelector
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_endpoint_security_group",
            "aci_epg_object_type",
            "aci_epg_object_id",
            "aci_epg_object",
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
            "aci_endpoint_security_group",
            "aci_epg_object_type",
            "aci_epg_object_id",
            "aci_epg_object",
            "nb_tenant",
        )

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_aci_epg_object(self, obj):
        """Return the ACI EPG object as nested JSON."""
        if obj.aci_epg_object_id is None:
            return None
        serializer = get_serializer_for_model(obj.aci_epg_object)
        context = {"request": self.context["request"]}
        return serializer(obj.aci_epg_object, nested=True, context=context).data


class ACIEsgEndpointSelectorSerializer(NetBoxModelSerializer):
    """Serializer for the ACI ESG Endpoint Selector model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:aciesgendpointselector-detail"
    )
    aci_endpoint_security_group = ACIEndpointSecurityGroupSerializer(
        nested=True, required=True
    )
    ep_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(ESG_ENDPOINT_SELECTORS_MODELS),
        required=False,
        default=None,
        allow_null=True,
    )
    ep_object_id = serializers.IntegerField(
        required=False,
        default=None,
        allow_null=True,
    )
    ep_object = serializers.SerializerMethodField(read_only=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIEsgEndpointSelector
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_endpoint_security_group",
            "ep_object_type",
            "ep_object_id",
            "ep_object",
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
            "aci_endpoint_security_group",
            "ep_object_type",
            "ep_object_id",
            "ep_object",
            "nb_tenant",
        )

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_ep_object(self, obj):
        """Return the endpoint object as nested JSON."""
        if obj.ep_object_id is None:
            return None
        serializer = get_serializer_for_model(obj.ep_object)
        context = {"request": self.context["request"]}
        return serializer(obj.ep_object, nested=True, context=context).data
