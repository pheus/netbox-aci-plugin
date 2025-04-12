# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer

from ....models.tenant.endpoint_security_groups import ACIEndpointSecurityGroup
from .app_profiles import ACIAppProfileSerializer
from .vrfs import ACIVRFSerializer


class ACIEndpointSecurityGroupSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Endpoint Security Group model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:"
        "aciendpointsecuritygroup-detail"
    )
    aci_app_profile = ACIAppProfileSerializer(nested=True, required=True)
    aci_vrf = ACIVRFSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIEndpointSecurityGroup
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_app_profile",
            "aci_vrf",
            "nb_tenant",
            "description",
            "admin_shutdown",
            "intra_esg_isolation_enabled",
            "preferred_group_member_enabled",
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
            "aci_app_profile",
            "aci_vrf",
            "nb_tenant",
        )
