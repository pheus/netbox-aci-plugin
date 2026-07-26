# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from netbox.filtersets import NetBoxModelFilterSet
from users.filterset_mixins import OwnerFilterMixin
from utilities.filtersets import register_filterset

from ...models.fabric.nodes import ACINode
from ...models.fabric.vpc_protection_groups import ACIVPCProtectionGroup
from ..mixins import ACIFabricFilterSetMixin, NBTenantFilterSetMixin


@register_filterset
class ACIVPCProtectionGroupFilterSet(
    ACIFabricFilterSetMixin,
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    NetBoxModelFilterSet,
):
    """Filter set for the ACI VPC Protection Group model."""

    aci_node_a_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACINode.objects.all(),
        to_field_name="id",
        label=_("ACI Node A (ID)"),
    )
    aci_node_b_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACINode.objects.all(),
        to_field_name="id",
        label=_("ACI Node B (ID)"),
    )

    class Meta:
        model = ACIVPCProtectionGroup
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "logical_pair_id",
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
