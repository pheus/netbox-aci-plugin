# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer
from users.api.serializers_.mixins import OwnerMixin

from ....constants import ACI_NAME_MAX_LEN
from ....models.access_policies.domains import ACIRoutedDomain
from ..fabric.fabrics import ACIFabricSerializer


class ACIRoutedDomainSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for the ACI Routed Domain model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acirouteddomain-detail"
    )
    aci_fabric = ACIFabricSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    security_domains = serializers.ListField(
        child=serializers.CharField(max_length=ACI_NAME_MAX_LEN),
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = ACIRoutedDomain
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "nb_tenant",
            "security_domains",
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
