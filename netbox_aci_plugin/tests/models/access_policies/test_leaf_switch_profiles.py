# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the ACI Leaf Switch Profile models."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.test.utils import CaptureQueriesContext

from core.choices import ObjectChangeActionChoices
from tenancy.models import Tenant

from ....choices import NodeRoleChoices
from ....models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
)
from ....models.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlock,
    ACILeafSelector,
    ACILeafSwitchProfile,
    ACILeafSwitchProfileInterfaceBinding,
)
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ..base import ACIBaseTestCase


class ACILeafSwitchProfileTestCase(ACIBaseTestCase):
    """Test case for the ACILeafSwitchProfile model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACILeafSwitchProfile model."""
        super().setUpTestData()

        cls.aci_leaf_switch_profile_name = "ACITestLeafSwitchProfile"
        cls.aci_leaf_switch_profile_alias = "ACITestLeafSwitchProfileAlias"
        cls.aci_leaf_switch_profile_description = (
            "ACI Test Leaf Switch Profile for NetBox ACI Plugin"
        )
        cls.aci_leaf_switch_profile_comments = """
        ACI Leaf Switch Profile for NetBox ACI Plugin testing.
        """

        # Create objects
        cls.aci_leaf_switch_profile = ACILeafSwitchProfile.objects.create(
            name=cls.aci_leaf_switch_profile_name,
            name_alias=cls.aci_leaf_switch_profile_alias,
            description=cls.aci_leaf_switch_profile_description,
            comments=cls.aci_leaf_switch_profile_comments,
            aci_fabric=cls.aci_fabric,
            nb_tenant=cls.nb_tenant,
        )

    def test_aci_leaf_switch_profile_instance(self) -> None:
        """Test type of created ACI Leaf Switch Profile."""
        self.assertTrue(isinstance(self.aci_leaf_switch_profile, ACILeafSwitchProfile))

    def test_aci_leaf_switch_profile_str(self) -> None:
        """Test string value of created ACI Leaf Switch Profile."""
        self.assertEqual(
            self.aci_leaf_switch_profile.__str__(),
            self.aci_leaf_switch_profile.name,
        )

    def test_aci_leaf_switch_profile_name_alias(self) -> None:
        """Test alias of created ACI Leaf Switch Profile."""
        self.assertEqual(
            self.aci_leaf_switch_profile.name_alias,
            self.aci_leaf_switch_profile_alias,
        )

    def test_aci_leaf_switch_profile_description(self) -> None:
        """Test description of created ACI Leaf Switch Profile."""
        self.assertEqual(
            self.aci_leaf_switch_profile.description,
            self.aci_leaf_switch_profile_description,
        )

    def test_aci_leaf_switch_profile_aci_fabric_instance(self) -> None:
        """Test the ACI Fabric instance associated with the profile."""
        self.assertTrue(isinstance(self.aci_leaf_switch_profile.aci_fabric, ACIFabric))
        self.assertEqual(
            self.aci_leaf_switch_profile.aci_fabric.name, self.aci_fabric_name
        )

    def test_aci_leaf_switch_profile_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with the profile."""
        self.assertTrue(isinstance(self.aci_leaf_switch_profile.nb_tenant, Tenant))
        self.assertEqual(
            self.aci_leaf_switch_profile.nb_tenant.name, self.nb_tenant_name
        )

    def test_aci_leaf_switch_profile_parent_object(self) -> None:
        """Test parent object of ACI Leaf Switch Profile is the ACI Fabric."""
        self.assertEqual(self.aci_leaf_switch_profile.parent_object, self.aci_fabric)

    def test_invalid_aci_leaf_switch_profile_name(self) -> None:
        """Test validation of ACI Leaf Switch Profile naming."""
        profile = ACILeafSwitchProfile(
            name="Invalid Name With Spaces", aci_fabric=self.aci_fabric
        )
        with self.assertRaises(ValidationError) as cm:
            profile.full_clean()
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_leaf_switch_profile_name_length(self) -> None:
        """Test validation of ACI Leaf Switch Profile name length."""
        profile = ACILeafSwitchProfile(name="A" * 65, aci_fabric=self.aci_fabric)
        with self.assertRaises(ValidationError) as cm:
            profile.full_clean()
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_leaf_switch_profile_name_alias(self) -> None:
        """Test validation of ACI Leaf Switch Profile name alias."""
        profile = ACILeafSwitchProfile(
            name="ACILeafSwitchProfileTest1",
            name_alias="Invalid Alias",
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(ValidationError) as cm:
            profile.full_clean()
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_leaf_switch_profile_name_alias_length(self) -> None:
        """Test validation of ACI Leaf Switch Profile name alias length."""
        profile = ACILeafSwitchProfile(
            name="ACILeafSwitchProfileTest1",
            name_alias="A" * 65,
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(ValidationError) as cm:
            profile.full_clean()
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_leaf_switch_profile_description(self) -> None:
        """Test validation of ACI Leaf Switch Profile description."""
        profile = ACILeafSwitchProfile(
            name="ACILeafSwitchProfileTest1",
            description="Invalid Description: ö",
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(ValidationError) as cm:
            profile.full_clean()
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_leaf_switch_profile_description_length(self) -> None:
        """Test validation of ACI Leaf Switch Profile description length."""
        profile = ACILeafSwitchProfile(
            name="ACILeafSwitchProfileTest1",
            description="A" * 129,
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(ValidationError) as cm:
            profile.full_clean()
        self.assertIn("description", cm.exception.error_dict)

    def test_constraint_unique_aci_leaf_switch_profile_name_per_fabric(
        self,
    ) -> None:
        """Test unique constraint of profile name per ACI Fabric."""
        duplicate_profile = ACILeafSwitchProfile(
            name=self.aci_leaf_switch_profile_name,
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_profile.save()

    def test_aci_leaf_switch_profile_name_reusable_in_another_fabric(self) -> None:
        """Test the same profile name is allowed in a second ACI Fabric."""
        other_fabric = ACIFabric.objects.create(
            name="ACITestLeafSwitchProfileOtherFabric",
            fabric_id=128,
            infra_vlan_vid=3901,
        )
        profile = ACILeafSwitchProfile.objects.create(
            name=self.aci_leaf_switch_profile_name,
            aci_fabric=other_fabric,
        )
        self.assertEqual(profile.name, self.aci_leaf_switch_profile_name)

    def test_invalid_switch_profile_fabric_move_strands_binding(self) -> None:
        """Test clean rejects a Fabric move stranding an assigned binding."""
        interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACILSPMoveInterfaceProfile", aci_fabric=self.aci_fabric
        )
        ACILeafSwitchProfileInterfaceBinding.objects.create(
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
            aci_leaf_interface_profile=interface_profile,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACILSPMoveOtherFabric", fabric_id=150, infra_vlan_vid=3920
        )
        self.aci_leaf_switch_profile.aci_fabric = other_fabric
        with self.assertRaises(ValidationError) as cm:
            self.aci_leaf_switch_profile.full_clean()
        self.assertIn("aci_fabric", cm.exception.error_dict)

    def test_switch_profile_fabric_move_without_binding(self) -> None:
        """Test a Fabric move is allowed when no binding is assigned."""
        other_fabric = ACIFabric.objects.create(
            name="ACILSPMoveFreeFabric", fabric_id=151, infra_vlan_vid=3921
        )
        self.aci_leaf_switch_profile.aci_fabric = other_fabric
        self.aci_leaf_switch_profile.full_clean()

    def test_switch_profile_fabric_move_with_binding_in_target(self) -> None:
        """Test a Fabric move is allowed when the binding is already there.

        Pins the guard's `.exclude()` half. A bare `.exists()` would
        reject this move, and the zero-binding case above cannot tell
        the two apart.
        """
        other_fabric = ACIFabric.objects.create(
            name="ACILSPMoveTargetFabric", fabric_id=153, infra_vlan_vid=3923
        )
        profile_in_target = ACILeafInterfaceProfile.objects.create(
            name="ACILSPMoveTargetProfile", aci_fabric=other_fabric
        )
        # Created directly, since the Binding's own clean() rejects the
        # cross-Fabric pair this scenario has to start from
        ACILeafSwitchProfileInterfaceBinding.objects.create(
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
            aci_leaf_interface_profile=profile_in_target,
        )
        self.aci_leaf_switch_profile.aci_fabric = other_fabric
        self.aci_leaf_switch_profile.full_clean()

    def test_aci_leaf_switch_profile_selector_count_zero(self) -> None:
        """Test selector_count is 0 for a profile with no Selectors."""
        self.assertEqual(self.aci_leaf_switch_profile.selector_count, 0)

    def test_aci_leaf_switch_profile_selector_count_nonzero(self) -> None:
        """Test selector_count counts the profile's Selectors."""
        ACILeafSelector.objects.create(
            name="ACILSPSelectorCount1",
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
        )
        ACILeafSelector.objects.create(
            name="ACILSPSelectorCount2",
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
        )
        self.assertEqual(self.aci_leaf_switch_profile.selector_count, 2)

    def test_aci_nodes_empty_for_profile_without_selectors(self) -> None:
        """Test aci_nodes is empty for a profile without Selectors."""
        self.assertFalse(self.aci_leaf_switch_profile.aci_nodes.exists())

    def test_aci_nodes_unions_blocks_across_selectors(self) -> None:
        """Test aci_nodes unions Node Blocks contributed by every Selector."""
        leaf_102 = ACINode.objects.create(
            name="ACILSPAciNodesLeaf102",
            aci_pod=self.aci_pod,
            node_id=102,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        selector1 = ACILeafSelector.objects.create(
            name="ACILSPAciNodesSelector1",
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
        )
        ACILeafNodeBlock.objects.create(
            name="ACILSPAciNodesBlock1",
            aci_leaf_selector=selector1,
            node_id_from=101,
            node_id_to=101,
        )
        selector2 = ACILeafSelector.objects.create(
            name="ACILSPAciNodesSelector2",
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
        )
        ACILeafNodeBlock.objects.create(
            name="ACILSPAciNodesBlock2",
            aci_leaf_selector=selector2,
            node_id_from=102,
            node_id_to=102,
        )
        self.assertQuerySetEqual(
            self.aci_leaf_switch_profile.aci_nodes.order_by("node_id"),
            [self.aci_node, leaf_102],
        )

    def test_aci_nodes_excludes_other_fabrics(self) -> None:
        """Test aci_nodes excludes a same-ID Node in another Fabric."""
        other_fabric = ACIFabric.objects.create(
            name="ACILSPAciNodesOtherFabric",
            fabric_id=154,
            infra_vlan_vid=3924,
        )
        other_pod = ACIPod.objects.create(
            name="ACILSPAciNodesOtherPod", aci_fabric=other_fabric, pod_id=1
        )
        other_leaf = ACINode.objects.create(
            name="ACILSPAciNodesOtherLeaf",
            aci_pod=other_pod,
            node_id=self.aci_node.node_id,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        selector = ACILeafSelector.objects.create(
            name="ACILSPAciNodesOtherFabricSelector",
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
        )
        ACILeafNodeBlock.objects.create(
            name="ACILSPAciNodesOtherFabricBlock",
            aci_leaf_selector=selector,
            node_id_from=other_leaf.node_id,
            node_id_to=other_leaf.node_id,
        )
        self.assertQuerySetEqual(
            self.aci_leaf_switch_profile.aci_nodes, [self.aci_node]
        )

    def test_aci_nodes_query_count_constant_across_selector_count(self) -> None:
        """Query count for aci_nodes must not scale with Selector count.

        Both aci_nodes properties this one aggregates build a fresh
        queryset per call, so a naive loop over Selectors would cost a
        query per Selector. Pins the single-query collapse instead.
        """
        single_profile = ACILeafSwitchProfile.objects.create(
            name="ACILSPAciNodesSingleProfile", aci_fabric=self.aci_fabric
        )
        single_selector = ACILeafSelector.objects.create(
            name="ACILSPAciNodesSingleSelector",
            aci_leaf_switch_profile=single_profile,
        )
        ACILeafNodeBlock.objects.create(
            name="ACILSPAciNodesSingleBlock",
            aci_leaf_selector=single_selector,
            node_id_from=101,
            node_id_to=101,
        )

        multi_profile = ACILeafSwitchProfile.objects.create(
            name="ACILSPAciNodesMultiProfile", aci_fabric=self.aci_fabric
        )
        for index in range(3):
            selector = ACILeafSelector.objects.create(
                name=f"ACILSPAciNodesMultiSelector{index}",
                aci_leaf_switch_profile=multi_profile,
            )
            ACILeafNodeBlock.objects.create(
                name=f"ACILSPAciNodesMultiBlock{index}",
                aci_leaf_selector=selector,
                node_id_from=101,
                node_id_to=101,
            )

        with CaptureQueriesContext(connection) as single_ctx:
            list(single_profile.aci_nodes)
        with CaptureQueriesContext(connection) as multi_ctx:
            list(multi_profile.aci_nodes)

        self.assertEqual(
            len(single_ctx.captured_queries),
            len(multi_ctx.captured_queries),
            "Query count for aci_nodes grew with the profile's Selector count.",
        )


class ACILeafSelectorTestCase(ACIBaseTestCase):
    """Test case for the ACILeafSelector model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACILeafSelector model."""
        super().setUpTestData()

        cls.aci_leaf_selector_name = "ACITestLeafSelector"
        cls.aci_leaf_selector_alias = "ACITestLeafSelectorAlias"
        cls.aci_leaf_selector_description = (
            "ACI Test Leaf Selector for NetBox ACI Plugin"
        )

        # Create objects
        cls.aci_leaf_switch_profile = ACILeafSwitchProfile.objects.create(
            name="ACITestLeafSelectorProfile",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_selector = ACILeafSelector.objects.create(
            name=cls.aci_leaf_selector_name,
            name_alias=cls.aci_leaf_selector_alias,
            description=cls.aci_leaf_selector_description,
            aci_leaf_switch_profile=cls.aci_leaf_switch_profile,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_leaf_selector_empty = ACILeafSelector.objects.create(
            name="ACITestLeafSelectorEmpty",
            aci_leaf_switch_profile=cls.aci_leaf_switch_profile,
        )

        # The base test case already provides a Leaf node 101 in aci_fabric
        cls.f1_leaf_101 = cls.aci_node
        cls.f1_leaf_102 = ACINode.objects.create(
            name="ACITestLeafSelectorLeaf102",
            aci_pod=cls.aci_pod,
            node_id=102,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        # A Spine inside the block range, excluded by role alone
        cls.f1_spine_103 = ACINode.objects.create(
            name="ACITestLeafSelectorSpine103",
            aci_pod=cls.aci_pod,
            node_id=103,
            role=NodeRoleChoices.ROLE_SPINE,
        )
        # A Leaf reusing node ID 101 in a second fabric, where the
        # (_aci_fabric, node_id) constraint permits the duplicate
        cls.aci_fabric2 = ACIFabric.objects.create(
            name="ACITestLeafSelectorFabric2",
            fabric_id=130,
            infra_vlan_vid=3903,
        )
        cls.aci_pod2 = ACIPod.objects.create(
            name="ACITestLeafSelectorPod2",
            aci_fabric=cls.aci_fabric2,
            pod_id=1,
        )
        cls.f2_leaf_101 = ACINode.objects.create(
            name="ACITestLeafSelectorFabric2Leaf101",
            aci_pod=cls.aci_pod2,
            node_id=101,
            role=NodeRoleChoices.ROLE_LEAF,
        )

        cls.aci_leaf_node_block = ACILeafNodeBlock.objects.create(
            name="ACITestLeafSelectorBlock",
            aci_leaf_selector=cls.aci_leaf_selector,
            node_id_from=101,
            node_id_to=104,
        )

    def test_aci_leaf_selector_instance(self) -> None:
        """Test type of created ACI Leaf Selector."""
        self.assertTrue(isinstance(self.aci_leaf_selector, ACILeafSelector))

    def test_aci_leaf_selector_str(self) -> None:
        """Test string value of created ACI Leaf Selector."""
        self.assertEqual(self.aci_leaf_selector.__str__(), self.aci_leaf_selector.name)

    def test_aci_leaf_selector_name_alias(self) -> None:
        """Test alias of created ACI Leaf Selector."""
        self.assertEqual(
            self.aci_leaf_selector.name_alias, self.aci_leaf_selector_alias
        )

    def test_aci_leaf_selector_description(self) -> None:
        """Test description of created ACI Leaf Selector."""
        self.assertEqual(
            self.aci_leaf_selector.description, self.aci_leaf_selector_description
        )

    def test_aci_leaf_selector_parent_object(self) -> None:
        """Test parent object of ACI Leaf Selector is the profile."""
        self.assertEqual(
            self.aci_leaf_selector.parent_object, self.aci_leaf_switch_profile
        )

    def test_aci_leaf_selector_aci_fabric(self) -> None:
        """Test aci_fabric returns the ACI Fabric of the related profile."""
        self.assertTrue(isinstance(self.aci_leaf_selector.aci_fabric, ACIFabric))
        self.assertEqual(self.aci_leaf_selector.aci_fabric, self.aci_fabric)

    def test_aci_leaf_selector_to_objectchange(self) -> None:
        """Test to_objectchange sets the profile as the related object."""
        objectchange = self.aci_leaf_selector.to_objectchange(
            ObjectChangeActionChoices.ACTION_UPDATE
        )
        self.assertEqual(objectchange.related_object, self.aci_leaf_switch_profile)

    def test_aci_leaf_selector_aci_nodes(self) -> None:
        """Test aci_nodes returns the Leaf nodes covered by the blocks."""
        self.assertQuerySetEqual(
            self.aci_leaf_selector.aci_nodes.order_by("node_id"),
            [self.f1_leaf_101, self.f1_leaf_102],
        )

    def test_aci_leaf_selector_aci_nodes_excludes_non_leaf_roles(self) -> None:
        """Test aci_nodes excludes a Spine node inside the block range."""
        self.assertNotIn(self.f1_spine_103, self.aci_leaf_selector.aci_nodes)

    def test_aci_leaf_selector_aci_nodes_excludes_other_fabrics(self) -> None:
        """Test aci_nodes excludes the same node ID in another ACI Fabric."""
        self.assertNotIn(self.f2_leaf_101, self.aci_leaf_selector.aci_nodes)

    def test_aci_leaf_selector_without_blocks_returns_no_nodes(self) -> None:
        """Test aci_nodes is empty for a selector without node blocks."""
        self.assertFalse(self.aci_leaf_selector_empty.aci_nodes.exists())

    def test_aci_leaf_selector_aci_nodes_unions_multiple_blocks(self) -> None:
        """Test aci_nodes unions the ranges of all the selector's blocks."""
        ACILeafNodeBlock.objects.create(
            name="ACITestLeafSelectorBlock2",
            aci_leaf_selector=self.aci_leaf_selector,
            node_id_from=105,
            node_id_to=106,
        )
        leaf_105 = ACINode.objects.create(
            name="ACITestLeafSelectorLeaf105",
            aci_pod=self.aci_pod,
            node_id=105,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        self.assertQuerySetEqual(
            self.aci_leaf_selector.aci_nodes.order_by("node_id"),
            [self.f1_leaf_101, self.f1_leaf_102, leaf_105],
        )

    def test_aci_leaf_selector_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with the selector."""
        self.assertTrue(isinstance(self.aci_leaf_selector.nb_tenant, Tenant))
        self.assertEqual(self.aci_leaf_selector.nb_tenant.name, self.nb_tenant_name)

    def test_invalid_aci_leaf_selector_name(self) -> None:
        """Test validation of ACI Leaf Selector naming."""
        selector = ACILeafSelector(
            name="Invalid Name With Spaces",
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
        )
        with self.assertRaises(ValidationError) as cm:
            selector.full_clean()
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_leaf_selector_name_length(self) -> None:
        """Test validation of ACI Leaf Selector name length."""
        selector = ACILeafSelector(
            name="A" * 65,
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
        )
        with self.assertRaises(ValidationError) as cm:
            selector.full_clean()
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_leaf_selector_name_alias(self) -> None:
        """Test validation of ACI Leaf Selector name alias."""
        selector = ACILeafSelector(
            name="ACILeafSelectorTest1",
            name_alias="Invalid Alias",
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
        )
        with self.assertRaises(ValidationError) as cm:
            selector.full_clean()
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_leaf_selector_name_alias_length(self) -> None:
        """Test validation of ACI Leaf Selector name alias length."""
        selector = ACILeafSelector(
            name="ACILeafSelectorTest1",
            name_alias="A" * 65,
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
        )
        with self.assertRaises(ValidationError) as cm:
            selector.full_clean()
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_leaf_selector_description(self) -> None:
        """Test validation of ACI Leaf Selector description."""
        selector = ACILeafSelector(
            name="ACILeafSelectorTest1",
            description="Invalid Description: ö",
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
        )
        with self.assertRaises(ValidationError) as cm:
            selector.full_clean()
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_leaf_selector_description_length(self) -> None:
        """Test validation of ACI Leaf Selector description length."""
        selector = ACILeafSelector(
            name="ACILeafSelectorTest1",
            description="A" * 129,
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
        )
        with self.assertRaises(ValidationError) as cm:
            selector.full_clean()
        self.assertIn("description", cm.exception.error_dict)

    def test_constraint_unique_aci_leaf_selector_name_per_profile(self) -> None:
        """Test unique constraint of selector name per profile."""
        duplicate_selector = ACILeafSelector(
            name=self.aci_leaf_selector_name,
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_selector.save()

    def test_aci_leaf_selector_name_reusable_in_another_profile(self) -> None:
        """Test the same selector name is allowed in a second profile."""
        other_profile = ACILeafSwitchProfile.objects.create(
            name="ACITestLeafSelectorOtherProfile",
            aci_fabric=self.aci_fabric,
        )
        selector = ACILeafSelector.objects.create(
            name=self.aci_leaf_selector_name,
            aci_leaf_switch_profile=other_profile,
        )
        self.assertEqual(selector.name, self.aci_leaf_selector_name)

    def test_aci_leaf_selector_node_block_count_zero(self) -> None:
        """Test node_block_count is 0 for a selector with no Node Blocks."""
        self.assertEqual(self.aci_leaf_selector_empty.node_block_count, 0)

    def test_aci_leaf_selector_node_block_count_nonzero(self) -> None:
        """Test node_block_count counts the selector's Node Blocks."""
        self.assertEqual(self.aci_leaf_selector.node_block_count, 1)


class ACILeafNodeBlockTestCase(ACIBaseTestCase):
    """Test case for the ACILeafNodeBlock model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACILeafNodeBlock model."""
        super().setUpTestData()

        cls.aci_leaf_node_block_name = "ACITestLeafNodeBlock"
        cls.aci_leaf_node_block_alias = "ACITestLeafNodeBlockAlias"
        cls.aci_leaf_node_block_description = (
            "ACI Test Leaf Node Block for NetBox ACI Plugin"
        )

        # Create objects
        cls.aci_leaf_switch_profile = ACILeafSwitchProfile.objects.create(
            name="ACITestLeafNodeBlockProfile",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_selector = ACILeafSelector.objects.create(
            name="ACITestLeafNodeBlockSelector",
            aci_leaf_switch_profile=cls.aci_leaf_switch_profile,
        )
        cls.aci_leaf_node_block = ACILeafNodeBlock.objects.create(
            name=cls.aci_leaf_node_block_name,
            name_alias=cls.aci_leaf_node_block_alias,
            description=cls.aci_leaf_node_block_description,
            aci_leaf_selector=cls.aci_leaf_selector,
            node_id_from=101,
            node_id_to=104,
            nb_tenant=cls.nb_tenant,
        )

        # The base test case already provides a Leaf node 101 in aci_fabric
        cls.f1_leaf_101 = cls.aci_node
        cls.f1_leaf_102 = ACINode.objects.create(
            name="ACITestLeafNodeBlockLeaf102",
            aci_pod=cls.aci_pod,
            node_id=102,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        # A Spine inside the block range, excluded by role alone
        cls.f1_spine_103 = ACINode.objects.create(
            name="ACITestLeafNodeBlockSpine103",
            aci_pod=cls.aci_pod,
            node_id=103,
            role=NodeRoleChoices.ROLE_SPINE,
        )
        # A Leaf reusing node ID 101 in a second fabric, where the
        # (_aci_fabric, node_id) constraint permits the duplicate
        cls.aci_fabric2 = ACIFabric.objects.create(
            name="ACITestLeafNodeBlockFabric2",
            fabric_id=129,
            infra_vlan_vid=3902,
        )
        cls.aci_pod2 = ACIPod.objects.create(
            name="ACITestLeafNodeBlockPod2",
            aci_fabric=cls.aci_fabric2,
            pod_id=1,
        )
        cls.f2_leaf_101 = ACINode.objects.create(
            name="ACITestLeafNodeBlockFabric2Leaf101",
            aci_pod=cls.aci_pod2,
            node_id=101,
            role=NodeRoleChoices.ROLE_LEAF,
        )

    def test_aci_leaf_node_block_instance(self) -> None:
        """Test type of created ACI Leaf Node Block."""
        self.assertTrue(isinstance(self.aci_leaf_node_block, ACILeafNodeBlock))

    def test_aci_leaf_node_block_str(self) -> None:
        """Test string value of created ACI Leaf Node Block."""
        self.assertEqual(
            self.aci_leaf_node_block.__str__(), self.aci_leaf_node_block.name
        )

    def test_aci_leaf_node_block_name_alias(self) -> None:
        """Test alias of created ACI Leaf Node Block."""
        self.assertEqual(
            self.aci_leaf_node_block.name_alias, self.aci_leaf_node_block_alias
        )

    def test_aci_leaf_node_block_description(self) -> None:
        """Test description of created ACI Leaf Node Block."""
        self.assertEqual(
            self.aci_leaf_node_block.description,
            self.aci_leaf_node_block_description,
        )

    def test_aci_leaf_node_block_node_id_range(self) -> None:
        """Test the node ID range of created ACI Leaf Node Block."""
        self.assertEqual(self.aci_leaf_node_block.node_id_from, 101)
        self.assertEqual(self.aci_leaf_node_block.node_id_to, 104)

    def test_aci_leaf_node_block_parent_object(self) -> None:
        """Test parent object of ACI Leaf Node Block is the selector."""
        self.assertEqual(self.aci_leaf_node_block.parent_object, self.aci_leaf_selector)

    def test_aci_leaf_node_block_aci_fabric(self) -> None:
        """Test aci_fabric returns the ACI Fabric of the related selector."""
        self.assertTrue(isinstance(self.aci_leaf_node_block.aci_fabric, ACIFabric))
        self.assertEqual(self.aci_leaf_node_block.aci_fabric, self.aci_fabric)

    def test_aci_leaf_node_block_to_objectchange(self) -> None:
        """Test to_objectchange sets the selector as the related object."""
        objectchange = self.aci_leaf_node_block.to_objectchange(
            ObjectChangeActionChoices.ACTION_UPDATE
        )
        self.assertEqual(objectchange.related_object, self.aci_leaf_selector)

    def test_aci_leaf_node_block_node_id_query(self) -> None:
        """Test node_id_query matches the node IDs within the range."""
        matched = ACINode.objects.filter(self.aci_leaf_node_block.node_id_query)
        self.assertIn(self.f1_leaf_102, matched)
        self.assertIn(self.f1_spine_103, matched)

    def test_aci_leaf_node_block_valid_node_id_range(self) -> None:
        """Test clean accepts a block whose start equals its end."""
        block = ACILeafNodeBlock(
            aci_leaf_selector=self.aci_leaf_selector,
            name="ACITestLeafNodeBlockSingle",
            node_id_from=101,
            node_id_to=101,
        )
        block.full_clean()

    def test_invalid_aci_leaf_node_block_node_id_from_greater_than_to(
        self,
    ) -> None:
        """Test clean rejects a block whose start exceeds its end."""
        block = ACILeafNodeBlock(
            aci_leaf_selector=self.aci_leaf_selector,
            name="ACITestLeafNodeBlockReversed",
            node_id_from=104,
            node_id_to=101,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("node_id_to", cm.exception.error_dict)

    def test_invalid_aci_leaf_node_block_node_id_below_leaf_minimum(
        self,
    ) -> None:
        """Test validation rejects a block covering APIC node IDs."""
        block = ACILeafNodeBlock(
            aci_leaf_selector=self.aci_leaf_selector,
            name="ACITestLeafNodeBlockApicRange",
            node_id_from=1,
            node_id_to=100,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("node_id_from", cm.exception.error_dict)
        self.assertIn("node_id_to", cm.exception.error_dict)

    def test_aci_leaf_node_block_aci_nodes(self) -> None:
        """Test aci_nodes returns the Leaf nodes within the block range."""
        self.assertQuerySetEqual(
            self.aci_leaf_node_block.aci_nodes.order_by("node_id"),
            [self.f1_leaf_101, self.f1_leaf_102],
        )

    def test_aci_leaf_node_block_aci_nodes_excludes_non_leaf_roles(self) -> None:
        """Test aci_nodes excludes a Spine node inside the block range."""
        self.assertNotIn(self.f1_spine_103, self.aci_leaf_node_block.aci_nodes)

    def test_aci_leaf_node_block_aci_nodes_excludes_other_fabrics(self) -> None:
        """Test aci_nodes excludes the same node ID in another ACI Fabric."""
        self.assertNotIn(self.f2_leaf_101, self.aci_leaf_node_block.aci_nodes)

    def test_aci_leaf_node_block_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with the block."""
        self.assertTrue(isinstance(self.aci_leaf_node_block.nb_tenant, Tenant))
        self.assertEqual(self.aci_leaf_node_block.nb_tenant.name, self.nb_tenant_name)

    def test_invalid_aci_leaf_node_block_name(self) -> None:
        """Test validation of ACI Leaf Node Block naming."""
        block = ACILeafNodeBlock(
            name="Invalid Name With Spaces",
            aci_leaf_selector=self.aci_leaf_selector,
            node_id_from=101,
            node_id_to=104,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_leaf_node_block_name_length(self) -> None:
        """Test validation of ACI Leaf Node Block name length."""
        block = ACILeafNodeBlock(
            name="A" * 65,
            aci_leaf_selector=self.aci_leaf_selector,
            node_id_from=101,
            node_id_to=104,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_leaf_node_block_name_alias(self) -> None:
        """Test validation of ACI Leaf Node Block name alias."""
        block = ACILeafNodeBlock(
            name="ACILeafNodeBlockTest1",
            name_alias="Invalid Alias",
            aci_leaf_selector=self.aci_leaf_selector,
            node_id_from=101,
            node_id_to=104,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_leaf_node_block_name_alias_length(self) -> None:
        """Test validation of ACI Leaf Node Block name alias length."""
        block = ACILeafNodeBlock(
            name="ACILeafNodeBlockTest1",
            name_alias="A" * 65,
            aci_leaf_selector=self.aci_leaf_selector,
            node_id_from=101,
            node_id_to=104,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_leaf_node_block_description(self) -> None:
        """Test validation of ACI Leaf Node Block description."""
        block = ACILeafNodeBlock(
            name="ACILeafNodeBlockTest1",
            description="Invalid Description: ö",
            aci_leaf_selector=self.aci_leaf_selector,
            node_id_from=101,
            node_id_to=104,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_leaf_node_block_description_length(self) -> None:
        """Test validation of ACI Leaf Node Block description length."""
        block = ACILeafNodeBlock(
            name="ACILeafNodeBlockTest1",
            description="A" * 129,
            aci_leaf_selector=self.aci_leaf_selector,
            node_id_from=101,
            node_id_to=104,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("description", cm.exception.error_dict)

    def test_constraint_unique_aci_leaf_node_block_name_per_selector(
        self,
    ) -> None:
        """Test unique constraint of block name per selector."""
        duplicate_block = ACILeafNodeBlock(
            name=self.aci_leaf_node_block_name,
            aci_leaf_selector=self.aci_leaf_selector,
            node_id_from=201,
            node_id_to=202,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_block.save()

    def test_aci_leaf_node_block_name_reusable_in_another_selector(self) -> None:
        """Test the same block name is allowed in a second selector."""
        other_selector = ACILeafSelector.objects.create(
            name="ACITestLeafNodeBlockOtherSelector",
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
        )
        block = ACILeafNodeBlock.objects.create(
            name=self.aci_leaf_node_block_name,
            aci_leaf_selector=other_selector,
            node_id_from=101,
            node_id_to=104,
        )
        self.assertEqual(block.name, self.aci_leaf_node_block_name)


class ACILeafSwitchProfileInterfaceBindingTestCase(ACIBaseTestCase):
    """Test case for the ACILeafSwitchProfileInterfaceBinding model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACILeafSwitchProfileInterfaceBinding."""
        super().setUpTestData()

        cls.aci_leaf_switch_profile = ACILeafSwitchProfile.objects.create(
            name="ACITestSwitchInterfaceBindingProfile",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACITestSwitchInterfaceBindingInterfaceProfile",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_switch_interface_binding_comments = """
        ACI Leaf Switch Profile Interface Binding for NetBox ACI Plugin testing.
        """

        # Create objects
        cls.aci_switch_interface_binding = (
            ACILeafSwitchProfileInterfaceBinding.objects.create(
                aci_leaf_switch_profile=cls.aci_leaf_switch_profile,
                aci_leaf_interface_profile=cls.aci_leaf_interface_profile,
                comments=cls.aci_switch_interface_binding_comments,
            )
        )

    def test_aci_switch_interface_binding_instance(self) -> None:
        """Test type of created ACI Leaf Switch Profile Interface Binding."""
        self.assertTrue(
            isinstance(
                self.aci_switch_interface_binding,
                ACILeafSwitchProfileInterfaceBinding,
            )
        )

    def test_aci_switch_interface_binding_str(self) -> None:
        """Test string value of the created Binding."""
        self.assertEqual(
            self.aci_switch_interface_binding.__str__(),
            f"{self.aci_leaf_switch_profile} - {self.aci_leaf_interface_profile}",
        )

    def test_aci_switch_interface_binding_comments(self) -> None:
        """Test comments of ACI Leaf Switch Profile Interface Binding."""
        self.assertEqual(
            self.aci_switch_interface_binding.comments,
            self.aci_switch_interface_binding_comments,
        )

    def test_aci_switch_interface_binding_aci_leaf_switch_profile_instance(
        self,
    ) -> None:
        """Test the ACI Leaf Switch Profile instance on the binding."""
        self.assertTrue(
            isinstance(
                self.aci_switch_interface_binding.aci_leaf_switch_profile,
                ACILeafSwitchProfile,
            )
        )
        self.assertEqual(
            self.aci_switch_interface_binding.aci_leaf_switch_profile,
            self.aci_leaf_switch_profile,
        )

    def test_aci_switch_interface_binding_aci_leaf_interface_profile_instance(
        self,
    ) -> None:
        """Test the ACI Leaf Interface Profile instance on the binding."""
        self.assertTrue(
            isinstance(
                self.aci_switch_interface_binding.aci_leaf_interface_profile,
                ACILeafInterfaceProfile,
            )
        )
        self.assertEqual(
            self.aci_switch_interface_binding.aci_leaf_interface_profile,
            self.aci_leaf_interface_profile,
        )

    def test_aci_switch_interface_binding_aci_fabric(self) -> None:
        """Test aci_fabric returns the ACI Fabric of the related profile."""
        self.assertTrue(
            isinstance(self.aci_switch_interface_binding.aci_fabric, ACIFabric)
        )
        self.assertEqual(self.aci_switch_interface_binding.aci_fabric, self.aci_fabric)

    def test_aci_switch_interface_binding_parent_object(self) -> None:
        """Test parent object is the ACI Leaf Switch Profile."""
        self.assertEqual(
            self.aci_switch_interface_binding.parent_object,
            self.aci_leaf_switch_profile,
        )

    def test_aci_switch_interface_binding_to_objectchange(self) -> None:
        """Test to_objectchange relates the ACI Leaf Switch Profile."""
        objectchange = self.aci_switch_interface_binding.to_objectchange(
            ObjectChangeActionChoices.ACTION_UPDATE
        )
        self.assertEqual(objectchange.related_object, self.aci_leaf_switch_profile)

    def test_aci_switch_interface_binding_valid_same_fabric(self) -> None:
        """Test clean accepts a profile pair from the same ACI Fabric."""
        other_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACITestSwitchInterfaceBindingSameFabricInterfaceProfile",
            aci_fabric=self.aci_fabric,
        )
        binding = ACILeafSwitchProfileInterfaceBinding(
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
            aci_leaf_interface_profile=other_interface_profile,
        )
        binding.full_clean()

    def test_invalid_aci_switch_interface_binding_cross_fabric(self) -> None:
        """Test clean rejects an interface profile from another ACI Fabric."""
        other_fabric = ACIFabric.objects.create(
            name="ACITestSwitchInterfaceBindingOtherFabric",
            fabric_id=128,
            infra_vlan_vid=3901,
        )
        other_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACITestSwitchInterfaceBindingOtherInterfaceProfile",
            aci_fabric=other_fabric,
        )
        binding = ACILeafSwitchProfileInterfaceBinding(
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
            aci_leaf_interface_profile=other_interface_profile,
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("aci_leaf_interface_profile", cm.exception.error_dict)

    def test_constraint_unique_aci_switch_interface_binding(self) -> None:
        """Test unique constraint of the switch and interface profile pair."""
        duplicate_binding = ACILeafSwitchProfileInterfaceBinding(
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_binding.save()
