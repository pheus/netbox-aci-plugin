# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from dcim.models import MACAddress
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from ipam.models import VRF, IPAddress, Prefix
from netbox.filtersets import NetBoxModelFilterSet
from tenancy.models import Tenant
from utilities.filters import ContentTypeFilter

from ...choices import QualityOfServiceClassChoices, USegAttributeTypeChoices
from ...models.tenant.app_profiles import ACIAppProfile
from ...models.tenant.bridge_domains import ACIBridgeDomain
from ...models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
    ACIUSegNetworkAttribute,
)
from ...models.tenant.endpoint_security_groups import ACIEndpointSecurityGroup
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF


class ACIEndpointGroupFilterSet(NetBoxModelFilterSet):
    """Filter set for the ACI Endpoint Group model."""

    aci_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_app_profile__aci_tenant__name",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant (name)"),
    )
    aci_tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_app_profile__aci_tenant",
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Tenant (ID)"),
    )
    aci_app_profile = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_app_profile__name",
        queryset=ACIAppProfile.objects.all(),
        to_field_name="name",
        label=_("ACI Application Profile (name)"),
    )
    aci_app_profile_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIAppProfile.objects.all(),
        to_field_name="id",
        label=_("ACI Application Profile (ID)"),
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
    qos_class = django_filters.MultipleChoiceFilter(
        choices=QualityOfServiceClassChoices,
        null_value=None,
    )

    # Filters extended with a custom filter method
    shares_aci_vrf_with_aci_esg_id = django_filters.ModelChoiceFilter(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        method="filter_shares_aci_vrf_with_aci_esg_id",
        label=_("ACI VRF shared with ACI ESG (ID)"),
    )

    class Meta:
        model = ACIEndpointGroup
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_app_profile",
            "aci_bridge_domain",
            "nb_tenant",
            "admin_shutdown",
            "custom_qos_policy_name",
            "flood_in_encap_enabled",
            "intra_epg_isolation_enabled",
            "qos_class",
            "preferred_group_member_enabled",
            "proxy_arp_enabled",
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
    def filter_shares_aci_vrf_with_aci_esg_id(
        self, queryset, name, aci_endpoint_security_group
    ):
        """Return a QuerySet filtered by a shared ACI VRF for a given ESG."""
        if aci_endpoint_security_group is None:
            return queryset.none()
        return queryset.filter(
            aci_bridge_domain__aci_vrf=aci_endpoint_security_group.aci_vrf
        )


class ACIUSegEndpointGroupFilterSet(NetBoxModelFilterSet):
    """Filter set for the ACI uSeg Endpoint Group model."""

    aci_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_app_profile__aci_tenant__name",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant (name)"),
    )
    aci_tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_app_profile__aci_tenant",
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Tenant (ID)"),
    )
    aci_app_profile = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_app_profile__name",
        queryset=ACIAppProfile.objects.all(),
        to_field_name="name",
        label=_("ACI Application Profile (name)"),
    )
    aci_app_profile_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIAppProfile.objects.all(),
        to_field_name="id",
        label=_("ACI Application Profile (ID)"),
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
    qos_class = django_filters.MultipleChoiceFilter(
        choices=QualityOfServiceClassChoices,
        null_value=None,
    )

    # Filters extended with a custom filter method
    shares_aci_vrf_with_aci_esg_id = django_filters.ModelChoiceFilter(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        method="filter_shares_aci_vrf_with_aci_esg_id",
        label=_("ACI VRF shared with ACI ESG (ID)"),
    )

    class Meta:
        model = ACIUSegEndpointGroup
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_app_profile",
            "aci_bridge_domain",
            "nb_tenant",
            "admin_shutdown",
            "custom_qos_policy_name",
            "flood_in_encap_enabled",
            "intra_epg_isolation_enabled",
            "qos_class",
            "preferred_group_member_enabled",
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
    def filter_shares_aci_vrf_with_aci_esg_id(
        self, queryset, name, aci_endpoint_security_group
    ):
        """Return a QuerySet filtered by a shared ACI VRF for a given ESG."""
        if aci_endpoint_security_group is None:
            return queryset.none()
        return queryset.filter(
            aci_bridge_domain__aci_vrf=aci_endpoint_security_group.aci_vrf
        )


