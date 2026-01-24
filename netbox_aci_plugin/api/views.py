# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.api.viewsets import NetBoxModelViewSet

from ..filtersets.fabric.fabrics import ACIFabricFilterSet
from ..filtersets.fabric.nodes import ACINodeFilterSet
from ..filtersets.fabric.pods import ACIPodFilterSet
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
from ..models.fabric.fabrics import ACIFabric
from ..models.fabric.nodes import ACINode
from ..models.fabric.pods import ACIPod
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
    ACIFabricSerializer,
    ACINodeSerializer,
    ACIPodSerializer,
    ACITenantSerializer,
    ACIUSegEndpointGroupSerializer,
    ACIUSegNetworkAttributeSerializer,
    ACIVRFSerializer,
)


class ACIFabricListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Fabric instances."""

    queryset = ACIFabric.objects.select_related(
        "infra_vlan",
        "gipo_pool",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIFabricSerializer
    filterset_class = ACIFabricFilterSet


class ACIPodListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Pod instances."""

    queryset = ACIPod.objects.select_related(
        "aci_fabric",
        "tep_pool",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIPodSerializer
    filterset_class = ACIPodFilterSet


class ACINodeListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Node instances."""

    queryset = ACINode.objects.select_related(
        "aci_pod",
        "node_object_type",
        "tep_ip_address",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "node_object",
        "tags",
    )
    serializer_class = ACINodeSerializer
    filterset_class = ACINodeFilterSet


class ACITenantListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Tenant instances."""

    queryset = ACITenant.objects.select_related(
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACITenantSerializer
    filterset_class = ACITenantFilterSet


class ACIAppProfileListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Application Profile instances."""

    queryset = ACIAppProfile.objects.select_related(
        "aci_tenant",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIAppProfileSerializer
    filterset_class = ACIAppProfileFilterSet


class ACIVRFListViewSet(NetBoxModelViewSet):
    """API view for listing ACI VRF instances."""

    queryset = ACIVRF.objects.select_related(
        "aci_tenant",
        "nb_tenant",
        "owner",
        "nb_vrf",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIVRFSerializer
    filterset_class = ACIVRFFilterSet


class ACIBridgeDomainListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Bridge Domain instances."""

    queryset = ACIBridgeDomain.objects.select_related(
        "aci_tenant",
        "aci_vrf",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIBridgeDomainSerializer
    filterset_class = ACIBridgeDomainFilterSet


class ACIBridgeDomainSubnetListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Bridge Domain Subnet instances."""

    queryset = ACIBridgeDomainSubnet.objects.select_related(
        "aci_bridge_domain",
        "gateway_ip_address",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIBridgeDomainSubnetSerializer
    filterset_class = ACIBridgeDomainSubnetFilterSet


class ACIEndpointGroupListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Endpoint Group instances."""

    queryset = ACIEndpointGroup.objects.select_related(
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIEndpointGroupSerializer
    filterset_class = ACIEndpointGroupFilterSet


class ACIUSegEndpointGroupListViewSet(NetBoxModelViewSet):
    """API view for listing ACI uSeg Endpoint Group instances."""

    queryset = ACIUSegEndpointGroup.objects.select_related(
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIUSegEndpointGroupSerializer
    filterset_class = ACIUSegEndpointGroupFilterSet


class ACIUSegNetworkAttributeListViewSet(NetBoxModelViewSet):
    """API view for listing ACI uSeg Network Attribute instances."""

    queryset = ACIUSegNetworkAttribute.objects.select_related(
        "aci_useg_endpoint_group",
        "attr_object_type",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "attr_object",
        "tags",
    )
    serializer_class = ACIUSegNetworkAttributeSerializer
    filterset_class = ACIUSegNetworkAttributeFilterSet


class ACIEndpointSecurityGroupListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Endpoint Security Group instances."""

    queryset = ACIEndpointSecurityGroup.objects.select_related(
        "aci_app_profile",
        "aci_vrf",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIEndpointSecurityGroupSerializer
    filterset_class = ACIEndpointSecurityGroupFilterSet


class ACIEsgEndpointGroupSelectorListViewSet(NetBoxModelViewSet):
    """API view for listing ACI ESG Endpoint Group (EPG) Selector instances."""

    queryset = ACIEsgEndpointGroupSelector.objects.select_related(
        "aci_endpoint_security_group",
        "aci_epg_object_type",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "aci_epg_object",
        "tags",
    )
    serializer_class = ACIEsgEndpointGroupSelectorSerializer
    filterset_class = ACIEsgEndpointGroupSelectorFilterSet


class ACIEsgEndpointSelectorListViewSet(NetBoxModelViewSet):
    """API view for listing ACI ESG Endpoint Selector instances."""

    queryset = ACIEsgEndpointSelector.objects.select_related(
        "aci_endpoint_security_group",
        "ep_object_type",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "ep_object",
        "tags",
    )
    serializer_class = ACIEsgEndpointSelectorSerializer
    filterset_class = ACIEsgEndpointSelectorFilterSet


class ACIContractFilterListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Contract Filter instances."""

    queryset = ACIContractFilter.objects.select_related(
        "aci_tenant",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIContractFilterSerializer
    filterset_class = ACIContractFilterFilterSet


class ACIContractFilterEntryListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Contract Filter Entry instances."""

    queryset = ACIContractFilterEntry.objects.select_related(
        "aci_contract_filter",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIContractFilterEntrySerializer
    filterset_class = ACIContractFilterEntryFilterSet


class ACIContractListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Contract instances."""

    queryset = ACIContract.objects.select_related(
        "aci_tenant",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIContractSerializer
    filterset_class = ACIContractFilterSet


class ACIContractRelationListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Contract Relation instances."""

    queryset = ACIContractRelation.objects.select_related(
        "aci_contract",
        "aci_object_type",
    ).prefetch_related(
        "aci_object",
        "tags",
    )
    serializer_class = ACIContractRelationSerializer
    filterset_class = ACIContractRelationFilterSet


class ACIContractSubjectListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Contract Subject instances."""

    queryset = ACIContractSubject.objects.select_related(
        "aci_contract",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIContractSubjectSerializer
    filterset_class = ACIContractSubjectFilterSet


class ACIContractSubjectFilterListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Contract Subject Filter instances."""

    queryset = ACIContractSubjectFilter.objects.select_related(
        "aci_contract_filter",
        "aci_contract_subject",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIContractSubjectFilterSerializer
    filterset_class = ACIContractSubjectFilterFilterSet
