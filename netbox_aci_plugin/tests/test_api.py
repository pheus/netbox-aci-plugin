# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import reverse
from rest_framework import status
from tenancy.models import Tenant
from utilities.testing import APITestCase, APIViewTestCases

from ..api.urls import app_name
from ..models.tenant_app_profiles import ACIAppProfile
from ..models.tenants import ACITenant


class AppTest(APITestCase):
    """API test case for NetBox ACI plugin."""

    def test_root(self) -> None:
        """Test API root access of plugin."""
        url = reverse("plugins-api:netbox_aci_plugin-api:api-root")
        response = self.client.get(f"{url}?format=api", **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ACITenantAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Tenant."""

    model = ACITenant
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "alias",
        "description",
        "display",
        "id",
        "name",
        "nb_tenant",
        "url",
    ]

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Tenants for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_tenants = (
            ACITenant(
                name="ACITestTenantAPI1",
                alias="TestingTenant1",
                description="First ACI Test Tenant",
                comments="# ACI Test Tenant 1",
                nb_tenant=nb_tenant1,
            ),
            ACITenant(
                name="ACITestTenantAPI2",
                alias="TestingTenant2",
                description="Second ACI Test Tenant",
                comments="# ACI Test Tenant 2",
                nb_tenant=nb_tenant1,
            ),
            ACITenant(
                name="ACITestTenantAPI3",
                alias="TestingTenant3",
                description="Third ACI Test Tenant",
                comments="# ACI Test Tenant 3",
                nb_tenant=nb_tenant2,
            ),
        )
        ACITenant.objects.bulk_create(aci_tenants)

        cls.create_data = [
            {
                "name": "ACITestTenantAPI4",
                "alias": "TestingTenant4",
                "description": "Forth ACI Test Tenant",
                "comments": "# ACI Test Tenant 4",
                "nb_tenant": nb_tenant1.id,
            },
            {
                "name": "ACITestTenantAPI5",
                "alias": "TestingTenant5",
                "description": "Fifth ACI Test Tenant",
                "comments": "# ACI Test Tenant 5",
                "nb_tenant": nb_tenant2.id,
            },
        ]


class ACIAppProfileAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI AppProfile."""

    model = ACIAppProfile
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_tenant",
        "alias",
        "description",
        "display",
        "id",
        "name",
        "nb_tenant",
        "url",
    ]

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI AppProfile for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI1")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI2")

        aci_app_profiles = (
            ACIAppProfile(
                name="ACIAppProfileTestAPI1",
                alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_tenant=aci_tenant1,
                nb_tenant=nb_tenant1,
            ),
            ACIAppProfile(
                name="ACIAppProfileTestAPI2",
                alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_tenant=aci_tenant2,
                nb_tenant=nb_tenant1,
            ),
            ACIAppProfile(
                name="ACIAppProfileTestAPI3",
                alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_tenant=aci_tenant1,
                nb_tenant=nb_tenant2,
            ),
        )
        ACIAppProfile.objects.bulk_create(aci_app_profiles)

        cls.create_data = [
            {
                "name": "ACIAppProfileTestAPI4",
                "alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_tenant": aci_tenant2.id,
                "nb_tenant": nb_tenant1.id,
            },
            {
                "name": "ACIAppProfileTestAPI5",
                "alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_tenant": aci_tenant1.id,
                "nb_tenant": nb_tenant2.id,
            },
        ]
