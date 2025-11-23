# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from ipam.api.serializers import IPAddressSerializer
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer
from utilities.api import get_serializer_for_model

from ....constants import NODE_OBJECT_TYPES
from ....models.fabric.nodes import ACINode
from .pods import ACIPodSerializer


class ACINodeSerializer(NetBoxModelSerializer):
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
    node_object = serializers.SerializerMethodField(read_only=True)
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

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_node_object(self, obj):
        """Return the node object as nested JSON."""
        if obj.node_object_id is None:
            return None
        serializer = get_serializer_for_model(obj.node_object)
        context = {"request": self.context["request"]}
        return serializer(obj.node_object, nested=True, context=context).data
