# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from netbox.filtersets import NetBoxModelFilterSet
from users.filterset_mixins import OwnerFilterMixin
from utilities.filtersets import register_filterset

from ...models.access_policies.domains import ACIRoutedDomain
from ...models.fabric.fabrics import ACIFabric
from ..mixins import NBTenantFilterSetMixin


@register_filterset
class ACIRoutedDomainFilterSet(
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    NetBoxModelFilterSet,
):
    """Filter set for the ACI Routed Domain model."""

    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    security_domain = django_filters.CharFilter(
        method="filter_security_domain",
        label=_("Security Domain"),
    )

    class Meta:
        model = ACIRoutedDomain
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "nb_tenant",
        )

    def filter_security_domain(self, queryset, name, value):
        """Return a QuerySet filtered by assigned ACI security domain."""
        if not (cleaned_value := value.strip()):
            return queryset
        return queryset.filter(security_domains__contains=[cleaned_value])

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's name or description."""
        if not value.strip():
            return queryset
        queryset_filter: Q = (
            Q(name__icontains=value)
            | Q(name_alias__icontains=value)
            | Q(description__icontains=value)
        )
        return queryset.filter(queryset_filter)
