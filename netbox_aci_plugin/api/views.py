# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.api.viewsets import NetBoxModelViewSet

from ..filtersets.tenants import ACITenantFilterSet
from ..models.tenants import ACITenant
from .serializers import ACITenantSerializer


class ACITenantListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Tenant instances."""

    queryset = ACITenant.objects.prefetch_related("tags")
    serializer_class = ACITenantSerializer
    filterset_class = ACITenantFilterSet
