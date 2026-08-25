# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.api.routers import NetBoxRouter

from . import views

app_name = "netbox_aci_plugin"
router = NetBoxRouter()

# ACI Fabric
router.register("fabrics", views.ACIFabricListViewSet)
router.register("pods", views.ACIPodListViewSet)
router.register("nodes", views.ACINodeListViewSet)
router.register("node-interfaces", views.ACINodeInterfaceListViewSet)
router.register("vpc-protection-groups", views.ACIVPCProtectionGroupListViewSet)

# ACI Access Policies
router.register(
    "attachable-access-entity-profiles",
    views.ACIAttachableAccessEntityProfileListViewSet,
)
router.register("aaep-domain-bindings", views.ACIAAEPDomainBindingListViewSet)
router.register(
    "leaf-interface-policy-groups", views.ACILeafInterfacePolicyGroupListViewSet
)
router.register("leaf-interface-overrides", views.ACILeafInterfaceOverrideListViewSet)
router.register("leaf-interface-profiles", views.ACILeafInterfaceProfileListViewSet)
router.register("leaf-interface-selectors", views.ACILeafInterfaceSelectorListViewSet)
router.register("leaf-port-blocks", views.ACILeafPortBlockListViewSet)
router.register("leaf-switch-profiles", views.ACILeafSwitchProfileListViewSet)
router.register("leaf-selectors", views.ACILeafSelectorListViewSet)
router.register("leaf-node-blocks", views.ACILeafNodeBlockListViewSet)
router.register(
    "leaf-switch-profile-interface-bindings",
    views.ACILeafSwitchProfileInterfaceBindingListViewSet,
)
router.register("physical-domains", views.ACIPhysicalDomainListViewSet)
router.register("routed-domains", views.ACIRoutedDomainListViewSet)
router.register("vlan-pools", views.ACIVLANPoolListViewSet)
router.register("vlan-pool-ranges", views.ACIVLANPoolRangeListViewSet)

# ACI Tenant
router.register("tenants", views.ACITenantListViewSet)
router.register("app-profiles", views.ACIAppProfileListViewSet)
router.register("bridge-domains", views.ACIBridgeDomainListViewSet)
router.register("bridge-domain-subnets", views.ACIBridgeDomainSubnetListViewSet)
router.register("l3outs", views.ACIL3OutListViewSet)
router.register("external-endpoint-groups", views.ACIExternalEndpointGroupListViewSet)
router.register("external-subnets", views.ACIExternalSubnetListViewSet)
router.register(
    "bridge-domain-l3out-bindings", views.ACIBridgeDomainL3OutBindingListViewSet
)
router.register("endpoint-groups", views.ACIEndpointGroupListViewSet)
router.register("useg-endpoint-groups", views.ACIUSegEndpointGroupListViewSet)
router.register("useg-network-attributes", views.ACIUSegNetworkAttributeListViewSet)
router.register(
    "endpoint-group-domain-bindings", views.ACIEndpointGroupDomainBindingListViewSet
)
router.register(
    "endpoint-group-aaep-bindings", views.ACIEndpointGroupAAEPBindingListViewSet
)
router.register("endpoint-security-groups", views.ACIEndpointSecurityGroupListViewSet)
router.register(
    "esg-endpoint-group-selectors", views.ACIEsgEndpointGroupSelectorListViewSet
)
router.register("esg-endpoint-selectors", views.ACIEsgEndpointSelectorListViewSet)
router.register("vrfs", views.ACIVRFListViewSet)
router.register("contract-filters", views.ACIContractFilterListViewSet)
router.register("contract-filter-entries", views.ACIContractFilterEntryListViewSet)
router.register("contracts", views.ACIContractListViewSet)
router.register("contract-relations", views.ACIContractRelationListViewSet)
router.register("contract-subjects", views.ACIContractSubjectListViewSet)
router.register("contract-subject-filters", views.ACIContractSubjectFilterListViewSet)

urlpatterns = router.urls
