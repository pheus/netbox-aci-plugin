# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from .models.tenants import ACITenant
from .views.tenants import (
    ACITenantDeleteView,
    ACITenantEditView,
    ACITenantListView,
    ACITenantView,
)

urlpatterns: tuple = (
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
)
