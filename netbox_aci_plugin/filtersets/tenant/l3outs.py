# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filtersets for Tenant L3Out models."""

import contextlib

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from netaddr.core import AddrFormatError
from netaddr.ip import IPNetwork

from ipam.models import Prefix
from netbox.filtersets import NetBoxModelFilterSet
from users.filterset_mixins import OwnerFilterMixin
from utilities.filters import MultiValueCharFilter
from utilities.filtersets import register_filterset

from ...choices import (
    QualityOfServiceClassChoices,
    QualityOfServiceDSCPChoices,
)
from ...filtersets.mixins import (
    ACITenantFilterSetMixin,
    ACITenantOrCommonFilterSetMixin,
    NBTenantFilterSetMixin,
)
from ...models.access_policies.domains import ACIRoutedDomain
from ...models.fabric.fabrics import ACIFabric
from ...models.tenant.l3outs import (
    ACIExternalEndpointGroup,
    ACIExternalSubnet,
    ACIL3Out,
)
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF


@register_filterset
class ACIL3OutFilterSet(
    ACITenantFilterSetMixin,
    ACITenantOrCommonFilterSetMixin,
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    NetBoxModelFilterSet,
):
    """Filterset for ACIL3Out model."""

    aci_vrf = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_vrf__name",
        queryset=ACIVRF.objects.all(),
        to_field_name="name",
        label=_("ACI VRF (name)"),
    )
    aci_vrf_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIVRF.objects.all(),
        label=_("ACI VRF (ID)"),
    )
    aci_routed_domain = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_routed_domain__name",
        queryset=ACIRoutedDomain.objects.all(),
        to_field_name="name",
        label=_("ACI Routed Domain (name)"),
    )
    aci_routed_domain_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIRoutedDomain.objects.all(),
        label=_("ACI Routed Domain (ID)"),
    )
    target_dscp = django_filters.MultipleChoiceFilter(
        choices=QualityOfServiceDSCPChoices,
        null_value=None,
    )

    class Meta:
        model = ACIL3Out
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "aci_vrf",
            "aci_routed_domain",
            "nb_tenant",
            "target_dscp",
            "import_route_control_enforcement_enabled",
            "bgp_enabled",
            "ospf_enabled",
            "eigrp_enabled",
            "l3_multicast_ipv4_enabled",
            "l3_multicast_ipv6_enabled",
            "multipod_enabled",
        )

    def search(self, queryset, name, value):
        """Search ACIL3Out instances."""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
            | Q(name_alias__icontains=value)
            | Q(description__icontains=value)
            | Q(aci_routed_domain__name__icontains=value)
            | Q(aci_tenant__name__icontains=value)
            | Q(aci_vrf__name__icontains=value)
        )


@register_filterset
class ACIExternalEndpointGroupFilterSet(
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    NetBoxModelFilterSet,
):
    """Filterset for ACIExternalEndpointGroup model."""

    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_l3out__aci_tenant__aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_l3out__aci_tenant__aci_fabric",
        queryset=ACIFabric.objects.all(),
        label=_("ACI Fabric (ID)"),
    )
    aci_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_l3out__aci_tenant__name",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant (name)"),
    )
    aci_tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_l3out__aci_tenant",
        queryset=ACITenant.objects.all(),
        label=_("ACI Tenant (ID)"),
    )
    aci_l3out = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_l3out__name",
        queryset=ACIL3Out.objects.all(),
        to_field_name="name",
        label=_("ACI L3Out (name)"),
    )
    aci_l3out_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIL3Out.objects.all(),
        label=_("ACI L3Out (ID)"),
    )
    aci_vrf = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_l3out__aci_vrf__name",
        queryset=ACIVRF.objects.all(),
        to_field_name="name",
        label=_("ACI VRF (name)"),
    )
    aci_vrf_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_l3out__aci_vrf",
        queryset=ACIVRF.objects.all(),
        label=_("ACI VRF (ID)"),
    )
    qos_class = django_filters.MultipleChoiceFilter(
        choices=QualityOfServiceClassChoices,
        null_value=None,
    )
    target_dscp = django_filters.MultipleChoiceFilter(
        choices=QualityOfServiceDSCPChoices,
        null_value=None,
    )

    class Meta:
        model = ACIExternalEndpointGroup
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "preferred_group_member_enabled",
            "qos_class",
            "target_dscp",
        )

    def search(self, queryset, name, value):
        """Search ACIExternalEndpointGroup instances."""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
            | Q(name_alias__icontains=value)
            | Q(description__icontains=value)
            | Q(aci_l3out__name__icontains=value)
            | Q(aci_l3out__aci_tenant__name__icontains=value)
            | Q(aci_l3out__aci_vrf__name__icontains=value)
        )


