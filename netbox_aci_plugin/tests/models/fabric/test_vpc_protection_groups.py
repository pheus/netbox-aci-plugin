# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from tenancy.models import Tenant

from ....choices import NodeRoleChoices
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ....models.fabric.vpc_protection_groups import ACIVPCProtectionGroup
from ..base import ACIBaseTestCase


class ACIVPCProtectionGroupTestCase(ACIBaseTestCase):
    """Test case for ACIVPCProtectionGroup model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACIVPCProtectionGroup model."""
        super().setUpTestData()

        cls.aci_vpc_group_name = "ACITestVPCGroup"
        cls.aci_vpc_group_alias = "ACITestVPCGroupAlias"
        cls.aci_vpc_group_description = (
            "ACI Test VPC Protection Group for NetBox ACI Plugin"
        )
        cls.aci_vpc_group_comments = (
            "ACI VPC Protection Group for NetBox ACI Plugin testing."
        )
        cls.aci_vpc_group_pair_id = 1

        # A second leaf node in the base Pod, paired with the base fixture's
        # ACI Node as the primary VPC protection group.
        cls.aci_node_b = ACINode.objects.create(
            name="ACIBaseTestNodeB",
            aci_pod=cls.aci_pod,
            node_id=102,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        # Two further unpaired leaf nodes in the base Pod, reused across the
        # membership-exclusivity and ordered_nodes scenarios below.
        cls.aci_node_unpaired_1 = ACINode.objects.create(
            name="ACIBaseTestNodeUnpaired1",
            aci_pod=cls.aci_pod,
            node_id=106,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.aci_node_unpaired_2 = ACINode.objects.create(
            name="ACIBaseTestNodeUnpaired2",
            aci_pod=cls.aci_pod,
            node_id=107,
            role=NodeRoleChoices.ROLE_LEAF,
        )

        cls.aci_vpc_group = ACIVPCProtectionGroup.objects.create(
            name=cls.aci_vpc_group_name,
            name_alias=cls.aci_vpc_group_alias,
            description=cls.aci_vpc_group_description,
            comments=cls.aci_vpc_group_comments,
            aci_fabric=cls.aci_fabric,
            logical_pair_id=cls.aci_vpc_group_pair_id,
            aci_node_a=cls.aci_node,
            aci_node_b=cls.aci_node_b,
            nb_tenant=cls.nb_tenant,
        )

    def test_aci_vpc_protection_group_instance(self) -> None:
        """Test type of created ACI VPC Protection Group."""
        self.assertTrue(isinstance(self.aci_vpc_group, ACIVPCProtectionGroup))

    def test_aci_vpc_protection_group_str(self) -> None:
        """Test string value of created ACI VPC Protection Group."""
        self.assertEqual(self.aci_vpc_group.__str__(), self.aci_vpc_group_name)

    def test_aci_vpc_protection_group_alias(self) -> None:
        """Test alias of ACI VPC Protection Group."""
        self.assertEqual(self.aci_vpc_group.name_alias, self.aci_vpc_group_alias)

    def test_aci_vpc_protection_group_description(self) -> None:
        """Test description of ACI VPC Protection Group."""
        self.assertEqual(self.aci_vpc_group.description, self.aci_vpc_group_description)

    def test_aci_vpc_protection_group_aci_fabric_instance(self) -> None:
        """Test the ACI Fabric instance of ACI VPC Protection Group."""
        self.assertTrue(isinstance(self.aci_vpc_group.aci_fabric, ACIFabric))
        self.assertEqual(self.aci_vpc_group.aci_fabric.name, self.aci_fabric_name)

    def test_aci_vpc_protection_group_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant associated with ACI VPC Protection Group."""
        self.assertTrue(isinstance(self.aci_vpc_group.nb_tenant, Tenant))
        self.assertEqual(self.aci_vpc_group.nb_tenant.name, self.nb_tenant_name)

    def test_aci_vpc_protection_group_logical_pair_id(self) -> None:
        """Test logical pair ID of ACI VPC Protection Group."""
        self.assertEqual(self.aci_vpc_group.logical_pair_id, self.aci_vpc_group_pair_id)

    def test_aci_vpc_protection_group_aci_node_a_instance(self) -> None:
        """Test the ACI Node A instance of ACI VPC Protection Group."""
        self.assertTrue(isinstance(self.aci_vpc_group.aci_node_a, ACINode))
        self.assertEqual(self.aci_vpc_group.aci_node_a, self.aci_node)

    def test_aci_vpc_protection_group_aci_node_b_instance(self) -> None:
        """Test the ACI Node B instance of ACI VPC Protection Group."""
        self.assertTrue(isinstance(self.aci_vpc_group.aci_node_b, ACINode))
        self.assertEqual(self.aci_vpc_group.aci_node_b, self.aci_node_b)

    def test_aci_vpc_protection_group_parent_object(self) -> None:
        """Test parent object of ACI VPC Protection Group is the ACI Fabric."""
        self.assertEqual(self.aci_vpc_group.parent_object, self.aci_fabric)

    def test_aci_vpc_protection_group_aci_pod(self) -> None:
        """Test aci_pod returns the ACI Pod of the related ACI nodes."""
        self.assertEqual(self.aci_vpc_group.aci_pod, self.aci_pod)

    def test_aci_vpc_protection_group_ordered_nodes(self) -> None:
        """Test ordered_nodes returns the pair sorted by ACI node ID."""
        group = ACIVPCProtectionGroup(
            aci_fabric=self.aci_fabric,
            aci_node_a=self.aci_node_unpaired_2,
            aci_node_b=self.aci_node_unpaired_1,
        )
        self.assertEqual(
            group.ordered_nodes,
            (self.aci_node_unpaired_1, self.aci_node_unpaired_2),
        )

    def test_invalid_aci_vpc_protection_group_name(self) -> None:
        """Test validation of ACI VPC Protection Group naming."""
        group = ACIVPCProtectionGroup(name="Invalid Name With Spaces")
        with self.assertRaises(ValidationError):
            group.full_clean()

    def test_invalid_aci_vpc_protection_group_name_length(self) -> None:
        """Test validation of ACI VPC Protection Group name length."""
        group = ACIVPCProtectionGroup(name="A" * 65)
        with self.assertRaises(ValidationError):
            group.full_clean()

    def test_invalid_aci_vpc_protection_group_name_alias(self) -> None:
        """Test validation of ACI VPC Protection Group name alias."""
        group = ACIVPCProtectionGroup(
            name="ACIVPCGroupTest1", name_alias="Invalid Alias"
        )
        with self.assertRaises(ValidationError):
            group.full_clean()

    def test_invalid_aci_vpc_protection_group_name_alias_length(self) -> None:
        """Test validation of ACI VPC Protection Group name alias length."""
        group = ACIVPCProtectionGroup(name="ACIVPCGroupTest1", name_alias="A" * 65)
        with self.assertRaises(ValidationError):
            group.full_clean()

    def test_invalid_aci_vpc_protection_group_description(self) -> None:
        """Test validation of ACI VPC Protection Group description."""
        group = ACIVPCProtectionGroup(
            name="ACIVPCGroupTest1", description="Invalid Description: ö"
        )
        with self.assertRaises(ValidationError):
            group.full_clean()

    def test_invalid_aci_vpc_protection_group_description_length(self) -> None:
        """Test validation of ACI VPC Protection Group description length."""
        group = ACIVPCProtectionGroup(name="ACIVPCGroupTest1", description="A" * 129)
        with self.assertRaises(ValidationError):
            group.full_clean()

    def test_invalid_aci_vpc_protection_group_pair_id_min(self) -> None:
        """Test validation of VPC Protection Group pair ID lower bound."""
        group = ACIVPCProtectionGroup(name="ACIVPCGroupTest1", logical_pair_id=0)
        with self.assertRaises(ValidationError) as cm:
            group.full_clean()
        self.assertIn("logical_pair_id", cm.exception.error_dict)

    def test_invalid_aci_vpc_protection_group_pair_id_max(self) -> None:
        """Test validation of VPC Protection Group pair ID upper bound."""
        group = ACIVPCProtectionGroup(name="ACIVPCGroupTest1", logical_pair_id=1001)
        with self.assertRaises(ValidationError) as cm:
            group.full_clean()
        self.assertIn("logical_pair_id", cm.exception.error_dict)

    def test_invalid_aci_vpc_protection_group_same_node(self) -> None:
        """Test clean rejects a group with the same node in both positions."""
        group = ACIVPCProtectionGroup(
            name="ACIVPCGroupSameNode",
            aci_fabric=self.aci_fabric,
            logical_pair_id=90,
            aci_node_a=self.aci_node_unpaired_1,
            aci_node_b=self.aci_node_unpaired_1,
        )
        with self.assertRaises(ValidationError) as cm:
            group.full_clean()
        self.assertIn("aci_node_b", cm.exception.error_dict)

    def test_constraint_check_aci_vpc_protection_group_distinct_nodes(self) -> None:
        """Test the distinct-nodes CheckConstraint via a direct ORM write."""
        group = ACIVPCProtectionGroup(
            name="ACIVPCGroupCheckConstraint",
            aci_fabric=self.aci_fabric,
            logical_pair_id=91,
            aci_node_a=self.aci_node_unpaired_2,
            aci_node_b=self.aci_node_unpaired_2,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            group.save()

    def test_invalid_aci_vpc_protection_group_node_a_spine_role(self) -> None:
        """Test clean rejects a spine-role ACI Node as node A."""
        spine_node = ACINode.objects.create(
            name="ACIVPCGroupSpineNodeA",
            aci_pod=self.aci_pod,
            node_id=210,
            role=NodeRoleChoices.ROLE_SPINE,
        )
        group = ACIVPCProtectionGroup(
            name="ACIVPCGroupSpineA",
            aci_fabric=self.aci_fabric,
            logical_pair_id=92,
            aci_node_a=spine_node,
            aci_node_b=self.aci_node_unpaired_1,
        )
        with self.assertRaises(ValidationError) as cm:
            group.full_clean()
        self.assertIn("aci_node_a", cm.exception.error_dict)

    def test_invalid_aci_vpc_protection_group_node_b_spine_role(self) -> None:
        """Test clean rejects a spine-role ACI Node as node B."""
        spine_node = ACINode.objects.create(
            name="ACIVPCGroupSpineNodeB",
            aci_pod=self.aci_pod,
            node_id=211,
            role=NodeRoleChoices.ROLE_SPINE,
        )
        group = ACIVPCProtectionGroup(
            name="ACIVPCGroupSpineB",
            aci_fabric=self.aci_fabric,
            logical_pair_id=93,
            aci_node_a=self.aci_node_unpaired_2,
            aci_node_b=spine_node,
        )
        with self.assertRaises(ValidationError) as cm:
            group.full_clean()
        self.assertIn("aci_node_b", cm.exception.error_dict)

    def test_invalid_aci_vpc_protection_group_node_a_cross_fabric(self) -> None:
        """Test clean rejects a node A from a different ACI Fabric."""
        other_fabric = ACIFabric.objects.create(
            name="ACIBaseTestFabricOtherA",
            fabric_id=self.aci_fabric_id + 1,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 1,
        )
        other_pod = ACIPod.objects.create(
            name="ACIBaseTestPodOtherA", aci_fabric=other_fabric, pod_id=1
        )
        other_node = ACINode.objects.create(
            name="ACIVPCGroupOtherFabricNodeA",
            aci_pod=other_pod,
            node_id=101,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        group = ACIVPCProtectionGroup(
            name="ACIVPCGroupCrossFabricA",
            aci_fabric=self.aci_fabric,
            logical_pair_id=94,
            aci_node_a=other_node,
            aci_node_b=self.aci_node_unpaired_1,
        )
        with self.assertRaises(ValidationError) as cm:
            group.full_clean()
        self.assertIn("aci_node_a", cm.exception.error_dict)

    def test_invalid_aci_vpc_protection_group_node_b_cross_fabric(self) -> None:
        """Test clean rejects a node B from a different ACI Fabric."""
        other_fabric = ACIFabric.objects.create(
            name="ACIBaseTestFabricOtherB",
            fabric_id=self.aci_fabric_id + 2,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 2,
        )
        other_pod = ACIPod.objects.create(
            name="ACIBaseTestPodOtherB", aci_fabric=other_fabric, pod_id=1
        )
        other_node = ACINode.objects.create(
            name="ACIVPCGroupOtherFabricNodeB",
            aci_pod=other_pod,
            node_id=101,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        group = ACIVPCProtectionGroup(
            name="ACIVPCGroupCrossFabricB",
            aci_fabric=self.aci_fabric,
            logical_pair_id=95,
            aci_node_a=self.aci_node_unpaired_2,
            aci_node_b=other_node,
        )
        with self.assertRaises(ValidationError) as cm:
            group.full_clean()
        self.assertIn("aci_node_b", cm.exception.error_dict)

    def test_invalid_aci_vpc_protection_group_cross_pod(self) -> None:
        """Test clean rejects nodes A and B from different ACI Pods."""
        other_pod = ACIPod.objects.create(
            name="ACIBaseTestPod2", aci_fabric=self.aci_fabric, pod_id=2
        )
        other_pod_node = ACINode.objects.create(
            name="ACIVPCGroupOtherPodNode",
            aci_pod=other_pod,
            node_id=108,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        group = ACIVPCProtectionGroup(
            name="ACIVPCGroupCrossPod",
            aci_fabric=self.aci_fabric,
            logical_pair_id=96,
            aci_node_a=self.aci_node_unpaired_1,
            aci_node_b=other_pod_node,
        )
        with self.assertRaises(ValidationError) as cm:
            group.full_clean()
        self.assertIn("aci_node_b", cm.exception.error_dict)

    def test_invalid_aci_vpc_protection_group_stored_node_fabric_mismatch(
        self,
    ) -> None:
        """Test clean reads the stored fabric, not an unsaved ACI Pod one."""
        other_fabric = ACIFabric.objects.create(
            name="ACIVPCGroupDirtyPodFabric",
            fabric_id=self.aci_fabric_id + 3,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 3,
        )
        group = ACIVPCProtectionGroup(
            name="ACIVPCGroupDirtyPod",
            aci_fabric=other_fabric,
            logical_pair_id=200,
            aci_node_a=self.aci_node_unpaired_1,
            aci_node_b=self.aci_node_unpaired_2,
        )
        # Dirty the in-memory Pod so a Pod-chained check would accept a
        # group scoped to a Fabric the nodes do not belong to
        group.aci_node_a.aci_pod.aci_fabric = other_fabric
        group.aci_node_b.aci_pod.aci_fabric = other_fabric

        with self.assertRaises(ValidationError) as cm:
            group.full_clean()
        self.assertIn("aci_node_a", cm.exception.error_dict)
        self.assertIn("aci_node_b", cm.exception.error_dict)

    def test_invalid_aci_vpc_protection_group_stored_node_role(self) -> None:
        """Test clean reads the stored role, not an unsaved in-memory one."""
        spine_node = ACINode.objects.create(
            name="ACIVPCGroupStoredSpine",
            aci_pod=self.aci_pod,
            node_id=112,
            role=NodeRoleChoices.ROLE_SPINE,
        )
        # Dirty the in-memory role: a stored Spine must still be rejected
        spine_node.role = NodeRoleChoices.ROLE_LEAF

        group = ACIVPCProtectionGroup(
            name="ACIVPCGroupDirtyRole",
            aci_fabric=self.aci_fabric,
            logical_pair_id=201,
            aci_node_a=spine_node,
            aci_node_b=self.aci_node_unpaired_1,
        )
        with self.assertRaises(ValidationError) as cm:
            group.full_clean()
        self.assertIn("aci_node_a", cm.exception.error_dict)

    def test_invalid_aci_vpc_protection_group_stored_node_pod(self) -> None:
        """Test clean reads the stored ACI Pod, not an in-memory one."""
        other_pod = ACIPod.objects.create(
            name="ACIVPCGroupStoredOtherPod", aci_fabric=self.aci_fabric, pod_id=30
        )
        other_pod_node = ACINode.objects.create(
            name="ACIVPCGroupStoredOtherPodNode",
            aci_pod=other_pod,
            node_id=113,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        # Dirty the in-memory Pod: a stored cross-Pod pair must be rejected
        other_pod_node.aci_pod = self.aci_pod

        group = ACIVPCProtectionGroup(
            name="ACIVPCGroupDirtyPodId",
            aci_fabric=self.aci_fabric,
            logical_pair_id=202,
            aci_node_a=self.aci_node_unpaired_1,
            aci_node_b=other_pod_node,
        )
        with self.assertRaises(ValidationError) as cm:
            group.full_clean()
        self.assertIn("aci_node_b", cm.exception.error_dict)

    def test_invalid_aci_vpc_protection_group_unknown_node_id(self) -> None:
        """Test clean reports an unknown node ID without DoesNotExist."""
        group = ACIVPCProtectionGroup(
            name="ACIVPCGroupUnknownNode",
            aci_fabric=self.aci_fabric,
            logical_pair_id=203,
            aci_node_a_id=999999,
            aci_node_b=self.aci_node_unpaired_1,
        )
        with self.assertRaises(ValidationError) as cm:
            group.full_clean()
        self.assertIn("aci_node_a", cm.exception.error_dict)

    def test_invalid_aci_vpc_protection_group_node_already_paired_as_node_a(
        self,
    ) -> None:
        """Test clean rejects reusing a paired node as node A."""
        group = ACIVPCProtectionGroup(
            name="ACIVPCGroupReuseA",
            aci_fabric=self.aci_fabric,
            logical_pair_id=97,
            aci_node_a=self.aci_node,
            aci_node_b=self.aci_node_unpaired_1,
        )
        with self.assertRaises(ValidationError) as cm:
            group.full_clean()
        self.assertIn("aci_node_a", cm.exception.error_dict)

    def test_invalid_aci_vpc_protection_group_node_already_paired_as_node_b(
        self,
    ) -> None:
        """Test clean rejects reusing a paired node as node B."""
        group = ACIVPCProtectionGroup(
            name="ACIVPCGroupReuseB",
            aci_fabric=self.aci_fabric,
            logical_pair_id=98,
            aci_node_a=self.aci_node_unpaired_2,
            aci_node_b=self.aci_node_b,
        )
        with self.assertRaises(ValidationError) as cm:
            group.full_clean()
        self.assertIn("aci_node_b", cm.exception.error_dict)

    def test_constraint_unique_aci_vpc_protection_group_name(self) -> None:
        """Test unique constraint of ACI VPC Protection Group name."""
        duplicate = ACIVPCProtectionGroup(
            name=self.aci_vpc_group_name,
            aci_fabric=self.aci_fabric,
            logical_pair_id=99,
            aci_node_a=self.aci_node_unpaired_1,
            aci_node_b=self.aci_node_unpaired_2,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate.save()

    def test_constraint_unique_aci_vpc_protection_group_pair_id(self) -> None:
        """Test unique constraint of ACI VPC Protection Group pair ID."""
        duplicate = ACIVPCProtectionGroup(
            name="ACIVPCGroupDuplicatePairId",
            aci_fabric=self.aci_fabric,
            logical_pair_id=self.aci_vpc_group_pair_id,
            aci_node_a=self.aci_node_unpaired_1,
            aci_node_b=self.aci_node_unpaired_2,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate.save()

    def test_constraint_unique_aci_vpc_protection_group_reversed_pair(self) -> None:
        """Test the order-independent pair uniqueness constraint."""
        reversed_group = ACIVPCProtectionGroup(
            name="ACIVPCGroupReversedPair",
            aci_fabric=self.aci_fabric,
            logical_pair_id=100,
            aci_node_a=self.aci_node_b,
            aci_node_b=self.aci_node,
        )
        with self.assertRaises(IntegrityError) as cm, transaction.atomic():
            reversed_group.save()
        # Pin the Least/Greatest constraint: a name or pair-ID collision
        # would otherwise satisfy this test without exercising the pair
        self.assertIn(
            "netbox_aci_plugin_acivpcprotectiongroup_uniq_pair",
            str(cm.exception),
        )

    def test_invalid_aci_vpc_protection_group_reversed_pair(self) -> None:
        """Test clean rejects a reversed pair through the membership guard."""
        reversed_group = ACIVPCProtectionGroup(
            name="ACIVPCGroupReversedPairClean",
            aci_fabric=self.aci_fabric,
            logical_pair_id=101,
            aci_node_a=self.aci_node_b,
            aci_node_b=self.aci_node,
        )
        with self.assertRaises(ValidationError) as cm:
            reversed_group.full_clean()
        self.assertIn("aci_node_a", cm.exception.error_dict)
        self.assertIn("aci_node_b", cm.exception.error_dict)

    def test_aci_vpc_protection_group_protect_on_node_delete(self) -> None:
        """Test ACI Node deletion is blocked by a VPC protection group."""
        with self.assertRaises(ProtectedError):
            self.aci_node.delete()

    def test_default_ordering_queryset_evaluates(self) -> None:
        """Test that the default-ordered queryset evaluates without error."""
        self.assertIsNotNone(list(ACIVPCProtectionGroup.objects.all()))
