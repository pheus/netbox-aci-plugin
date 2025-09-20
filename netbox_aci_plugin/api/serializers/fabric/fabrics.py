# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.constants import LOCATION_SCOPE_TYPES
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from ipam.api.serializers import PrefixSerializer, VLANSerializer
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer
from utilities.api import get_serializer_for_model

from ....models.fabric.fabrics import ACIFabric


class ACIFabricSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Fabric model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acifabric-detail"
    )
    infra_vlan = VLANSerializer(nested=True, required=False, allow_null=True)
    gipo_pool = PrefixSerializer(nested=True, required=False, allow_null=True)
    scope_type = ContentTypeField(
        queryset=ContentType.objects.filter(model__in=LOCATION_SCOPE_TYPES),
        required=False,
        default=None,
        allow_null=True,
    )
    scope_id = serializers.IntegerField(
        required=False,
        default=None,
        allow_null=True,
    )
    scope = serializers.SerializerMethodField(read_only=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIFabric
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "fabric_id",
            "infra_vlan_vid",
            "infra_vlan",
            "gipo_pool",
            "scope_type",
            "scope_id",
            "scope",
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
            "description",
            "fabric_id",
            "nb_tenant",
        )

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_scope(self, obj):
        """Return the attribute object as nested JSON."""
        if obj.scope_id is None:
            return None
        serializer = get_serializer_for_model(obj.scope)
        context = {"request": self.context["request"]}
        return serializer(obj.scope, nested=True, context=context).data
