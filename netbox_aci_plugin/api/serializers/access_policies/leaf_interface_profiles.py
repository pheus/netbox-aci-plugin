# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer
from users.api.serializers_.mixins import OwnerMixin

from ....models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
    ACILeafInterfaceSelector,
    ACILeafPortBlock,
)
from ..fabric.fabrics import ACIFabricSerializer
from .interface_policy_groups import ACILeafInterfacePolicyGroupSerializer


class ACILeafInterfaceProfileSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for the ACI Leaf Interface Profile model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acileafinterfaceprofile-detail"
    )
    aci_fabric = ACIFabricSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACILeafInterfaceProfile
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
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


class ACILeafInterfaceSelectorSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for the ACI Leaf Interface Selector model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acileafinterfaceselector-detail"
    )
    aci_leaf_interface_profile = ACILeafInterfaceProfileSerializer(
        nested=True, required=True
    )
    aci_leaf_interface_policy_group = ACILeafInterfacePolicyGroupSerializer(
        nested=True, required=False, allow_null=True
    )
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACILeafInterfaceSelector
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_leaf_interface_profile",
            "aci_leaf_interface_policy_group",
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
            "aci_leaf_interface_profile",
            "nb_tenant",
        )


class ACILeafPortBlockSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for the ACI Leaf Port Block model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acileafportblock-detail"
    )
    aci_leaf_interface_selector = ACILeafInterfaceSelectorSerializer(
        nested=True, required=True
    )
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACILeafPortBlock
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_leaf_interface_selector",
            "nb_tenant",
            "module_from",
            "module_to",
            "port_from",
            "port_to",
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
            "aci_leaf_interface_selector",
            "nb_tenant",
            "module_from",
            "module_to",
            "port_from",
            "port_to",
        )
