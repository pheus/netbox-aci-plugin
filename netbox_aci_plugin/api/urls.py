# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.api.routers import NetBoxRouter

from . import views

app_name = "netbox_aci_plugin"
router = NetBoxRouter()
router.register("tenants", views.ACITenantListViewSet)
router.register("app-profiles", views.ACIAppProfileListViewSet)
router.register("bridge-domains", views.ACIBridgeDomainListViewSet)
router.register("bridge-domain-subnets", views.ACIBridgeDomainSubnetListViewSet)
router.register("endpoint-groups", views.ACIEndpointGroupListViewSet)
router.register("useg-endpoint-groups", views.ACIUSegEndpointGroupListViewSet)
router.register("useg-network-attributes", views.ACIUSegNetworkAttributeListViewSet)
router.register("endpoint-security-groups", views.ACIEndpointSecurityGroupListViewSet)
router.register(
    "esg-endpoint-group-selector", views.ACIEsgEndpointGroupSelectorListViewSet
)
router.register("esg-endpoint-selector", views.ACIEsgEndpointSelectorListViewSet)
router.register("vrfs", views.ACIVRFListViewSet)
router.register("contract-filters", views.ACIContractFilterListViewSet)
router.register("contract-filter-entries", views.ACIContractFilterEntryListViewSet)
router.register("contracts", views.ACIContractListViewSet)
router.register("contract-relations", views.ACIContractRelationListViewSet)
router.register("contract-subjects", views.ACIContractSubjectListViewSet)
router.register("contract-subject-filters", views.ACIContractSubjectFilterListViewSet)

urlpatterns = router.urls
