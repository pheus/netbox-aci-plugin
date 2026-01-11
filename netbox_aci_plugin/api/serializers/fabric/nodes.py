# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from ipam.api.serializers import IPAddressSerializer
from netbox.api.fields import ContentTypeField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer
from users.api.serializers_.mixins import OwnerMixin

from ....constants import NODE_OBJECT_TYPES
from ....models.fabric.nodes import ACINode
from .pods import ACIPodSerializer


class ACINodeSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for the ACI Node model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acinode-detail"
    )
    aci_pod = ACIPodSerializer(nested=True, required=True)
    node_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(NODE_OBJECT_TYPES),
        required=False,
        default=None,
        allow_null=True,
    )
    node_object_id = serializers.IntegerField(
        required=False,
        default=None,
        allow_null=True,
    )
    node_object = GFKSerializerField(read_only=True)
    tep_ip_address = IPAddressSerializer(nested=True, required=False, allow_null=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACINode
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_pod",
            "node_object_type",
            "node_object_id",
            "node_object",
            "node_id",
            "role",
            "node_type",
            "tep_ip_address",
            "nb_tenant",
            "owner",
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
            "aci_pod",
            "node_id",
            "nb_tenant",
        )
