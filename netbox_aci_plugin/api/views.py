# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.api.viewsets import NetBoxModelViewSet

from ..filtersets.tenant.app_profiles import ACIAppProfileFilterSet
from ..filtersets.tenant.bridge_domains import (
    ACIBridgeDomainFilterSet,
    ACIBridgeDomainSubnetFilterSet,
)
from ..filtersets.tenant.contract_filters import (
    ACIContractFilterEntryFilterSet,
    ACIContractFilterFilterSet,
)
from ..filtersets.tenant.contracts import (
    ACIContractFilterSet,
    ACIContractRelationFilterSet,
    ACIContractSubjectFilterFilterSet,
    ACIContractSubjectFilterSet,
)
from ..filtersets.tenant.endpoint_groups import (
    ACIEndpointGroupFilterSet,
    ACIUSegEndpointGroupFilterSet,
    ACIUSegNetworkAttributeFilterSet,
)
from ..filtersets.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroupFilterSet,
    ACIEsgEndpointGroupSelectorFilterSet,
    ACIEsgEndpointSelectorFilterSet,
)
from ..filtersets.tenant.tenants import ACITenantFilterSet
from ..filtersets.tenant.vrfs import ACIVRFFilterSet
from ..models.tenant.app_profiles import ACIAppProfile
from ..models.tenant.bridge_domains import (
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)
from ..models.tenant.contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from ..models.tenant.contracts import (
    ACIContract,
    ACIContractRelation,
    ACIContractSubject,
    ACIContractSubjectFilter,
)
from ..models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
    ACIUSegNetworkAttribute,
)
from ..models.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroup,
    ACIEsgEndpointGroupSelector,
    ACIEsgEndpointSelector,
)
from ..models.tenant.tenants import ACITenant
from ..models.tenant.vrfs import ACIVRF
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
    ACIEndpointSecurityGroupSerializer,
    ACIEsgEndpointGroupSelectorSerializer,
    ACIEsgEndpointSelectorSerializer,
    ACITenantSerializer,
    ACIUSegEndpointGroupSerializer,
    ACIUSegNetworkAttributeSerializer,
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


class ACIUSegEndpointGroupListViewSet(NetBoxModelViewSet):
    """API view for listing ACI uSeg Endpoint Group instances."""

    queryset = ACIUSegEndpointGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
        "tags",
    )
    serializer_class = ACIUSegEndpointGroupSerializer
    filterset_class = ACIUSegEndpointGroupFilterSet


class ACIUSegNetworkAttributeListViewSet(NetBoxModelViewSet):
    """API view for listing ACI uSeg Network Attribute instances."""

    queryset = ACIUSegNetworkAttribute.objects.prefetch_related(
        "aci_useg_endpoint_group",
        "attr_object",
        "nb_tenant",
        "tags",
    )
    serializer_class = ACIUSegNetworkAttributeSerializer
    filterset_class = ACIUSegNetworkAttributeFilterSet


class ACIEndpointSecurityGroupListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Endpoint Security Group instances."""

    queryset = ACIEndpointSecurityGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_vrf",
        "nb_tenant",
        "tags",
    )
    serializer_class = ACIEndpointSecurityGroupSerializer
    filterset_class = ACIEndpointSecurityGroupFilterSet


class ACIEsgEndpointGroupSelectorListViewSet(NetBoxModelViewSet):
    """API view for listing ACI ESG Endpoint Group (EPG) Selector instances."""

    queryset = ACIEsgEndpointGroupSelector.objects.prefetch_related(
        "aci_endpoint_security_group",
        "aci_epg_object",
        "nb_tenant",
        "tags",
    )
    serializer_class = ACIEsgEndpointGroupSelectorSerializer
    filterset_class = ACIEsgEndpointGroupSelectorFilterSet


class ACIEsgEndpointSelectorListViewSet(NetBoxModelViewSet):
    """API view for listing ACI ESG Endpoint Selector instances."""

    queryset = ACIEsgEndpointSelector.objects.prefetch_related(
        "aci_endpoint_security_group",
        "ep_object",
        "nb_tenant",
        "tags",
    )
    serializer_class = ACIEsgEndpointSelectorSerializer
    filterset_class = ACIEsgEndpointSelectorFilterSet


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
