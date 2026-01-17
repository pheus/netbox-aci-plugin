# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from ipam.models import IPAddress
from netbox.filtersets import NetBoxModelFilterSet
from users.filterset_mixins import OwnerFilterMixin
from utilities.filters import MultiValueMACAddressFilter
from utilities.filtersets import register_filterset

from ...choices import (
    BDMultiDestinationFloodingChoices,
    BDUnknownMulticastChoices,
    BDUnknownUnicastChoices,
)
from ...models.fabric.fabrics import ACIFabric
from ...models.tenant.bridge_domains import (
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF
from ..mixins import ACITenantFilterSetMixin, NBTenantFilterSetMixin


@register_filterset
class ACIBridgeDomainFilterSet(
    ACITenantFilterSetMixin,
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    NetBoxModelFilterSet,
):
    """Filter set for the ACI Bridge Domain model."""

    aci_vrf = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_vrf__name",
        queryset=ACIVRF.objects.all(),
        to_field_name="name",
        label=_("ACI VRF (name)"),
    )
    aci_vrf_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIVRF.objects.all(),
        to_field_name="id",
        label=_("ACI VRF (ID)"),
    )
    mac_address = MultiValueMACAddressFilter(
        field_name="mac_address",
        label=_("MAC address"),
    )
    multi_destination_flooding = django_filters.MultipleChoiceFilter(
        choices=BDMultiDestinationFloodingChoices,
        null_value=None,
    )
    unknown_ipv4_multicast = django_filters.MultipleChoiceFilter(
        choices=BDUnknownMulticastChoices,
        null_value=None,
    )
    unknown_ipv6_multicast = django_filters.MultipleChoiceFilter(
        choices=BDUnknownMulticastChoices,
        null_value=None,
    )
    unknown_unicast = django_filters.MultipleChoiceFilter(
        choices=BDUnknownUnicastChoices,
        null_value=None,
    )
    virtual_mac_address = MultiValueMACAddressFilter(
        field_name="virtual_mac_address",
        label=_("Virtual MAC address"),
    )

    # Filters extended with a custom filter method
    present_in_aci_tenant_or_common_id = django_filters.ModelChoiceFilter(
        queryset=ACITenant.objects.all(),
        method="filter_present_in_aci_tenant_or_common_id",
        label=_("ACI Tenant (ID)"),
    )

    class Meta:
        model = ACIBridgeDomain
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "aci_vrf",
            "nb_tenant",
            "advertise_host_routes_enabled",
            "arp_flooding_enabled",
            "clear_remote_mac_enabled",
            "dhcp_labels",
            "ep_move_detection_enabled",
            "igmp_interface_policy_name",
            "igmp_snooping_policy_name",
            "ip_data_plane_learning_enabled",
            "limit_ip_learn_enabled",
            "mac_address",
            "multi_destination_flooding",
            "pim_ipv4_enabled",
            "pim_ipv4_destination_filter",
            "pim_ipv4_source_filter",
            "pim_ipv6_enabled",
            "unicast_routing_enabled",
            "unknown_ipv4_multicast",
            "unknown_ipv6_multicast",
            "unknown_unicast",
            "virtual_mac_address",
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

    @extend_schema_field(OpenApiTypes.INT)
    def filter_present_in_aci_tenant_or_common_id(self, queryset, name, aci_tenant):
        """Return a QuerySet filtered by given ACI Tenant or 'common'."""
        if aci_tenant is None:
            return queryset.none()
        return queryset.filter(
            Q(aci_tenant=aci_tenant)
            | Q(
                aci_tenant__name="common",
                aci_tenant__aci_fabric_id=aci_tenant.aci_fabric_id,
            )
        )


@register_filterset
class ACIBridgeDomainSubnetFilterSet(
    NBTenantFilterSetMixin, OwnerFilterMixin, NetBoxModelFilterSet
):
    """Filter set for the ACI Bridge Domain Subnet model."""

    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_bridge_domain__aci_tenant__aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_bridge_domain__aci_tenant__aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    aci_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_bridge_domain__aci_tenant__name",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant (name)"),
    )
    aci_tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_bridge_domain__aci_tenant",
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Tenant (ID)"),
    )
    aci_vrf = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_bridge_domain__aci_vrf__name",
        queryset=ACIVRF.objects.all(),
        to_field_name="name",
        label=_("ACI VRF (name)"),
    )
    aci_vrf_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_bridge_domain__aci_vrf",
        queryset=ACIVRF.objects.all(),
        to_field_name="id",
        label=_("ACI VRF (ID)"),
    )
    aci_bridge_domain = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_bridge_domain__name",
        queryset=ACIBridgeDomain.objects.all(),
        to_field_name="name",
        label=_("ACI Bridge Domain (name)"),
    )
    aci_bridge_domain_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIBridgeDomain.objects.all(),
        to_field_name="id",
        label=_("ACI Bridge Domain (ID)"),
    )
    gateway_ip_address = django_filters.ModelMultipleChoiceFilter(
        field_name="gateway_ip_address__address",
        queryset=IPAddress.objects.all(),
        to_field_name="address",
        label=_("Gateway IP address (address)"),
    )
    gateway_ip_address_id = django_filters.ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        to_field_name="id",
        label=_("Gateway IP address (ID)"),
    )

    class Meta:
        model = ACIBridgeDomainSubnet
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_vrf",
            "aci_bridge_domain",
            "gateway_ip_address",
            "nb_tenant",
            "advertised_externally_enabled",
            "igmp_querier_enabled",
            "ip_data_plane_learning_enabled",
            "no_default_gateway",
            "nd_ra_enabled",
            "nd_ra_prefix_policy_name",
            "preferred_ip_address_enabled",
            "shared_enabled",
            "virtual_ip_enabled",
        )

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's description."""
        if not value.strip():
            return queryset
        queryset_filter: Q = (
            Q(name__icontains=value)
            | Q(name_alias__icontains=value)
            | Q(description__icontains=value)
            | Q(gateway_ip__istartswith=value)
        )
        return queryset.filter(queryset_filter)
