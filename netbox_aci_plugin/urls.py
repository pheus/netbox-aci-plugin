# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import include, path
from utilities.urls import get_model_urls

from .views.tenant_app_profiles import (
    ACIAppProfileBulkDeleteView,
    ACIAppProfileBulkEditView,
    ACIAppProfileBulkImportView,
    ACIAppProfileEditView,
    ACIAppProfileListView,
    ACIEndpointGroupEditView,
    ACIEndpointGroupListView,
)
from .views.tenant_networks import (
    ACIBridgeDomainBulkDeleteView,
    ACIBridgeDomainBulkEditView,
    ACIBridgeDomainEditView,
    ACIBridgeDomainListView,
    ACIBridgeDomainSubnetEditView,
    ACIBridgeDomainSubnetListView,
    ACIVRFBulkDeleteView,
    ACIVRFBulkEditView,
    ACIVRFBulkImportView,
    ACIVRFEditView,
    ACIVRFListView,
)
from .views.tenants import (
    ACITenantBulkDeleteView,
    ACITenantBulkEditView,
    ACITenantBulkImportView,
    ACITenantEditView,
    ACITenantListView,
)

urlpatterns: tuple = (
    # ACI Tenants
    path("tenants/", ACITenantListView.as_view(), name="acitenant_list"),
    path("tenants/add/", ACITenantEditView.as_view(), name="acitenant_add"),
    path(
        "tenants/delete/",
        ACITenantBulkDeleteView.as_view(),
        name="acitenant_bulk_delete",
    ),
    path(
        "tenants/edit/",
        ACITenantBulkEditView.as_view(),
        name="acitenant_bulk_edit",
    ),
    path(
        "tenants/import/",
        ACITenantBulkImportView.as_view(),
        name="acitenant_import",
    ),
    path(
        "tenants/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "acitenant")),
    ),
    # ACI Application Profiles
    path(
        "app-profiles/",
        ACIAppProfileListView.as_view(),
        name="aciappprofile_list",
    ),
    path(
        "app-profiles/add/",
        ACIAppProfileEditView.as_view(),
        name="aciappprofile_add",
    ),
    path(
        "app-profiles/delete/",
        ACIAppProfileBulkDeleteView.as_view(),
        name="aciappprofile_bulk_delete",
    ),
    path(
        "app-profiles/edit/",
        ACIAppProfileBulkEditView.as_view(),
        name="aciappprofile_bulk_edit",
    ),
    path(
        "app-profiles/import/",
        ACIAppProfileBulkImportView.as_view(),
        name="aciappprofile_import",
    ),
    path(
        "app-profiles/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "aciappprofile")),
    ),
    # ACI Endpoint Group
    path(
        "endpoint-groups/",
        ACIEndpointGroupListView.as_view(),
        name="aciendpointgroup_list",
    ),
    path(
        "endpoint-groups/add/",
        ACIEndpointGroupEditView.as_view(),
        name="aciendpointgroup_add",
    ),
    path(
        "endpoint-groups/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "aciendpointgroup")),
    ),
    # ACI Bridge Domain
    path(
        "bridge-domains/",
        ACIBridgeDomainListView.as_view(),
        name="acibridgedomain_list",
    ),
    path(
        "bridge-domains/add/",
        ACIBridgeDomainEditView.as_view(),
        name="acibridgedomain_add",
    ),
    path(
        "bridge-domains/delete/",
        ACIBridgeDomainBulkDeleteView.as_view(),
        name="acibridgedomain_bulk_delete",
    ),
    path(
        "bridge-domains/edit/",
        ACIBridgeDomainBulkEditView.as_view(),
        name="acibridgedomain_bulk_edit",
    ),
    path(
        "bridge-domains/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "acibridgedomain")),
    ),
    # ACI Bridge Domain Subnet
    path(
        "bridge-domain-subnets/",
        ACIBridgeDomainSubnetListView.as_view(),
        name="acibridgedomainsubnet_list",
    ),
    path(
        "bridge-domain-subnets/add/",
        ACIBridgeDomainSubnetEditView.as_view(),
        name="acibridgedomainsubnet_add",
    ),
    path(
        "bridge-domain-subnets/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "acibridgedomainsubnet")),
    ),
    # ACI VRF
    path("vrfs/", ACIVRFListView.as_view(), name="acivrf_list"),
    path("vrfs/add/", ACIVRFEditView.as_view(), name="acivrf_add"),
    path(
        "vrfs/delete/",
        ACIVRFBulkDeleteView.as_view(),
        name="acivrf_bulk_delete",
    ),
    path(
        "vrfs/edit/",
        ACIVRFBulkEditView.as_view(),
        name="acivrf_bulk_edit",
    ),
    path(
        "vrfs/import/",
        ACIVRFBulkImportView.as_view(),
        name="acivrf_import",
    ),
    path(
        "vrfs/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "acivrf")),
    ),
)
