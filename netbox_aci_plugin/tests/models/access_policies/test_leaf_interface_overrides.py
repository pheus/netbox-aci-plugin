# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the ACI Leaf Interface Override models."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from core.choices import ObjectChangeActionChoices

from ....choices import LeafInterfacePolicyGroupTypeChoices, NodeRoleChoices
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
from ..base import ACIBaseTestCase


class ACILeafInterfaceOverrideTestCase(ACIBaseTestCase):
    """Test case for the ACILeafInterfaceOverride model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACILeafInterfaceOverride model."""
        super().setUpTestData()

        cls.aci_policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACITestOverridePolicyGroup",
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        cls.aci_node_interface = ACINodeInterface.objects.create(
            aci_node=cls.aci_node, module=1, port=17
        )
        cls.aci_override_description = (
            "ACI Test Leaf Interface Override for NetBox ACI Plugin"
        )
        cls.aci_override_comments = """
        ACI Leaf Interface Override for NetBox ACI Plugin testing.
        """

        # Create objects
        cls.aci_override = ACILeafInterfaceOverride.objects.create(
            aci_node_interface=cls.aci_node_interface,
            aci_leaf_interface_policy_group=cls.aci_policy_group,
            description=cls.aci_override_description,
            comments=cls.aci_override_comments,
        )

    def free_node_interface(self, port: int = 18) -> ACINodeInterface:
        """Return an unbound ACI Node Interface in the base ACI Fabric."""
        return ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=1, port=port
        )

    def foreign_node_interface(self) -> ACINodeInterface:
        """Return an ACI Node Interface in a second ACI Fabric."""
        other_fabric = ACIFabric.objects.create(
            name="ACITestOverrideForeignFabric",
            fabric_id=132,
            infra_vlan_vid=3905,
        )
        other_pod = ACIPod.objects.create(
            name="ACITestOverrideForeignPod",
            aci_fabric=other_fabric,
            pod_id=1,
        )
        other_node = ACINode.objects.create(
            name="ACITestOverrideForeignNode",
            aci_pod=other_pod,
            node_id=101,
        )
        return ACINodeInterface.objects.create(aci_node=other_node, module=1, port=1)

    def test_aci_leaf_interface_override_instance(self) -> None:
        """Test type of created ACI Leaf Interface Override."""
        self.assertTrue(isinstance(self.aci_override, ACILeafInterfaceOverride))

    def test_aci_leaf_interface_override_str(self) -> None:
        """Test string value of created ACI Leaf Interface Override."""
        self.assertEqual(
            self.aci_override.__str__(),
            f"{self.aci_node_interface} - {self.aci_policy_group}",
        )

    def test_aci_leaf_interface_override_description(self) -> None:
        """Test description of created ACI Leaf Interface Override."""
        self.assertEqual(self.aci_override.description, self.aci_override_description)

    def test_aci_leaf_interface_override_comments(self) -> None:
        """Test comments of created ACI Leaf Interface Override."""
        self.assertEqual(self.aci_override.comments, self.aci_override_comments)

    def test_aci_leaf_interface_override_node_interface_instance(self) -> None:
        """Test the ACI Node Interface instance of the override."""
        self.assertTrue(
            isinstance(self.aci_override.aci_node_interface, ACINodeInterface)
        )
        self.assertEqual(self.aci_override.aci_node_interface, self.aci_node_interface)

    def test_aci_leaf_interface_override_policy_group_instance(self) -> None:
        """Test the policy group instance associated with the override."""
        self.assertTrue(
            isinstance(
                self.aci_override.aci_leaf_interface_policy_group,
                ACILeafInterfacePolicyGroup,
            )
        )
        self.assertEqual(
            self.aci_override.aci_leaf_interface_policy_group,
            self.aci_policy_group,
        )

    def test_aci_leaf_interface_override_reverse_accessor(self) -> None:
        """Test the override is reachable from its ACI Node Interface."""
        self.assertEqual(
            self.aci_node_interface.aci_leaf_interface_override,
            self.aci_override,
        )

    def test_aci_leaf_interface_override_aci_fabric(self) -> None:
        """Test the derived ACI Fabric of the override."""
        self.assertTrue(isinstance(self.aci_override.aci_fabric, ACIFabric))
        self.assertEqual(self.aci_override.aci_fabric, self.aci_fabric)

    def test_aci_leaf_interface_override_parent_object(self) -> None:
        """Test parent object of the override is the ACI Node Interface."""
        self.assertEqual(self.aci_override.parent_object, self.aci_node_interface)

    def test_aci_leaf_interface_override_to_objectchange(self) -> None:
        """Test to_objectchange sets the port as the related object."""
        objectchange = self.aci_override.to_objectchange(
            ObjectChangeActionChoices.ACTION_UPDATE
        )
        self.assertEqual(objectchange.related_object, self.aci_node_interface)

    def test_aci_leaf_interface_override_apic_name(self) -> None:
        """Test the derived APIC name without a sub port."""
        self.assertEqual(self.aci_override.apic_name, "override-101-1-17")

    def test_aci_leaf_interface_override_apic_name_with_sub_port(self) -> None:
        """Test the derived APIC name includes a non-zero sub port."""
        node_interface = ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=1, port=17, sub_port=2
        )
        override = ACILeafInterfaceOverride.objects.create(
            aci_node_interface=node_interface,
            aci_leaf_interface_policy_group=self.aci_policy_group,
        )
        self.assertEqual(override.apic_name, "override-101-1-17-2")

    def test_invalid_aci_leaf_interface_override_description(self) -> None:
        """Test validation of ACI Leaf Interface Override description."""
        override = ACILeafInterfaceOverride(
            aci_node_interface=self.free_node_interface(),
            aci_leaf_interface_policy_group=self.aci_policy_group,
            description="Invalid Description: ö",
        )
        with self.assertRaises(ValidationError) as cm:
            override.full_clean()
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_leaf_interface_override_description_length(
        self,
    ) -> None:
        """Test validation of the override description length."""
        override = ACILeafInterfaceOverride(
            aci_node_interface=self.free_node_interface(),
            aci_leaf_interface_policy_group=self.aci_policy_group,
            description="A" * 129,
        )
        with self.assertRaises(ValidationError) as cm:
            override.full_clean()
        self.assertIn("description", cm.exception.error_dict)

    def test_aci_leaf_interface_override_valid(self) -> None:
        """Test clean accepts an override within one ACI Fabric."""
        override = ACILeafInterfaceOverride(
            aci_node_interface=self.free_node_interface(),
            aci_leaf_interface_policy_group=self.aci_policy_group,
        )
        override.full_clean()

    def test_invalid_aci_override_cross_fabric_policy_group(self) -> None:
        """Test clean rejects a policy group from a different ACI Fabric."""
        other_fabric = ACIFabric.objects.create(
            name="ACITestOverrideCrossFabric",
            fabric_id=129,
            infra_vlan_vid=3902,
        )
        other_policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACITestOverrideOtherPolicyGroup",
            aci_fabric=other_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        override = ACILeafInterfaceOverride(
            aci_node_interface=self.free_node_interface(),
            aci_leaf_interface_policy_group=other_policy_group,
        )
        with self.assertRaises(ValidationError) as cm:
            override.full_clean()
        self.assertIn("aci_leaf_interface_policy_group", cm.exception.error_dict)

    def test_invalid_aci_override_port_channel_policy_group(self) -> None:
        """Test clean rejects a Port Channel policy group."""
        pc_policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACITestOverridePCPolicyGroup",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_PC,
        )
        override = ACILeafInterfaceOverride(
            aci_node_interface=self.free_node_interface(),
            aci_leaf_interface_policy_group=pc_policy_group,
        )
        with self.assertRaises(ValidationError) as cm:
            override.full_clean()
        self.assertIn("aci_leaf_interface_policy_group", cm.exception.error_dict)

    def test_invalid_aci_override_vpc_policy_group(self) -> None:
        """Test clean rejects a Virtual Port Channel policy group."""
        vpc_policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACITestOverrideVPCPolicyGroup",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_VPC,
        )
        override = ACILeafInterfaceOverride(
            aci_node_interface=self.free_node_interface(),
            aci_leaf_interface_policy_group=vpc_policy_group,
        )
        with self.assertRaises(ValidationError) as cm:
            override.full_clean()
        self.assertIn("aci_leaf_interface_policy_group", cm.exception.error_dict)

    def test_invalid_aci_override_cross_fabric_node_interface(self) -> None:
        """Test clean rejects a node interface from another ACI Fabric."""
        override = ACILeafInterfaceOverride(
            aci_node_interface=self.foreign_node_interface(),
            aci_leaf_interface_policy_group=self.aci_policy_group,
        )
        with self.assertRaises(ValidationError) as cm:
            override.full_clean()
        self.assertIn("aci_leaf_interface_policy_group", cm.exception.error_dict)

    def test_constraint_one_override_per_node_interface(self) -> None:
        """Test a second override on the same ACI Node Interface fails."""
        duplicate_override = ACILeafInterfaceOverride(
            aci_node_interface=self.aci_node_interface,
            aci_leaf_interface_policy_group=self.aci_policy_group,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_override.save()

    def _other_fabric(self) -> ACIFabric:
        """Return a second ACI Fabric with no Overrides of its own."""
        return ACIFabric.objects.create(
            name="ACITestOverrideOtherFabric",
            fabric_id=self.aci_fabric.fabric_id + 50,
            infra_vlan_vid=self.aci_fabric.infra_vlan_vid + 50,
        )

    def test_invalid_aci_pod_fabric_move_stranding_override(self) -> None:
        """Test moving the ACI Pod to another ACI Fabric is refused."""
        self.aci_pod.aci_fabric = self._other_fabric()

        with self.assertRaises(ValidationError) as cm:
            self.aci_pod.full_clean()

        self.assertIn("aci_fabric", cm.exception.error_dict)

    def test_invalid_aci_node_pod_move_stranding_override(self) -> None:
        """Test moving the ACI Node to a Pod in another Fabric is refused."""
        other_pod = ACIPod.objects.create(
            name="ACITestOverrideOtherPod",
            aci_fabric=self._other_fabric(),
            pod_id=9,
        )
        self.aci_node.aci_pod = other_pod

        with self.assertRaises(ValidationError) as cm:
            self.aci_node.full_clean()

        self.assertIn("aci_pod", cm.exception.error_dict)

    def test_invalid_aci_node_interface_node_move_stranding_override(self) -> None:
        """Test moving the Interface to a Node in another Fabric is refused."""
        other_pod = ACIPod.objects.create(
            name="ACITestOverrideOtherPod2",
            aci_fabric=self._other_fabric(),
            pod_id=10,
        )
        other_node = ACINode.objects.create(
            name="ACITestOverrideOtherNode",
            aci_pod=other_pod,
            node_id=201,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        self.aci_node_interface.aci_node = other_node

        with self.assertRaises(ValidationError) as cm:
            self.aci_node_interface.full_clean()

        self.assertIn("aci_node", cm.exception.error_dict)
