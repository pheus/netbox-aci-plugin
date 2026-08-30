# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for the ACI VPC Protection Group model."""

from utilities.testing import ChangeLoggedFilterSetTestMixin

from ....choices import NodeRoleChoices
from ....filtersets.fabric.vpc_protection_groups import ACIVPCProtectionGroupFilterSet
from ....models.fabric.nodes import ACINode
from ....models.fabric.vpc_protection_groups import ACIVPCProtectionGroup
from ...models.base import ACIBaseTestCase


class ACIVPCProtectionGroupFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTestMixin
):
    """Test case for ACIVPCProtectionGroupFilterSet."""

    queryset = ACIVPCProtectionGroup.objects.all()
    filterset = ACIVPCProtectionGroupFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIVPCProtectionGroupFilterSet tests."""
        super().setUpTestData()
        cls.aci_node_b = ACINode.objects.create(
            name="ACIFSVPCTestNodeB",
            aci_pod=cls.aci_pod,
            node_id=102,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.aci_node_c = ACINode.objects.create(
            name="ACIFSVPCTestNodeC",
            aci_pod=cls.aci_pod,
            node_id=103,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.aci_node_d = ACINode.objects.create(
            name="ACIFSVPCTestNodeD",
            aci_pod=cls.aci_pod,
            node_id=104,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.aci_node_e = ACINode.objects.create(
            name="ACIFSVPCTestNodeE",
            aci_pod=cls.aci_pod,
            node_id=105,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.aci_node_f = ACINode.objects.create(
            name="ACIFSVPCTestNodeF",
            aci_pod=cls.aci_pod,
            node_id=106,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.aci_vpc_group_1 = ACIVPCProtectionGroup.objects.create(
            name="ACIFSTestVPCGroup1",
            name_alias="ACIFSTestVPCGroup1Alias",
            aci_fabric=cls.aci_fabric,
            logical_pair_id=1,
            aci_node_a=cls.aci_node,
            aci_node_b=cls.aci_node_b,
        )
        cls.aci_vpc_group_2 = ACIVPCProtectionGroup.objects.create(
            name="ACIFSTestVPCGroup2",
            aci_fabric=cls.aci_fabric,
            logical_pair_id=2,
            aci_node_a=cls.aci_node_c,
            aci_node_b=cls.aci_node_d,
        )
        # A third group, so test_id has more than two objects to filter
        cls.aci_vpc_group_3 = ACIVPCProtectionGroup.objects.create(
            name="ACIFSTestVPCGroup3",
            aci_fabric=cls.aci_fabric,
            logical_pair_id=3,
            aci_node_a=cls.aci_node_e,
            aci_node_b=cls.aci_node_f,
        )

    def test_q(self) -> None:
        """Test q search matches the name field."""
        params = {"q": "ACIFSTestVPCGroup1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_vpc_group_1, qs)
        self.assertNotIn(self.aci_vpc_group_2, qs)

    def test_q_name_alias(self) -> None:
        """Test q search matches the name_alias field."""
        params = {"q": "ACIFSTestVPCGroup1Alias"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_vpc_group_1, qs)
        self.assertNotIn(self.aci_vpc_group_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())

    def test_aci_node_a_id(self) -> None:
        """Test filtering by the ACI Node A ID."""
        params = {"aci_node_a_id": [self.aci_node.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_vpc_group_1, qs)
        self.assertNotIn(self.aci_vpc_group_2, qs)

    def test_aci_node_b_id(self) -> None:
        """Test filtering by the ACI Node B ID."""
        params = {"aci_node_b_id": [self.aci_node_b.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_vpc_group_1, qs)
        self.assertNotIn(self.aci_vpc_group_2, qs)

    def test_logical_pair_id(self) -> None:
        """Test filtering by the logical pair ID."""
        params = {"logical_pair_id": [1]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_vpc_group_1, qs)
        self.assertNotIn(self.aci_vpc_group_2, qs)
        self.assertNotIn(self.aci_vpc_group_3, qs)
