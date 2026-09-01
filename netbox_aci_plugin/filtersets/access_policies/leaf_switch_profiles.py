# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

from netbox.filtersets import NetBoxModelFilterSet
from users.filterset_mixins import OwnerFilterMixin
from utilities.filtersets import register_filterset

from ...models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
)
from ...models.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlock,
    ACILeafSelector,
    ACILeafSwitchProfile,
    ACILeafSwitchProfileInterfaceBinding,
)
from ...models.fabric.fabrics import ACIFabric
from ...models.fabric.nodes import ACINode
from ..mixins import ACIFabricFilterSetMixin, NBTenantFilterSetMixin


@register_filterset
class ACILeafSwitchProfileFilterSet(
    ACIFabricFilterSetMixin,
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    NetBoxModelFilterSet,
):
    """Filter set for the ACI Leaf Switch Profile model."""

    covering_aci_node_id = django_filters.ModelChoiceFilter(
        queryset=ACINode.objects.all(),
        method="filter_covering_aci_node_id",
        label=_("ACI Node (ID)"),
    )

    class Meta:
        model = ACILeafSwitchProfile
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

    @extend_schema_field(OpenApiTypes.INT)
    def filter_covering_aci_node_id(self, queryset, name, aci_node):
        """Return a QuerySet of Profiles whose blocks cover the ACI Node.

        Delegates to the Node so the leaf-role rule and the Fabric
        scoping stay in one place.
        """
        if aci_node is None:
            return queryset.none()
        return queryset.filter(pk__in=aci_node.aci_leaf_switch_profiles.values("pk"))


@register_filterset
class ACILeafSelectorFilterSet(
    NBTenantFilterSetMixin, OwnerFilterMixin, NetBoxModelFilterSet
):
    """Filter set for the ACI Leaf Selector model."""

    # The parent is a fabric-scoped model, not a tenant-scoped one, so
    # ACIFabricFilterSetMixin's direct 'aci_fabric' join path does not
    # apply here. Fabric is reached through the parent Profile FK, same
    # indirect shape as ACIVLANPoolRangeFilterSet and
    # ACIAAEPDomainBindingFilterSet.
    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_switch_profile__aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_switch_profile__aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    aci_leaf_switch_profile = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_switch_profile__name",
        queryset=ACILeafSwitchProfile.objects.all(),
        to_field_name="name",
        label=_("ACI Leaf Switch Profile (name)"),
    )
    aci_leaf_switch_profile_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACILeafSwitchProfile.objects.all(),
        to_field_name="id",
        label=_("ACI Leaf Switch Profile (ID)"),
    )

    class Meta:
        model = ACILeafSelector
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_leaf_switch_profile",
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
class ACILeafNodeBlockFilterSet(
    NBTenantFilterSetMixin, OwnerFilterMixin, NetBoxModelFilterSet
):
    """Filter set for the ACI Leaf Node Block model."""

    # Two indirection hops up to the Fabric, through the Selector and
    # then the Profile. Same reasoning as ACILeafSelectorFilterSet.
    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_selector__aci_leaf_switch_profile__aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_selector__aci_leaf_switch_profile__aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    aci_leaf_switch_profile = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_selector__aci_leaf_switch_profile__name",
        queryset=ACILeafSwitchProfile.objects.all(),
        to_field_name="name",
        label=_("ACI Leaf Switch Profile (name)"),
    )
    aci_leaf_switch_profile_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_selector__aci_leaf_switch_profile",
        queryset=ACILeafSwitchProfile.objects.all(),
        to_field_name="id",
        label=_("ACI Leaf Switch Profile (ID)"),
    )
    aci_leaf_selector = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_selector__name",
        queryset=ACILeafSelector.objects.all(),
        to_field_name="name",
        label=_("ACI Leaf Selector (name)"),
    )
    aci_leaf_selector_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACILeafSelector.objects.all(),
        to_field_name="id",
        label=_("ACI Leaf Selector (ID)"),
    )

    class Meta:
        model = ACILeafNodeBlock
        # node_id_from and node_id_to are plain numeric model fields, so
        # NetBoxModelFilterSet.get_filters() already synthesizes their
        # __gte, __lte, __lt, __gt, __n and __empty lookups automatically.
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_leaf_selector",
            "node_id_from",
            "node_id_to",
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
class ACILeafSwitchProfileInterfaceBindingFilterSet(NetBoxModelFilterSet):
    """Filter set for the ACI Leaf Switch Profile Interface Binding model."""

    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_switch_profile__aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_switch_profile__aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    aci_leaf_switch_profile = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_leaf_switch_profile__name",
        queryset=ACILeafSwitchProfile.objects.all(),
        to_field_name="name",
        label=_("ACI Leaf Switch Profile (name)"),
    )
    aci_leaf_switch_profile_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACILeafSwitchProfile.objects.all(),
        to_field_name="id",
        label=_("ACI Leaf Switch Profile (ID)"),
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

    class Meta:
        model = ACILeafSwitchProfileInterfaceBinding
        fields: tuple = ("id", "comments")

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's related object names."""
        if not value.strip():
            return queryset
        queryset_filter: Q = (
            Q(aci_leaf_switch_profile__name__icontains=value)
            | Q(aci_leaf_interface_profile__name__icontains=value)
            | Q(comments__icontains=value)
        )
        return queryset.filter(queryset_filter)
