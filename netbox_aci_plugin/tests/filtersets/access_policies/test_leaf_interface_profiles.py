# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for access-policy Leaf Interface Profile models."""

from utilities.testing import ChangeLoggedFilterSetTests

from ....choices import LeafInterfacePolicyGroupTypeChoices
from ....filtersets.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfileFilterSet,
    ACILeafInterfaceSelectorFilterSet,
    ACILeafPortBlockFilterSet,
)
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ....models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
    ACILeafInterfaceSelector,
    ACILeafPortBlock,
)
from ....models.fabric.fabrics import ACIFabric
from ...models.base import ACIBaseTestCase


class ACILeafInterfaceProfileFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTests
):
    """Test case for ACILeafInterfaceProfileFilterSet."""

    queryset = ACILeafInterfaceProfile.objects.all()
    filterset = ACILeafInterfaceProfileFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafInterfaceProfileFilterSet tests."""
        super().setUpTestData()
        cls.aci_leaf_interface_profile1 = ACILeafInterfaceProfile.objects.create(
            name="LeafInterfaceProfile1",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_interface_profile2 = ACILeafInterfaceProfile.objects.create(
            name="LeafInterfaceProfile2",
            name_alias="LeafInterfaceProfile2Alias",
            aci_fabric=cls.aci_fabric,
        )
        cls.other_fabric = ACIFabric.objects.create(
            name="ACILeafInterfaceProfileFilterSetOtherFabric",
            fabric_id=cls.aci_fabric.fabric_id + 1,
            infra_vlan_vid=cls.aci_fabric.infra_vlan_vid + 1,
        )
        cls.aci_leaf_interface_profile3 = ACILeafInterfaceProfile.objects.create(
            name="LeafInterfaceProfile3",
            aci_fabric=cls.other_fabric,
        )

    def test_q(self) -> None:
        """Test q search matches the name field."""
        params = {"q": "LeafInterfaceProfile1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_interface_profile1, qs)
        self.assertNotIn(self.aci_leaf_interface_profile2, qs)

    def test_q_name_alias(self) -> None:
        """Test q search matches the name alias field."""
        params = {"q": "LeafInterfaceProfile2Alias"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_interface_profile2, qs)
        self.assertNotIn(self.aci_leaf_interface_profile1, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())

    def test_filter_aci_fabric(self) -> None:
        """Test filtering by the ACI fabric."""
        params = {"aci_fabric_id": [self.aci_fabric.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_interface_profile1, qs)
        self.assertNotIn(self.aci_leaf_interface_profile3, qs)


class ACILeafInterfaceSelectorFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTests
):
    """Test case for ACILeafInterfaceSelectorFilterSet."""

    queryset = ACILeafInterfaceSelector.objects.all()
    filterset = ACILeafInterfaceSelectorFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafInterfaceSelectorFilterSet tests."""
        super().setUpTestData()
        cls.aci_leaf_interface_profile1 = ACILeafInterfaceProfile.objects.create(
            name="LeafInterfaceProfile1",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_interface_profile2 = ACILeafInterfaceProfile.objects.create(
            name="LeafInterfaceProfile2",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_interface_policy_group1 = (
            ACILeafInterfacePolicyGroup.objects.create(
                name="LeafInterfacePolicyGroup1",
                aci_fabric=cls.aci_fabric,
                group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            )
        )
        cls.aci_leaf_interface_selector1 = ACILeafInterfaceSelector.objects.create(
            name="LeafInterfaceSelector1",
            aci_leaf_interface_profile=cls.aci_leaf_interface_profile1,
            aci_leaf_interface_policy_group=cls.aci_leaf_interface_policy_group1,
        )
        cls.aci_leaf_interface_selector2 = ACILeafInterfaceSelector.objects.create(
            name="LeafInterfaceSelector2",
            name_alias="LeafInterfaceSelector2Alias",
            aci_leaf_interface_profile=cls.aci_leaf_interface_profile1,
        )
        cls.aci_leaf_interface_selector3 = ACILeafInterfaceSelector.objects.create(
            name="LeafInterfaceSelector3",
            aci_leaf_interface_profile=cls.aci_leaf_interface_profile2,
        )
        cls.other_fabric = ACIFabric.objects.create(
            name="ACILeafInterfaceSelectorFilterSetOtherFabric",
            fabric_id=cls.aci_fabric.fabric_id + 1,
            infra_vlan_vid=cls.aci_fabric.infra_vlan_vid + 1,
        )
        cls.other_aci_leaf_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="LeafInterfaceProfileOther",
            aci_fabric=cls.other_fabric,
        )
        cls.aci_leaf_interface_selector4 = ACILeafInterfaceSelector.objects.create(
            name="LeafInterfaceSelector4",
            aci_leaf_interface_profile=cls.other_aci_leaf_interface_profile,
        )

    def test_q(self) -> None:
        """Test q search matches the name field."""
        params = {"q": "LeafInterfaceSelector1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_interface_selector1, qs)
        self.assertNotIn(self.aci_leaf_interface_selector2, qs)

    def test_q_name_alias(self) -> None:
        """Test q search matches the name alias field."""
        params = {"q": "LeafInterfaceSelector2Alias"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_interface_selector2, qs)
        self.assertNotIn(self.aci_leaf_interface_selector1, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())

    def test_filter_aci_leaf_interface_profile(self) -> None:
        """Test filtering by the parent Leaf Interface Profile."""
        params = {
            "aci_leaf_interface_profile_id": [self.aci_leaf_interface_profile1.pk]
        }
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_interface_selector1, qs)
        self.assertIn(self.aci_leaf_interface_selector2, qs)
        self.assertNotIn(self.aci_leaf_interface_selector3, qs)

    def test_filter_aci_fabric(self) -> None:
        """Test filtering by the ACI fabric of the parent Profile."""
        params = {"aci_fabric_id": [self.aci_fabric.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_interface_selector1, qs)
        self.assertNotIn(self.aci_leaf_interface_selector4, qs)

    def test_filter_aci_leaf_interface_policy_group(self) -> None:
        """Test filtering by the assigned Leaf Interface Policy Group."""
        params = {
            "aci_leaf_interface_policy_group_id": [
                self.aci_leaf_interface_policy_group1.pk
            ]
        }
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_interface_selector1, qs)
        self.assertNotIn(self.aci_leaf_interface_selector2, qs)


class ACILeafPortBlockFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACILeafPortBlockFilterSet."""

    queryset = ACILeafPortBlock.objects.all()
    filterset = ACILeafPortBlockFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafPortBlockFilterSet tests."""
        super().setUpTestData()
        cls.aci_leaf_interface_profile1 = ACILeafInterfaceProfile.objects.create(
            name="LeafInterfaceProfile1",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_interface_selector1 = ACILeafInterfaceSelector.objects.create(
            name="LeafInterfaceSelector1",
            aci_leaf_interface_profile=cls.aci_leaf_interface_profile1,
        )
        cls.aci_leaf_interface_selector2 = ACILeafInterfaceSelector.objects.create(
            name="LeafInterfaceSelector2",
            aci_leaf_interface_profile=cls.aci_leaf_interface_profile1,
        )
        cls.aci_leaf_port_block1 = ACILeafPortBlock.objects.create(
            name="PortBlock1",
            aci_leaf_interface_selector=cls.aci_leaf_interface_selector1,
            module_from=1,
            module_to=1,
            port_from=1,
            port_to=4,
        )
        cls.aci_leaf_port_block2 = ACILeafPortBlock.objects.create(
            name="PortBlock2",
            name_alias="PortBlock2Alias",
            aci_leaf_interface_selector=cls.aci_leaf_interface_selector1,
            module_from=2,
            module_to=2,
            port_from=5,
            port_to=8,
        )
        cls.aci_leaf_port_block3 = ACILeafPortBlock.objects.create(
            name="PortBlock3",
            aci_leaf_interface_selector=cls.aci_leaf_interface_selector2,
            module_from=3,
            module_to=3,
            port_from=9,
            port_to=12,
        )
        cls.other_fabric = ACIFabric.objects.create(
            name="ACILeafPortBlockFilterSetOtherFabric",
            fabric_id=cls.aci_fabric.fabric_id + 1,
            infra_vlan_vid=cls.aci_fabric.infra_vlan_vid + 1,
        )
        cls.other_aci_leaf_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="LeafInterfaceProfileOther",
            aci_fabric=cls.other_fabric,
        )
        cls.other_aci_leaf_interface_selector = ACILeafInterfaceSelector.objects.create(
            name="LeafInterfaceSelectorOther",
            aci_leaf_interface_profile=cls.other_aci_leaf_interface_profile,
        )
        cls.aci_leaf_port_block4 = ACILeafPortBlock.objects.create(
            name="PortBlock4",
            aci_leaf_interface_selector=cls.other_aci_leaf_interface_selector,
            module_from=4,
            module_to=4,
            port_from=1,
            port_to=4,
        )

    def test_q(self) -> None:
        """Test q search matches the name field."""
        params = {"q": "PortBlock1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_port_block1, qs)
        self.assertNotIn(self.aci_leaf_port_block2, qs)

    def test_q_name_alias(self) -> None:
        """Test q search matches the name alias field."""
        params = {"q": "PortBlock2Alias"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_port_block2, qs)
        self.assertNotIn(self.aci_leaf_port_block1, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())

    def test_filter_aci_leaf_interface_selector(self) -> None:
        """Test filtering by the parent Leaf Interface Selector."""
        params = {
            "aci_leaf_interface_selector_id": [self.aci_leaf_interface_selector1.pk]
        }
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_port_block1, qs)
        self.assertIn(self.aci_leaf_port_block2, qs)
        self.assertNotIn(self.aci_leaf_port_block3, qs)

    def test_filter_aci_leaf_interface_profile(self) -> None:
        """Test filtering by the parent Selector's Leaf Interface Profile."""
        params = {
            "aci_leaf_interface_profile_id": [self.aci_leaf_interface_profile1.pk]
        }
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_port_block3, qs)
        self.assertNotIn(self.aci_leaf_port_block4, qs)

    def test_filter_aci_fabric(self) -> None:
        """Test filtering by the ACI fabric of the parent chain."""
        params = {"aci_fabric_id": [self.aci_fabric.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_port_block1, qs)
        self.assertNotIn(self.aci_leaf_port_block4, qs)

    def test_filter_module_from_range(self) -> None:
        """Test filtering by the auto-generated module_from gte/lte range.

        module_from is a plain numeric field in Meta.fields, so
        NetBoxModelFilterSet synthesizes the __gte/__lte lookups. No
        explicit filter declaration is needed for them.
        """
        params = {"module_from__gte": [2], "module_from__lte": [2]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_port_block2, qs)
        self.assertNotIn(self.aci_leaf_port_block1, qs)
        self.assertNotIn(self.aci_leaf_port_block3, qs)

    def test_filter_module_to_range(self) -> None:
        """Test filtering by the auto-generated module_to gte/lte range."""
        params = {"module_to__gte": [2], "module_to__lte": [2]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_port_block2, qs)
        self.assertNotIn(self.aci_leaf_port_block1, qs)
        self.assertNotIn(self.aci_leaf_port_block3, qs)

    def test_filter_port_from_range(self) -> None:
        """Test filtering by the auto-generated port_from gte/lte range."""
        params = {"port_from__gte": [5], "port_from__lte": [5]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_port_block2, qs)
        self.assertNotIn(self.aci_leaf_port_block1, qs)
        self.assertNotIn(self.aci_leaf_port_block3, qs)

    def test_filter_port_to_range(self) -> None:
        """Test filtering by the auto-generated port_to gte/lte range."""
        params = {"port_to__gte": [6], "port_to__lte": [10]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_port_block2, qs)
        self.assertNotIn(self.aci_leaf_port_block1, qs)
        self.assertNotIn(self.aci_leaf_port_block3, qs)
