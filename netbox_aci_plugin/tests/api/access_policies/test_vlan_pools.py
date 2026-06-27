# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""API tests for access-policy VLAN pool models."""

from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....choices import (
    VLANAllocationModeChoices,
    VLANPoolRangeAllocationModeChoices,
    VLANPoolRangeRoleChoices,
)
from ....models.access_policies.vlan_pools import ACIVLANPool, ACIVLANPoolRange
from ....models.fabric.fabrics import ACIFabric


class ACIVLANPoolAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI VLAN Pool."""

    model = ACIVLANPool
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_fabric",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acifabric",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI VLAN Pool for API view testing."""
        aci_fabric1 = ACIFabric.objects.create(
            name="ACITestFabricAPI1",
            fabric_id=111,
            infra_vlan_vid=3900,
        )
        aci_fabric2 = ACIFabric.objects.create(
            name="ACITestFabricAPI2",
            fabric_id=112,
            infra_vlan_vid=3900,
        )
        vlan_pools: tuple = (
            ACIVLANPool(
                name="ACIVLANPoolTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                aci_fabric=aci_fabric1,
                allocation_mode=VLANAllocationModeChoices.MODE_STATIC,
                comments="# ACI Test 1",
            ),
            ACIVLANPool(
                name="ACIVLANPoolTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                aci_fabric=aci_fabric1,
                allocation_mode=VLANAllocationModeChoices.MODE_DYNAMIC,
                comments="# ACI Test 2",
            ),
            ACIVLANPool(
                name="ACIVLANPoolTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                aci_fabric=aci_fabric2,
                allocation_mode=VLANAllocationModeChoices.MODE_STATIC,
                comments="# ACI Test 3",
            ),
        )
        ACIVLANPool.objects.bulk_create(vlan_pools)

        cls.create_data: list[dict] = [
            {
                "name": "ACIVLANPoolTestAPI4",
                "name_alias": "Testing",
                "description": "Fourth ACI Test",
                "aci_fabric": aci_fabric1.id,
                "allocation_mode": VLANAllocationModeChoices.MODE_STATIC,
                "comments": "# ACI Test 4",
            },
            {
                "name": "ACIVLANPoolTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "aci_fabric": aci_fabric2.id,
                "allocation_mode": VLANAllocationModeChoices.MODE_DYNAMIC,
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIVLANPoolRangeAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI VLAN Pool Range."""

    model = ACIVLANPoolRange
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_vlan_pool",
        "display",
        "id",
        "url",
        "vlan_id_from",
        "vlan_id_to",
    ]
    user_permissions = ("netbox_aci_plugin.view_acivlanpool",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI VLAN Pool Range for API view testing."""
        aci_fabric = ACIFabric.objects.create(
            name="ACITestFabricAPI1",
            fabric_id=111,
            infra_vlan_vid=3900,
        )
        aci_vlan_pool = ACIVLANPool.objects.create(
            name="ACIVLANPoolRangeTestAPI",
            aci_fabric=aci_fabric,
        )
        vlan_pool_ranges: tuple = (
            ACIVLANPoolRange(
                aci_vlan_pool=aci_vlan_pool,
                vlan_id_from=100,
                vlan_id_to=199,
                role=VLANPoolRangeRoleChoices.ROLE_EXTERNAL,
                comments="# ACI Test 1",
            ),
            ACIVLANPoolRange(
                aci_vlan_pool=aci_vlan_pool,
                vlan_id_from=200,
                vlan_id_to=299,
                allocation_mode=VLANPoolRangeAllocationModeChoices.MODE_DYNAMIC,
                role=VLANPoolRangeRoleChoices.ROLE_INTERNAL,
                comments="# ACI Test 2",
            ),
            ACIVLANPoolRange(
                aci_vlan_pool=aci_vlan_pool,
                vlan_id_from=300,
                vlan_id_to=399,
                comments="# ACI Test 3",
            ),
        )
        ACIVLANPoolRange.objects.bulk_create(vlan_pool_ranges)

        cls.create_data: list[dict] = [
            {
                "aci_vlan_pool": aci_vlan_pool.id,
                "vlan_id_from": 400,
                "vlan_id_to": 499,
                "allocation_mode": VLANPoolRangeAllocationModeChoices.MODE_INHERIT,
                "role": VLANPoolRangeRoleChoices.ROLE_EXTERNAL,
                "comments": "# ACI Test 4",
            },
            {
                "aci_vlan_pool": aci_vlan_pool.id,
                "vlan_id_from": 500,
                "vlan_id_to": 599,
                "allocation_mode": VLANPoolRangeAllocationModeChoices.MODE_STATIC,
                "role": VLANPoolRangeRoleChoices.ROLE_INTERNAL,
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "comments": "New comments",
        }
