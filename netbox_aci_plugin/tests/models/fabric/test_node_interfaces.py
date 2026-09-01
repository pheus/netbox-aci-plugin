# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from core.choices import ObjectChangeActionChoices
from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, Interface
from tenancy.models import Tenant

from ....choices import LeafInterfacePolicyGroupTypeChoices, NodeRoleChoices
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ....models.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverride,
)
from ....models.fabric.node_interfaces import ACINodeInterface
from ....models.fabric.nodes import ACINode
from ..base import ACIBaseTestCase


class ACINodeInterfaceTestCase(ACIBaseTestCase):
    """Test case for ACINodeInterface model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACINodeInterface model."""
        super().setUpTestData()

        cls.aci_node_interface_module = 1
        cls.aci_node_interface_port = 1
        cls.aci_node_interface_sub_port = 0
        cls.aci_node_interface_description = (
            "ACI Test Node Interface for NetBox ACI Plugin"
        )
        cls.aci_node_interface_comments = (
            "ACI Node Interface for NetBox ACI Plugin testing."
        )

        cls.nb_interface1 = Interface.objects.create(
            device=cls.aci_node_object1,
            name="eth1/1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )

        cls.aci_node_interface = ACINodeInterface.objects.create(
            aci_node=cls.aci_node,
            nb_interface=cls.nb_interface1,
            module=cls.aci_node_interface_module,
            port=cls.aci_node_interface_port,
            sub_port=cls.aci_node_interface_sub_port,
            description=cls.aci_node_interface_description,
            nb_tenant=cls.nb_tenant,
            comments=cls.aci_node_interface_comments,
        )

    def test_aci_node_interface_instance(self) -> None:
        """Test type of created ACI Node Interface."""
        self.assertTrue(isinstance(self.aci_node_interface, ACINodeInterface))

    def test_aci_node_interface_str(self) -> None:
        """Test string value of created ACI Node Interface."""
        self.assertEqual(
            self.aci_node_interface.__str__(),
            f"{self.aci_node}:{self.aci_node_interface.interface_token}",
        )

    def test_aci_node_interface_description(self) -> None:
        """Test description of ACI Node Interface."""
        self.assertEqual(
            self.aci_node_interface.description, self.aci_node_interface_description
        )

    def test_aci_node_interface_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant associated with ACI Node Interface."""
        self.assertTrue(isinstance(self.aci_node_interface.nb_tenant, Tenant))
        self.assertEqual(self.aci_node_interface.nb_tenant.name, self.nb_tenant_name)

    def test_invalid_aci_node_interface_description(self) -> None:
        """Test validation of ACI Node Interface description."""
        interface = ACINodeInterface(
            aci_node=self.aci_node,
            port=41,
            description="Invalid Description: ö",
        )
        with self.assertRaises(ValidationError) as cm:
            interface.full_clean()

        # Check the specific field that failed
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_node_interface_description_length(self) -> None:
        """Test validation of ACI Node Interface description length."""
        interface = ACINodeInterface(
            aci_node=self.aci_node,
            port=42,
            description="T" * 129,  # Exceeding the maximum length of 128
        )
        with self.assertRaises(ValidationError) as cm:
            interface.full_clean()

        # Check the specific field that failed
        self.assertIn("description", cm.exception.error_dict)

    def test_aci_node_interface_aci_node_instance(self) -> None:
        """Test the ACI Node instance associated with ACI Node Interface."""
        self.assertTrue(isinstance(self.aci_node_interface.aci_node, ACINode))
        self.assertEqual(self.aci_node_interface.aci_node, self.aci_node)

    def test_aci_node_interface_nb_interface_instance(self) -> None:
        """Test the NetBox interface instance of ACI Node Interface."""
        self.assertTrue(isinstance(self.aci_node_interface.nb_interface, Interface))
        self.assertEqual(self.aci_node_interface.nb_interface, self.nb_interface1)

    def test_aci_node_interface_module(self) -> None:
        """Test module of ACI Node Interface."""
        self.assertEqual(self.aci_node_interface.module, self.aci_node_interface_module)

    def test_aci_node_interface_port(self) -> None:
        """Test port of ACI Node Interface."""
        self.assertEqual(self.aci_node_interface.port, self.aci_node_interface_port)

    def test_aci_node_interface_sub_port(self) -> None:
        """Test sub port of ACI Node Interface."""
        self.assertEqual(
            self.aci_node_interface.sub_port, self.aci_node_interface_sub_port
        )

    def test_aci_node_interface_defaults(self) -> None:
        """Test default values of ACI Node Interface."""
        iface = ACINodeInterface.objects.create(aci_node=self.aci_node, port=5)
        self.assertEqual(iface.module, 1)
        self.assertEqual(iface.sub_port, 0)

    def test_aci_node_interface_interface_token_plain(self) -> None:
        """Test interface_token without a sub port and the default module."""
        iface = ACINodeInterface(aci_node=self.aci_node, module=1, port=10)
        self.assertEqual(iface.interface_token, "eth1/10")

    def test_aci_node_interface_interface_token_sub_port(self) -> None:
        """Test interface_token includes a non-zero sub port."""
        iface = ACINodeInterface(aci_node=self.aci_node, module=1, port=10, sub_port=3)
        self.assertEqual(iface.interface_token, "eth1/10/3")

    def test_aci_node_interface_interface_token_non_default_module(self) -> None:
        """Test interface_token reflects a non-default module."""
        iface = ACINodeInterface(aci_node=self.aci_node, module=2, port=10)
        self.assertEqual(iface.interface_token, "eth2/10")

    def test_aci_node_interface_sub_port_zero_and_one_are_distinct(self) -> None:
        """Test sub port 0 and 1 are distinct coordinates on the same port."""
        other = ACINodeInterface.objects.create(
            aci_node=self.aci_node,
            module=self.aci_node_interface_module,
            port=self.aci_node_interface_port,
            sub_port=1,
        )
        self.assertNotEqual(other.pk, self.aci_node_interface.pk)

    def test_aci_node_interface_sub_port_display_zero_is_none(self) -> None:
        """Test sub_port_display is None for the APIC 0 (none) sentinel."""
        self.assertIsNone(self.aci_node_interface.sub_port_display)

    def test_aci_node_interface_sub_port_display_nonzero(self) -> None:
        """Test sub_port_display returns a non-zero sub port unchanged."""
        iface = ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=1, port=11, sub_port=3
        )
        self.assertEqual(iface.sub_port_display, 3)

    def test_aci_node_interface_leaf_interface_override_absent(self) -> None:
        """Test leaf_interface_override is None without an Override."""
        self.assertIsNone(self.aci_node_interface.leaf_interface_override)

    def test_aci_node_interface_leaf_interface_override_present(self) -> None:
        """Test leaf_interface_override returns the linked Override."""
        policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACINodeInterfaceOverridePolicyGroup",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        override = ACILeafInterfaceOverride.objects.create(
            aci_node_interface=self.aci_node_interface,
            aci_leaf_interface_policy_group=policy_group,
        )
        refetched = ACINodeInterface.objects.select_related(
            "aci_leaf_interface_override"
        ).get(pk=self.aci_node_interface.pk)
        self.assertEqual(refetched.leaf_interface_override, override)

    def test_aci_node_interface_leaf_interface_override_without_select_related(
        self,
    ) -> None:
        """Test leaf_interface_override resolves on an unwarmed instance."""
        policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACINodeInterfaceOverrideColdCachePolicyGroup",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        override = ACILeafInterfaceOverride.objects.create(
            aci_node_interface=self.aci_node_interface,
            aci_leaf_interface_policy_group=policy_group,
        )
        refetched = ACINodeInterface.objects.get(pk=self.aci_node_interface.pk)
        self.assertEqual(refetched.leaf_interface_override, override)

    def test_constraint_unique_aci_node_interface_coordinates(self) -> None:
        """Test unique constraint of ACI Node Interface coordinates."""
        duplicate = ACINodeInterface(
            aci_node=self.aci_node,
            module=self.aci_node_interface_module,
            port=self.aci_node_interface_port,
            sub_port=self.aci_node_interface_sub_port,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate.save()

    def test_invalid_aci_node_interface_duplicate_coordinates(self) -> None:
        """Test full_clean surfaces the coordinate uniqueness constraint."""
        duplicate = ACINodeInterface(
            aci_node=self.aci_node,
            module=self.aci_node_interface_module,
            port=self.aci_node_interface_port,
            sub_port=self.aci_node_interface_sub_port,
        )
        with self.assertRaises(ValidationError) as cm:
            duplicate.full_clean()
        self.assertIn("__all__", cm.exception.error_dict)

    def test_invalid_aci_node_interface_spine_node(self) -> None:
        """Test clean rejects an ACI Node without the Leaf role."""
        spine_node = ACINode.objects.create(
            name="ACINodeInterfaceSpineNode",
            aci_pod=self.aci_pod,
            node_id=201,
            role=NodeRoleChoices.ROLE_SPINE,
        )
        iface = ACINodeInterface(aci_node=spine_node, module=1, port=1)
        with self.assertRaises(ValidationError) as cm:
            iface.full_clean()
        self.assertIn("aci_node", cm.exception.error_dict)

    def test_invalid_aci_node_interface_device_mismatch(self) -> None:
        """Test clean rejects an nb_interface on the wrong device."""
        other_device = Device.objects.create(
            name="ACINodeInterfaceOtherDevice",
            device_type=self.device_type1,
            role=self.device_role1,
            site=self.site,
        )
        other_interface = Interface.objects.create(
            device=other_device,
            name="eth1/1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        iface = ACINodeInterface(
            aci_node=self.aci_node, nb_interface=other_interface, module=1, port=2
        )
        with self.assertRaises(ValidationError) as cm:
            iface.full_clean()
        self.assertIn("nb_interface", cm.exception.error_dict)

    def test_aci_node_interface_matching_device_accepted(self) -> None:
        """Test full_clean accepts an nb_interface on the node's device."""
        matching_interface = Interface.objects.create(
            device=self.aci_node_object1,
            name="eth1/2",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        iface = ACINodeInterface(
            aci_node=self.aci_node, nb_interface=matching_interface, module=1, port=3
        )
        iface.full_clean()

    def test_invalid_aci_node_interface_nb_interface_type_lag(self) -> None:
        """Test clean rejects a LAG type nb_interface."""
        lag_interface = Interface.objects.create(
            device=self.aci_node_object1,
            name="port-channel1",
            type=InterfaceTypeChoices.TYPE_LAG,
        )
        iface = ACINodeInterface(
            aci_node=self.aci_node, nb_interface=lag_interface, module=1, port=4
        )
        with self.assertRaises(ValidationError) as cm:
            iface.full_clean()
        self.assertIn("nb_interface", cm.exception.error_dict)

    def test_invalid_aci_node_interface_nb_interface_type_virtual(self) -> None:
        """Test clean rejects a virtual type nb_interface."""
        virtual_interface = Interface.objects.create(
            device=self.aci_node_object1,
            name="vEth1",
            type=InterfaceTypeChoices.TYPE_VIRTUAL,
        )
        iface = ACINodeInterface(
            aci_node=self.aci_node, nb_interface=virtual_interface, module=1, port=6
        )
        with self.assertRaises(ValidationError) as cm:
            iface.full_clean()
        self.assertIn("nb_interface", cm.exception.error_dict)

    def test_invalid_aci_node_interface_module_min(self) -> None:
        """Test validation of ACI Node Interface module lower bound."""
        iface = ACINodeInterface(aci_node=self.aci_node, module=0, port=1)
        with self.assertRaises(ValidationError) as cm:
            iface.full_clean()
        self.assertIn("module", cm.exception.error_dict)

    def test_invalid_aci_node_interface_module_max(self) -> None:
        """Test validation of ACI Node Interface module upper bound."""
        iface = ACINodeInterface(aci_node=self.aci_node, module=256, port=1)
        with self.assertRaises(ValidationError) as cm:
            iface.full_clean()
        self.assertIn("module", cm.exception.error_dict)

    def test_invalid_aci_node_interface_port_min(self) -> None:
        """Test validation of ACI Node Interface port lower bound."""
        iface = ACINodeInterface(aci_node=self.aci_node, module=1, port=0)
        with self.assertRaises(ValidationError) as cm:
            iface.full_clean()
        self.assertIn("port", cm.exception.error_dict)

    def test_invalid_aci_node_interface_port_max(self) -> None:
        """Test validation of ACI Node Interface port upper bound."""
        iface = ACINodeInterface(aci_node=self.aci_node, module=1, port=128)
        with self.assertRaises(ValidationError) as cm:
            iface.full_clean()
        self.assertIn("port", cm.exception.error_dict)

    def test_invalid_aci_node_interface_sub_port_max(self) -> None:
        """Test validation of ACI Node Interface sub port upper bound."""
        iface = ACINodeInterface(aci_node=self.aci_node, module=1, port=1, sub_port=65)
        with self.assertRaises(ValidationError) as cm:
            iface.full_clean()
        self.assertIn("sub_port", cm.exception.error_dict)

    def test_constraint_unique_aci_node_interface_nb_interface(self) -> None:
        """Test unique constraint of ACI Node Interface nb_interface."""
        duplicate = ACINodeInterface(
            aci_node=self.aci_node, nb_interface=self.nb_interface1, module=1, port=7
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate.save()

    def test_aci_node_interface_protect_on_node_delete(self) -> None:
        """Test ACI Node deletion is blocked by a node interface."""
        with self.assertRaises(ProtectedError):
            self.aci_node.delete()

    def test_aci_node_interface_set_null_on_interface_delete(self) -> None:
        """Test nb_interface is cleared when the interface is deleted."""
        self.nb_interface1.delete()
        self.aci_node_interface.refresh_from_db()
        self.assertIsNone(self.aci_node_interface.nb_interface)

    def test_invalid_aci_node_interface_nb_interface_without_aci_node(self) -> None:
        """Test clean skips the device match when no ACI Node is set."""
        # A fresh interface, so the OneToOne uniqueness check cannot fire
        # and mask what this test is about
        free_interface = Interface.objects.create(
            device=self.aci_node_object1,
            name="eth1/99",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        node_interface = ACINodeInterface(
            nb_interface=free_interface,
            module=1,
            port=99,
            sub_port=0,
        )
        with self.assertRaises(ValidationError) as cm:
            node_interface.full_clean()
        # The missing ACI Node is the only real error. A device-mismatch
        # error would name a Node the user never selected
        self.assertIn("aci_node", cm.exception.error_dict)
        self.assertNotIn("nb_interface", cm.exception.error_dict)

    def test_aci_node_interface_to_objectchange(self) -> None:
        """Test to_objectchange sets the ACI Node as the related object."""
        objectchange = self.aci_node_interface.to_objectchange(
            ObjectChangeActionChoices.ACTION_UPDATE
        )
        self.assertEqual(objectchange.related_object, self.aci_node)

    def test_aci_node_interface_parent_object(self) -> None:
        """Test parent object of ACI Node Interface is the ACI Node."""
        self.assertEqual(self.aci_node_interface.parent_object, self.aci_node)

    def test_aci_node_interface_aci_fabric(self) -> None:
        """Test aci_fabric of ACI Node Interface is the ACI Node's fabric."""
        self.assertEqual(self.aci_node_interface.aci_fabric, self.aci_fabric)

    def test_default_ordering_queryset_evaluates(self) -> None:
        """Test that the default-ordered queryset evaluates without error."""
        self.assertIsNotNone(list(ACINodeInterface.objects.all()))
