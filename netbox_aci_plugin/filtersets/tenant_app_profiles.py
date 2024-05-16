# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from netbox.filtersets import NetBoxModelFilterSet
from tenancy.models import Tenant

from ..models.tenant_app_profiles import ACIAppProfile
from ..models.tenants import ACITenant


class ACIAppProfileFilterSet(NetBoxModelFilterSet):
    """Filter set for ACI Application Profile model."""

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
        label=_("NetBox Tenant (name)"),
    )
    nb_tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        to_field_name="id",
        label=_("NetBox Tenant (ID)"),
    )

    class Meta:
        model = ACIAppProfile
        fields: tuple = (
            "id",
            "name",
            "alias",
            "description",
            "aci_tenant",
            "nb_tenant",
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
