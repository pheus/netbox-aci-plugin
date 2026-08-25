# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer

from ....models.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverride,
)
from ..fabric.node_interfaces import ACINodeInterfaceSerializer
from .interface_policy_groups import ACILeafInterfacePolicyGroupSerializer


class ACILeafInterfaceOverrideSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Leaf Interface Override model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acileafinterfaceoverride-detail"
    )
    aci_node_interface = ACINodeInterfaceSerializer(nested=True, required=True)
    aci_leaf_interface_policy_group = ACILeafInterfacePolicyGroupSerializer(
        nested=True, required=True
    )

    class Meta:
        model = ACILeafInterfaceOverride
        fields: tuple = (
            "id",
            "url",
            "display",
            "aci_node_interface",
            "aci_leaf_interface_policy_group",
            "description",
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
            "aci_node_interface",
            "aci_leaf_interface_policy_group",
            "description",
        )
