# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet

from ..models.tenants import ACITenant


class ACITenantFilterSet(NetBoxModelFilterSet):
    """Filter set for ACI Tenant model."""

    class Meta:
        model = ACITenant
        fields: tuple = (
            "id",
            "name",
            "alias",
            "description",
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
