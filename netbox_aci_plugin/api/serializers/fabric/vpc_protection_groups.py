# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer
from users.api.serializers_.mixins import OwnerMixin

from ....models.fabric.vpc_protection_groups import ACIVPCProtectionGroup
from .fabrics import ACIFabricSerializer
from .nodes import ACINodeSerializer


class ACIVPCProtectionGroupSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for the ACI VPC Protection Group model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acivpcprotectiongroup-detail"
    )
    aci_fabric = ACIFabricSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    aci_node_a = ACINodeSerializer(nested=True, required=True)
    aci_node_b = ACINodeSerializer(nested=True, required=True)

    class Meta:
        model = ACIVPCProtectionGroup
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "nb_tenant",
            "aci_node_a",
            "aci_node_b",
            "logical_pair_id",
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
            "aci_fabric",
            "logical_pair_id",
            "nb_tenant",
            "aci_node_a",
            "aci_node_b",
        )
