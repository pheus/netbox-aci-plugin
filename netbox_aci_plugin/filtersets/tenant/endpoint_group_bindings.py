# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from netbox.filtersets import NetBoxModelFilterSet
from utilities.filters import ContentTypeFilter
from utilities.filtersets import register_filterset

from ...choices import DeploymentImmediacyChoices, ResolutionImmediacyChoices
from ...models.access_policies.domains import ACIPhysicalDomain
from ...models.fabric.fabrics import ACIFabric
from ...models.tenant.endpoint_group_bindings import ACIEndpointGroupDomainBinding
from ...models.tenant.endpoint_groups import ACIEndpointGroup, ACIUSegEndpointGroup


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
