# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from dcim.models import Region, Site, SiteGroup
from ipam.models import Prefix
from tenancy.models import Tenant

from ....choices import NodeRoleChoices
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ....models.fabric.vpc_protection_groups import ACIVPCProtectionGroup
from ..base import ACIBaseTestCase


class ACIPodTestCase(ACIBaseTestCase):
    """Test case for ACIPod model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACIPod model."""
        super().setUpTestData()

        cls.aci_pod_name = "ACITestPod"
        cls.aci_pod_alias = "ACITestPodAlias"
        cls.aci_pod_description = "ACI Test Pod for NetBox ACI Plugin"
        cls.aci_pod_comments = """
        ACI Pod for NetBox ACI Plugin testing.
        """
        cls.aci_pod_id = 10
        cls.aci_pod_tep_pool_prefix = "10.32.0.0/19"

        # Create related objects
        cls.aci_pod_tep_pool = Prefix(prefix=cls.aci_pod_tep_pool_prefix)
        cls.aci_pod_tep_pool.full_clean()
        cls.aci_pod_tep_pool.save()

        # Create objects
        cls.aci_pod = ACIPod.objects.create(
            name=cls.aci_pod_name,
            name_alias=cls.aci_pod_alias,
            description=cls.aci_pod_description,
            pod_id=cls.aci_pod_id,
            aci_fabric=cls.aci_fabric,
            tep_pool=cls.aci_pod_tep_pool,
            nb_tenant=cls.nb_tenant,
            comments=cls.aci_pod_comments,
        )

    def test_aci_pod_instance(self) -> None:
        """Test type of created ACI Pod."""
        self.assertTrue(isinstance(self.aci_pod, ACIPod))

    def test_aci_pod_str(self) -> None:
        """Test string value of created ACI Pod."""
        self.assertEqual(self.aci_pod.__str__(), self.aci_pod.name)

    def test_aci_pod_alias(self) -> None:
        """Test alias of ACI Pod."""
        self.assertEqual(self.aci_pod.name_alias, self.aci_pod_alias)

    def test_aci_pod_description(self) -> None:
        """Test description of ACI Pod."""
        self.assertEqual(self.aci_pod.description, self.aci_pod_description)

    def test_aci_pod_aci_fabric_instance(self) -> None:
        """Test the ACI Fabric instance associated with ACI Pod."""
        self.assertTrue(isinstance(self.aci_pod.aci_fabric, ACIFabric))
        self.assertEqual(self.aci_pod.aci_fabric.name, self.aci_fabric_name)

    def test_aci_pod_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant associated with ACI Pod."""
        self.assertTrue(isinstance(self.aci_pod.nb_tenant, Tenant))
        self.assertEqual(self.aci_pod.nb_tenant.name, self.nb_tenant_name)

    def test_aci_pod_pod_id(self) -> None:
        """Test pod ID of ACI Pod."""
        self.assertEqual(self.aci_pod.pod_id, self.aci_pod_id)

    def test_aci_pod_tep_pool(self) -> None:
        """Test the NetBox Prefix associated with ACI Pod."""
        self.assertTrue(isinstance(self.aci_pod.tep_pool, Prefix))
        self.assertEqual(self.aci_pod.tep_pool, self.aci_pod_tep_pool)
        self.assertEqual(
            str(self.aci_pod.tep_pool.prefix), self.aci_pod_tep_pool_prefix
        )

    def test_aci_pod_parent_object(self) -> None:
        """Test parent object of ACI Pod is the ACI Fabric."""
        self.assertEqual(self.aci_pod.parent_object, self.aci_fabric)

    def test_aci_pod_scope_ancestor_deletion(self) -> None:
        """Test ACI Pod survives deletion of a scope ancestor."""
        region = Region.objects.create(name="ACI-Test-Region", slug="aci-test-region")
        site_group = SiteGroup.objects.create(
            name="ACI-Test-SiteGroup", slug="aci-test-sitegroup"
        )
        site = Site.objects.create(
            name="ACI-Test-Site",
            slug="aci-test-site",
            region=region,
            group=site_group,
        )
        aci_pod = ACIPod.objects.create(
            name="ACITestPodScoped",
            pod_id=2,
            aci_fabric=self.aci_fabric,
            scope=site,
        )
        self.assertEqual(aci_pod._region, region)  # noqa: SLF001
        self.assertEqual(aci_pod._site_group, site_group)  # noqa: SLF001

        region.delete()
        site_group.delete()

        aci_pod.refresh_from_db()
        self.assertIsNone(aci_pod._region)  # noqa: SLF001
        self.assertIsNone(aci_pod._site_group)  # noqa: SLF001
        self.assertEqual(aci_pod._site, site)  # noqa: SLF001

    def test_invalid_aci_pod_name(self) -> None:
        """Test validation of ACI Pod naming."""
        pod = ACIPod(
            name="ACI Test Pod 1",
            aci_fabric=self.aci_fabric,
            pod_id=20,
        )
        with self.assertRaises(ValidationError) as cm:
            pod.full_clean()

        # Check the specific field that failed
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_pod_name_length(self) -> None:
        """Test validation of ACI Pod name length."""
        pod = ACIPod(
            name="T" * 65,  # Exceeding the maximum length of 64
            aci_fabric=self.aci_fabric,
            pod_id=20,
        )
        with self.assertRaises(ValidationError) as cm:
            pod.full_clean()

        # Check the specific field that failed
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_pod_name_alias(self) -> None:
        """Test validation of ACI pod aliasing."""
        pod = ACIPod(
            name="ACIPodTest1",
            name_alias="Invalid Alias",
            aci_fabric=self.aci_fabric,
            pod_id=20,
        )
        with self.assertRaises(ValidationError) as cm:
            pod.full_clean()

        # Check the specific field that failed
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_pod_description(self) -> None:
        """Test validation of ACI Pod description."""
        pod = ACIPod(
            name="ACITestPod1",
            description="Invalid Description: ö",
            aci_fabric=self.aci_fabric,
            pod_id=20,
        )
        with self.assertRaises(ValidationError) as cm:
            pod.full_clean()

        # Check the specific field that failed
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_pod_description_length(self) -> None:
        """Test validation of ACI Pod description length."""
        pod = ACIPod(
            name="ACITestPod1",
            description="T" * 129,  # Exceeding the maximum length of 128
            aci_fabric=self.aci_fabric,
            pod_id=20,
        )
        with self.assertRaises(ValidationError) as cm:
            pod.full_clean()

        # Check the specific field that failed
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_pod_id(self) -> None:
        """Test validation of ACI Pod ID value."""
        pod = ACIPod(
            name="ACITestPod1",
            aci_fabric=self.aci_fabric,
            pod_id=5000,
        )
        with self.assertRaises(ValidationError) as cm:
            pod.full_clean()

        # Check the specific field that failed
        self.assertIn("pod_id", cm.exception.error_dict)

    def test_invalid_aci_pod_tep_pool(self) -> None:
        """Test validation of the ACI Pod TEP pool prefix."""
        invalid_tep_pool = Prefix(prefix="10.0.0.0/27")
        invalid_tep_pool.full_clean()
        invalid_tep_pool.save()
        pod = ACIPod(
            name="ACITestPod1",
            aci_fabric=self.aci_fabric,
            pod_id=20,
            tep_pool=invalid_tep_pool,
        )
        with self.assertRaises(ValidationError) as cm:
            pod.full_clean()

        # Check the specific field that failed
        self.assertIn("tep_pool", cm.exception.error_dict)

    def test_constraint_unique_aci_pod_name(self) -> None:
        """Test unique constraint of ACI Pod name."""
        duplicate_pod = ACIPod(
            name=self.aci_pod_name,
            aci_fabric=self.aci_fabric,
            pod_id=100,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_pod.save()

    def test_constraint_unique_aci_pod_id(self) -> None:
        """Test unique constraint of ACI Pod ID."""
        duplicate_pod = ACIPod(
            name="ACITestPod1",
            aci_fabric=self.aci_fabric,
            pod_id=self.aci_pod_id,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_pod.save()

    # A Fabric move cascades to every child Node's cache, and is refused
    # on a conflict in the target Fabric

    def test_invalid_aci_pod_fabric_move_node_id_conflict(self) -> None:
        """Test full_clean rejects a move that collides on a Node ID."""
        ACINode.objects.create(
            name="ACIPodMoveConflictChild",
            aci_pod=self.aci_pod,
            node_id=313,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACIPodMoveConflictFabric",
            fabric_id=self.aci_fabric_id + 20,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 20,
        )
        other_pod = ACIPod.objects.create(
            name="ACIPodMoveConflictOtherPod", aci_fabric=other_fabric, pod_id=1
        )
        ACINode.objects.create(
            name="ACIPodMoveConflictOtherNode",
            aci_pod=other_pod,
            node_id=313,
            role=NodeRoleChoices.ROLE_LEAF,
        )

        self.aci_pod.aci_fabric = other_fabric
        with self.assertRaises(ValidationError) as cm:
            self.aci_pod.full_clean()
        self.assertIn("aci_fabric", cm.exception.error_dict)

    def test_aci_pod_save_node_id_conflict_rejected_message_only(self) -> None:
        """Test direct save rejects a Node ID conflict, message-only."""
        ACINode.objects.create(
            name="ACIPodSaveConflictChild",
            aci_pod=self.aci_pod,
            node_id=318,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACIPodSaveConflictFabric",
            fabric_id=self.aci_fabric_id + 22,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 22,
        )
        other_pod = ACIPod.objects.create(
            name="ACIPodSaveConflictOtherPod", aci_fabric=other_fabric, pod_id=1
        )
        ACINode.objects.create(
            name="ACIPodSaveConflictOtherNode",
            aci_pod=other_pod,
            node_id=318,
            role=NodeRoleChoices.ROLE_LEAF,
        )

        self.aci_pod.aci_fabric = other_fabric
        with self.assertRaises(ValidationError) as cm:
            self.aci_pod.save()
        self.assertIn("already has ACI Nodes using", " ".join(cm.exception.messages))
        self.assertFalse(hasattr(cm.exception, "error_dict"))

    def test_aci_pod_fabric_move_updates_child_node_caches(self) -> None:
        """Test a successful move updates every child Node's cache."""
        node_1 = ACINode.objects.create(
            name="ACIPodMoveCacheNode1",
            aci_pod=self.aci_pod,
            node_id=314,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node_2 = ACINode.objects.create(
            name="ACIPodMoveCacheNode2",
            aci_pod=self.aci_pod,
            node_id=315,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACIPodMoveCacheFabric",
            fabric_id=self.aci_fabric_id + 21,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 21,
        )

        self.aci_pod.aci_fabric = other_fabric
        self.aci_pod.save()

        node_1.refresh_from_db()
        node_2.refresh_from_db()
        self.assertEqual(node_1._aci_fabric_id, other_fabric.pk)  # noqa: SLF001
        self.assertEqual(node_2._aci_fabric_id, other_fabric.pk)  # noqa: SLF001

    def test_constraint_aci_pod_fabric_move_direct_save_rolls_back(self) -> None:
        """Test a DB-level move conflict rolls back the Pod and Node caches."""
        child_node = ACINode.objects.create(
            name="ACIPodRollbackChild",
            aci_pod=self.aci_pod,
            node_id=300,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACIPodConflictFabric",
            fabric_id=self.aci_fabric_id + 10,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 10,
        )
        # The pre-check does not look at pod_id, so the Pod's own
        # (aci_fabric, pod_id) constraint is the backstop here
        ACIPod.objects.create(
            name="ACIPodConflictOther", aci_fabric=other_fabric, pod_id=self.aci_pod_id
        )

        self.aci_pod.aci_fabric = other_fabric
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.aci_pod.save()

        self.aci_pod.refresh_from_db()
        child_node.refresh_from_db()
        self.assertEqual(self.aci_pod.aci_fabric, self.aci_fabric)
        self.assertEqual(child_node._aci_fabric_id, self.aci_fabric.pk)  # noqa: SLF001

    def test_aci_pod_clean_tolerates_a_missing_stored_row(self) -> None:
        """Test clean degrades to no pending move when the row is gone."""
        other_fabric = ACIFabric.objects.create(
            name="ACIPodMissingRowFabric",
            fabric_id=self.aci_fabric_id + 21,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 21,
        )
        # A pk that was never persisted, as a hand-built instance or a
        # concurrent delete would produce. Resolving the move must not
        # raise DoesNotExist out of a routine edit
        orphan = ACIPod(
            pk=999999,
            name="ACIPodOrphan",
            aci_fabric=other_fabric,
            pod_id=99,
        )
        orphan.clean()

    def test_aci_pod_save_update_fields_name_no_cascade(self) -> None:
        """Test a name-only save does not cascade an in-memory Fabric edit."""
        child_node = ACINode.objects.create(
            name="ACIPodNameOnlyChild",
            aci_pod=self.aci_pod,
            node_id=301,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACIPodNameOnlyFabric",
            fabric_id=self.aci_fabric_id + 11,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 11,
        )

        self.aci_pod.aci_fabric = other_fabric
        self.aci_pod.name = "ACIPodRenamedOnly"
        self.aci_pod.save(update_fields={"name"})
        self.aci_pod.refresh_from_db()
        child_node.refresh_from_db()
        self.assertEqual(self.aci_pod.name, "ACIPodRenamedOnly")
        self.assertEqual(self.aci_pod.aci_fabric, self.aci_fabric)
        self.assertEqual(child_node._aci_fabric_id, self.aci_fabric.pk)  # noqa: SLF001

    def test_aci_pod_save_update_fields_aci_fabric_runs_cascade(self) -> None:
        """Test save(update_fields={"aci_fabric"}) runs the move cascade."""
        child_node = ACINode.objects.create(
            name="ACIPodFieldNameChild",
            aci_pod=self.aci_pod,
            node_id=302,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACIPodFieldNameFabric",
            fabric_id=self.aci_fabric_id + 12,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 12,
        )

        self.aci_pod.aci_fabric = other_fabric
        self.aci_pod.save(update_fields={"aci_fabric"})

        child_node.refresh_from_db()
        self.assertEqual(child_node._aci_fabric_id, other_fabric.pk)  # noqa: SLF001

    def test_aci_pod_save_update_fields_aci_fabric_id_runs_cascade(self) -> None:
        """Test save(update_fields={"aci_fabric_id"}) also cascades."""
        child_node = ACINode.objects.create(
            name="ACIPodFieldIdChild",
            aci_pod=self.aci_pod,
            node_id=303,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACIPodFieldIdFabric",
            fabric_id=self.aci_fabric_id + 13,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 13,
        )

        self.aci_pod.aci_fabric = other_fabric
        self.aci_pod.save(update_fields={"aci_fabric_id"})

        child_node.refresh_from_db()
        self.assertEqual(child_node._aci_fabric_id, other_fabric.pk)  # noqa: SLF001

    def test_aci_pod_save_update_fields_generator_runs_cascade(self) -> None:
        """Test a single-use update_fields iterable still cascades a move."""
        node_a = ACINode.objects.create(
            name="ACIPodGeneratorNodeA",
            aci_pod=self.aci_pod,
            node_id=330,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node_b = ACINode.objects.create(
            name="ACIPodGeneratorNodeB",
            aci_pod=self.aci_pod,
            node_id=331,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        group = ACIVPCProtectionGroup.objects.create(
            name="ACIPodGeneratorGroup",
            aci_fabric=self.aci_fabric,
            logical_pair_id=70,
            aci_node_a=node_a,
            aci_node_b=node_b,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACIPodGeneratorFabric",
            fabric_id=self.aci_fabric_id + 30,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 30,
        )

        self.aci_pod.aci_fabric = other_fabric
        self.aci_pod.save(update_fields=(field for field in ("aci_fabric",)))

        self.aci_pod.refresh_from_db()
        node_a.refresh_from_db()
        group.refresh_from_db()
        self.assertEqual(self.aci_pod.aci_fabric, other_fabric)
        self.assertEqual(node_a._aci_fabric_id, other_fabric.pk)  # noqa: SLF001
        self.assertEqual(group.aci_fabric, other_fabric)

    def test_aci_pod_save_update_fields_empty_generator_skipped(self) -> None:
        """Test an empty update_fields iterable skips the save."""
        original_name = self.aci_pod.name
        self.aci_pod.name = "ACIPodNeverPersisted"
        self.aci_pod.save(update_fields=(field for field in ()))

        self.aci_pod.refresh_from_db()
        self.assertEqual(self.aci_pod.name, original_name)

    # The move also carries the Pod's VPC Protection Groups, is refused on
    # a conflict there, and rolls everything back together on failure

    def test_aci_pod_fabric_move_rewrites_protection_group_fabric(self) -> None:
        """Test a successful move rewrites the Pod's protection groups too."""
        node_a = ACINode.objects.create(
            name="ACIPodGroupNodeA",
            aci_pod=self.aci_pod,
            node_id=304,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node_b = ACINode.objects.create(
            name="ACIPodGroupNodeB",
            aci_pod=self.aci_pod,
            node_id=305,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        group = ACIVPCProtectionGroup.objects.create(
            name="ACIPodMoveGroup",
            aci_fabric=self.aci_fabric,
            logical_pair_id=50,
            aci_node_a=node_a,
            aci_node_b=node_b,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACIPodGroupMoveFabric",
            fabric_id=self.aci_fabric_id + 14,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 14,
        )

        self.aci_pod.aci_fabric = other_fabric
        self.aci_pod.save()

        group.refresh_from_db()
        self.assertEqual(group.aci_fabric, other_fabric)

    def test_invalid_aci_pod_fabric_move_group_name_conflict(self) -> None:
        """Test full_clean rejects a move colliding on a group name."""
        node_a = ACINode.objects.create(
            name="ACIPodNameConflictA",
            aci_pod=self.aci_pod,
            node_id=306,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node_b = ACINode.objects.create(
            name="ACIPodNameConflictB",
            aci_pod=self.aci_pod,
            node_id=307,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        ACIVPCProtectionGroup.objects.create(
            name="ACIPodConflictGroupName",
            aci_fabric=self.aci_fabric,
            logical_pair_id=51,
            aci_node_a=node_a,
            aci_node_b=node_b,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACIPodGroupNameConflictFabric",
            fabric_id=self.aci_fabric_id + 15,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 15,
        )
        other_pod = ACIPod.objects.create(
            name="ACIPodGroupNameConflictOtherPod", aci_fabric=other_fabric, pod_id=1
        )
        other_node_a = ACINode.objects.create(
            name="ACIPodNameConflictOtherA",
            aci_pod=other_pod,
            node_id=401,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        other_node_b = ACINode.objects.create(
            name="ACIPodNameConflictOtherB",
            aci_pod=other_pod,
            node_id=402,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        ACIVPCProtectionGroup.objects.create(
            name="ACIPodConflictGroupName",  # same name, different Fabric
            aci_fabric=other_fabric,
            logical_pair_id=999,
            aci_node_a=other_node_a,
            aci_node_b=other_node_b,
        )

        self.aci_pod.aci_fabric = other_fabric
        with self.assertRaises(ValidationError) as cm:
            self.aci_pod.full_clean()
        self.assertIn("aci_fabric", cm.exception.error_dict)

    def test_invalid_aci_pod_fabric_move_group_pair_id_conflict(self) -> None:
        """Test full_clean rejects a move colliding on a group pair ID."""
        node_a = ACINode.objects.create(
            name="ACIPodPairIdConflictA",
            aci_pod=self.aci_pod,
            node_id=316,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node_b = ACINode.objects.create(
            name="ACIPodPairIdConflictB",
            aci_pod=self.aci_pod,
            node_id=317,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        ACIVPCProtectionGroup.objects.create(
            name="ACIPodPairIdConflictGroup",
            aci_fabric=self.aci_fabric,
            logical_pair_id=60,
            aci_node_a=node_a,
            aci_node_b=node_b,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACIPodPairIdConflictFabric",
            fabric_id=self.aci_fabric_id + 16,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 16,
        )
        other_pod = ACIPod.objects.create(
            name="ACIPodPairIdConflictOtherPod", aci_fabric=other_fabric, pod_id=1
        )
        other_node_a = ACINode.objects.create(
            name="ACIPodPairIdConflictOtherA",
            aci_pod=other_pod,
            node_id=403,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        other_node_b = ACINode.objects.create(
            name="ACIPodPairIdConflictOtherB",
            aci_pod=other_pod,
            node_id=404,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        ACIVPCProtectionGroup.objects.create(
            name="ACIPodPairIdConflictOtherGroupName",  # different name
            aci_fabric=other_fabric,
            logical_pair_id=60,  # same pair ID
            aci_node_a=other_node_a,
            aci_node_b=other_node_b,
        )

        self.aci_pod.aci_fabric = other_fabric
        with self.assertRaises(ValidationError) as cm:
            self.aci_pod.full_clean()
        self.assertIn("aci_fabric", cm.exception.error_dict)

    def test_aci_pod_fabric_move_failed_cascade_rolls_back_everything(
        self,
    ) -> None:
        """Test a failed cascade rolls back the Pod, caches and groups."""
        node_a = ACINode.objects.create(
            name="ACIPodCascadeRollbackA",
            aci_pod=self.aci_pod,
            node_id=308,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node_b = ACINode.objects.create(
            name="ACIPodCascadeRollbackB",
            aci_pod=self.aci_pod,
            node_id=309,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        group = ACIVPCProtectionGroup.objects.create(
            name="ACIPodCascadeRollbackGroup",
            aci_fabric=self.aci_fabric,
            logical_pair_id=52,
            aci_node_a=node_a,
            aci_node_b=node_b,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACIPodCascadeRollbackFabric",
            fabric_id=self.aci_fabric_id + 17,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 17,
        )
        ACIPod.objects.create(
            name="ACIPodCascadeRollbackOtherPod",
            aci_fabric=other_fabric,
            pod_id=self.aci_pod_id,
        )

        self.aci_pod.aci_fabric = other_fabric
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.aci_pod.save()

        self.aci_pod.refresh_from_db()
        node_a.refresh_from_db()
        node_b.refresh_from_db()
        group.refresh_from_db()
        self.assertEqual(self.aci_pod.aci_fabric, self.aci_fabric)
        self.assertEqual(node_a._aci_fabric_id, self.aci_fabric.pk)  # noqa: SLF001
        self.assertEqual(node_b._aci_fabric_id, self.aci_fabric.pk)  # noqa: SLF001
        self.assertEqual(group.aci_fabric, self.aci_fabric)

    def test_aci_pod_save_unrelated_field_no_cascade(self) -> None:
        """Test a save with no Fabric change performs no cascade at all."""
        child_node = ACINode.objects.create(
            name="ACIPodUnrelatedChild",
            aci_pod=self.aci_pod,
            node_id=310,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        original_fabric_cache = child_node._aci_fabric_id  # noqa: SLF001

        self.aci_pod.comments = "Updated comments only."
        self.aci_pod.save()

        child_node.refresh_from_db()
        self.assertEqual(child_node._aci_fabric_id, original_fabric_cache)  # noqa: SLF001

    def test_invalid_aci_pod_fabric_move_straddling_group_conflict(self) -> None:
        """Test full_clean rejects a move when a group straddles two Pods."""
        other_pod_same_fabric = ACIPod.objects.create(
            name="ACIPodStraddleOtherPod", aci_fabric=self.aci_fabric, pod_id=20
        )
        node_a = ACINode.objects.create(
            name="ACIPodStraddleNodeA",
            aci_pod=self.aci_pod,
            node_id=311,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node_b = ACINode.objects.create(
            name="ACIPodStraddleNodeB",
            aci_pod=other_pod_same_fabric,
            node_id=312,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        # Validation keeps a group's members in one Pod, but a direct
        # create() can still straddle two
        group = ACIVPCProtectionGroup.objects.create(
            name="ACIPodStraddleGroup",
            aci_fabric=self.aci_fabric,
            logical_pair_id=53,
            aci_node_a=node_a,
            aci_node_b=node_b,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACIPodStraddleFabric",
            fabric_id=self.aci_fabric_id + 19,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 19,
        )

        self.aci_pod.aci_fabric = other_fabric
        with self.assertRaises(ValidationError) as cm:
            self.aci_pod.full_clean()
        self.assertIn("aci_fabric", cm.exception.error_dict)
        self.assertIn(group.name, " ".join(cm.exception.message_dict["aci_fabric"]))

    # The move transition is resolved fresh on every call and never
    # memoized on the instance: a result cached during full_clean()
    # would let save() cascade a transition nobody validated.

    def _create_move_fabric(self, offset: int, name: str) -> ACIFabric:
        """Create an extra ACI Fabric to serve as a move target."""
        return ACIFabric.objects.create(
            name=name,
            fabric_id=self.aci_fabric_id + offset,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + offset,
        )

    def _create_pod_pair_group(
        self, node_id_a: int, node_id_b: int, name: str, logical_pair_id: int
    ) -> ACIVPCProtectionGroup:
        """Pair two fresh Leaf Nodes of the test Pod in a Protection Group."""
        node_a = ACINode.objects.create(
            name=f"{name}NodeA",
            aci_pod=self.aci_pod,
            node_id=node_id_a,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        node_b = ACINode.objects.create(
            name=f"{name}NodeB",
            aci_pod=self.aci_pod,
            node_id=node_id_b,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        return ACIVPCProtectionGroup.objects.create(
            name=name,
            aci_fabric=self.aci_fabric,
            logical_pair_id=logical_pair_id,
            aci_node_a=node_a,
            aci_node_b=node_b,
        )

    def test_aci_pod_fabric_change_after_clean_still_cascades(self) -> None:
        """Test a Fabric set after a no-move full_clean still cascades."""
        child_node = ACINode.objects.create(
            name="ACIPodLateMoveChild",
            aci_pod=self.aci_pod,
            node_id=320,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        other_fabric = self._create_move_fabric(21, "ACIPodLateMoveFabric")

        # Resolves a "no move pending" transition first.
        self.aci_pod.full_clean()

        self.aci_pod.aci_fabric = other_fabric
        self.aci_pod.save()

        child_node.refresh_from_db()
        self.assertEqual(child_node._aci_fabric_id, other_fabric.pk)  # noqa: SLF001

    def test_aci_pod_retargeted_move_revalidates_the_final_fabric(self) -> None:
        """Test retargeting after full_clean revalidates the saved Fabric."""
        ACINode.objects.create(
            name="ACIPodRetargetChild",
            aci_pod=self.aci_pod,
            node_id=321,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        fabric_b = self._create_move_fabric(22, "ACIPodRetargetFabricB")
        fabric_c = self._create_move_fabric(23, "ACIPodRetargetFabricC")
        # Only Fabric C already uses the Node ID the Pod brings along,
        # so a transition validated against B must not be reused for C.
        ACINode.objects.create(
            name="ACIPodRetargetIncumbent",
            aci_pod=ACIPod.objects.create(
                name="ACIPodRetargetFabricCPod", aci_fabric=fabric_c, pod_id=21
            ),
            node_id=321,
            role=NodeRoleChoices.ROLE_LEAF,
        )

        self.aci_pod.aci_fabric = fabric_b
        self.aci_pod.full_clean()

        self.aci_pod.aci_fabric = fabric_c
        with self.assertRaises(ValidationError) as cm:
            self.aci_pod.save()

        self.assertIn("321", " ".join(cm.exception.messages))

    def test_aci_pod_group_created_after_clean_still_moves(self) -> None:
        """Test a Protection Group added after full_clean still moves."""
        other_fabric = self._create_move_fabric(24, "ACIPodLateGroupFabric")

        self.aci_pod.aci_fabric = other_fabric
        self.aci_pod.full_clean()

        group = self._create_pod_pair_group(322, 323, "ACIPodLateGroup", 54)
        # Built from the dirty Pod object, so their caches must still hold
        # the Fabric the Pod row actually has
        for node in group.ordered_nodes:
            self.assertEqual(node._aci_fabric_id, self.aci_fabric.pk)  # noqa: SLF001

        self.aci_pod.save()

        group.refresh_from_db()
        self.assertEqual(group.aci_fabric, other_fabric)

    def test_aci_pod_save_after_move_does_not_cascade_again(self) -> None:
        """Test a later unrelated save does not replay the finished move."""
        group = self._create_pod_pair_group(324, 325, "ACIPodReplayGroup", 55)
        other_fabric = self._create_move_fabric(25, "ACIPodReplayFabric")

        self.aci_pod.aci_fabric = other_fabric
        self.aci_pod.save()
        group.refresh_from_db()
        moved_at = group.last_updated

        self.aci_pod.comments = "Unrelated edit after the move."
        self.aci_pod.save()

        group.refresh_from_db()
        self.assertEqual(group.last_updated, moved_at)

    def test_aci_pod_fabric_move_persists_only_the_group_fabric(self) -> None:
        """Test the cascade rewrites the Fabric without clobbering a rename."""
        group = self._create_pod_pair_group(326, 327, "ACIPodScopedGroup", 56)
        other_fabric = self._create_move_fabric(26, "ACIPodScopedFabric")
        renamed = "ACIPodScopedGroupRenamed"

        self.aci_pod.aci_fabric = other_fabric
        self.aci_pod.full_clean()

        # Stands in for a concurrent edit landing between validation
        # and the cascade.
        ACIVPCProtectionGroup.objects.filter(pk=group.pk).update(name=renamed)
        self.aci_pod.save()

        group.refresh_from_db()
        self.assertEqual(group.aci_fabric, other_fabric)
        self.assertEqual(group.name, renamed)
