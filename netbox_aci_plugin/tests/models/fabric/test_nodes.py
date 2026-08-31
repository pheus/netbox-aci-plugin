# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.test.utils import CaptureQueriesContext

from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, Interface, Location, Region, Site, SiteGroup
from ipam.models import IPAddress
from tenancy.models import Tenant
from virtualization.models import Cluster, ClusterType, VirtualMachine

from ....choices import NodeRoleChoices, NodeTypeChoices
from ....models.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlock,
    ACILeafSelector,
    ACILeafSwitchProfile,
)
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.node_interfaces import ACINodeInterface
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ....models.fabric.vpc_protection_groups import ACIVPCProtectionGroup
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

        # Read-only move targets and a paired partner for cls.aci_node.
        # The transition tests create their own Nodes instead.
        cls.aci_pod2 = ACIPod.objects.create(
            name="ACINodePod2",
            aci_fabric=cls.aci_fabric,
            pod_id=5,
        )
        cls.aci_fabric2 = ACIFabric.objects.create(
            name="ACINodeOtherFabric",
            fabric_id=cls.aci_fabric_id + 1,
            infra_vlan_vid=cls.aci_fabric_infra_vlan_vid + 1,
        )
        cls.aci_pod3 = ACIPod.objects.create(
            name="ACINodeOtherFabricPod",
            aci_fabric=cls.aci_fabric2,
            pod_id=1,
        )
        cls.aci_node_vpc_partner = ACINode.objects.create(
            name="ACINodeVPCPartner",
            aci_pod=cls.aci_pod,
            node_id=150,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.aci_vpc_group = ACIVPCProtectionGroup.objects.create(
            name="ACINodeVPCGroup",
            aci_fabric=cls.aci_fabric,
            logical_pair_id=1,
            aci_node_a=cls.aci_node,
            aci_node_b=cls.aci_node_vpc_partner,
        )

    def _create_paired_nodes(
        self, node_id_a: int, node_id_b: int
    ) -> tuple[ACINode, ACINode, ACIVPCProtectionGroup]:
        """Create and pair two fresh Leaf Nodes in a new VPC Protection Group.

        Always parented by self.aci_pod, so the transition tests can
        move or reconfigure the pair without touching shared fixtures.
        """
        node_a = ACINode.objects.create(
            name=f"ACINodeD23A{node_id_a}",
            aci_pod=self.aci_pod,
            node_id=node_id_a,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node_b = ACINode.objects.create(
            name=f"ACINodeD23B{node_id_b}",
            aci_pod=self.aci_pod,
            node_id=node_id_b,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        group = ACIVPCProtectionGroup.objects.create(
            name=f"ACINodeD23Group{node_id_a}",
            aci_fabric=self.aci_fabric,
            logical_pair_id=node_id_a,
            aci_node_a=node_a,
            aci_node_b=node_b,
        )
        return node_a, node_b, group

    def test_aci_node_instance(self) -> None:
        """Test type of created ACI Node."""
        self.assertTrue(isinstance(self.aci_node, ACINode))

    def test_aci_node_str(self) -> None:
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
        self.assertIn("__all__", cm.exception.error_dict)

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

    def test_aci_node_save_update_fields_atomic_tuple(self) -> None:
        """Test save expands a node object field to relation and caches."""
        cluster_type = ClusterType.objects.create(
            name="ACINodeAtomicClusterType", slug="acinodeatomicclustertype"
        )
        cluster = Cluster.objects.create(name="ACINodeAtomicCluster", type=cluster_type)
        vm_content_type = ContentType.objects.get_for_model(VirtualMachine)

        for offset, field_name in enumerate(
            ("node_object_id", "node_object_type", "node_object_type_id")
        ):
            with self.subTest(field_name=field_name):
                device = Device.objects.create(
                    name=f"ACINodeAtomicDevice{offset}",
                    device_type=self.device_type1,
                    role=self.device_role1,
                    site=self.site,
                )
                virtual_machine = VirtualMachine.objects.create(
                    name=f"ACINodeAtomicVM{offset}", cluster=cluster
                )
                node = ACINode.objects.create(
                    name=f"ACINodeAtomic{offset}",
                    aci_pod=self.aci_pod,
                    node_id=111 + offset,
                    role=NodeRoleChoices.ROLE_LEAF,
                    node_object=device,
                )

                node.node_object = virtual_machine
                node.save(update_fields={field_name})
                node.refresh_from_db()

                self.assertEqual(node.node_object_type_id, vm_content_type.pk)
                self.assertEqual(node.node_object_id, virtual_machine.pk)
                self.assertIsNone(node._device)  # noqa: SLF001
                self.assertEqual(
                    node._virtual_machine,  # noqa: SLF001
                    virtual_machine,
                )

    def test_aci_node_save_update_fields_unrelated_partial_inert(self) -> None:
        """Test an unrelated save leaves node object and caches unchanged."""
        device = Device.objects.create(
            name="ACINodeInertDevice",
            device_type=self.device_type1,
            role=self.device_role1,
            site=self.site,
        )
        cluster_type = ClusterType.objects.create(
            name="ACINodeInertClusterType", slug="acinodeinertclustertype"
        )
        cluster = Cluster.objects.create(name="ACINodeInertCluster", type=cluster_type)
        virtual_machine = VirtualMachine.objects.create(
            name="ACINodeInertVM", cluster=cluster
        )
        node = ACINode.objects.create(
            name="ACINodeInert",
            aci_pod=self.aci_pod,
            node_id=114,
            role=NodeRoleChoices.ROLE_LEAF,
            node_object=device,
        )

        node.node_object = virtual_machine
        node.name = "ACINodeInertRenamed"
        node.save(update_fields={"name"})
        node.refresh_from_db()

        self.assertEqual(node.name, "ACINodeInertRenamed")
        self.assertEqual(node.node_object, device)
        self.assertEqual(node._device, device)  # noqa: SLF001
        self.assertIsNone(node._virtual_machine)  # noqa: SLF001

    def test_aci_node_save_update_fields_empty_set_skipped(self) -> None:
        """Test an empty update_fields set skips the save."""
        device = Device.objects.create(
            name="ACINodeSkippedDevice",
            device_type=self.device_type1,
            role=self.device_role1,
            site=self.site,
        )
        node = ACINode.objects.create(
            name="ACINodeSkipped",
            aci_pod=self.aci_pod,
            node_id=115,
            role=NodeRoleChoices.ROLE_LEAF,
            node_object=device,
        )

        node.name = "ACINodeSkippedRenamed"
        with CaptureQueriesContext(connection) as queries:
            node.save(update_fields=set())
        node.refresh_from_db()

        # No write may reach the database, not even a no-op UPDATE
        self.assertFalse(
            [
                q
                for q in queries.captured_queries
                if q["sql"].lstrip().upper().startswith("UPDATE")
            ]
        )
        self.assertEqual(node.name, "ACINodeSkipped")

    def test_aci_node_save_full_persists_source_and_caches(self) -> None:
        """Test a full save persists node object and caches together."""
        device = Device.objects.create(
            name="ACINodeFullSaveDevice",
            device_type=self.device_type1,
            role=self.device_role1,
            site=self.site,
        )
        cluster_type = ClusterType.objects.create(
            name="ACINodeFullSaveClusterType", slug="acinodefullsaveclustertype"
        )
        cluster = Cluster.objects.create(
            name="ACINodeFullSaveCluster", type=cluster_type
        )
        virtual_machine = VirtualMachine.objects.create(
            name="ACINodeFullSaveVM", cluster=cluster
        )
        node = ACINode.objects.create(
            name="ACINodeFullSave",
            aci_pod=self.aci_pod,
            node_id=116,
            role=NodeRoleChoices.ROLE_LEAF,
            node_object=device,
        )

        node.node_object = virtual_machine
        node.save()
        node.refresh_from_db()

        self.assertEqual(node.node_object, virtual_machine)
        self.assertIsNone(node._device)  # noqa: SLF001
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

    def test_multiple_unassigned_node_objects_allowed(self) -> None:
        """Test that two ACI Nodes without a node_object both pass clean."""
        ACINode.objects.create(
            name="ACINodeUnassigned1",
            aci_pod=self.aci_pod,
            node_id=120,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node2 = ACINode(
            name="ACINodeUnassigned2",
            aci_pod=self.aci_pod,
            node_id=121,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        # Multiple unassigned nodes must not raise a uniqueness ValidationError
        node2.full_clean()

    # The fabric-scope cache and its fabric-wide uniqueness enforcement

    def test_aci_node_aci_fabric_cache_set_on_create(self) -> None:
        """Test _aci_fabric is cached on create without caller input."""
        node = ACINode.objects.create(
            name="ACINodeCacheOnCreate",
            aci_pod=self.aci_pod,
            node_id=160,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        self.assertEqual(node._aci_fabric_id, self.aci_pod.aci_fabric_id)  # noqa: SLF001

    def test_invalid_aci_node_duplicate_node_id_across_pods_same_fabric(
        self,
    ) -> None:
        """Test full_clean rejects a Node ID reused across two Pods."""
        node = ACINode(
            name="ACINodeDupCleanAcrossPods",
            aci_pod=self.aci_pod2,
            node_id=self.aci_node_id,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()
        self.assertIn("node_id", cm.exception.error_dict)

    def test_constraint_unique_aci_node_id_across_pods_same_fabric(self) -> None:
        """Test the DB constraint rejects a Node ID reused across Pods."""
        duplicate_node = ACINode(
            name="ACINodeDupDirectAcrossPods",
            aci_pod=self.aci_pod2,
            node_id=self.aci_node_id,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_node.save()

    def test_aci_node_same_node_id_different_fabric_accepted(self) -> None:
        """Test the same Node ID in a different ACI Fabric is accepted."""
        node = ACINode(
            name="ACINodeSameIdOtherFabric",
            aci_pod=self.aci_pod3,
            node_id=self.aci_node_id,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node.full_clean()
        node.save()

    def test_aci_node_save_update_fields_aci_pod_persists_fabric_cache(
        self,
    ) -> None:
        """Test save(update_fields={"aci_pod"}) also persists _aci_fabric."""
        node = ACINode.objects.create(
            name="ACINodeCachePersist",
            aci_pod=self.aci_pod,
            node_id=161,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node.aci_pod = self.aci_pod3
        node.save(update_fields={"aci_pod"})
        node.refresh_from_db()
        self.assertEqual(node.aci_pod, self.aci_pod3)
        self.assertEqual(node._aci_fabric_id, self.aci_pod3.aci_fabric_id)  # noqa: SLF001

    def test_aci_node_save_update_fields_aci_pod_id_persists_fabric_cache(
        self,
    ) -> None:
        """Test save(update_fields={"aci_pod_id"}) persists _aci_fabric."""
        node = ACINode.objects.create(
            name="ACINodeAttnameCache",
            aci_pod=self.aci_pod,
            node_id=171,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node.aci_pod = self.aci_pod3
        node.save(update_fields={"aci_pod_id"})
        node.refresh_from_db()
        self.assertEqual(node.aci_pod, self.aci_pod3)
        self.assertEqual(node._aci_fabric_id, self.aci_pod3.aci_fabric_id)  # noqa: SLF001

    def test_aci_node_save_update_fields_generator_persists_fabric_cache(
        self,
    ) -> None:
        """Test a single-use update_fields iterable persists _aci_fabric."""
        node = ACINode.objects.create(
            name="ACINodeGeneratorCache",
            aci_pod=self.aci_pod,
            node_id=170,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node.aci_pod = self.aci_pod3
        node.save(update_fields=(field for field in ("aci_pod",)))
        node.refresh_from_db()
        self.assertEqual(node.aci_pod, self.aci_pod3)
        self.assertEqual(node._aci_fabric_id, self.aci_pod3.aci_fabric_id)  # noqa: SLF001

    def test_aci_node_vpc_protection_group_as_node_a(self) -> None:
        """Test vpc_protection_group returns the group from the A side."""
        self.assertEqual(self.aci_node.vpc_protection_group, self.aci_vpc_group)

    def test_aci_node_vpc_protection_group_as_node_b(self) -> None:
        """Test vpc_protection_group returns the group from the B side."""
        self.assertEqual(
            self.aci_node_vpc_partner.vpc_protection_group, self.aci_vpc_group
        )

    def test_aci_node_vpc_protection_group_none_when_unpaired(self) -> None:
        """Test vpc_protection_group is None for a Node without a group."""
        node = ACINode.objects.create(
            name="ACINodeNoGroup",
            aci_pod=self.aci_pod,
            node_id=162,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        self.assertIsNone(node.vpc_protection_group)

    def test_aci_node_vpc_peer_node_from_node_a(self) -> None:
        """Test vpc_peer_node returns the B side when viewed from A."""
        self.assertEqual(self.aci_node.vpc_peer_node, self.aci_node_vpc_partner)

    def test_aci_node_vpc_peer_node_from_node_b(self) -> None:
        """Test vpc_peer_node returns the A side when viewed from B."""
        self.assertEqual(self.aci_node_vpc_partner.vpc_peer_node, self.aci_node)

    def test_aci_node_vpc_peer_node_none_when_unpaired(self) -> None:
        """Test vpc_peer_node is None for a Node without a group."""
        node = ACINode.objects.create(
            name="ACINodeNoGroupPeer",
            aci_pod=self.aci_pod,
            node_id=163,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        self.assertIsNone(node.vpc_peer_node)

    def test_aci_leaf_switch_profiles_empty_without_coverage(self) -> None:
        """Test aci_leaf_switch_profiles is empty for an uncovered Leaf."""
        self.assertFalse(self.aci_node.aci_leaf_switch_profiles.exists())

    def test_aci_leaf_switch_profiles_empty_for_non_leaf_role(self) -> None:
        """Test aci_leaf_switch_profiles is empty for an in-range Spine."""
        spine = ACINode.objects.create(
            name="ACINodeSwitchProfileSpine",
            aci_pod=self.aci_pod,
            node_id=180,
            role=NodeRoleChoices.ROLE_SPINE,
        )
        profile = ACILeafSwitchProfile.objects.create(
            name="ACINodeSwitchProfileForSpine", aci_fabric=self.aci_fabric
        )
        selector = ACILeafSelector.objects.create(
            name="ACINodeSwitchProfileSpineSelector",
            aci_leaf_switch_profile=profile,
        )
        ACILeafNodeBlock.objects.create(
            name="ACINodeSwitchProfileSpineBlock",
            aci_leaf_selector=selector,
            node_id_from=180,
            node_id_to=180,
        )
        self.assertFalse(spine.aci_leaf_switch_profiles.exists())

    def test_aci_leaf_switch_profiles_returns_covering_profile(self) -> None:
        """Test aci_leaf_switch_profiles returns the covering Profile."""
        leaf = ACINode.objects.create(
            name="ACINodeSwitchProfileLeaf",
            aci_pod=self.aci_pod,
            node_id=181,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        profile = ACILeafSwitchProfile.objects.create(
            name="ACINodeSwitchProfileSingle", aci_fabric=self.aci_fabric
        )
        selector = ACILeafSelector.objects.create(
            name="ACINodeSwitchProfileSingleSelector",
            aci_leaf_switch_profile=profile,
        )
        ACILeafNodeBlock.objects.create(
            name="ACINodeSwitchProfileSingleBlock",
            aci_leaf_selector=selector,
            node_id_from=181,
            node_id_to=181,
        )
        self.assertQuerySetEqual(leaf.aci_leaf_switch_profiles, [profile])

    def test_aci_leaf_switch_profiles_returns_every_covering_profile(self) -> None:
        """Test aci_leaf_switch_profiles lists every covering Profile.

        A Leaf legitimately sits in more than one Profile at once, for
        example a per-node profile and a per-VPC-pair profile, so this
        is a queryset rather than a single object.
        """
        leaf = ACINode.objects.create(
            name="ACINodeSwitchProfileMultiLeaf",
            aci_pod=self.aci_pod,
            node_id=182,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        profile1 = ACILeafSwitchProfile.objects.create(
            name="ACINodeSwitchProfileMulti1", aci_fabric=self.aci_fabric
        )
        selector1 = ACILeafSelector.objects.create(
            name="ACINodeSwitchProfileMultiSelector1",
            aci_leaf_switch_profile=profile1,
        )
        ACILeafNodeBlock.objects.create(
            name="ACINodeSwitchProfileMultiBlock1",
            aci_leaf_selector=selector1,
            node_id_from=182,
            node_id_to=182,
        )
        profile2 = ACILeafSwitchProfile.objects.create(
            name="ACINodeSwitchProfileMulti2", aci_fabric=self.aci_fabric
        )
        selector2 = ACILeafSelector.objects.create(
            name="ACINodeSwitchProfileMultiSelector2",
            aci_leaf_switch_profile=profile2,
        )
        ACILeafNodeBlock.objects.create(
            name="ACINodeSwitchProfileMultiBlock2",
            aci_leaf_selector=selector2,
            node_id_from=180,
            node_id_to=185,
        )
        self.assertCountEqual(leaf.aci_leaf_switch_profiles, [profile1, profile2])

    def test_aci_leaf_switch_profiles_excludes_other_fabrics(self) -> None:
        """Test aci_leaf_switch_profiles excludes another Fabric's Profile."""
        other_fabric = ACIFabric.objects.create(
            name="ACINodeSwitchProfileOtherFabric",
            fabric_id=200,
            infra_vlan_vid=3910,
        )
        other_pod = ACIPod.objects.create(
            name="ACINodeSwitchProfileOtherPod", aci_fabric=other_fabric, pod_id=1
        )
        other_leaf = ACINode.objects.create(
            name="ACINodeSwitchProfileOtherLeaf",
            aci_pod=other_pod,
            node_id=183,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        profile = ACILeafSwitchProfile.objects.create(
            name="ACINodeSwitchProfileOwnFabric", aci_fabric=self.aci_fabric
        )
        selector = ACILeafSelector.objects.create(
            name="ACINodeSwitchProfileOwnFabricSelector",
            aci_leaf_switch_profile=profile,
        )
        ACILeafNodeBlock.objects.create(
            name="ACINodeSwitchProfileOwnFabricBlock",
            aci_leaf_selector=selector,
            node_id_from=183,
            node_id_to=183,
        )
        self.assertFalse(other_leaf.aci_leaf_switch_profiles.exists())

    def test_aci_leaf_switch_profiles_query_count(self) -> None:
        """Test aci_leaf_switch_profiles resolves in a single query."""
        leaf = ACINode.objects.create(
            name="ACINodeSwitchProfileQueryCountLeaf",
            aci_pod=self.aci_pod,
            node_id=184,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        profile = ACILeafSwitchProfile.objects.create(
            name="ACINodeSwitchProfileQueryCount", aci_fabric=self.aci_fabric
        )
        selector = ACILeafSelector.objects.create(
            name="ACINodeSwitchProfileQueryCountSelector",
            aci_leaf_switch_profile=profile,
        )
        ACILeafNodeBlock.objects.create(
            name="ACINodeSwitchProfileQueryCountBlock",
            aci_leaf_selector=selector,
            node_id_from=184,
            node_id_to=184,
        )
        with CaptureQueriesContext(connection) as ctx:
            resolved = list(leaf.aci_leaf_switch_profiles)
        self.assertEqual(resolved, [profile])
        self.assertEqual(len(ctx.captured_queries), 1)

    def test_aci_node_vpc_protection_group_raises_on_double_membership(
        self,
    ) -> None:
        """Test vpc_protection_group raises loudly on a corrupt double pair."""
        node_x = ACINode.objects.create(
            name="ACINodeDoubleX",
            aci_pod=self.aci_pod,
            node_id=163,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node_y = ACINode.objects.create(
            name="ACINodeDoubleY",
            aci_pod=self.aci_pod,
            node_id=164,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node_z = ACINode.objects.create(
            name="ACINodeDoubleZ",
            aci_pod=self.aci_pod,
            node_id=165,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        # Bypass clean(): its membership-exclusivity guard would reject
        # this, but a direct ORM write can still create it.
        ACIVPCProtectionGroup.objects.create(
            name="ACINodeDoubleGroup1",
            aci_fabric=self.aci_fabric,
            logical_pair_id=163,
            aci_node_a=node_x,
            aci_node_b=node_y,
        )
        ACIVPCProtectionGroup.objects.create(
            name="ACINodeDoubleGroup2",
            aci_fabric=self.aci_fabric,
            logical_pair_id=164,
            aci_node_a=node_x,
            aci_node_b=node_z,
        )
        with self.assertRaises(ACIVPCProtectionGroup.MultipleObjectsReturned):
            _ = node_x.vpc_protection_group

    # The cache never needs priming by the caller, and no other field's
    # validation depends on it

    def test_aci_node_full_clean_without_priming_aci_fabric(self) -> None:
        """Test full_clean populates the fabric cache without caller input."""
        node = ACINode(
            name="ACINodeBootstrap",
            aci_pod=self.aci_pod,
            node_id=166,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node.full_clean()
        self.assertEqual(node._aci_fabric_id, self.aci_pod.aci_fabric_id)  # noqa: SLF001

    def test_invalid_aci_node_missing_aci_pod_error_not_on_aci_fabric(
        self,
    ) -> None:
        """Test a missing aci_pod is keyed to aci_pod, never to _aci_fabric."""
        node = ACINode(name="ACINodeNoPod", node_id=167, role=NodeRoleChoices.ROLE_LEAF)
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()
        self.assertIn("aci_pod", cm.exception.error_dict)
        self.assertNotIn("_aci_fabric", cm.exception.error_dict)

    def test_aci_node_save_update_fields_name_leaves_pod_and_fabric_unchanged(
        self,
    ) -> None:
        """Test a name-only save ignores an in-memory Pod mutation."""
        node = ACINode.objects.create(
            name="ACINodeNamePartial",
            aci_pod=self.aci_pod,
            node_id=168,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node.aci_pod = self.aci_pod3
        node.name = "ACINodeNamePartialRenamed"
        node.save(update_fields={"name"})
        node.refresh_from_db()
        self.assertEqual(node.name, "ACINodeNamePartialRenamed")
        self.assertEqual(node.aci_pod, self.aci_pod)
        self.assertEqual(node._aci_fabric_id, self.aci_pod.aci_fabric_id)  # noqa: SLF001

    def test_constraint_aci_node_aci_fabric_not_null(self) -> None:
        """Test the database rejects a Node row with no cached ACI Fabric."""
        node = ACINode(
            name="ACINodeNoFabricCache",
            aci_pod=self.aci_pod,
            node_id=169,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        # bulk_create bypasses save(), so cache_related_objects() never
        # runs and _aci_fabric_id reaches the database still unset.
        with self.assertRaises(IntegrityError), transaction.atomic():
            ACINode.objects.bulk_create([node])

    # A Node in a VPC Protection Group keeps its ACI Pod and stays a Leaf,
    # enforced in clean() field-keyed and in save() message-only

    def test_invalid_aci_node_paired_move_to_pod_same_fabric(self) -> None:
        """Test full_clean rejects a paired Node moving within its Fabric."""
        node_a, _node_b, _group = self._create_paired_nodes(200, 201)
        node_a.aci_pod = self.aci_pod2
        with self.assertRaises(ValidationError) as cm:
            node_a.full_clean()
        self.assertIn("aci_pod", cm.exception.error_dict)

    def test_invalid_aci_node_paired_move_to_pod_another_fabric(self) -> None:
        """Test full_clean rejects a paired Node moving to another Fabric."""
        node_a, _node_b, _group = self._create_paired_nodes(202, 203)
        node_a.aci_pod = self.aci_pod3
        with self.assertRaises(ValidationError) as cm:
            node_a.full_clean()
        self.assertIn("aci_pod", cm.exception.error_dict)

    def test_invalid_aci_node_paired_role_change_to_spine(self) -> None:
        """Test full_clean rejects a paired Node's role changing to Spine."""
        node_a, _node_b, _group = self._create_paired_nodes(204, 205)
        node_a.role = NodeRoleChoices.ROLE_SPINE
        with self.assertRaises(ValidationError) as cm:
            node_a.full_clean()
        self.assertIn("role", cm.exception.error_dict)

    def test_invalid_aci_node_paired_role_change_to_apic(self) -> None:
        """Test full_clean rejects a paired Node's role changing to APIC."""
        node_a, _node_b, _group = self._create_paired_nodes(206, 207)
        node_a.role = NodeRoleChoices.ROLE_APIC
        with self.assertRaises(ValidationError) as cm:
            node_a.full_clean()
        self.assertIn("role", cm.exception.error_dict)

    def test_aci_node_unpaired_moves_freely(self) -> None:
        """Test full_clean allows an unpaired Node to change Pod and role."""
        node = ACINode.objects.create(
            name="ACINodeUnpairedMove",
            aci_pod=self.aci_pod,
            node_id=208,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node.aci_pod = self.aci_pod2
        node.role = NodeRoleChoices.ROLE_SPINE
        node.full_clean()

    def test_aci_node_paired_move_allowed_after_group_removed(self) -> None:
        """Test full_clean allows a move once the protection group is gone."""
        node_a, _node_b, group = self._create_paired_nodes(209, 210)
        group.delete()
        node_a.aci_pod = self.aci_pod2
        node_a.full_clean()

    # A Node carrying ACI Node Interfaces keeps its Leaf role and its
    # assigned device, so neither change strands an existing interface

    def _create_node_with_interface(
        self, node_id: int, name: str, *, link_interface: bool = True
    ) -> tuple[ACINode, Device, ACINodeInterface]:
        """Return a Leaf Node, its device and one ACI Node Interface."""
        device = Device.objects.create(
            name=name,
            device_type=self.device_type1,
            role=self.device_role1,
            site=self.site,
        )
        node = ACINode.objects.create(
            name=name,
            aci_pod=self.aci_pod,
            node_id=node_id,
            role=NodeRoleChoices.ROLE_LEAF,
            node_object=device,
        )
        nb_interface = None
        if link_interface:
            nb_interface = Interface.objects.create(
                device=device,
                name="eth1/1",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            )
        interface = ACINodeInterface.objects.create(
            aci_node=node, nb_interface=nb_interface, port=1
        )
        return node, device, interface

    def test_invalid_aci_node_role_change_strands_node_interfaces(self) -> None:
        """Test clean rejects a role change while Node Interfaces exist."""
        node, _device, _interface = self._create_node_with_interface(
            211, "ACINodeRoleStrand"
        )
        node.role = NodeRoleChoices.ROLE_SPINE
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()
        self.assertIn("role", cm.exception.error_dict)

    def test_invalid_aci_node_object_cleared_strands_node_interfaces(self) -> None:
        """Test clean rejects clearing the Node Object of a linked port."""
        node, _device, _interface = self._create_node_with_interface(
            212, "ACINodeObjectCleared"
        )
        node.node_object = None
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()
        self.assertIn("node_object", cm.exception.error_dict)

    def test_invalid_aci_node_object_reassigned_strands_node_interfaces(self) -> None:
        """Test clean rejects repointing the Node Object of a linked port."""
        node, _device, _interface = self._create_node_with_interface(
            213, "ACINodeObjectMoved"
        )
        node.node_object = Device.objects.create(
            name="ACINodeObjectMovedTarget",
            device_type=self.device_type1,
            role=self.device_role1,
            site=self.site,
        )
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()
        self.assertIn("node_object", cm.exception.error_dict)

    def test_aci_node_object_cleared_without_linked_node_interfaces(self) -> None:
        """Test clearing the Node Object is allowed with no linked port.

        Pins the guard's `nb_interface__isnull=False` filter. Without it
        the cleared-device branch flags any ACI Node Interface at all,
        including one that never referenced a NetBox interface.
        """
        node, _device, _interface = self._create_node_with_interface(
            214, "ACINodeObjectClearedFree", link_interface=False
        )
        node.node_object = None
        node.full_clean()

    def test_aci_node_object_reassigned_to_the_matching_device(self) -> None:
        """Test a Node Object change to the port's own device is allowed.

        Pins the guard's `.exclude()` half. A bare `.exists()` would
        reject this, and the no-linked-port case above cannot tell the
        two apart.
        """
        node, device, _interface = self._create_node_with_interface(
            215, "ACINodeObjectSameDevice"
        )
        # Re-assigning the identical device is the smallest change that
        # still re-runs the guard against a populated interface set
        node.node_object = device
        node.full_clean()

    def test_aci_node_save_paired_aci_pod_change_rejected_message_only(
        self,
    ) -> None:
        """Test direct save rejects a paired Node Pod change, message-only."""
        node_a, _node_b, _group = self._create_paired_nodes(211, 212)
        node_a.aci_pod = self.aci_pod2
        with self.assertRaises(ValidationError) as cm:
            node_a.save()
        self.assertIn(
            "cannot be moved to another ACI Pod", " ".join(cm.exception.messages)
        )
        self.assertFalse(hasattr(cm.exception, "error_dict"))

    def test_aci_node_save_paired_aci_pod_id_change_rejected_message_only(
        self,
    ) -> None:
        """Test the attname spelling still triggers the paired-Node guard."""
        node_a, _node_b, _group = self._create_paired_nodes(225, 226)
        node_a.aci_pod = self.aci_pod2
        with self.assertRaises(ValidationError) as cm:
            node_a.save(update_fields={"aci_pod_id"})
        self.assertIn(
            "cannot be moved to another ACI Pod", " ".join(cm.exception.messages)
        )
        self.assertFalse(hasattr(cm.exception, "error_dict"))

    def test_aci_node_save_paired_role_change_rejected_message_only(
        self,
    ) -> None:
        """Test direct save rejects a paired Node role change, message-only."""
        node_a, _node_b, _group = self._create_paired_nodes(213, 214)
        node_a.role = NodeRoleChoices.ROLE_SPINE
        with self.assertRaises(ValidationError) as cm:
            node_a.save()
        self.assertIn("must retain the Leaf role", " ".join(cm.exception.messages))
        self.assertFalse(hasattr(cm.exception, "error_dict"))

    def test_aci_node_save_paired_unrelated_field_succeeds(self) -> None:
        """Test a scoped save touching neither Pod nor role still succeeds."""
        node_a, _node_b, _group = self._create_paired_nodes(215, 216)
        node_a.name = "ACINodeD23Renamed"
        node_a.save(update_fields={"name"})
        node_a.refresh_from_db()
        self.assertEqual(node_a.name, "ACINodeD23Renamed")

    def test_aci_node_save_role_only_ignores_unsaved_aci_pod(self) -> None:
        """Test a role-only save ignores an ACI Pod left dirty in memory."""
        node_a, _node_b, _group = self._create_paired_nodes(217, 218)
        node_a.aci_pod = self.aci_pod2

        node_a.save(update_fields={"role"})

        node_a.refresh_from_db()
        self.assertEqual(node_a.aci_pod, self.aci_pod)

    def test_aci_node_save_aci_pod_only_ignores_unsaved_role(self) -> None:
        """Test an ACI Pod save ignores a role left dirty in memory."""
        node_a, _node_b, _group = self._create_paired_nodes(219, 220)
        node_a.role = NodeRoleChoices.ROLE_SPINE

        node_a.save(update_fields={"aci_pod"})

        node_a.refresh_from_db()
        self.assertEqual(node_a.role, NodeRoleChoices.ROLE_LEAF)

    # The fabric cache follows the stored ACI Pod, never an unsaved change
    # to the Pod object in memory

    def test_aci_node_create_ignores_unsaved_aci_pod_fabric(self) -> None:
        """Test a new Node caches the Pod's stored ACI Fabric."""
        other_fabric = ACIFabric.objects.create(
            name="ACINodeDirtyPodFabric",
            fabric_id=self.aci_fabric_id + 31,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 31,
        )
        self.aci_pod.aci_fabric = other_fabric

        node = ACINode.objects.create(
            name="ACINodeDirtyPodCreate",
            aci_pod=self.aci_pod,
            node_id=222,
            role=NodeRoleChoices.ROLE_LEAF,
        )

        node.refresh_from_db()
        self.assertEqual(node._aci_fabric_id, self.aci_fabric.pk)  # noqa: SLF001

    def test_aci_node_save_ignores_unsaved_aci_pod_fabric(self) -> None:
        """Test a full save keeps the Pod's stored ACI Fabric cached."""
        node = ACINode.objects.create(
            name="ACINodeDirtyPodSave",
            aci_pod=self.aci_pod,
            node_id=223,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACINodeDirtyPodSaveFabric",
            fabric_id=self.aci_fabric_id + 32,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 32,
        )
        node.aci_pod.aci_fabric = other_fabric

        node.save()

        node.refresh_from_db()
        self.assertEqual(node._aci_fabric_id, self.aci_fabric.pk)  # noqa: SLF001

    def test_invalid_aci_node_duplicate_id_uses_stored_pod_fabric(self) -> None:
        """Test the duplicate Node ID check uses the Pod's stored Fabric."""
        ACINode.objects.create(
            name="ACINodeStoredFabricIncumbent",
            aci_pod=self.aci_pod,
            node_id=224,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACINodeStoredFabricOther",
            fabric_id=self.aci_fabric_id + 33,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 33,
        )
        # Pointing the Pod object at an empty Fabric must not excuse the
        # duplicate in the Fabric the Pod really belongs to
        self.aci_pod.aci_fabric = other_fabric

        duplicate = ACINode(
            name="ACINodeStoredFabricDuplicate",
            aci_pod=self.aci_pod,
            node_id=224,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        with self.assertRaises(ValidationError) as cm:
            duplicate.full_clean()

        self.assertIn("node_id", cm.exception.error_dict)

    def test_invalid_aci_node_unknown_aci_pod_stays_a_field_error(self) -> None:
        """Test an ACI Pod ID matching no row reports on the field."""
        unused_pod_pk = ACIPod.objects.order_by("-pk").first().pk + 1
        node = ACINode(
            name="ACINodeUnknownPod",
            aci_pod_id=unused_pod_pk,
            node_id=221,
            role=NodeRoleChoices.ROLE_LEAF,
        )

        with self.assertRaises(ValidationError) as cm:
            node.full_clean()

        self.assertIn("aci_pod", cm.exception.error_dict)
