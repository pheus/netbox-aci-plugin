# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.api.viewsets import NetBoxModelViewSet

from ..filtersets.access_policies.aaep import (
    ACIAAEPDomainBindingFilterSet,
    ACIAttachableAccessEntityProfileFilterSet,
)
from ..filtersets.access_policies.domains import (
    ACIPhysicalDomainFilterSet,
    ACIRoutedDomainFilterSet,
)
from ..filtersets.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroupFilterSet,
)
from ..filtersets.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfileFilterSet,
    ACILeafInterfaceSelectorFilterSet,
    ACILeafPortBlockFilterSet,
)
from ..filtersets.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlockFilterSet,
    ACILeafSelectorFilterSet,
    ACILeafSwitchProfileFilterSet,
)
from ..filtersets.access_policies.vlan_pools import (
    ACIVLANPoolFilterSet,
    ACIVLANPoolRangeFilterSet,
)
from ..filtersets.fabric.fabrics import ACIFabricFilterSet
from ..filtersets.fabric.node_interfaces import ACINodeInterfaceFilterSet
from ..filtersets.fabric.nodes import ACINodeFilterSet
from ..filtersets.fabric.pods import ACIPodFilterSet
from ..filtersets.fabric.vpc_protection_groups import ACIVPCProtectionGroupFilterSet
from ..filtersets.tenant.app_profiles import ACIAppProfileFilterSet
from ..filtersets.tenant.bridge_domains import (
    ACIBridgeDomainFilterSet,
    ACIBridgeDomainL3OutBindingFilterSet,
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
from ..filtersets.tenant.endpoint_group_bindings import (
    ACIEndpointGroupAAEPBindingFilterSet,
    ACIEndpointGroupDomainBindingFilterSet,
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
from ..filtersets.tenant.l3outs import (
    ACIExternalEndpointGroupFilterSet,
    ACIExternalSubnetFilterSet,
    ACIL3OutFilterSet,
)
from ..filtersets.tenant.tenants import ACITenantFilterSet
from ..filtersets.tenant.vrfs import ACIVRFFilterSet
from ..models.access_policies.aaep import (
    ACIAAEPDomainBinding,
    ACIAttachableAccessEntityProfile,
)
from ..models.access_policies.domains import ACIPhysicalDomain, ACIRoutedDomain
from ..models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ..models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
    ACILeafInterfaceSelector,
    ACILeafPortBlock,
)
from ..models.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlock,
    ACILeafSelector,
    ACILeafSwitchProfile,
)
from ..models.access_policies.vlan_pools import ACIVLANPool, ACIVLANPoolRange
from ..models.fabric.fabrics import ACIFabric
from ..models.fabric.node_interfaces import ACINodeInterface
from ..models.fabric.nodes import ACINode
from ..models.fabric.pods import ACIPod
from ..models.fabric.vpc_protection_groups import ACIVPCProtectionGroup
from ..models.tenant.app_profiles import ACIAppProfile
from ..models.tenant.bridge_domains import (
    ACIBridgeDomain,
    ACIBridgeDomainL3OutBinding,
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
from ..models.tenant.endpoint_group_bindings import (
    ACIEndpointGroupAAEPBinding,
    ACIEndpointGroupDomainBinding,
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
from ..models.tenant.l3outs import (
    ACIExternalEndpointGroup,
    ACIExternalSubnet,
    ACIL3Out,
)
from ..models.tenant.tenants import ACITenant
from ..models.tenant.vrfs import ACIVRF
from .serializers import (
    ACIAAEPDomainBindingSerializer,
    ACIAppProfileSerializer,
    ACIAttachableAccessEntityProfileSerializer,
    ACIBridgeDomainL3OutBindingSerializer,
    ACIBridgeDomainSerializer,
    ACIBridgeDomainSubnetSerializer,
    ACIContractFilterEntrySerializer,
    ACIContractFilterSerializer,
    ACIContractRelationSerializer,
    ACIContractSerializer,
    ACIContractSubjectFilterSerializer,
    ACIContractSubjectSerializer,
    ACIEndpointGroupAAEPBindingSerializer,
    ACIEndpointGroupDomainBindingSerializer,
    ACIEndpointGroupSerializer,
    ACIEndpointSecurityGroupSerializer,
    ACIEsgEndpointGroupSelectorSerializer,
    ACIEsgEndpointSelectorSerializer,
    ACIExternalEndpointGroupSerializer,
    ACIExternalSubnetSerializer,
    ACIFabricSerializer,
    ACIL3OutSerializer,
    ACILeafInterfacePolicyGroupSerializer,
    ACILeafInterfaceProfileSerializer,
    ACILeafInterfaceSelectorSerializer,
    ACILeafNodeBlockSerializer,
    ACILeafPortBlockSerializer,
    ACILeafSelectorSerializer,
    ACILeafSwitchProfileSerializer,
    ACINodeInterfaceSerializer,
    ACINodeSerializer,
    ACIPhysicalDomainSerializer,
    ACIPodSerializer,
    ACIRoutedDomainSerializer,
    ACITenantSerializer,
    ACIUSegEndpointGroupSerializer,
    ACIUSegNetworkAttributeSerializer,
    ACIVLANPoolRangeSerializer,
    ACIVLANPoolSerializer,
    ACIVPCProtectionGroupSerializer,
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


class ACINodeInterfaceListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Node Interface instances."""

    queryset = ACINodeInterface.objects.select_related(
        "aci_node",
        "aci_node__aci_pod",
        "aci_node__aci_pod__aci_fabric",
        "aci_node___aci_fabric",
        "nb_interface",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACINodeInterfaceSerializer
    filterset_class = ACINodeInterfaceFilterSet


class ACIVPCProtectionGroupListViewSet(NetBoxModelViewSet):
    """API view for listing ACI VPC Protection Group instances."""

    # Both nested Node serializers render their Pod, and the nested Pod
    # renders its Fabric, so the graph has to be walked on both sides
    queryset = ACIVPCProtectionGroup.objects.select_related(
        "aci_fabric",
        "aci_node_a",
        "aci_node_a__aci_pod",
        "aci_node_a__aci_pod__aci_fabric",
        "aci_node_a__aci_pod__nb_tenant",
        "aci_node_a__nb_tenant",
        "aci_node_b",
        "aci_node_b__aci_pod",
        "aci_node_b__aci_pod__aci_fabric",
        "aci_node_b__aci_pod__nb_tenant",
        "aci_node_b__nb_tenant",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIVPCProtectionGroupSerializer
    filterset_class = ACIVPCProtectionGroupFilterSet


class ACIAttachableAccessEntityProfileListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Attachable Access Entity Profile instances."""

    queryset = ACIAttachableAccessEntityProfile.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIAttachableAccessEntityProfileSerializer
    filterset_class = ACIAttachableAccessEntityProfileFilterSet


class ACIAAEPDomainBindingListViewSet(NetBoxModelViewSet):
    """API view for listing ACI AAEP Domain Binding instances."""

    queryset = ACIAAEPDomainBinding.objects.select_related(
        "aci_aaep",
        "aci_domain_object_type",
    ).prefetch_related(
        "aci_domain_object",
        "tags",
    )
    serializer_class = ACIAAEPDomainBindingSerializer
    filterset_class = ACIAAEPDomainBindingFilterSet


class ACILeafInterfacePolicyGroupListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Leaf Interface Policy Group instances."""

    queryset = ACILeafInterfacePolicyGroup.objects.select_related(
        "aci_fabric",
        "aci_aaep",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACILeafInterfacePolicyGroupSerializer
    filterset_class = ACILeafInterfacePolicyGroupFilterSet


class ACILeafInterfaceProfileListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Leaf Interface Profile instances."""

    queryset = ACILeafInterfaceProfile.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACILeafInterfaceProfileSerializer
    filterset_class = ACILeafInterfaceProfileFilterSet


class ACILeafInterfaceSelectorListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Leaf Interface Selector instances."""

    queryset = ACILeafInterfaceSelector.objects.select_related(
        "aci_leaf_interface_profile",
        "aci_leaf_interface_profile__aci_fabric",
        "aci_leaf_interface_policy_group",
        "aci_leaf_interface_policy_group__aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACILeafInterfaceSelectorSerializer
    filterset_class = ACILeafInterfaceSelectorFilterSet


class ACILeafPortBlockListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Leaf Port Block instances."""

    queryset = ACILeafPortBlock.objects.select_related(
        "aci_leaf_interface_selector",
        "aci_leaf_interface_selector__aci_leaf_interface_profile",
        "aci_leaf_interface_selector__aci_leaf_interface_profile__aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACILeafPortBlockSerializer
    filterset_class = ACILeafPortBlockFilterSet


class ACILeafSwitchProfileListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Leaf Switch Profile instances."""

    queryset = ACILeafSwitchProfile.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACILeafSwitchProfileSerializer
    filterset_class = ACILeafSwitchProfileFilterSet


class ACILeafSelectorListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Leaf Selector instances."""

    queryset = ACILeafSelector.objects.select_related(
        "aci_leaf_switch_profile",
        "aci_leaf_switch_profile__aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACILeafSelectorSerializer
    filterset_class = ACILeafSelectorFilterSet


class ACILeafNodeBlockListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Leaf Node Block instances."""

    queryset = ACILeafNodeBlock.objects.select_related(
        "aci_leaf_selector",
        "aci_leaf_selector__aci_leaf_switch_profile",
        "aci_leaf_selector__aci_leaf_switch_profile__aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACILeafNodeBlockSerializer
    filterset_class = ACILeafNodeBlockFilterSet


class ACIPhysicalDomainListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Physical Domain instances."""

    queryset = ACIPhysicalDomain.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
        "aci_vlan_pool",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIPhysicalDomainSerializer
    filterset_class = ACIPhysicalDomainFilterSet


class ACIRoutedDomainListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Routed Domain instances."""

    queryset = ACIRoutedDomain.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
        "aci_vlan_pool",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIRoutedDomainSerializer
    filterset_class = ACIRoutedDomainFilterSet


class ACIVLANPoolListViewSet(NetBoxModelViewSet):
    """API view for listing ACI VLAN Pool instances."""

    queryset = ACIVLANPool.objects.select_related(
        "aci_fabric",
        "nb_vlan_group",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIVLANPoolSerializer
    filterset_class = ACIVLANPoolFilterSet


class ACIVLANPoolRangeListViewSet(NetBoxModelViewSet):
    """API view for listing ACI VLAN Pool Range instances."""

    queryset = ACIVLANPoolRange.objects.select_related(
        "aci_vlan_pool",
        "aci_vlan_pool__aci_fabric",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIVLANPoolRangeSerializer
    filterset_class = ACIVLANPoolRangeFilterSet


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


class ACIL3OutListViewSet(NetBoxModelViewSet):
    """API view for listing ACI L3Out instances."""

    queryset = ACIL3Out.objects.select_related(
        "aci_tenant",
        "aci_vrf",
        "aci_routed_domain",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIL3OutSerializer
    filterset_class = ACIL3OutFilterSet


class ACIExternalEndpointGroupListViewSet(NetBoxModelViewSet):
    """API view for listing ACI External EPG instances."""

    queryset = ACIExternalEndpointGroup.objects.select_related(
        "aci_l3out",
        "aci_l3out__aci_tenant",
        "aci_l3out__aci_vrf",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIExternalEndpointGroupSerializer
    filterset_class = ACIExternalEndpointGroupFilterSet


class ACIExternalSubnetListViewSet(NetBoxModelViewSet):
    """API view for listing ACI External Subnet instances."""

    queryset = ACIExternalSubnet.objects.select_related(
        "aci_external_endpoint_group",
        "aci_external_endpoint_group__aci_l3out",
        "nb_prefix",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    serializer_class = ACIExternalSubnetSerializer
    filterset_class = ACIExternalSubnetFilterSet


class ACIBridgeDomainL3OutBindingListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Bridge Domain L3Out Binding instances."""

    queryset = ACIBridgeDomainL3OutBinding.objects.select_related(
        "aci_bridge_domain",
        "aci_l3out",
    ).prefetch_related("tags")
    serializer_class = ACIBridgeDomainL3OutBindingSerializer
    filterset_class = ACIBridgeDomainL3OutBindingFilterSet


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


class ACIEndpointGroupDomainBindingListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Endpoint Group Domain Binding instances."""

    queryset = ACIEndpointGroupDomainBinding.objects.select_related(
        "aci_epg_object_type",
        "aci_domain_object_type",
    ).prefetch_related(
        "aci_epg_object",
        "aci_domain_object",
        "tags",
    )
    serializer_class = ACIEndpointGroupDomainBindingSerializer
    filterset_class = ACIEndpointGroupDomainBindingFilterSet


class ACIEndpointGroupAAEPBindingListViewSet(NetBoxModelViewSet):
    """API view for listing ACI Endpoint Group AAEP Binding instances."""

    queryset = ACIEndpointGroupAAEPBinding.objects.select_related(
        "aci_endpoint_group__aci_app_profile__aci_tenant__aci_fabric",
        "aci_aaep__aci_fabric",
        "nb_vlan",
        "primary_nb_vlan",
    ).prefetch_related("tags")
    serializer_class = ACIEndpointGroupAAEPBindingSerializer
    filterset_class = ACIEndpointGroupAAEPBindingFilterSet


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
