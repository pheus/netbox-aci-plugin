# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer
from users.api.serializers_.mixins import OwnerMixin

from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ..fabric.fabrics import ACIFabricSerializer
from .aaep import ACIAttachableAccessEntityProfileSerializer


class ACILeafInterfacePolicyGroupSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for the ACI Leaf Interface Policy Group model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acileafinterfacepolicygroup-detail"
    )
    aci_fabric = ACIFabricSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    aci_aaep = ACIAttachableAccessEntityProfileSerializer(
        nested=True, required=False, allow_null=True
    )

    class Meta:
        model = ACILeafInterfacePolicyGroup
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "nb_tenant",
            "aci_aaep",
            "group_type",
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
            "group_type",
        )
