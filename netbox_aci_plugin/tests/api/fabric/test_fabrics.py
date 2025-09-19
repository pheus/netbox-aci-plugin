# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ipam.models import VLAN, Prefix
from tenancy.models import Tenant
from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....models.fabric.fabrics import ACIFabric


class ACIFabricAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Fabric."""

    model = ACIFabric
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "description",
        "display",
        "fabric_id",
        "id",
        "name",
        "nb_tenant",
        "url",
    ]
    user_permissions = (
        "ipam.view_prefix",
        "ipam.view_vlan",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Fabric for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        infra_vlan1 = VLAN.objects.create(vid=3000, name="Infra-VLAN1")
        infra_vlan2 = VLAN.objects.create(vid=4000, name="Infra-VLAN1")
        gipo_pool1 = Prefix.objects.create(prefix="225.0.0.0/15")
        gipo_pool2 = Prefix.objects.create(prefix="225.0.0.0/15")

        aci_fabrics: tuple = (
            ACIFabric(
                name="ACIFabricTestAPI1",
                description="First ACI Test",
                fabric_id="101",
                infra_vlan_vid="3000",
                infra_vlan=infra_vlan1,
                gipo_pool=gipo_pool1,
                nb_tenant=nb_tenant1,
                comments="# ACI Test 1",
            ),
            ACIFabric(
                name="ACIFabricTestAPI2",
                description="Second ACI Test",
                fabric_id="102",
                infra_vlan_vid="3000",
                nb_tenant=nb_tenant2,
                comments="# ACI Test 2",
            ),
            ACIFabric(
                name="ACIFabricTestAPI3",
                description="Third ACI Test",
                fabric_id="103",
                infra_vlan_vid="4000",
                infra_vlan=infra_vlan2,
                gipo_pool=gipo_pool2,
                nb_tenant=nb_tenant2,
                comments="# ACI Test 3",
            ),
        )
        ACIFabric.objects.bulk_create(aci_fabrics)

        cls.create_data: list[dict] = [
            {
                "name": "ACIFabricTestAPI4",
                "description": "Forth ACI Test",
                "fabric_id": 104,
                "infra_vlan_vid": 3000,
                "infra_vlan": infra_vlan1.id,
                "gipo_pool": gipo_pool1.id,
                "nb_tenant": nb_tenant1.id,
                "comments": "# ACI Test 4",
            },
            {
                "name": "ACIFabricTestAPI5",
                "description": "Fifth ACI Test",
                "fabric_id": 105,
                "infra_vlan_vid": 4000,
                "infra_vlan": infra_vlan2.id,
                "gipo_pool": gipo_pool2.id,
                "nb_tenant": nb_tenant2.id,
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }
