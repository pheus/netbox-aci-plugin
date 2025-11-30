# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.models import Device, Site
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from ipam.models import IPAddress
from tenancy.models import Tenant

from ....choices import NodeRoleChoices, NodeTypeChoices
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ..base import ACIBaseTestCase


class ACINodeTestCase(ACIBaseTestCase):
    """Test case for ACINode model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACINode model."""
        super().setUpTestData()

        cls.aci_node_name = "ACITestNode"
        cls.aci_node_alias = "ACITestNodeAlias"
        cls.aci_node_description = "ACI Test Node for NetBox ACI Plugin"
        cls.aci_node_comments = """
        ACI Node for NetBox ACI Plugin testing.
        """
        cls.aci_node_id = 102
        cls.aci_node_role = NodeRoleChoices.ROLE_LEAF
        cls.aci_node_type = NodeTypeChoices.TYPE_UNKNOWN
        cls.aci_node_tep_ip_str = "10.0.0.2/24"

        # Create related objects
        cls.aci_node_tep_ip_address = IPAddress.objects.create(
            address=cls.aci_node_tep_ip_str
        )
        cls.aci_node_object = Device.objects.create(
            name=cls.aci_node_name,
            device_type=cls.device_type1,
            role=cls.device_role1,
            site=cls.site,
        )

        # Create objects
        cls.aci_node = ACINode.objects.create(
            name=cls.aci_node_name,
            name_alias=cls.aci_node_alias,
            description=cls.aci_node_description,
            aci_pod=cls.aci_pod,
            node_id=cls.aci_node_id,
            node_object=cls.aci_node_object,
            role=cls.aci_node_role,
            node_type=cls.aci_node_type,
            tep_ip_address=cls.aci_node_tep_ip_address,
            nb_tenant=cls.nb_tenant,
            comments=cls.aci_node_comments,
        )

    def test_aci_node_instance(self) -> None:
        """Test type of created ACI Node."""
        self.assertTrue(isinstance(self.aci_node, ACINode))

    def test_aci_node_str_return_value(self) -> None:
        """Test string value of created ACI Node."""
        self.assertEqual(self.aci_node.__str__(), self.aci_node.name)

    def test_aci_node_alias(self) -> None:
        """Test alias of ACI Node."""
        self.assertEqual(self.aci_node.name_alias, self.aci_node_alias)

    def test_aci_node_description(self) -> None:
        """Test description of ACI Node."""
        self.assertEqual(self.aci_node.description, self.aci_node_description)

    def test_aci_node_aci_pod_instance(self) -> None:
        """Test the ACI Fabric instance associated with ACI Node."""
        self.assertTrue(isinstance(self.aci_node.aci_pod, ACIPod))
        self.assertEqual(self.aci_node.aci_pod.name, self.aci_pod_name)

    def test_aci_node_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant associated with ACI Node."""
        self.assertTrue(isinstance(self.aci_node.nb_tenant, Tenant))
        self.assertEqual(self.aci_node.nb_tenant.name, self.nb_tenant_name)

    def test_aci_node_node_id(self) -> None:
        """Test node ID of ACI Node."""
        self.assertEqual(self.aci_node.node_id, self.aci_node_id)

    def test_aci_node_tep_ip_address(self) -> None:
        """Test the NetBox Prefix associated with ACI Node."""
        self.assertTrue(isinstance(self.aci_node.tep_ip_address, IPAddress))
        self.assertEqual(self.aci_node.tep_ip_address, self.aci_node_tep_ip_address)
        self.assertEqual(
            str(self.aci_node.tep_ip_address.address), self.aci_node_tep_ip_str
        )

    def test_aci_node_role(self) -> None:
        """Test 'role' choice of ACI Node."""
        self.assertEqual(self.aci_node.role, self.aci_node_role)

    def test_aci_node_get_role_color(self) -> None:
        """Test the 'get_role_color' method of ACI Node."""
        self.assertEqual(
            self.aci_node.get_role_color(),
            NodeRoleChoices.colors.get(self.aci_node_role),
        )

    def test_aci_node_node_type(self) -> None:
        """Test 'node_type' choice of ACI Node."""
        self.assertEqual(self.aci_node.node_type, self.aci_node_type)

    def test_aci_node_get_node_type_color(self) -> None:
        """Test the 'get_node_type_color' method of ACI Node."""
        self.assertEqual(
            self.aci_node.get_node_type_color(),
            NodeTypeChoices.colors.get(self.aci_node_type),
        )

    def test_invalid_aci_node_name(self) -> None:
        """Test validation of ACI Node naming."""
        node = ACINode(
            name="ACI Test Node 1",
            aci_pod=self.aci_pod,
            node_id=102,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()

        # Check the specific field that failed
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_node_name_length(self) -> None:
        """Test validation of ACI Node name length."""
        node = ACINode(
            name="T" * 65,  # Exceeding the maximum length of 64
            aci_pod=self.aci_pod,
            node_id=102,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()

        # Check the specific field that failed
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_node_name_alias(self) -> None:
        """Test validation of ACI node aliasing."""
        node = ACINode(
            name="ACINodeTest1",
            name_alias="Invalid Alias",
            aci_pod=self.aci_pod,
            node_id=102,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()

        # Check the specific field that failed
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_node_description(self) -> None:
        """Test validation of ACI Node description."""
        node = ACINode(
            name="ACITestNode1",
            description="Invalid Description: ö",
            aci_pod=self.aci_pod,
            node_id=102,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()

        # Check the specific field that failed
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_node_description_length(self) -> None:
        """Test validation of ACI Node description length."""
        node = ACINode(
            name="ACITestNode1",
            description="T" * 129,  # Exceeding the maximum length of 128
            aci_pod=self.aci_pod,
            node_id=102,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()

        # Check the specific field that failed
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_node_id(self) -> None:
        """Test validation of ACI Node ID value."""
        node = ACINode(
            name="ACITestNode1",
            aci_pod=self.aci_pod,
            node_id=5000,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()

        # Check the specific field that failed
        self.assertIn("node_id", cm.exception.error_dict)

    def test_invalid_aci_node_id_role_leaf(self) -> None:
        """Test validation of ACI Node ID value with role 'leaf'."""
        node = ACINode(
            name="ACITestNode1",
            aci_pod=self.aci_pod,
            node_id=1,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()

        # Check the specific field that failed
        self.assertIn("node_id", cm.exception.error_dict)

    def test_invalid_aci_node_id_role_apic(self) -> None:
        """Test validation of ACI Node ID value with role 'apic'."""
        node = ACINode(
            name="ACITestNode1",
            aci_pod=self.aci_pod,
            node_id=110,
            role=NodeRoleChoices.ROLE_APIC,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()

        # Check the specific field that failed
        self.assertIn("node_id", cm.exception.error_dict)

    def test_invalid_aci_node_object(self) -> None:
        """Test validation of the Node object with an invalid Site."""
        invalid_site = Site.objects.create(name="Invalid Site", slug="invalid-site")
        invalid_node_object = Device.objects.create(
            name="ACITestInvalidNode1",
            device_type=self.device_type1,
            role=self.device_role1,
            site=invalid_site,
        )
        node = ACINode(
            name="ACITestNode1",
            aci_pod=self.aci_pod,
            node_id=110,
            node_object=invalid_node_object,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()

        # Check the specific field that failed
        self.assertIn("node_object", cm.exception.error_dict)

    def test_invalid_aci_node_tep_ip_wrong_vrf(self) -> None:
        """Test validation of the ACI Node TEP IP address."""
        invalid_tep_ip_address = IPAddress(address="10.0.0.10/19", vrf=self.nb_vrf)
        invalid_tep_ip_address.full_clean()
        invalid_tep_ip_address.save()
        node = ACINode(
            name="ACITestNode1",
            aci_pod=self.aci_pod,
            node_id=110,
            tep_ip_address=invalid_tep_ip_address,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()

        # Check the specific field that failed
        self.assertIn("tep_ip_address", cm.exception.error_dict)

    def test_invalid_aci_node_tep_ip_wrong_subnet(self) -> None:
        """Test validation of the ACI Node TEP IP address."""
        invalid_tep_ip_address = IPAddress(address="192.168.0.1/24")
        invalid_tep_ip_address.full_clean()
        invalid_tep_ip_address.save()
        node = ACINode(
            name="ACITestNode1",
            aci_pod=self.aci_pod,
            node_id=110,
            tep_ip_address=invalid_tep_ip_address,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()

        # Check the specific field that failed
        self.assertIn("tep_ip_address", cm.exception.error_dict)

    def test_invalid_aci_node_tep_ip_wrong_prefix_length(self) -> None:
        """Test validation of the ACI Node TEP IP address."""
        invalid_tep_ip_address = IPAddress(address="10.0.0.10/24")
        invalid_tep_ip_address.full_clean()
        invalid_tep_ip_address.save()
        node = ACINode(
            name="ACITestNode1",
            aci_pod=self.aci_pod,
            node_id=110,
            tep_ip_address=invalid_tep_ip_address,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()

        # Check the specific field that failed
        self.assertIn("tep_ip_address", cm.exception.error_dict)

    def test_constraint_unique_aci_node_name(self) -> None:
        """Test unique constraint of ACI Node name."""
        duplicate_node = ACINode(
            name=self.aci_node_name,
            aci_pod=self.aci_pod,
            node_id=100,
        )
        with self.assertRaises(IntegrityError):
            duplicate_node.save()

    def test_constraint_unique_aci_node_id(self) -> None:
        """Test unique constraint of ACI Node ID."""
        duplicate_node = ACINode(
            name="ACITestNode1",
            aci_pod=self.aci_pod,
            node_id=self.aci_node_id,
        )
        with self.assertRaises(IntegrityError):
            duplicate_node.save()
