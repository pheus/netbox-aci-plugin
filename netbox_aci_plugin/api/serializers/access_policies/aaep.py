# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from netbox.api.fields import ContentTypeField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer
from users.api.serializers_.mixins import OwnerMixin

from ....constants import AAEP_DOMAIN_OBJECT_TYPES
from ....models.access_policies.aaep import (
    ACIAAEPDomainBinding,
    ACIAttachableAccessEntityProfile,
)
from ..fabric.fabrics import ACIFabricSerializer


class ACIAttachableAccessEntityProfileSerializer(OwnerMixin, NetBoxModelSerializer):
    """Serializer for the ACI Attachable Access Entity Profile model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:aciattachableaccessentityprofile-detail"
    )
    aci_fabric = ACIFabricSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIAttachableAccessEntityProfile
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "nb_tenant",
            "infra_vlan",
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


class ACIAAEPDomainBindingSerializer(NetBoxModelSerializer):
    """Serializer for the ACI AAEP Domain Binding model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:aciaaepdomainbinding-detail"
    )
    aci_aaep = ACIAttachableAccessEntityProfileSerializer(nested=True, required=True)
    aci_domain_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(AAEP_DOMAIN_OBJECT_TYPES),
        required=False,
        default=None,
        allow_null=True,
    )
    aci_domain_object_id = serializers.IntegerField(
        required=False,
        default=None,
        allow_null=True,
    )
    aci_domain_object = GFKSerializerField(read_only=True)

    class Meta:
        model = ACIAAEPDomainBinding
        fields: tuple = (
            "id",
            "url",
            "display",
            "aci_aaep",
            "aci_domain_object_type",
            "aci_domain_object_id",
            "aci_domain_object",
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
            "aci_aaep",
            "aci_domain_object_type",
            "aci_domain_object_id",
            "aci_domain_object",
        )
