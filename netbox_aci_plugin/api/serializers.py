# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.api.serializers import (
    NetBoxModelSerializer,
    WritableNestedSerializer,
)
from rest_framework import serializers

from ..models.tenants import ACITenant


class NestedACITenantListSerializer(WritableNestedSerializer):
    """Nested serializer for ACI Tenant model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acitenant-list"
    )

    class Meta:
        model = ACITenant
        fields: tuple = ("id", "url", "display", "name", "alias")


class ACITenantSerializer(NetBoxModelSerializer):
    """Serializer for ACI Tenant model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acitenant-detail"
    )

    class Meta:
        model = ACITenant
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "alias",
            "description",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
