# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from dcim.base_filtersets import ScopedFilterSet
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from ipam.models import Prefix
from netbox.filtersets import NetBoxModelFilterSet
from users.filterset_mixins import OwnerFilterMixin
from utilities.filtersets import register_filterset

from ...models.fabric.pods import ACIPod
from ..mixins import ACIFabricFilterSetMixin, NBTenantFilterSetMixin


@register_filterset
class ACIPodFilterSet(
    ACIFabricFilterSetMixin,
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    ScopedFilterSet,
    NetBoxModelFilterSet,
):
    """Filter set for the ACI Pod model."""

    tep_pool = django_filters.ModelMultipleChoiceFilter(
        field_name="tep_pool__prefix",
        queryset=Prefix.objects.all(),
        to_field_name="prefix",
        label=_("TEP Pool (prefix)"),
    )
    tep_pool_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        to_field_name="id",
        label=_("TEP Pool (ID)"),
    )

    class Meta:
        model = ACIPod
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "pod_id",
            "tep_pool",
            "scope_type",
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
