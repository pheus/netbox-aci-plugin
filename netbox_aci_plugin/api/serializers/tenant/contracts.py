# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer
from utilities.api import get_serializer_for_model

from ....constants import CONTRACT_RELATION_OBJECT_TYPES
from ....models.tenant.contracts import (
    ACIContract,
    ACIContractRelation,
    ACIContractSubject,
    ACIContractSubjectFilter,
)
from .contract_filters import ACIContractFilterSerializer
from .tenants import ACITenantSerializer


class ACIContractSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Contract model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acicontract-detail"
    )
    aci_tenant = ACITenantSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIContract
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "nb_tenant",
            "qos_class",
            "scope",
            "target_dscp",
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
            "aci_tenant",
            "nb_tenant",
            "scope",
        )


class ACIContractRelationSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Contract Relation model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acicontractrelation-detail"
    )
    aci_contract = ACIContractSerializer(nested=True, required=True)
    aci_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(CONTRACT_RELATION_OBJECT_TYPES),
        required=False,
        default=None,
        allow_null=True,
    )
    aci_object_id = serializers.IntegerField(
        required=False,
        default=None,
        allow_null=True,
    )
    aci_object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ACIContractRelation
        fields: tuple = (
            "id",
            "url",
            "display",
            "aci_contract",
            "aci_object_type",
            "aci_object_id",
            "aci_object",
            "role",
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
            "aci_contract",
            "aci_object_type",
            "aci_object_id",
            "aci_object",
            "role",
        )

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_aci_object(self, obj):
        """Return the ACI object as nested JSON."""
        if obj.aci_object_id is None:
            return None
        serializer = get_serializer_for_model(obj.aci_object)
        context = {"request": self.context["request"]}
        return serializer(obj.aci_object, nested=True, context=context).data


class ACIContractSubjectSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Contract Subject model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acicontractsubject-detail"
    )
    aci_contract = ACIContractSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIContractSubject
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_contract",
            "nb_tenant",
            "apply_both_directions_enabled",
            "qos_class",
            "qos_class_cons_to_prov",
            "qos_class_prov_to_cons",
            "reverse_filter_ports_enabled",
            "service_graph_name",
            "service_graph_name_cons_to_prov",
            "service_graph_name_prov_to_cons",
            "target_dscp",
            "target_dscp_cons_to_prov",
            "target_dscp_prov_to_cons",
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
            "aci_contract",
            "nb_tenant",
        )


class ACIContractSubjectFilterSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Contract Subject Filter model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acicontractsubjectfilter-detail"
    )
    aci_contract_filter = ACIContractFilterSerializer(nested=True, required=True)
    aci_contract_subject = ACIContractSubjectSerializer(nested=True, required=True)

    class Meta:
        model = ACIContractSubjectFilter
        fields: tuple = (
            "id",
            "url",
            "display",
            "aci_contract_filter",
            "aci_contract_subject",
            "action",
            "apply_direction",
            "log_enabled",
            "policy_compression_enabled",
            "priority",
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
            "aci_contract_filter",
            "aci_contract_subject",
            "action",
        )
