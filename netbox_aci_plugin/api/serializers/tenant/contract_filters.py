# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer

from ....models.tenant.contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from .tenants import ACITenantSerializer


class ACIContractFilterSerializer(NetBoxModelSerializer):
    """Serializer for the ACI Contract Filter model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acicontractfilter-detail"
    )
    aci_tenant = ACITenantSerializer(nested=True, required=True)
    nb_tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ACIContractFilter
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
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
            "name_alias",
            "description",
            "aci_tenant",
            "nb_tenant",
        )


class ACIContractFilterEntrySerializer(NetBoxModelSerializer):
    """Serializer for the ACI Contract Filter Entry model."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aci_plugin-api:acicontractfilterentry-detail"
    )
    aci_contract_filter = ACIContractFilterSerializer(nested=True, required=True)

    class Meta:
        model = ACIContractFilterEntry
        fields: tuple = (
            "id",
            "url",
            "display",
            "name",
            "name_alias",
            "description",
            "aci_contract_filter",
            "arp_opc",
            "destination_from_port",
            "destination_to_port",
            "ether_type",
            "icmp_v4_type",
            "icmp_v6_type",
            "ip_protocol",
            "match_dscp",
            "match_only_fragments_enabled",
            "source_from_port",
            "source_to_port",
            "stateful_enabled",
            "tcp_rules",
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
            "aci_contract_filter",
        )
