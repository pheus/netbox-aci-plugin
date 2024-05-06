# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.filtersets import NetBoxModelFilterSet

from ..models.tenants import ACITenant


class ACITenantFilterSet(NetBoxModelFilterSet):
    """Filter set for ACI Tenant model."""

    class Meta:
        model = ACITenant
        fields: tuple = (
            "id",
            "name",
        )

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the models description."""
        return queryset.filter(description__icontains=value)
