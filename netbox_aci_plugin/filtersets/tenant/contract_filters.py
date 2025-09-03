# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from netbox.filtersets import NetBoxModelFilterSet
from tenancy.models import Tenant

from ...choices import (
    ContractFilterARPOpenPeripheralCodesChoices,
    ContractFilterEtherTypeChoices,
    ContractFilterICMPv4TypesChoices,
    ContractFilterICMPv6TypesChoices,
    ContractFilterIPProtocolChoices,
    ContractFilterPortChoices,
    QualityOfServiceDSCPChoices,
    add_custom_choice,
)
from ...models.tenant.contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from ...models.tenant.tenants import ACITenant


class ACIContractFilterFilterSet(NetBoxModelFilterSet):
    """Filter set for the ACI Contract Filter model."""

    aci_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_tenant__name",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant (name)"),
    )
    aci_tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Tenant (ID)"),
    )
    nb_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="nb_tenant__name",
        queryset=Tenant.objects.all(),
        to_field_name="name",
        label=_("NetBox tenant (name)"),
    )
    nb_tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        to_field_name="id",
        label=_("NetBox tenant (ID)"),
    )

    # Filters extended with a custom filter method
    present_in_aci_tenant_or_common_id = django_filters.ModelChoiceFilter(
        queryset=ACITenant.objects.all(),
        method="filter_present_in_aci_tenant_or_common_id",
        label=_("ACI Tenant (ID)"),
    )

    class Meta:
        model = ACIContractFilter
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "nb_tenant",
        )

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's description."""
        if not value.strip():
            return queryset
        queryset_filter: Q = (
            Q(name__icontains=value)
            | Q(name_alias__icontains=value)
            | Q(description__icontains=value)
        )
        return queryset.filter(queryset_filter)

    @extend_schema_field(OpenApiTypes.INT)
    def filter_present_in_aci_tenant_or_common_id(self, queryset, name, aci_tenant_id):
        """Return a QuerySet filtered by given ACI Tenant or 'common'."""
        if aci_tenant_id is None:
            return queryset.none()
        return queryset.filter(
            Q(aci_tenant=aci_tenant_id) | Q(aci_tenant__name="common")
        )


class ACIContractFilterEntryFilterSet(NetBoxModelFilterSet):
    """Filter set for the ACI Contract Filter Entry model."""

    aci_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract_filter__aci_tenant__name",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant (name)"),
    )
    aci_tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract_filter__aci_tenant",
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Tenant (ID)"),
    )
    aci_contract_filter = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract_filter__name",
        queryset=ACIContractFilter.objects.all(),
        to_field_name="name",
        label=_("ACI Contract Filter (name)"),
    )
    aci_contract_filter_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIContractFilter.objects.all(),
        to_field_name="id",
        label=_("ACI Contract Filter (ID)"),
    )
    nb_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract_filter__nb_tenant__name",
        queryset=Tenant.objects.all(),
        to_field_name="name",
        label=_("NetBox tenant (name)"),
    )
    nb_tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_contract_filter__nb_tenant",
        queryset=Tenant.objects.all(),
        to_field_name="id",
        label=_("NetBox tenant (ID)"),
    )
    arp_opc = django_filters.MultipleChoiceFilter(
        choices=ContractFilterARPOpenPeripheralCodesChoices,
        null_value=None,
    )
    destination_from_port = django_filters.MultipleChoiceFilter(
        choices=add_custom_choice(ContractFilterPortChoices),
        null_value=None,
        label=_("Destination from-port (choice)"),
    )
    destination_from_port_custom = django_filters.CharFilter(
        field_name="destination_from_port",
        label=_("Destination from-port (custom)"),
    )
    destination_to_port = django_filters.MultipleChoiceFilter(
        choices=add_custom_choice(ContractFilterPortChoices),
        null_value=None,
        label=_("Destination from-port (choice)"),
    )
    destination_to_port_custom = django_filters.CharFilter(
        field_name="destination_to_port",
        label=_("Destination to-port (custom)"),
    )
    ether_type = django_filters.MultipleChoiceFilter(
        choices=ContractFilterEtherTypeChoices,
        null_value=None,
    )
    icmp_v4_type = django_filters.MultipleChoiceFilter(
        choices=ContractFilterICMPv4TypesChoices,
        null_value=None,
    )
    icmp_v6_type = django_filters.MultipleChoiceFilter(
        choices=ContractFilterICMPv6TypesChoices,
        null_value=None,
    )
    ip_protocol = django_filters.MultipleChoiceFilter(
        choices=add_custom_choice(ContractFilterIPProtocolChoices),
        null_value=None,
        label=_("IP Protocol (choice)"),
    )
    ip_protocol_custom = django_filters.CharFilter(
        field_name="ip_protocol",
        label=_("IP Protocol (custom)"),
    )
    match_dscp = django_filters.MultipleChoiceFilter(
        choices=QualityOfServiceDSCPChoices,
        null_value=None,
    )
    source_from_port = django_filters.MultipleChoiceFilter(
        choices=add_custom_choice(ContractFilterPortChoices),
        null_value=None,
        label=_("Source from-port (choice)"),
    )
    source_from_port_custom = django_filters.CharFilter(
        field_name="source_from_port",
        label=_("Source from-port (custom)"),
    )
    source_to_port = django_filters.MultipleChoiceFilter(
        choices=add_custom_choice(ContractFilterPortChoices),
        null_value=None,
        label=_("Source from-port (choice)"),
    )
    source_to_port_custom = django_filters.CharFilter(
        field_name="source_to_port",
        label=_("Source to-port (custom)"),
    )

    class Meta:
        model = ACIContractFilterEntry
        fields: tuple = (
            "id",
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
        )
        filter_overrides = {
            ArrayField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            }
        }

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's description."""
        if not value.strip():
            return queryset
        queryset_filter: Q = (
            Q(name__icontains=value)
            | Q(name_alias__icontains=value)
            | Q(description__icontains=value)
        )
        return queryset.filter(queryset_filter)
