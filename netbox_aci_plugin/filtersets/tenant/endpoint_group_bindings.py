# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from ipam.models import VLAN
from netbox.filtersets import NetBoxModelFilterSet
from utilities.filters import ContentTypeFilter
from utilities.filtersets import register_filterset

from ...choices import (
    DeploymentImmediacyChoices,
    PortModeChoices,
    ResolutionImmediacyChoices,
)
from ...models.access_policies.aaep import ACIAttachableAccessEntityProfile
from ...models.access_policies.domains import ACIPhysicalDomain
from ...models.fabric.fabrics import ACIFabric
from ...models.tenant.app_profiles import ACIAppProfile
from ...models.tenant.endpoint_group_bindings import (
    ACIEndpointGroupAAEPBinding,
    ACIEndpointGroupDomainBinding,
)
from ...models.tenant.endpoint_groups import ACIEndpointGroup, ACIUSegEndpointGroup
from ...models.tenant.tenants import ACITenant


@register_filterset
class ACIEndpointGroupDomainBindingFilterSet(NetBoxModelFilterSet):
    """Filter set for the ACI Endpoint Group Domain Binding model."""

    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_physical_domain__aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_physical_domain__aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    aci_epg_object_type = ContentTypeFilter(
        label=_("ACI EPG Object Type"),
    )
    aci_domain_object_type = ContentTypeFilter(
        label=_("ACI Domain Object Type"),
    )
    deployment_immediacy = django_filters.MultipleChoiceFilter(
        choices=DeploymentImmediacyChoices,
        null_value=None,
    )
    resolution_immediacy = django_filters.MultipleChoiceFilter(
        choices=ResolutionImmediacyChoices,
        null_value=None,
    )

    # Cached related objects filters
    aci_endpoint_group = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_endpoint_group__name",
        queryset=ACIEndpointGroup.objects.all(),
        to_field_name="name",
        label=_("ACI Endpoint Group (name)"),
    )
    aci_endpoint_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_endpoint_group",
        queryset=ACIEndpointGroup.objects.all(),
        to_field_name="id",
        label=_("ACI Endpoint Group (ID)"),
    )
    aci_useg_endpoint_group = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_useg_endpoint_group__name",
        queryset=ACIUSegEndpointGroup.objects.all(),
        to_field_name="name",
        label=_("ACI uSeg Endpoint Group (name)"),
    )
    aci_useg_endpoint_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_useg_endpoint_group",
        queryset=ACIUSegEndpointGroup.objects.all(),
        to_field_name="id",
        label=_("ACI uSeg Endpoint Group (ID)"),
    )
    aci_physical_domain = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_physical_domain__name",
        queryset=ACIPhysicalDomain.objects.all(),
        to_field_name="name",
        label=_("ACI Physical Domain (name)"),
    )
    aci_physical_domain_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_physical_domain",
        queryset=ACIPhysicalDomain.objects.all(),
        to_field_name="id",
        label=_("ACI Physical Domain (ID)"),
    )

    class Meta:
        model = ACIEndpointGroupDomainBinding
        fields: tuple = (
            "id",
            "aci_epg_object_type",
            "aci_epg_object_id",
            "aci_domain_object_type",
            "aci_domain_object_id",
            "deployment_immediacy",
            "resolution_immediacy",
        )

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's related object names."""
        if not value.strip():
            return queryset
        queryset_filter: Q = (
            Q(aci_endpoint_group__name__icontains=value)
            | Q(aci_useg_endpoint_group__name__icontains=value)
            | Q(aci_physical_domain__name__icontains=value)
        )
        return queryset.filter(queryset_filter)


