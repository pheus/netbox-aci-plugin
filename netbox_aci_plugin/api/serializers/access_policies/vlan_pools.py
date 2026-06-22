# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers

from ipam.api.serializers import VLANGroupSerializer
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer
from users.api.serializers_.mixins import OwnerMixin

from ....models.access_policies.vlan_pools import ACIVLANPool, ACIVLANPoolRange
from ..fabric.fabrics import ACIFabricSerializer


class ACIVLANPoolSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for the ACI VLAN Pool model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acivlanpool-detail"
    )
    aci_fabric = ACIFabricSerializer(nested=True, required=True)
    nb_vlan_group = VLANGroupSerializer(nested=True, required=False, allow_null=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIVLANPool
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "allocation_mode",
            "nb_vlan_group",
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
            "aci_fabric",
            "nb_tenant",
        )


class ACIVLANPoolRangeSerializer(NetBoxModelSerializer):
    """Serializer for the ACI VLAN Pool Range model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acivlanpoolrange-detail"
    )
    aci_vlan_pool = ACIVLANPoolSerializer(nested=True, required=True)

    class Meta:
        model = ACIVLANPoolRange
        fields: tuple = (
            "id",
            "url",
            "display",
            "aci_vlan_pool",
            "vlan_id_from",
            "vlan_id_to",
            "allocation_mode",
            "role",
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
            "aci_vlan_pool",
            "vlan_id_from",
            "vlan_id_to",
        )
