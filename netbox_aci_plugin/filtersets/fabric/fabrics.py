# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from dcim.base_filtersets import ScopedFilterSet
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from ipam.models import VLAN, Prefix
from netbox.filtersets import NetBoxModelFilterSet
from users.filterset_mixins import OwnerFilterMixin
from utilities.filtersets import register_filterset

from ...models.fabric.fabrics import ACIFabric
from ..mixins import NBTenantFilterSetMixin


@register_filterset
class ACIFabricFilterSet(
    NBTenantFilterSetMixin, OwnerFilterMixin, ScopedFilterSet, NetBoxModelFilterSet
):
    """Filter set for the ACI Fabric model."""

    infra_vlan = django_filters.ModelMultipleChoiceFilter(
        field_name="infra_vlan__vid",
        queryset=VLAN.objects.all(),
        to_field_name="vid",
        label=_("Infrastructure VLAN (VID)"),
    )
    infra_vlan_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VLAN.objects.all(),
        to_field_name="id",
        label=_("Infrastructure VLAN (ID)"),
    )
    gipo_pool = django_filters.ModelMultipleChoiceFilter(
        field_name="gipo_pool__prefix",
        queryset=Prefix.objects.all(),
        to_field_name="prefix",
        label=_("GIPo Pool (prefix)"),
    )
    gipo_pool_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        to_field_name="id",
        label=_("GIPo Pool (ID)"),
    )

    class Meta:
        model = ACIFabric
        fields: tuple = (
            "id",
            "name",
            "description",
            "fabric_id",
            "infra_vlan_vid",
            "infra_vlan",
            "gipo_pool",
            "scope_type",
            "nb_tenant",
        )

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's description."""
        if not value.strip():
            return queryset
        queryset_filter: Q = Q(name__icontains=value) | Q(description__icontains=value)
        return queryset.filter(queryset_filter)
