# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers

from dcim.api.serializers import InterfaceSerializer
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer
from users.api.serializers_.mixins import OwnerMixin

from ....models.fabric.node_interfaces import ACINodeInterface
from .nodes import ACINodeSerializer


class ACINodeInterfaceSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for the ACI Node Interface model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acinodeinterface-detail"
    )
    aci_node = ACINodeSerializer(nested=True, required=True)
    nb_interface = InterfaceSerializer(nested=True, required=False, allow_null=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    interface_token = serializers.CharField(read_only=True)

    class Meta:
        model = ACINodeInterface
        fields: tuple = (
            "id",
            "url",
            "display",
            "aci_node",
            "nb_interface",
            "module",
            "port",
            "sub_port",
            "interface_token",
            "description",
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
            "aci_node",
            "module",
            "port",
            "sub_port",
            "interface_token",
            "nb_tenant",
        )
