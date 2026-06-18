# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from dcim.models import Device, Location, Region, Site, SiteGroup
from ipam.models import IPAddress
from tenancy.models import Tenant
from virtualization.models import Cluster, ClusterType, VirtualMachine

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

    def test_aci_node_parent_object(self) -> None:
        """Test parent object of ACI Node is the ACI Pod."""
        self.assertEqual(self.aci_node.parent_object, self.aci_pod)

    def test_invalid_aci_node_object_type_without_object(self) -> None:
        """Test clean requires a node object when an object type is set."""
        node = ACINode(
            name="ACINodeTypeOnly",
            aci_pod=self.aci_pod,
            node_id=103,
            role=NodeRoleChoices.ROLE_LEAF,
            node_object_type=ContentType.objects.get_for_model(Device),
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()
        self.assertIn("node_object", cm.exception.error_dict)

    def test_invalid_aci_node_tep_ip_without_tep_pool(self) -> None:
        """Test clean rejects a TEP IP when the Pod has no TEP Pool."""
        pod_no_pool = ACIPod.objects.create(
            name="ACINodeNoPoolPod",
            aci_fabric=self.aci_fabric,
            pod_id=2,
        )
        node = ACINode(
            name="ACINodeNoPool",
            aci_pod=pod_no_pool,
            node_id=105,
            role=NodeRoleChoices.ROLE_LEAF,
            tep_ip_address=self.aci_node_tep_ip_address,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()
        self.assertIn("tep_ip_address", cm.exception.error_dict)

    def test_invalid_aci_node_object_already_assigned(self) -> None:
        """Test clean rejects a node object already assigned to a node."""
        node = ACINode(
            name="ACINodeDuplicateObject",
            aci_pod=self.aci_pod,
            node_id=106,
            role=NodeRoleChoices.ROLE_LEAF,
            node_object=self.aci_node_object,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()
        self.assertIn("node_object", cm.exception.error_dict)

    def test_aci_node_cache_related_objects_virtual_machine(self) -> None:
        """Test cache_related_objects handles a virtual machine object."""
        cluster_type = ClusterType.objects.create(
            name="ACINodeClusterType", slug="acinodeclustertype"
        )
        cluster = Cluster.objects.create(name="ACINodeCluster", type=cluster_type)
        virtual_machine = VirtualMachine.objects.create(
            name="ACINodeVM", cluster=cluster
        )
        node = ACINode(
            name="ACINodeVMNode",
            aci_pod=self.aci_pod,
            node_id=107,
            role=NodeRoleChoices.ROLE_LEAF,
            node_object=virtual_machine,
        )
        node.save()
        self.assertEqual(node._virtual_machine, virtual_machine)  # noqa: SLF001

    def test_aci_node_object_scope_with_region_group_location(self) -> None:
        """Test node-object scope validation accepts a matching site."""
        region = Region.objects.create(name="ACINodeRegion", slug="acinoderegion")
        site_group = SiteGroup.objects.create(
            name="ACINodeSiteGroup", slug="acinodesitegroup"
        )
        scoped_site = Site.objects.create(
            name="ACINodeScopedSite",
            slug="acinodescopedsite",
            region=region,
            group=site_group,
        )
        location = Location.objects.create(
            name="ACINodeLocation", slug="acinodelocation", site=scoped_site
        )
        device = Device.objects.create(
            name="ACINodeScopedDevice",
            device_type=self.device_type1,
            role=self.device_role1,
            site=scoped_site,
            location=location,
        )
        pod = ACIPod.objects.create(
            name="ACINodeScopePod",
            aci_fabric=self.aci_fabric,
            pod_id=3,
            scope=scoped_site,
        )
        node = ACINode(
            name="ACINodeScoped",
            aci_pod=pod,
            node_id=108,
            role=NodeRoleChoices.ROLE_LEAF,
            node_object=device,
        )
        node.full_clean()
        self.assertEqual(node.node_object, device)

    def test_invalid_aci_node_object_scope_region_mismatch(self) -> None:
        """Test node-object scope mismatch against a Region-scoped Pod."""
        region = Region.objects.create(name="ACINodePodRegion", slug="acinodepodregion")
        pod = ACIPod.objects.create(
            name="ACINodeRegionPod",
            aci_fabric=self.aci_fabric,
            pod_id=4,
            scope=region,
        )
        device = Device.objects.create(
            name="ACINodeRegionDevice",
            device_type=self.device_type1,
            role=self.device_role1,
            site=self.site,
        )
        node = ACINode(
            name="ACINodeRegionMismatch",
            aci_pod=pod,
            node_id=109,
            role=NodeRoleChoices.ROLE_LEAF,
            node_object=device,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()
        self.assertIn("node_object", cm.exception.error_dict)

    def test_constraint_unique_aci_node_name(self) -> None:
        """Test unique constraint of ACI Node name."""
        duplicate_node = ACINode(
            name=self.aci_node_name,
            aci_pod=self.aci_pod,
            node_id=100,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_node.save()

    def test_constraint_unique_aci_node_id(self) -> None:
        """Test unique constraint of ACI Node ID."""
        duplicate_node = ACINode(
            name="ACITestNode1",
            aci_pod=self.aci_pod,
            node_id=self.aci_node_id,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_node.save()
