# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.api.viewsets import NetBoxModelViewSet

from ..filtersets.tenant_app_profiles import (
    ACIAppProfileFilterSet,
    ACIEndpointGroupFilterSet,
)
from ..filtersets.tenant_contract_filters import (
    ACIContractFilterEntryFilterSet,
    ACIContractFilterFilterSet,
)
from ..filtersets.tenant_contracts import (
    ACIContractFilterSet,
    ACIContractRelationFilterSet,
    ACIContractSubjectFilterFilterSet,
    ACIContractSubjectFilterSet,
)
from ..filtersets.tenant_networks import (
    ACIBridgeDomainFilterSet,
    ACIBridgeDomainSubnetFilterSet,
    ACIVRFFilterSet,
)
from ..filtersets.tenants import ACITenantFilterSet
from ..models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup
from ..models.tenant_contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from ..models.tenant_contracts import (
    ACIContract,
    ACIContractRelation,
    ACIContractSubject,
    ACIContractSubjectFilter,
)
from ..models.tenant_networks import (
    ACIVRF,
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)
from ..models.tenants import ACITenant
from .serializers import (
    ACIAppProfileSerializer,
    ACIBridgeDomainSerializer,
    ACIBridgeDomainSubnetSerializer,
    ACIContractFilterEntrySerializer,
    ACIContractFilterSerializer,
    ACIContractRelationSerializer,
    ACIContractSerializer,
    ACIContractSubjectFilterSerializer,
    ACIContractSubjectSerializer,
    ACIEndpointGroupSerializer,
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


class ACIBridgeDomainListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Bridge Domain instances."""

    queryset = ACIBridgeDomain.objects.prefetch_related(
        "aci_tenant",
        "aci_vrf",
        "nb_tenant",
        "tags",
    )
    serializer_class = ACIBridgeDomainSerializer
    filterset_class = ACIBridgeDomainFilterSet


class ACIBridgeDomainSubnetListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Bridge Domain Subnet instances."""

    queryset = ACIBridgeDomainSubnet.objects.prefetch_related(
        "aci_bridge_domain",
        "gateway_ip_address",
        "nb_tenant",
        "tags",
    )
    serializer_class = ACIBridgeDomainSubnetSerializer
    filterset_class = ACIBridgeDomainSubnetFilterSet


class ACIEndpointGroupListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Endpoint Group instances."""

    queryset = ACIEndpointGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
        "tags",
    )
    serializer_class = ACIEndpointGroupSerializer
    filterset_class = ACIEndpointGroupFilterSet


class ACIContractFilterListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Contract Filter instances."""

    queryset = ACIContractFilter.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )
    serializer_class = ACIContractFilterSerializer
    filterset_class = ACIContractFilterFilterSet


class ACIContractFilterEntryListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Contract Filter Entry instances."""

    queryset = ACIContractFilterEntry.objects.prefetch_related(
        "aci_contract_filter",
        "tags",
    )
    serializer_class = ACIContractFilterEntrySerializer
    filterset_class = ACIContractFilterEntryFilterSet


class ACIContractListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Contract instances."""

    queryset = ACIContract.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )
    serializer_class = ACIContractSerializer
    filterset_class = ACIContractFilterSet


class ACIContractRelationListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Contract Relation instances."""

    queryset = ACIContractRelation.objects.prefetch_related(
        "aci_contract",
        "aci_object",
        "tags",
    )
    serializer_class = ACIContractRelationSerializer
    filterset_class = ACIContractRelationFilterSet


class ACIContractSubjectListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Contract Subject instances."""

    queryset = ACIContractSubject.objects.prefetch_related(
        "aci_contract",
        "nb_tenant",
        "tags",
    )
    serializer_class = ACIContractSubjectSerializer
    filterset_class = ACIContractSubjectFilterSet


class ACIContractSubjectFilterListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Contract Subject Filter instances."""

    queryset = ACIContractSubjectFilter.objects.prefetch_related(
        "aci_contract_filter",
        "aci_contract_subject",
        "tags",
    )
    serializer_class = ACIContractSubjectFilterSerializer
    filterset_class = ACIContractSubjectFilterFilterSet
