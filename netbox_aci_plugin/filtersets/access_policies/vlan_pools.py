# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from ipam.models import VLANGroup
from netbox.filtersets import NetBoxModelFilterSet
from users.filterset_mixins import OwnerFilterMixin
from utilities.filtersets import register_filterset

from ...choices import (
    VLANAllocationModeChoices,
    VLANPoolRangeAllocationModeChoices,
    VLANPoolRangeRoleChoices,
)
from ...models.access_policies.vlan_pools import ACIVLANPool, ACIVLANPoolRange
from ...models.fabric.fabrics import ACIFabric
from ..mixins import ACIFabricFilterSetMixin, NBTenantFilterSetMixin


@register_filterset
class ACIVLANPoolFilterSet(
    ACIFabricFilterSetMixin,
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    NetBoxModelFilterSet,
):
    """Filter set for the ACI VLAN Pool model."""

    allocation_mode = django_filters.MultipleChoiceFilter(
        choices=VLANAllocationModeChoices,
        null_value=None,
    )
    nb_vlan_group = django_filters.ModelMultipleChoiceFilter(
        field_name="nb_vlan_group__name",
        queryset=VLANGroup.objects.all(),
        to_field_name="name",
        label=_("NetBox VLAN group (name)"),
    )
    nb_vlan_group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VLANGroup.objects.all(),
        to_field_name="id",
        label=_("NetBox VLAN group (ID)"),
    )

    class Meta:
        model = ACIVLANPool
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "allocation_mode",
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
class ACIVLANPoolRangeFilterSet(NetBoxModelFilterSet):
    """Filter set for the ACI VLAN Pool Range model."""

    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_vlan_pool__aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_vlan_pool__aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    aci_vlan_pool = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_vlan_pool__name",
        queryset=ACIVLANPool.objects.all(),
        to_field_name="name",
        label=_("ACI VLAN Pool (name)"),
    )
    aci_vlan_pool_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIVLANPool.objects.all(),
        to_field_name="id",
        label=_("ACI VLAN Pool (ID)"),
    )
    allocation_mode = django_filters.MultipleChoiceFilter(
        choices=VLANPoolRangeAllocationModeChoices,
        null_value=None,
    )
    role = django_filters.MultipleChoiceFilter(
        choices=VLANPoolRangeRoleChoices,
        null_value=None,
    )

    class Meta:
        model = ACIVLANPoolRange
        fields: tuple = (
            "id",
            "vlan_id_from",
            "vlan_id_to",
            "comments",
        )

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the parent pool name or comments."""
        if not value.strip():
            return queryset
        queryset_filter: Q = Q(aci_vlan_pool__name__icontains=value) | Q(
            comments__icontains=value
        )
        return queryset.filter(queryset_filter)
