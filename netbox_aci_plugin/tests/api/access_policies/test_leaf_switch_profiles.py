# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""API tests for access-policy Leaf Switch Profile models."""

from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....models.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlock,
    ACILeafSelector,
    ACILeafSwitchProfile,
)
from ....models.fabric.fabrics import ACIFabric


class ACILeafSwitchProfileAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Leaf Switch Profile."""

    model = ACILeafSwitchProfile
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
        """Set up ACI Leaf Switch Profile for API view testing."""
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
        leaf_switch_profiles: tuple = (
            ACILeafSwitchProfile(
                name="ACILeafSwitchProfileTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                aci_fabric=aci_fabric1,
                comments="# ACI Test 1",
            ),
            ACILeafSwitchProfile(
                name="ACILeafSwitchProfileTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                aci_fabric=aci_fabric1,
                comments="# ACI Test 2",
            ),
            ACILeafSwitchProfile(
                name="ACILeafSwitchProfileTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                aci_fabric=aci_fabric2,
                comments="# ACI Test 3",
            ),
        )
        ACILeafSwitchProfile.objects.bulk_create(leaf_switch_profiles)

        cls.create_data: list[dict] = [
            {
                "name": "ACILeafSwitchProfileTestAPI4",
                "name_alias": "Testing",
                "description": "Fourth ACI Test",
                "aci_fabric": aci_fabric1.id,
                "comments": "# ACI Test 4",
            },
            {
                "name": "ACILeafSwitchProfileTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "aci_fabric": aci_fabric2.id,
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACILeafSelectorAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Leaf Selector."""

    model = ACILeafSelector
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_leaf_switch_profile",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acileafswitchprofile",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Leaf Selector for API view testing."""
        aci_fabric = ACIFabric.objects.create(
            name="ACITestFabricAPI1",
            fabric_id=111,
            infra_vlan_vid=3900,
        )
        aci_leaf_switch_profile = ACILeafSwitchProfile.objects.create(
            name="ACILeafSelectorTestAPIProfile",
            aci_fabric=aci_fabric,
        )

        leaf_selectors: tuple = (
            ACILeafSelector(
                name="ACILeafSelectorTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                aci_leaf_switch_profile=aci_leaf_switch_profile,
                comments="# ACI Test 1",
            ),
            ACILeafSelector(
                name="ACILeafSelectorTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                aci_leaf_switch_profile=aci_leaf_switch_profile,
                comments="# ACI Test 2",
            ),
            ACILeafSelector(
                name="ACILeafSelectorTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                aci_leaf_switch_profile=aci_leaf_switch_profile,
                comments="# ACI Test 3",
            ),
        )
        ACILeafSelector.objects.bulk_create(leaf_selectors)

        cls.create_data: list[dict] = [
            {
                "name": "ACILeafSelectorTestAPI4",
                "name_alias": "Testing",
                "description": "Fourth ACI Test",
                "aci_leaf_switch_profile": aci_leaf_switch_profile.id,
                "comments": "# ACI Test 4",
            },
            {
                "name": "ACILeafSelectorTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "aci_leaf_switch_profile": aci_leaf_switch_profile.id,
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACILeafNodeBlockAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Leaf Node Block."""

    model = ACILeafNodeBlock
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_leaf_selector",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "node_id_from",
        "node_id_to",
        "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acileafselector",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Leaf Node Block for API view testing."""
        aci_fabric = ACIFabric.objects.create(
            name="ACITestFabricAPI1",
            fabric_id=111,
            infra_vlan_vid=3900,
        )
        aci_leaf_switch_profile = ACILeafSwitchProfile.objects.create(
            name="ACILeafNodeBlockTestAPIProfile",
            aci_fabric=aci_fabric,
        )
        aci_leaf_selector = ACILeafSelector.objects.create(
            name="ACILeafNodeBlockTestAPISelector",
            aci_leaf_switch_profile=aci_leaf_switch_profile,
        )

        leaf_node_blocks: tuple = (
            ACILeafNodeBlock(
                name="ACILeafNodeBlockTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                aci_leaf_selector=aci_leaf_selector,
                node_id_from=101,
                node_id_to=199,
                comments="# ACI Test 1",
            ),
            ACILeafNodeBlock(
                name="ACILeafNodeBlockTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                aci_leaf_selector=aci_leaf_selector,
                node_id_from=200,
                node_id_to=299,
                comments="# ACI Test 2",
            ),
            ACILeafNodeBlock(
                name="ACILeafNodeBlockTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                aci_leaf_selector=aci_leaf_selector,
                node_id_from=300,
                node_id_to=399,
                comments="# ACI Test 3",
            ),
        )
        ACILeafNodeBlock.objects.bulk_create(leaf_node_blocks)

        cls.create_data: list[dict] = [
            {
                "name": "ACILeafNodeBlockTestAPI4",
                "name_alias": "Testing",
                "description": "Fourth ACI Test",
                "aci_leaf_selector": aci_leaf_selector.id,
                "node_id_from": 400,
                "node_id_to": 499,
                "comments": "# ACI Test 4",
            },
            {
                "name": "ACILeafNodeBlockTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "aci_leaf_selector": aci_leaf_selector.id,
                "node_id_from": 500,
                "node_id_to": 599,
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "comments": "New comments",
        }
