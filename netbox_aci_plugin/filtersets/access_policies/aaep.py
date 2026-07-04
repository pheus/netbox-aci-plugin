# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from netbox.filtersets import NetBoxModelFilterSet
from users.filterset_mixins import OwnerFilterMixin
from utilities.filters import ContentTypeFilter
from utilities.filtersets import register_filterset

from ...models.access_policies.aaep import (
    ACIAAEPDomainBinding,
    ACIAttachableAccessEntityProfile,
)
from ...models.access_policies.domains import ACIPhysicalDomain, ACIRoutedDomain
from ...models.fabric.fabrics import ACIFabric
from ..mixins import ACIFabricFilterSetMixin, NBTenantFilterSetMixin


@register_filterset
class ACIAttachableAccessEntityProfileFilterSet(
    ACIFabricFilterSetMixin,
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    NetBoxModelFilterSet,
):
    """Filter set for the ACI Attachable Access Entity Profile model."""

    class Meta:
        model = ACIAttachableAccessEntityProfile
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "infra_vlan",
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


@register_filterset
class ACIAAEPDomainBindingFilterSet(NetBoxModelFilterSet):
    """Filter set for the ACI AAEP Domain Binding model."""

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
    aci_domain_object_type = ContentTypeFilter(
        label=_("ACI Domain Object Type"),
    )

    # Cached related objects filters
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
    aci_routed_domain = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_routed_domain__name",
        queryset=ACIRoutedDomain.objects.all(),
        to_field_name="name",
        label=_("ACI Routed Domain (name)"),
    )
    aci_routed_domain_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_aci_routed_domain",
        queryset=ACIRoutedDomain.objects.all(),
        to_field_name="id",
        label=_("ACI Routed Domain (ID)"),
    )

    class Meta:
        model = ACIAAEPDomainBinding
        fields: tuple = (
            "id",
            "aci_aaep",
            "aci_domain_object_type",
            "aci_domain_object_id",
        )

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's related object names."""
        if not value.strip():
            return queryset
        queryset_filter: Q = (
            Q(aci_aaep__name__icontains=value)
            | Q(aci_physical_domain__name__icontains=value)
            | Q(aci_routed_domain__name__icontains=value)
        )
        return queryset.filter(queryset_filter)
