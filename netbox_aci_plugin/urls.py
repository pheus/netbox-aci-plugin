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
    path("tenants/", ACITenantListView.as_view(), name="acitenant_list"),
    path("tenants/add/", ACITenantEditView.as_view(), name="acitenant_add"),
    path("tenants/<int:pk>/", ACITenantView.as_view(), name="acitenant"),
    path(
        "tenants/<int:pk>/edit/",
        ACITenantEditView.as_view(),
        name="acitenant_edit",
    ),
    path(
        "tenants/<int:pk>/delete/",
        ACITenantDeleteView.as_view(),
        name="acitenant_delete",
    ),
    path(
        "tenants/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="acitenant_changelog",
        kwargs={"model": ACITenant},
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
        ACIAppProfileView.as_view(),
        name="aciappprofile",
    ),
    path(
        "app-profiles/<int:pk>/edit/",
        ACIAppProfileEditView.as_view(),
        name="aciappprofile_edit",
    ),
    path(
        "app-profiles/<int:pk>/delete/",
        ACIAppProfileDeleteView.as_view(),
        name="aciappprofile_delete",
    ),
    path(
        "app-profiles/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="aciappprofile_changelog",
        kwargs={"model": ACIAppProfile},
    ),
)
