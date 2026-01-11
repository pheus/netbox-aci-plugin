# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.constants import LOCATION_SCOPE_TYPES
from django.contrib.contenttypes.models import ContentType
from ipam.api.serializers import PrefixSerializer, VLANSerializer
from netbox.api.fields import ContentTypeField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer
from users.api.serializers_.mixins import OwnerMixin

from ....models.fabric.fabrics import ACIFabric


class ACIFabricSerializer(OwnerMixin, NetBoxModelSerializer):
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
    scope = GFKSerializerField(read_only=True)
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
            "description",
            "fabric_id",
            "nb_tenant",
        )
