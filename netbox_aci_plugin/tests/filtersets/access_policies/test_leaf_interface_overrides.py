# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for the access-policy Leaf Interface Override model."""

from utilities.testing import ChangeLoggedFilterSetTestMixin

from ....choices import LeafInterfacePolicyGroupTypeChoices
from ....filtersets.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverrideFilterSet,
)
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ....models.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverride,
)
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.node_interfaces import ACINodeInterface
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ...models.base import ACIBaseTestCase


class ACILeafInterfaceOverrideFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTestMixin
):
    """Test case for ACILeafInterfaceOverrideFilterSet."""

    queryset = ACILeafInterfaceOverride.objects.all()
    filterset = ACILeafInterfaceOverrideFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafInterfaceOverrideFilterSet tests."""
        super().setUpTestData()
        cls.aci_policy_group1 = ACILeafInterfacePolicyGroup.objects.create(
            name="LeafInterfaceOverrideFilterSetPolicyGroup1",
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        cls.aci_policy_group2 = ACILeafInterfacePolicyGroup.objects.create(
            name="LeafInterfaceOverrideFilterSetPolicyGroup2",
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        cls.aci_node_interface1 = ACINodeInterface.objects.create(
            aci_node=cls.aci_node, module=1, port=21
        )
        cls.aci_node_interface2 = ACINodeInterface.objects.create(
            aci_node=cls.aci_node, module=1, port=22
        )
        cls.aci_override1 = ACILeafInterfaceOverride.objects.create(
            aci_node_interface=cls.aci_node_interface1,
            aci_leaf_interface_policy_group=cls.aci_policy_group1,
            description="OverrideOneDescription",
        )
        cls.aci_override2 = ACILeafInterfaceOverride.objects.create(
            aci_node_interface=cls.aci_node_interface2,
            aci_leaf_interface_policy_group=cls.aci_policy_group2,
        )
        cls.other_fabric = ACIFabric.objects.create(
            name="ACILeafInterfaceOverrideFilterSetOtherFabric",
            fabric_id=cls.aci_fabric.fabric_id + 1,
            infra_vlan_vid=cls.aci_fabric.infra_vlan_vid + 1,
        )
        cls.other_aci_pod = ACIPod.objects.create(
            name="ACILeafInterfaceOverrideFilterSetOtherPod",
            aci_fabric=cls.other_fabric,
            pod_id=1,
        )
        cls.other_aci_node = ACINode.objects.create(
            name="ACILeafInterfaceOverrideFilterSetOtherNode",
            aci_pod=cls.other_aci_pod,
            node_id=101,
        )
        cls.other_aci_policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="LeafInterfaceOverrideFilterSetOtherPolicyGroup",
            aci_fabric=cls.other_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        cls.other_aci_node_interface = ACINodeInterface.objects.create(
            aci_node=cls.other_aci_node, module=1, port=1
        )
        cls.aci_override3 = ACILeafInterfaceOverride.objects.create(
            aci_node_interface=cls.other_aci_node_interface,
            aci_leaf_interface_policy_group=cls.other_aci_policy_group,
        )

    def test_q(self) -> None:
        """Test q search matches the Node name."""
        params = {"q": self.aci_node.name}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_override1, qs)
        self.assertIn(self.aci_override2, qs)
        self.assertNotIn(self.aci_override3, qs)

    def test_q_policy_group_name(self) -> None:
        """Test q search matches the Policy Group name."""
        params = {"q": "LeafInterfaceOverrideFilterSetPolicyGroup1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_override1, qs)
        self.assertNotIn(self.aci_override2, qs)

    def test_q_description(self) -> None:
        """Test q search matches the description field."""
        params = {"q": "OverrideOneDescription"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_override1, qs)
        self.assertNotIn(self.aci_override2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())

    def test_filter_aci_fabric(self) -> None:
        """Test filtering by the ACI Fabric of the Node Interface."""
        params = {"aci_fabric_id": [self.aci_fabric.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_override1, qs)
        self.assertNotIn(self.aci_override3, qs)

    def test_filter_aci_pod(self) -> None:
        """Test filtering by the ACI Pod of the Node Interface."""
        params = {"aci_pod_id": [self.aci_pod.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_override1, qs)
        self.assertNotIn(self.aci_override3, qs)

    def test_filter_aci_node(self) -> None:
        """Test filtering by the ACI Node of the Node Interface."""
        params = {"aci_node_id": [self.aci_node.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_override1, qs)
        self.assertNotIn(self.aci_override3, qs)

    def test_filter_aci_node_interface(self) -> None:
        """Test filtering by the assigned ACI Node Interface."""
        params = {"aci_node_interface_id": [self.aci_node_interface1.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_override1, qs)
        self.assertNotIn(self.aci_override2, qs)

    def test_filter_aci_leaf_interface_policy_group(self) -> None:
        """Test filtering by the assigned Leaf Interface Policy Group."""
        params = {"aci_leaf_interface_policy_group_id": [self.aci_policy_group1.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_override1, qs)
        self.assertNotIn(self.aci_override2, qs)