@register_filterset
class ACIExternalSubnetFilterSet(
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    NetBoxModelFilterSet,
):
    """Filterset for ACIExternalSubnet model."""

    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_external_endpoint_group__aci_l3out__aci_tenant__aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_external_endpoint_group__aci_l3out__aci_tenant__aci_fabric",
        queryset=ACIFabric.objects.all(),
        label=_("ACI Fabric (ID)"),
    )
    aci_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_external_endpoint_group__aci_l3out__aci_tenant__name",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant (name)"),
    )
    aci_tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_external_endpoint_group__aci_l3out__aci_tenant",
        queryset=ACITenant.objects.all(),
        label=_("ACI Tenant (ID)"),
    )
    aci_l3out = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_external_endpoint_group__aci_l3out__name",
        queryset=ACIL3Out.objects.all(),
        to_field_name="name",
        label=_("ACI L3Out (name)"),
    )
    aci_l3out_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_external_endpoint_group__aci_l3out",
        queryset=ACIL3Out.objects.all(),
        label=_("ACI L3Out (ID)"),
    )
    aci_external_endpoint_group = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_external_endpoint_group__name",
        queryset=ACIExternalEndpointGroup.objects.all(),
        to_field_name="name",
        label=_("ACI External Endpoint Group (name)"),
    )
    aci_external_endpoint_group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIExternalEndpointGroup.objects.all(),
        label=_("ACI External Endpoint Group (ID)"),
    )
    matched_prefix = MultiValueCharFilter(
        method="filter_prefix",
        label=_("Prefix"),
    )
    matched_prefix_within_include = django_filters.CharFilter(
        method="filter_prefix_within_include",
        label=_("Within and including matched prefix"),
    )
    nb_prefix = django_filters.ModelMultipleChoiceFilter(
        field_name="nb_prefix__prefix",
        queryset=Prefix.objects.all(),
        to_field_name="prefix",
        label=_("Prefix (prefix)"),
    )
    nb_prefix_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        label=_("Prefix (ID)"),
    )
    aci_vrf = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_external_endpoint_group__aci_l3out__aci_vrf__name",
        queryset=ACIVRF.objects.all(),
        to_field_name="name",
        label=_("ACI VRF (name)"),
    )
    aci_vrf_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_external_endpoint_group__aci_l3out__aci_vrf",
        queryset=ACIVRF.objects.all(),
        label=_("ACI VRF (ID)"),
    )

    class Meta:
        model = ACIExternalSubnet
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "matched_prefix",
            "import_route_control_enabled",
            "export_route_control_enabled",
            "shared_route_control_enabled",
            "import_security_enabled",
            "shared_security_enabled",
            "aggregate_import_route_control_enabled",
            "aggregate_export_route_control_enabled",
            "aggregate_shared_route_control_enabled",
            "bgp_route_summarization_enabled",
            "ospf_route_summarization_enabled",
            "eigrp_route_summarization_enabled",
        )

    def search(self, queryset, name, value):
        """Search ACIExternalSubnet instances."""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
            | Q(name_alias__icontains=value)
            | Q(description__icontains=value)
            | Q(aci_external_endpoint_group__name__icontains=value)
            | Q(aci_external_endpoint_group__aci_l3out__name__icontains=value)
        )

    def filter_prefix(self, queryset, name, value):
        """Filter queryset by exact matched prefix values."""
        query_values = []
        for v in value:
            with contextlib.suppress(AddrFormatError, ValueError):
                query_values.append(IPNetwork(v))
        return queryset.filter(matched_prefix__in=query_values)

    def filter_prefix_within_include(self, queryset, name, value):
        """Filter queryset to prefixes contained in or equal to value."""
        value = value.strip()
        if not value:
            return queryset
        try:
            query = str(IPNetwork(value).cidr)
            return queryset.filter(matched_prefix__net_contained_or_equal=query)
        except (AddrFormatError, ValueError):
            return queryset.none()
