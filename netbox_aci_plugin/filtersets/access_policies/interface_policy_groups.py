# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from netbox.filtersets import NetBoxModelFilterSet
from users.filterset_mixins import OwnerFilterMixin
from utilities.filtersets import register_filterset

from ...choices import LeafInterfacePolicyGroupTypeChoices
from ...models.access_policies.aaep import ACIAttachableAccessEntityProfile
from ...models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ..mixins import ACIFabricFilterSetMixin, NBTenantFilterSetMixin


@register_filterset
class ACILeafInterfacePolicyGroupFilterSet(
    ACIFabricFilterSetMixin,
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    NetBoxModelFilterSet,
):
    """Filter set for the ACI Leaf Interface Policy Group model."""

    group_type = django_filters.MultipleChoiceFilter(
        choices=LeafInterfacePolicyGroupTypeChoices,
        null_value=None,
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

    class Meta:
        model = ACILeafInterfacePolicyGroup
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "group_type",
            "aci_aaep",
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
