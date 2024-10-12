# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from netbox.filtersets import NetBoxModelFilterSet
from tenancy.models import Tenant

from ..models.tenant_contract_filters import ACIContractFilter
from ..models.tenants import ACITenant


class ACIContractFilterFilterSet(NetBoxModelFilterSet):
    """Filter set for ACI Contract Filter model."""

    aci_tenant = django_filters.ModelMultipleChoiceFilter(
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant (name)"),
    )
    aci_tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Tenant (ID)"),
    )
    nb_tenant = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        label=_("NetBox tenant (name)"),
    )
    nb_tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        to_field_name="id",
        label=_("NetBox tenant (ID)"),
    )

    class Meta:
        model = ACIContractFilter
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
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
    def filter_present_in_aci_tenant_or_common_id(
        self, queryset, name, aci_tenant_id
    ):
        """Return a QuerySet filtered by given ACI Tenant or 'common'."""
        if aci_tenant_id is None:
            return queryset.none
        return queryset.filter(
            Q(aci_tenant=aci_tenant_id) | Q(aci_tenant__name="common")
        )
