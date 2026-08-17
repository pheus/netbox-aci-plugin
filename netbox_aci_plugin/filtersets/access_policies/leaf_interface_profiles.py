# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from netbox.filtersets import NetBoxModelFilterSet
from users.filterset_mixins import OwnerFilterMixin
from utilities.filtersets import register_filterset

from ...models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ...models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
    ACILeafInterfaceSelector,
    ACILeafPortBlock,
)
from ...models.fabric.fabrics import ACIFabric
from ..mixins import ACIFabricFilterSetMixin, NBTenantFilterSetMixin


@register_filterset
class ACILeafInterfaceProfileFilterSet(
    ACIFabricFilterSetMixin,
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    NetBoxModelFilterSet,
):
    """Filter set for the ACI Leaf Interface Profile model."""

    class Meta:
        model = ACILeafInterfaceProfile
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
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
class ACILeafInterfaceSelectorFilterSet(
    NBTenantFilterSetMixin, OwnerFilterMixin, NetBoxModelFilterSet
):
    """Filter set for the ACI Leaf Interface Selector model."""

    # The parent is a fabric-scoped model, not a tenant-scoped one, so
    # ACIFabricFilterSetMixin's direct 'aci_fabric' join path does not
    # apply here. Fabric is reached through the parent Profile FK, same
    # indirect shape as ACIVLANPoolRangeFilterSet and
    # ACIAAEPDomainBindingFilterSet.
    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_interface_profile__aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_interface_profile__aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    aci_leaf_interface_profile = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_interface_profile__name",
        queryset=ACILeafInterfaceProfile.objects.all(),
        to_field_name="name",
        label=_("ACI Leaf Interface Profile (name)"),
    )
    aci_leaf_interface_profile_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACILeafInterfaceProfile.objects.all(),
        to_field_name="id",
        label=_("ACI Leaf Interface Profile (ID)"),
    )
    aci_leaf_interface_policy_group = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_interface_policy_group__name",
        queryset=ACILeafInterfacePolicyGroup.objects.all(),
        to_field_name="name",
        label=_("ACI Leaf Interface Policy Group (name)"),
    )
    aci_leaf_interface_policy_group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACILeafInterfacePolicyGroup.objects.all(),
        to_field_name="id",
        label=_("ACI Leaf Interface Policy Group (ID)"),
    )

    class Meta:
        model = ACILeafInterfaceSelector
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_leaf_interface_profile",
            "aci_leaf_interface_policy_group",
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
class ACILeafPortBlockFilterSet(
    NBTenantFilterSetMixin, OwnerFilterMixin, NetBoxModelFilterSet
):
    """Filter set for the ACI Leaf Port Block model."""

    # Two indirection hops up to the Fabric, through the Selector and
    # then the Profile. Same reasoning as ACILeafInterfaceSelectorFilterSet.
    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_interface_selector__aci_leaf_interface_profile__aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_interface_selector__aci_leaf_interface_profile__aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    aci_leaf_interface_profile = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_interface_selector__aci_leaf_interface_profile__name",
        queryset=ACILeafInterfaceProfile.objects.all(),
        to_field_name="name",
        label=_("ACI Leaf Interface Profile (name)"),
    )
    aci_leaf_interface_profile_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_interface_selector__aci_leaf_interface_profile",
        queryset=ACILeafInterfaceProfile.objects.all(),
        to_field_name="id",
        label=_("ACI Leaf Interface Profile (ID)"),
    )
    aci_leaf_interface_selector = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_interface_selector__name",
        queryset=ACILeafInterfaceSelector.objects.all(),
        to_field_name="name",
        label=_("ACI Leaf Interface Selector (name)"),
    )
    aci_leaf_interface_selector_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACILeafInterfaceSelector.objects.all(),
        to_field_name="id",
        label=_("ACI Leaf Interface Selector (ID)"),
    )

    class Meta:
        model = ACILeafPortBlock
        # module_from, module_to, port_from and port_to are plain numeric
        # model fields, so NetBoxModelFilterSet.get_filters() already
        # synthesizes their __gte, __lte, __lt, __gt, __n and __empty
        # lookups automatically.
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_leaf_interface_selector",
            "module_from",
            "module_to",
            "port_from",
            "port_to",
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
