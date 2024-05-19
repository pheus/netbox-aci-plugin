# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import include, path
from utilities.urls import get_model_urls

from .views.tenant_app_profiles import (
    ACIAppProfileEditView,
    ACIAppProfileListView,
)
from .views.tenant_networks import ACIVRFEditView, ACIVRFListView
from .views.tenants import ACITenantEditView, ACITenantListView

urlpatterns: tuple = (
    # ACI Tenants
    path("tenants/", ACITenantListView.as_view(), name="acitenant_list"),
    path("tenants/add/", ACITenantEditView.as_view(), name="acitenant_add"),
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
        "app-profiles/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "aciappprofile")),
    ),
    # ACI VRF
    path("vrfs/", ACIVRFListView.as_view(), name="acivrf_list"),
    path("vrfs/add/", ACIVRFEditView.as_view(), name="acivrf_add"),
    path(
        "vrfs/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "acivrf")),
    ),
)
