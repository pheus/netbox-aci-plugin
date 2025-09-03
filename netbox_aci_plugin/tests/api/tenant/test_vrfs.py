# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ipam.models import VRF
from tenancy.models import Tenant
from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF


class ACIVRFAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI VRF."""

    model = ACIVRF
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_tenant",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "nb_vrf",
        "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acitenant",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI VRF for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        nb_vrf1 = VRF.objects.create(name="NetBox-VRF-API-1", tenant=nb_tenant1)
        nb_vrf2 = VRF.objects.create(name="NetBox-VRF-API-2", tenant=nb_tenant2)
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI5")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI6")

        aci_vrfs: tuple = (
            ACIVRF(
                name="ACIVRFTestAPI1",
                name_alias="Testing",
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
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_tenant=aci_tenant2,
                nb_tenant=nb_tenant1,
                nb_vrf=nb_vrf2,
            ),
            ACIVRF(
                name="ACIVRFTestAPI3",
                name_alias="Testing",
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
                "name_alias": "Testing",
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
                "name_alias": "Testing",
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
        cls.bulk_update_data = {
            "description": "New description",
        }
