# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later
import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from netbox.filtersets import NetBoxModelFilterSet
from tenancy.models import Tenant

from ..models.tenants import ACITenant


class ACITenantFilterSet(NetBoxModelFilterSet):
    """Filter set for ACI Tenant model."""

    tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="tenant__name",
        queryset=Tenant.objects.all(),
        to_field_name="name",
        label=_("Tenant (name)"),
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label=_("Tenant (ID)"),
    )

    class Meta:
        model = ACITenant
        fields: tuple = (
            "id",
            "name",
            "alias",
            "description",
            "tenant",
        )

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the models description."""
        if not value.strip():
            return queryset
        queryset_filter = (
            Q(name__icontains=value)
            | Q(alias__icontains=value)
            | Q(description__icontains=value)
        )
        return queryset.filter(queryset_filter)
