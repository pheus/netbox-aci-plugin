# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from .models.tenant_app_profiles import ACIAppProfile
from .models.tenants import ACITenant
from .views.tenant_app_profiles import (
    ACIAppProfileDeleteView,
    ACIAppProfileEditView,
    ACIAppProfileListView,
    ACIAppProfileView,
)
from .views.tenants import (
    ACITenantDeleteView,
    ACITenantEditView,
    ACITenantListView,
    ACITenantView,
)

urlpatterns: tuple = (
    # ACI Tenants
    path("tenant/", ACITenantListView.as_view(), name="acitenant_list"),
    path("tenant/add/", ACITenantEditView.as_view(), name="acitenant_add"),
    path("tenant/<int:pk>/", ACITenantView.as_view(), name="acitenant"),
    path(
        "tenant/<int:pk>/edit/",
        ACITenantEditView.as_view(),
        name="acitenant_edit",
    ),
    path(
        "tenant/<int:pk>/delete/",
        ACITenantDeleteView.as_view(),
        name="acitenant_delete",
    ),
    path(
        "tenant/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="acitenant_changelog",
        kwargs={"model": ACITenant},
    ),
    # ACI Application Profiles
    path(
        "app-profile/",
        ACIAppProfileListView.as_view(),
        name="aciappprofile_list",
    ),
    path(
        "app-profile/add/",
        ACIAppProfileEditView.as_view(),
        name="aciappprofile_add",
    ),
    path(
        "app-profile/<int:pk>/",
        ACIAppProfileView.as_view(),
        name="aciappprofile",
    ),
    path(
        "app-profile/<int:pk>/edit/",
        ACIAppProfileEditView.as_view(),
        name="aciappprofile_edit",
    ),
    path(
        "app-profile/<int:pk>/delete/",
        ACIAppProfileDeleteView.as_view(),
        name="aciappprofile_delete",
    ),
    path(
        "app-profile/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="aciappprofile_changelog",
        kwargs={"model": ACIAppProfile},
    ),
)
