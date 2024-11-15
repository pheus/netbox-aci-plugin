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

from ..choices import (
    ContractScopeChoices,
    QualityOfServiceClassChoices,
    QualityOfServiceDSCPChoices,
)
from ..models.tenant_contracts import ACIContract
from ..models.tenants import ACITenant


class ACIContractFilterSet(NetBoxModelFilterSet):
    """Filter set for the ACI Contract model."""

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
    qos_class = django_filters.MultipleChoiceFilter(
        choices=QualityOfServiceClassChoices,
        null_value=None,
        label=_("QoS class"),
    )
    scope = django_filters.MultipleChoiceFilter(
        choices=ContractScopeChoices,
        null_value=None,
        label=_("Scope"),
    )
    target_dscp = django_filters.MultipleChoiceFilter(
        choices=QualityOfServiceDSCPChoices,
        null_value=None,
        label=_("Target DSCP"),
    )
    present_in_aci_tenant_or_common_id = django_filters.ModelChoiceFilter(
        queryset=ACITenant.objects.all(),
        method="filter_present_in_aci_tenant_or_common_id",
        label=_("ACI Tenant (ID)"),
    )

    class Meta:
        model = ACIContract
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "nb_tenant",
            "qos_class",
            "scope",
            "target_dscp",
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
