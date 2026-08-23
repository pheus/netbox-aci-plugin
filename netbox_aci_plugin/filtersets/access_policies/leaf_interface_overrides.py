# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from netbox.filtersets import NetBoxModelFilterSet
from utilities.filtersets import register_filterset

from ...models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ...models.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverride,
)
from ...models.fabric.fabrics import ACIFabric
from ...models.fabric.node_interfaces import ACINodeInterface
from ...models.fabric.nodes import ACINode
from ...models.fabric.pods import ACIPod


@register_filterset
class ACILeafInterfaceOverrideFilterSet(NetBoxModelFilterSet):
    """Filter set for the ACI Leaf Interface Override model."""

    # The model has no aci_fabric field, only a derived property, so
    # ACIFabricFilterSetMixin cannot bind. Reached through the Node
    # Interface's own indirect Node -> Pod -> Fabric chain instead.
    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_node_interface__aci_node___aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_node_interface__aci_node___aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    aci_pod_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_node_interface__aci_node__aci_pod",
        queryset=ACIPod.objects.all(),
        to_field_name="id",
        label=_("ACI Pod (ID)"),
    )
    aci_node_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_node_interface__aci_node",
        queryset=ACINode.objects.all(),
        to_field_name="id",
        label=_("ACI Node (ID)"),
    )
    aci_node_interface_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACINodeInterface.objects.all(),
        to_field_name="id",
        label=_("ACI Node Interface (ID)"),
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
        model = ACILeafInterfaceOverride
        fields: tuple = ("id", "description")

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's related object names."""
        if not value.strip():
            return queryset
        queryset_filter: Q = (
            Q(aci_node_interface__aci_node__name__icontains=value)
            | Q(aci_leaf_interface_policy_group__name__icontains=value)
            | Q(description__icontains=value)
        )
        return queryset.filter(queryset_filter)
