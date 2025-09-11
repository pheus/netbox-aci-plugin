# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet

from ...models.tenant.tenants import ACITenant
from ..mixins import NBTenantFilterSetMixin


class ACITenantFilterSet(NBTenantFilterSetMixin, NetBoxModelFilterSet):
    """Filter set for the ACI Tenant model."""

    class Meta:
        model = ACITenant
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
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
