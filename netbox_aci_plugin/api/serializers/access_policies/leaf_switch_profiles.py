# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer
from users.api.serializers_.mixins import OwnerMixin

from ....models.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlock,
    ACILeafSelector,
    ACILeafSwitchProfile,
    ACILeafSwitchProfileInterfaceBinding,
)
from ..fabric.fabrics import ACIFabricSerializer
from .leaf_interface_profiles import ACILeafInterfaceProfileSerializer


class ACILeafSwitchProfileSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for the ACI Leaf Switch Profile model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acileafswitchprofile-detail"
    )
    aci_fabric = ACIFabricSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACILeafSwitchProfile
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


class ACILeafSelectorSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for the ACI Leaf Selector model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acileafselector-detail"
    )
    aci_leaf_switch_profile = ACILeafSwitchProfileSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACILeafSelector
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_leaf_switch_profile",
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
            "aci_leaf_switch_profile",
            "nb_tenant",
        )


class ACILeafNodeBlockSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for the ACI Leaf Node Block model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acileafnodeblock-detail"
    )
    aci_leaf_selector = ACILeafSelectorSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACILeafNodeBlock
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_leaf_selector",
            "nb_tenant",
            "node_id_from",
            "node_id_to",
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
            "aci_leaf_selector",
            "nb_tenant",
            "node_id_from",
            "node_id_to",
        )


class ACILeafSwitchProfileInterfaceBindingSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Leaf Switch Profile Interface Binding model."""

    url = serializers.HyperlinkedIdentityField(
        view_name=(
            "plugins-api:netbox_aci_plugin-api:"
            "acileafswitchprofileinterfacebinding-detail"
        ),
    )
    aci_leaf_switch_profile = ACILeafSwitchProfileSerializer(nested=True, required=True)
    aci_leaf_interface_profile = ACILeafInterfaceProfileSerializer(
        nested=True, required=True
    )

    class Meta:
        model = ACILeafSwitchProfileInterfaceBinding
        fields: tuple = (
            "id",
            "url",
            "display",
            "aci_leaf_switch_profile",
            "aci_leaf_interface_profile",
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
            "aci_leaf_switch_profile",
            "aci_leaf_interface_profile",
        )
