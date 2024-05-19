# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.api.viewsets import NetBoxModelViewSet

from ..filtersets.tenant_app_profiles import ACIAppProfileFilterSet
from ..filtersets.tenant_networks import ACIVRFFilterSet
from ..filtersets.tenants import ACITenantFilterSet
from ..models.tenant_app_profiles import ACIAppProfile
from ..models.tenant_networks import ACIVRF
from ..models.tenants import ACITenant
from .serializers import (
    ACIAppProfileSerializer,
    ACITenantSerializer,
    ACIVRFSerializer,
)


class ACITenantListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Tenant instances."""

    queryset = ACITenant.objects.prefetch_related(
        "nb_tenant",
        "tags",
    )
    serializer_class = ACITenantSerializer
    filterset_class = ACITenantFilterSet


class ACIAppProfileListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Application Profile instances."""

    queryset = ACIAppProfile.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )
    serializer_class = ACIAppProfileSerializer
    filterset_class = ACIAppProfileFilterSet


class ACIVRFListViewSet(NetBoxModelViewSet):
    """API view for listing ACI VRF instances."""

    queryset = ACIVRF.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "nb_vrf",
        "tags",
    )
    serializer_class = ACIVRFSerializer
    filterset_class = ACIVRFFilterSet