@register_filterset
class ACIEndpointGroupAAEPBindingFilterSet(NetBoxModelFilterSet):
    """Filter set for the ACI Endpoint Group AAEP Binding model."""

    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_aaep__aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_aaep__aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    aci_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_endpoint_group__aci_app_profile__aci_tenant__name",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant (name)"),
    )
    aci_tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_endpoint_group__aci_app_profile__aci_tenant",
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Tenant (ID)"),
    )
    aci_app_profile = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_endpoint_group__aci_app_profile__name",
        queryset=ACIAppProfile.objects.all(),
        to_field_name="name",
        label=_("ACI Application Profile (name)"),
    )
    aci_app_profile_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_endpoint_group__aci_app_profile",
        queryset=ACIAppProfile.objects.all(),
        to_field_name="id",
        label=_("ACI Application Profile (ID)"),
    )
    aci_endpoint_group = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_endpoint_group__name",
        queryset=ACIEndpointGroup.objects.all(),
        to_field_name="name",
        label=_("ACI Endpoint Group (name)"),
    )
    aci_endpoint_group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIEndpointGroup.objects.all(),
        to_field_name="id",
        label=_("ACI Endpoint Group (ID)"),
    )
    aci_aaep = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_aaep__name",
        queryset=ACIAttachableAccessEntityProfile.objects.all(),
        to_field_name="name",
        label=_("ACI AAEP (name)"),
    )
    aci_aaep_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIAttachableAccessEntityProfile.objects.all(),
        to_field_name="id",
        label=_("ACI AAEP (ID)"),
    )
    nb_vlan = django_filters.ModelMultipleChoiceFilter(
        field_name="nb_vlan__vid",
        queryset=VLAN.objects.all(),
        to_field_name="vid",
        label=_("NetBox VLAN (VID)"),
    )
    nb_vlan_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VLAN.objects.all(),
        to_field_name="id",
        label=_("NetBox VLAN (ID)"),
    )
    primary_nb_vlan = django_filters.ModelMultipleChoiceFilter(
        field_name="primary_nb_vlan__vid",
        queryset=VLAN.objects.all(),
        to_field_name="vid",
        label=_("Primary NetBox VLAN (VID)"),
    )
    primary_nb_vlan_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VLAN.objects.all(),
        to_field_name="id",
        label=_("Primary NetBox VLAN (ID)"),
    )
    mode = django_filters.MultipleChoiceFilter(
        choices=PortModeChoices,
        null_value=None,
    )
    deployment_immediacy = django_filters.MultipleChoiceFilter(
        choices=DeploymentImmediacyChoices,
        null_value=None,
    )
    effective_encap_vlan_id = django_filters.NumberFilter(
        method="filter_effective_encap_vlan_id",
        label=_("Effective Encap VLAN ID"),
    )
    effective_primary_encap_vlan_id = django_filters.NumberFilter(
        method="filter_effective_primary_encap_vlan_id",
        label=_("Effective Primary Encap VLAN ID"),
    )

    class Meta:
        model = ACIEndpointGroupAAEPBinding
        fields: tuple = (
            "id",
            "aci_endpoint_group",
            "aci_aaep",
            "encap_vlan_id",
            "primary_encap_vlan_id",
            "mode",
            "deployment_immediacy",
        )

    def filter_effective_encap_vlan_id(self, queryset, name, value):
        """Return a QuerySet filtered by the effective VLAN ID.

        The snapshot is consulted only when no NetBox VLAN is assigned, so
        the filter matches the ``effective_encap_vlan_id`` property, where a
        live NetBox VLAN always wins over a stale snapshot.
        """
        return queryset.filter(
            Q(nb_vlan__vid=value) | Q(nb_vlan__isnull=True, encap_vlan_id=value)
        )

    def filter_effective_primary_encap_vlan_id(self, queryset, name, value):
        """Return a QuerySet filtered by the effective primary VLAN ID.

        The snapshot is consulted only when no primary NetBox VLAN is
        assigned, matching the ``effective_primary_encap_vlan_id`` property.
        """
        return queryset.filter(
            Q(primary_nb_vlan__vid=value)
            | Q(primary_nb_vlan__isnull=True, primary_encap_vlan_id=value)
        )

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's related object names."""
        if not value.strip():
            return queryset
        queryset_filter: Q = Q(aci_aaep__name__icontains=value) | Q(
            aci_endpoint_group__name__icontains=value
        )
        return queryset.filter(queryset_filter)
