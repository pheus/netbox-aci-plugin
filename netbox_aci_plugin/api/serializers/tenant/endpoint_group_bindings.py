# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from netbox.api.fields import ContentTypeField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import NetBoxModelSerializer

from ....constants import (
    EPG_DOMAIN_BINDING_DOMAIN_OBJECT_TYPES,
    EPG_DOMAIN_BINDING_EPG_OBJECT_TYPES,
)
from ....models.tenant.endpoint_group_bindings import ACIEndpointGroupDomainBinding


class ACIEndpointGroupDomainBindingSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Endpoint Group Domain Binding model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:aciendpointgroupdomainbinding-detail"
    )
    aci_epg_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(EPG_DOMAIN_BINDING_EPG_OBJECT_TYPES),
        required=False,
        default=None,
        allow_null=True,
    )
    aci_epg_object_id = serializers.IntegerField(
        required=False,
        default=None,
        allow_null=True,
    )
    aci_epg_object = GFKSerializerField(read_only=True)
    aci_domain_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(EPG_DOMAIN_BINDING_DOMAIN_OBJECT_TYPES),
        required=False,
        default=None,
        allow_null=True,
    )
    aci_domain_object_id = serializers.IntegerField(
        required=False,
        default=None,
        allow_null=True,
    )
    aci_domain_object = GFKSerializerField(read_only=True)

    class Meta:
        model = ACIEndpointGroupDomainBinding
        fields: tuple = (
            "id",
            "url",
            "display",
            "aci_epg_object_type",
            "aci_epg_object_id",
            "aci_epg_object",
            "aci_domain_object_type",
            "aci_domain_object_id",
            "aci_domain_object",
            "deployment_immediacy",
            "resolution_immediacy",
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
            "aci_epg_object_type",
            "aci_epg_object_id",
            "aci_epg_object",
            "aci_domain_object_type",
            "aci_domain_object_id",
            "aci_domain_object",
        )
