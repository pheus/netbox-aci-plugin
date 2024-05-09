# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer

from ..models.tenant_app_profiles import ACIAppProfile
from ..models.tenants import ACITenant


class ACITenantSerializer(NetBoxModelSerializer):
    """Serializer for ACI Tenant model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acitenant-detail"
    )
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACITenant
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "alias",
            "description",
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
            "alias",
            "description",
            "nb_tenant",
        )


class ACIAppProfileSerializer(NetBoxModelSerializer):
    """Serializer for ACI Application Profile model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:aciappprofile-detail"
    )
    aci_tenant = ACITenantSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIAppProfile
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "alias",
            "description",
            "aci_tenant",
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
            "alias",
            "description",
            "aci_tenant",
            "nb_tenant",
        )