class ACIUSegNetworkAttributeFilterSet(NetBoxModelFilterSet):
    """Filter set for the ACI uSeg Network Attribute model."""

    aci_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_useg_endpoint_group__aci_app_profile__aci_tenant__name",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant (name)"),
    )
    aci_tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_useg_endpoint_group__aci_app_profile__aci_tenant",
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Tenant (ID)"),
    )
    aci_app_profile = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_useg_endpoint_group__aci_app_profile__name",
        queryset=ACIAppProfile.objects.all(),
        to_field_name="name",
        label=_("ACI Application Profile (name)"),
    )
    aci_app_profile_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_useg_endpoint_group__aci_app_profile",
        queryset=ACIAppProfile.objects.all(),
        to_field_name="id",
        label=_("ACI Application Profile (ID)"),
    )
    aci_useg_endpoint_group = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_useg_endpoint_group__name",
        queryset=ACIUSegEndpointGroup.objects.all(),
        to_field_name="name",
        label=_("ACI uSeg Endpoint Group (name)"),
    )
    aci_useg_endpoint_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_useg_endpoint_group",
        queryset=ACIUSegEndpointGroup.objects.all(),
        to_field_name="id",
        label=_("ACI uSeg Endpoint Group (ID)"),
    )
    attr_object_type = ContentTypeFilter(
        label=_("Attribute Object Type"),
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
    type = django_filters.MultipleChoiceFilter(
        choices=USegAttributeTypeChoices,
        null_value=None,
    )

    # Cached related objects filters
    ip_address_vrf = django_filters.ModelMultipleChoiceFilter(
        field_name="_ip_address__vrf__name",
        queryset=VRF.objects.all(),
        to_field_name="name",
        label=_("VRF of IP Address (name)"),
    )
    ip_address_vrf_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_ip_address__vrf",
        queryset=VRF.objects.all(),
        to_field_name="id",
        label=_("VRF of IP Address (ID)"),
    )
    ip_address = django_filters.ModelMultipleChoiceFilter(
        field_name="_ip_address__address",
        queryset=IPAddress.objects.all(),
        to_field_name="address",
        label=_("IP Address (address)"),
    )
    ip_address_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_ip_address",
        queryset=IPAddress.objects.all(),
        to_field_name="id",
        label=_("IP Address (ID)"),
    )
    mac_address = django_filters.ModelMultipleChoiceFilter(
        field_name="_mac_address__mac_address",
        queryset=MACAddress.objects.all(),
        to_field_name="mac_address",
        label=_("MAC Address (MAC Address)"),
    )
    mac_address_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_mac_address",
        queryset=MACAddress.objects.all(),
        to_field_name="id",
        label=_("MAC Address (ID)"),
    )
    prefix_vrf = django_filters.ModelMultipleChoiceFilter(
        field_name="_prefix__vrf__name",
        queryset=VRF.objects.all(),
        to_field_name="name",
        label=_("VRF of Prefix (name)"),
    )
    prefix_vrf_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_prefix__vrf",
        queryset=VRF.objects.all(),
        to_field_name="id",
        label=_("VRF of Prefix (ID)"),
    )
    prefix = django_filters.ModelMultipleChoiceFilter(
        field_name="_prefix__prefix",
        queryset=Prefix.objects.all(),
        to_field_name="prefix",
        label=_("Prefix (Prefix)"),
    )
    prefix_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_prefix",
        queryset=Prefix.objects.all(),
        to_field_name="id",
        label=_("Prefix (ID)"),
    )

    class Meta:
        model = ACIUSegNetworkAttribute
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_useg_endpoint_group",
            "attr_object_type",
            "attr_object_id",
            "type",
            "use_epg_subnet",
        )

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's description."""
        if not value.strip():
            return queryset
        queryset_filter: Q = (
            Q(name__icontains=value)
            | Q(name_alias__icontains=value)
            | Q(description__icontains=value)
            | Q(aci_useg_endpoint_group__name__icontains=value)
            | Q(ip_address__address__icontains=value)
            | Q(mac_address__mac_address__icontains=value)
            | Q(prefix__prefix__icontains=value)
        )
        return queryset.filter(queryset_filter)
