# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from dcim.models import Interface
from netbox.filtersets import NetBoxModelFilterSet
from users.filterset_mixins import OwnerFilterMixin
from utilities.filtersets import register_filterset

from ...models.fabric.fabrics import ACIFabric
from ...models.fabric.node_interfaces import ACINodeInterface
from ...models.fabric.nodes import ACINode
from ...models.fabric.pods import ACIPod
from ..mixins import NBTenantFilterSetMixin


@register_filterset
class ACINodeInterfaceFilterSet(
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    NetBoxModelFilterSet,
):
    """Filter set for the ACI Node Interface model."""

    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_node___aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_node___aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    aci_pod_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_node__aci_pod",
        queryset=ACIPod.objects.all(),
        to_field_name="id",
        label=_("ACI Pod (ID)"),
    )
    aci_node_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACINode.objects.all(),
        to_field_name="id",
        label=_("ACI Node (ID)"),
    )
    nb_interface_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Interface.objects.all(),
        to_field_name="id",
        label=_("NetBox interface (ID)"),
    )

    class Meta:
        model = ACINodeInterface
        fields: tuple = (
            "id",
            "module",
            "port",
            "sub_port",
            "description",
        )

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's related object names."""
        if not value.strip():
            return queryset
        queryset_filter: Q = (
            Q(aci_node__name__icontains=value)
            | Q(nb_interface__name__icontains=value)
            | Q(description__icontains=value)
        )
        return queryset.filter(queryset_filter)
