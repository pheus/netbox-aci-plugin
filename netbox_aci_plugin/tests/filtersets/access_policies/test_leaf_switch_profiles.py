# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for access-policy Leaf Switch Profile models."""

from utilities.testing import ChangeLoggedFilterSetTests

from ....filtersets.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlockFilterSet,
    ACILeafSelectorFilterSet,
    ACILeafSwitchProfileFilterSet,
)
from ....models.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlock,
    ACILeafSelector,
    ACILeafSwitchProfile,
)
from ....models.fabric.fabrics import ACIFabric
from ...models.base import ACIBaseTestCase


class ACILeafSwitchProfileFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTests
):
    """Test case for ACILeafSwitchProfileFilterSet."""

    queryset = ACILeafSwitchProfile.objects.all()
    filterset = ACILeafSwitchProfileFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafSwitchProfileFilterSet tests."""
        super().setUpTestData()
        cls.aci_leaf_switch_profile1 = ACILeafSwitchProfile.objects.create(
            name="LeafSwitchProfile1",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_switch_profile2 = ACILeafSwitchProfile.objects.create(
            name="LeafSwitchProfile2",
            name_alias="LeafSwitchProfile2Alias",
            aci_fabric=cls.aci_fabric,
        )
        cls.other_fabric = ACIFabric.objects.create(
            name="ACILeafSwitchProfileFilterSetOtherFabric",
            fabric_id=cls.aci_fabric.fabric_id + 1,
            infra_vlan_vid=cls.aci_fabric.infra_vlan_vid + 1,
        )
        cls.aci_leaf_switch_profile3 = ACILeafSwitchProfile.objects.create(
            name="LeafSwitchProfile3",
            aci_fabric=cls.other_fabric,
        )

    def test_q(self) -> None:
        """Test q search matches the name field."""
        params = {"q": "LeafSwitchProfile1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_switch_profile1, qs)
        self.assertNotIn(self.aci_leaf_switch_profile2, qs)

    def test_q_name_alias(self) -> None:
        """Test q search matches the name alias field."""
        params = {"q": "LeafSwitchProfile2Alias"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_switch_profile2, qs)
        self.assertNotIn(self.aci_leaf_switch_profile1, qs)

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
        self.assertIn(self.aci_leaf_switch_profile1, qs)
        self.assertNotIn(self.aci_leaf_switch_profile3, qs)


class ACILeafSelectorFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACILeafSelectorFilterSet."""

    queryset = ACILeafSelector.objects.all()
    filterset = ACILeafSelectorFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafSelectorFilterSet tests."""
        super().setUpTestData()
        cls.aci_leaf_switch_profile1 = ACILeafSwitchProfile.objects.create(
            name="LeafSwitchProfile1",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_switch_profile2 = ACILeafSwitchProfile.objects.create(
            name="LeafSwitchProfile2",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_selector1 = ACILeafSelector.objects.create(
            name="LeafSelector1",
            aci_leaf_switch_profile=cls.aci_leaf_switch_profile1,
        )
        cls.aci_leaf_selector2 = ACILeafSelector.objects.create(
            name="LeafSelector2",
            name_alias="LeafSelector2Alias",
            aci_leaf_switch_profile=cls.aci_leaf_switch_profile1,
        )
        cls.aci_leaf_selector3 = ACILeafSelector.objects.create(
            name="LeafSelector3",
            aci_leaf_switch_profile=cls.aci_leaf_switch_profile2,
        )
        cls.other_fabric = ACIFabric.objects.create(
            name="ACILeafSelectorFilterSetOtherFabric",
            fabric_id=cls.aci_fabric.fabric_id + 1,
            infra_vlan_vid=cls.aci_fabric.infra_vlan_vid + 1,
        )
        cls.other_aci_leaf_switch_profile = ACILeafSwitchProfile.objects.create(
            name="LeafSwitchProfileOther",
            aci_fabric=cls.other_fabric,
        )
        cls.aci_leaf_selector4 = ACILeafSelector.objects.create(
            name="LeafSelector4",
            aci_leaf_switch_profile=cls.other_aci_leaf_switch_profile,
        )

    def test_q(self) -> None:
        """Test q search matches the name field."""
        params = {"q": "LeafSelector1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_selector1, qs)
        self.assertNotIn(self.aci_leaf_selector2, qs)

    def test_q_name_alias(self) -> None:
        """Test q search matches the name alias field."""
        params = {"q": "LeafSelector2Alias"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_selector2, qs)
        self.assertNotIn(self.aci_leaf_selector1, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())

    def test_filter_aci_leaf_switch_profile(self) -> None:
        """Test filtering by the parent Leaf Switch Profile."""
        params = {"aci_leaf_switch_profile_id": [self.aci_leaf_switch_profile1.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_selector1, qs)
        self.assertIn(self.aci_leaf_selector2, qs)
        self.assertNotIn(self.aci_leaf_selector3, qs)

    def test_filter_aci_fabric(self) -> None:
        """Test filtering by the ACI fabric of the parent Profile."""
        params = {"aci_fabric_id": [self.aci_fabric.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_selector1, qs)
        self.assertNotIn(self.aci_leaf_selector4, qs)


class ACILeafNodeBlockFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACILeafNodeBlockFilterSet."""

    queryset = ACILeafNodeBlock.objects.all()
    filterset = ACILeafNodeBlockFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafNodeBlockFilterSet tests."""
        super().setUpTestData()
        cls.aci_leaf_switch_profile1 = ACILeafSwitchProfile.objects.create(
            name="LeafSwitchProfile1",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_selector1 = ACILeafSelector.objects.create(
            name="LeafSelector1",
            aci_leaf_switch_profile=cls.aci_leaf_switch_profile1,
        )
        cls.aci_leaf_selector2 = ACILeafSelector.objects.create(
            name="LeafSelector2",
            aci_leaf_switch_profile=cls.aci_leaf_switch_profile1,
        )
        cls.aci_leaf_node_block1 = ACILeafNodeBlock.objects.create(
            name="NodeBlock1",
            aci_leaf_selector=cls.aci_leaf_selector1,
            node_id_from=101,
            node_id_to=104,
        )
        cls.aci_leaf_node_block2 = ACILeafNodeBlock.objects.create(
            name="NodeBlock2",
            name_alias="NodeBlock2Alias",
            aci_leaf_selector=cls.aci_leaf_selector1,
            node_id_from=201,
            node_id_to=204,
        )
        cls.aci_leaf_node_block3 = ACILeafNodeBlock.objects.create(
            name="NodeBlock3",
            aci_leaf_selector=cls.aci_leaf_selector2,
            node_id_from=301,
            node_id_to=304,
        )
        cls.other_fabric = ACIFabric.objects.create(
            name="ACILeafNodeBlockFilterSetOtherFabric",
            fabric_id=cls.aci_fabric.fabric_id + 1,
            infra_vlan_vid=cls.aci_fabric.infra_vlan_vid + 1,
        )
        cls.other_aci_leaf_switch_profile = ACILeafSwitchProfile.objects.create(
            name="LeafSwitchProfileOther",
            aci_fabric=cls.other_fabric,
        )
        cls.other_aci_leaf_selector = ACILeafSelector.objects.create(
            name="LeafSelectorOther",
            aci_leaf_switch_profile=cls.other_aci_leaf_switch_profile,
        )
        cls.aci_leaf_node_block4 = ACILeafNodeBlock.objects.create(
            name="NodeBlock4",
            aci_leaf_selector=cls.other_aci_leaf_selector,
            node_id_from=401,
            node_id_to=404,
        )

    def test_q(self) -> None:
        """Test q search matches the name field."""
        params = {"q": "NodeBlock1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_node_block1, qs)
        self.assertNotIn(self.aci_leaf_node_block2, qs)

    def test_q_name_alias(self) -> None:
        """Test q search matches the name alias field."""
        params = {"q": "NodeBlock2Alias"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_node_block2, qs)
        self.assertNotIn(self.aci_leaf_node_block1, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())

    def test_filter_aci_leaf_selector(self) -> None:
        """Test filtering by the parent Leaf Selector."""
        params = {"aci_leaf_selector_id": [self.aci_leaf_selector1.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_node_block1, qs)
        self.assertIn(self.aci_leaf_node_block2, qs)
        self.assertNotIn(self.aci_leaf_node_block3, qs)

    def test_filter_aci_leaf_switch_profile(self) -> None:
        """Test filtering by the parent Selector's Leaf Switch Profile."""
        params = {"aci_leaf_switch_profile_id": [self.aci_leaf_switch_profile1.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_node_block3, qs)
        self.assertNotIn(self.aci_leaf_node_block4, qs)

    def test_filter_aci_fabric(self) -> None:
        """Test filtering by the ACI fabric of the parent chain."""
        params = {"aci_fabric_id": [self.aci_fabric.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_node_block1, qs)
        self.assertNotIn(self.aci_leaf_node_block4, qs)

    def test_filter_node_id_from_range(self) -> None:
        """Test filtering by the auto-generated node_id_from gte/lte range.

        node_id_from is a plain numeric field in Meta.fields, so
        NetBoxModelFilterSet synthesizes the __gte/__lte lookups. No
        explicit filter declaration is needed for them.
        """
        params = {"node_id_from__gte": [150], "node_id_from__lte": [250]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_node_block2, qs)
        self.assertNotIn(self.aci_leaf_node_block1, qs)
        self.assertNotIn(self.aci_leaf_node_block3, qs)

    def test_filter_node_id_to_range(self) -> None:
        """Test filtering by the auto-generated node_id_to gte/lte range."""
        params = {"node_id_to__gte": [300], "node_id_to__lte": [305]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_leaf_node_block3, qs)
        self.assertNotIn(self.aci_leaf_node_block1, qs)
        self.assertNotIn(self.aci_leaf_node_block2, qs)
