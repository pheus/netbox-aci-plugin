# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import reverse
from ipam.models import VRF
from rest_framework import status
from tenancy.models import Tenant
from utilities.testing import APITestCase, APIViewTestCases

from ..api.urls import app_name
from ..models.tenant_app_profiles import ACIAppProfile
from ..models.tenant_networks import ACIVRF
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

        cls.create_data: list[dict] = [
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


class ACIVRFAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI VRF."""

    model = ACIVRF
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_tenant",
        "alias",
        "description",
        "display",
        "id",
        "name",
        "nb_tenant",
        "nb_vrf",
        "url",
    ]

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI VRF for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        nb_vrf1 = VRF.objects.create(
            name="NetBox-VRF-API-1", tenant=nb_tenant1
        )
        nb_vrf2 = VRF.objects.create(
            name="NetBox-VRF-API-2", tenant=nb_tenant2
        )
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI5")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI6")

        aci_vrfs: tuple = (
            ACIVRF(
                name="ACIVRFTestAPI1",
                alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_tenant=aci_tenant1,
                nb_tenant=nb_tenant1,
                nb_vrf=nb_vrf1,
                bd_enforcement_enabled=False,
                dns_labels=["DNS1", "DNS2"],
                ip_data_plane_learning_enabled=True,
                pc_enforcement_direction="ingress",
                pc_enforcement_preference="unenforced",
                pim_ipv4_enabled=False,
                pim_ipv6_enabled=False,
                preferred_group_enabled=False,
            ),
            ACIVRF(
                name="ACIVRFTestAPI2",
                alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_tenant=aci_tenant2,
                nb_tenant=nb_tenant1,
                nb_vrf=nb_vrf2,
            ),
            ACIVRF(
                name="ACIVRFTestAPI3",
                alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_tenant=aci_tenant1,
                nb_tenant=nb_tenant2,
                bd_enforcement_enabled=True,
                ip_data_plane_learning_enabled=False,
                pc_enforcement_direction="egress",
                pc_enforcement_preference="enforced",
                pim_ipv4_enabled=True,
                pim_ipv6_enabled=True,
                preferred_group_enabled=True,
            ),
        )
        ACIVRF.objects.bulk_create(aci_vrfs)

        cls.create_data: list[dict] = [
            {
                "name": "ACIVRFTestAPI4",
                "alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_tenant": aci_tenant2.id,
                "nb_tenant": nb_tenant1.id,
                "nb_vrf": nb_vrf2.id,
                "bd_enforcement_enabled": False,
                "ip_data_plane_learning_enabled": True,
                "pc_enforcement_direction": "ingress",
                "pc_enforcement_preference": "unenforced",
                "pim_ipv4_enabled": True,
                "preferred_group_enabled": False,
            },
            {
                "name": "ACIVRFTestAPI5",
                "alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_tenant": aci_tenant1.id,
                "nb_tenant": nb_tenant2.id,
                "nb_vrf": nb_vrf1.id,
                "ip_data_plane_learning_enabled": False,
                "pc_enforcement_direction": "egress",
                "pc_enforcement_preference": "enforced",
                "pim_ipv6_enabled": True,
                "preferred_group_enabled": False,
            },
        ]
