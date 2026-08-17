# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""API tests for access-policy Leaf Interface Profile models."""

from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....choices import LeafInterfacePolicyGroupTypeChoices
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ....models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
    ACILeafInterfaceSelector,
    ACILeafPortBlock,
)
from ....models.fabric.fabrics import ACIFabric


class ACILeafInterfaceProfileAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Leaf Interface Profile."""

    model = ACILeafInterfaceProfile
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
        """Set up ACI Leaf Interface Profile for API view testing."""
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
        leaf_interface_profiles: tuple = (
            ACILeafInterfaceProfile(
                name="ACILeafInterfaceProfileTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                aci_fabric=aci_fabric1,
                comments="# ACI Test 1",
            ),
            ACILeafInterfaceProfile(
                name="ACILeafInterfaceProfileTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                aci_fabric=aci_fabric1,
                comments="# ACI Test 2",
            ),
            ACILeafInterfaceProfile(
                name="ACILeafInterfaceProfileTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                aci_fabric=aci_fabric2,
                comments="# ACI Test 3",
            ),
        )
        ACILeafInterfaceProfile.objects.bulk_create(leaf_interface_profiles)

        cls.create_data: list[dict] = [
            {
                "name": "ACILeafInterfaceProfileTestAPI4",
                "name_alias": "Testing",
                "description": "Fourth ACI Test",
                "aci_fabric": aci_fabric1.id,
                "comments": "# ACI Test 4",
            },
            {
                "name": "ACILeafInterfaceProfileTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "aci_fabric": aci_fabric2.id,
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACILeafInterfaceSelectorAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Leaf Interface Selector."""

    model = ACILeafInterfaceSelector
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_leaf_interface_profile",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acileafinterfaceprofile",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Leaf Interface Selector for API view testing."""
        aci_fabric = ACIFabric.objects.create(
            name="ACITestFabricAPI1",
            fabric_id=111,
            infra_vlan_vid=3900,
        )
        aci_leaf_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACILeafInterfaceSelectorTestAPIProfile",
            aci_fabric=aci_fabric,
        )
        aci_leaf_interface_policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACILeafInterfaceSelectorTestAPIPolicyGroup",
            aci_fabric=aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )

        leaf_interface_selectors: tuple = (
            ACILeafInterfaceSelector(
                name="ACILeafInterfaceSelectorTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                aci_leaf_interface_profile=aci_leaf_interface_profile,
                aci_leaf_interface_policy_group=aci_leaf_interface_policy_group,
                comments="# ACI Test 1",
            ),
            ACILeafInterfaceSelector(
                name="ACILeafInterfaceSelectorTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                aci_leaf_interface_profile=aci_leaf_interface_profile,
                aci_leaf_interface_policy_group=aci_leaf_interface_policy_group,
                comments="# ACI Test 2",
            ),
            ACILeafInterfaceSelector(
                name="ACILeafInterfaceSelectorTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                aci_leaf_interface_profile=aci_leaf_interface_profile,
                comments="# ACI Test 3",
            ),
        )
        ACILeafInterfaceSelector.objects.bulk_create(leaf_interface_selectors)

        cls.create_data: list[dict] = [
            {
                "name": "ACILeafInterfaceSelectorTestAPI4",
                "name_alias": "Testing",
                "description": "Fourth ACI Test",
                "aci_leaf_interface_profile": aci_leaf_interface_profile.id,
                "aci_leaf_interface_policy_group": (aci_leaf_interface_policy_group.id),
                "comments": "# ACI Test 4",
            },
            {
                "name": "ACILeafInterfaceSelectorTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "aci_leaf_interface_profile": aci_leaf_interface_profile.id,
                "aci_leaf_interface_policy_group": (aci_leaf_interface_policy_group.id),
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACILeafPortBlockAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Leaf Port Block."""

    model = ACILeafPortBlock
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_leaf_interface_selector",
        "description",
        "display",
        "id",
        "module_from",
        "module_to",
        "name",
        "name_alias",
        "nb_tenant",
        "port_from",
        "port_to",
        "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acileafinterfaceselector",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Leaf Port Block for API view testing."""
        aci_fabric = ACIFabric.objects.create(
            name="ACITestFabricAPI1",
            fabric_id=111,
            infra_vlan_vid=3900,
        )
        aci_leaf_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACILeafPortBlockTestAPIProfile",
            aci_fabric=aci_fabric,
        )
        aci_leaf_interface_selector = ACILeafInterfaceSelector.objects.create(
            name="ACILeafPortBlockTestAPISelector",
            aci_leaf_interface_profile=aci_leaf_interface_profile,
        )

        leaf_port_blocks: tuple = (
            ACILeafPortBlock(
                name="ACILeafPortBlockTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                aci_leaf_interface_selector=aci_leaf_interface_selector,
                module_from=1,
                module_to=1,
                port_from=1,
                port_to=1,
                comments="# ACI Test 1",
            ),
            ACILeafPortBlock(
                name="ACILeafPortBlockTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                aci_leaf_interface_selector=aci_leaf_interface_selector,
                module_from=1,
                module_to=1,
                port_from=2,
                port_to=2,
                comments="# ACI Test 2",
            ),
            ACILeafPortBlock(
                name="ACILeafPortBlockTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                aci_leaf_interface_selector=aci_leaf_interface_selector,
                module_from=1,
                module_to=1,
                port_from=3,
                port_to=3,
                comments="# ACI Test 3",
            ),
        )
        ACILeafPortBlock.objects.bulk_create(leaf_port_blocks)

        cls.create_data: list[dict] = [
            {
                "name": "ACILeafPortBlockTestAPI4",
                "name_alias": "Testing",
                "description": "Fourth ACI Test",
                "aci_leaf_interface_selector": aci_leaf_interface_selector.id,
                "module_from": 1,
                "module_to": 1,
                "port_from": 4,
                "port_to": 4,
                "comments": "# ACI Test 4",
            },
            {
                "name": "ACILeafPortBlockTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "aci_leaf_interface_selector": aci_leaf_interface_selector.id,
                "module_from": 1,
                "module_to": 1,
                "port_from": 5,
                "port_to": 5,
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "comments": "New comments",
        }
