# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.api.routers import NetBoxRouter

from . import views

app_name = "netbox_aci_plugin"
router = NetBoxRouter()
router.register("tenants", views.ACITenantListViewSet)
router.register("app-profiles", views.ACIAppProfileListViewSet)

urlpatterns = router.urls
