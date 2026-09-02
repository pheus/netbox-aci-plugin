# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from tenancy.models import Tenant

from ....choices import LeafInterfacePolicyGroupTypeChoices
from ....models.access_policies.aaep import ACIAttachableAccessEntityProfile
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ....models.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverride,
)
from ....models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
    ACILeafInterfaceSelector,
)
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.node_interfaces import ACINodeInterface
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ..base import ACIBaseTestCase


class ACILeafInterfacePolicyGroupTestCase(ACIBaseTestCase):
    """Test case for ACILeafInterfacePolicyGroup model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACILeafInterfacePolicyGroup model."""
        super().setUpTestData()

        cls.aci_aaep_name = "ACITestAAEPForLIPG"
        cls.aci_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name=cls.aci_aaep_name, aci_fabric=cls.aci_fabric
        )

        cls.aci_lipg_name = "ACITestLIPGAccess"
        cls.aci_lipg_alias = "ACITestLIPGAlias"
        cls.aci_lipg_description = (
            "ACI Test Leaf Interface Policy Group for NetBox ACI Plugin"
        )
        cls.aci_lipg_comments = (
            "ACI Leaf Interface Policy Group for NetBox ACI Plugin testing."
        )

        cls.aci_lipg_access = ACILeafInterfacePolicyGroup.objects.create(
            name=cls.aci_lipg_name,
            name_alias=cls.aci_lipg_alias,
            description=cls.aci_lipg_description,
            comments=cls.aci_lipg_comments,
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            aci_aaep=cls.aci_aaep,
            nb_tenant=cls.nb_tenant,
        )
        # Minimal fixtures for the port channel / virtual port channel types,
        # covering the "bundle" APIC namespace shared by both.
        cls.aci_lipg_pc = ACILeafInterfacePolicyGroup.objects.create(
            name="ACITestLIPGPortChannel",
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_PC,
        )
        cls.aci_lipg_vpc = ACILeafInterfacePolicyGroup.objects.create(
            name="ACITestLIPGVirtualPortChannel",
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_VPC,
        )

    def test_aci_leaf_interface_policy_group_instance(self) -> None:
        """Test type of created ACI Leaf Interface Policy Group."""
        self.assertTrue(isinstance(self.aci_lipg_access, ACILeafInterfacePolicyGroup))

    def test_aci_leaf_interface_policy_group_alias(self) -> None:
        """Test alias of ACI Leaf Interface Policy Group."""
        self.assertEqual(self.aci_lipg_access.name_alias, self.aci_lipg_alias)

    def test_aci_leaf_interface_policy_group_description(self) -> None:
        """Test description of ACI Leaf Interface Policy Group."""
        self.assertEqual(self.aci_lipg_access.description, self.aci_lipg_description)

    def test_aci_leaf_interface_policy_group_aci_fabric_instance(self) -> None:
        """Test the ACI Fabric instance associated with the policy group."""
        self.assertTrue(isinstance(self.aci_lipg_access.aci_fabric, ACIFabric))
        self.assertEqual(self.aci_lipg_access.aci_fabric.name, self.aci_fabric_name)

    def test_aci_leaf_interface_policy_group_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant associated with the policy group."""
        self.assertTrue(isinstance(self.aci_lipg_access.nb_tenant, Tenant))
        self.assertEqual(self.aci_lipg_access.nb_tenant.name, self.nb_tenant_name)

    def test_aci_leaf_interface_policy_group_aci_aaep_instance(self) -> None:
        """Test the ACI AAEP instance associated with the policy group."""
        self.assertTrue(
            isinstance(self.aci_lipg_access.aci_aaep, ACIAttachableAccessEntityProfile)
        )
        self.assertEqual(self.aci_lipg_access.aci_aaep.name, self.aci_aaep_name)

    def test_aci_leaf_interface_policy_group_parent_object(self) -> None:
        """Test parent object of the policy group is the ACI Fabric."""
        self.assertEqual(self.aci_lipg_access.parent_object, self.aci_fabric)

    def test_aci_leaf_interface_policy_group_type_access(self) -> None:
        """Test the access type policy group's type value and color."""
        self.assertEqual(
            self.aci_lipg_access.group_type,
            LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        self.assertEqual(
            self.aci_lipg_access.get_group_type_color(),
            LeafInterfacePolicyGroupTypeChoices.colors.get(
                LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS
            ),
        )

    def test_aci_leaf_interface_policy_group_type_pc(self) -> None:
        """Test the port channel type policy group's type value and color."""
        self.assertEqual(
            self.aci_lipg_pc.group_type, LeafInterfacePolicyGroupTypeChoices.TYPE_PC
        )
        self.assertEqual(
            self.aci_lipg_pc.get_group_type_color(),
            LeafInterfacePolicyGroupTypeChoices.colors.get(
                LeafInterfacePolicyGroupTypeChoices.TYPE_PC
            ),
        )

    def test_aci_leaf_interface_policy_group_type_vpc(self) -> None:
        """Test the virtual port channel type's value and color."""
        self.assertEqual(
            self.aci_lipg_vpc.group_type, LeafInterfacePolicyGroupTypeChoices.TYPE_VPC
        )
        self.assertEqual(
            self.aci_lipg_vpc.get_group_type_color(),
            LeafInterfacePolicyGroupTypeChoices.colors.get(
                LeafInterfacePolicyGroupTypeChoices.TYPE_VPC
            ),
        )

    def test_aci_leaf_interface_policy_group_str(self) -> None:
        """Test str shows the type suffix for each policy group type."""
        self.assertEqual(
            self.aci_lipg_access.__str__(), f"{self.aci_lipg_name} (Access)"
        )
        self.assertEqual(
            self.aci_lipg_pc.__str__(), "ACITestLIPGPortChannel (Port Channel)"
        )
        self.assertEqual(
            self.aci_lipg_vpc.__str__(),
            "ACITestLIPGVirtualPortChannel (Virtual Port Channel)",
        )

    def test_aci_leaf_interface_policy_group_lag_type(self) -> None:
        """Test lag_type per policy group type."""
        self.assertIsNone(self.aci_lipg_access.lag_type)
        self.assertEqual(self.aci_lipg_pc.lag_type, "link")
        self.assertEqual(self.aci_lipg_vpc.lag_type, "node")

    def test_aci_leaf_interface_policy_group_apic_namespace(self) -> None:
        """Test apic_namespace per policy group type."""
        self.assertEqual(self.aci_lipg_access.apic_namespace, "access")
        self.assertEqual(self.aci_lipg_pc.apic_namespace, "bundle")
        self.assertEqual(self.aci_lipg_vpc.apic_namespace, "bundle")

        self.aci_lipg_access.group_type = "invalid"
        self.assertIsNone(self.aci_lipg_access.apic_namespace)

    def test_aci_leaf_interface_policy_group_access_and_bundle_name_coexist(
        self,
    ) -> None:
        """Test an access and a port channel group may share a name."""
        access = ACILeafInterfacePolicyGroup.objects.create(
            name="PG1",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        bundle = ACILeafInterfacePolicyGroup.objects.create(
            name="PG1",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_PC,
        )
        self.assertEqual(access.name, bundle.name)
        self.assertNotEqual(access.pk, bundle.pk)

    def test_constraint_unique_aci_leaf_interface_policy_group_access_name(
        self,
    ) -> None:
        """Test unique constraint of an access type name per ACI Fabric."""
        ACILeafInterfacePolicyGroup.objects.create(
            name="PG-Access-Dup",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        duplicate = ACILeafInterfacePolicyGroup(
            name="PG-Access-Dup",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate.save()

    def test_constraint_unique_aci_leaf_interface_policy_group_bundle_name(
        self,
    ) -> None:
        """Test the unique constraint shared by pc and vpc names."""
        ACILeafInterfacePolicyGroup.objects.create(
            name="PG-Bundle-Dup",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_PC,
        )
        duplicate = ACILeafInterfacePolicyGroup(
            name="PG-Bundle-Dup",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_VPC,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate.save()

    def test_invalid_aci_leaf_interface_policy_group_duplicate_bundle_name(
        self,
    ) -> None:
        """Test full_clean surfaces the bundle-name uniqueness constraint."""
        ACILeafInterfacePolicyGroup.objects.create(
            name="PG-Bundle-Clean",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_PC,
        )
        duplicate = ACILeafInterfacePolicyGroup(
            name="PG-Bundle-Clean",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_VPC,
        )
        with self.assertRaises(ValidationError) as cm:
            duplicate.full_clean()
        self.assertIn("__all__", cm.exception.error_dict)

    def test_invalid_aci_leaf_interface_policy_group_cross_fabric_aaep(self) -> None:
        """Test clean rejects an AAEP from a different ACI Fabric."""
        other_fabric = ACIFabric.objects.create(
            name="ACIBaseTestFabricOtherLIPG",
            fabric_id=self.aci_fabric_id + 1,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 1,
        )
        other_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACITestAAEPOtherFabric", aci_fabric=other_fabric
        )
        lipg = ACILeafInterfacePolicyGroup(
            name="ACILIPGCrossFabricAAEP",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            aci_aaep=other_aaep,
        )
        with self.assertRaises(ValidationError) as cm:
            lipg.full_clean()
        self.assertIn("aci_aaep", cm.exception.error_dict)

    def test_aci_leaf_interface_policy_group_aaep_less_create_accepted(self) -> None:
        """Test full_clean accepts a policy group without an AAEP."""
        lipg = ACILeafInterfacePolicyGroup(
            name="ACILIPGNoAAEP",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        lipg.full_clean()

    def test_invalid_aci_leaf_interface_policy_group_type_change(self) -> None:
        """Test clean rejects a group type change after creation."""
        self.aci_lipg_pc.group_type = LeafInterfacePolicyGroupTypeChoices.TYPE_VPC
        with self.assertRaises(ValidationError) as cm:
            self.aci_lipg_pc.full_clean()
        self.assertIn("group_type", cm.exception.error_dict)

    def test_invalid_aci_leaf_interface_policy_group_type_change_on_save(
        self,
    ) -> None:
        """Test save rejects a group type change bypassing full_clean."""
        self.aci_lipg_pc.group_type = LeafInterfacePolicyGroupTypeChoices.TYPE_VPC
        with self.assertRaises(ValidationError):
            self.aci_lipg_pc.save()

    def test_aci_leaf_interface_policy_group_partial_save_skips_type_guard(
        self,
    ) -> None:
        """Test a save excluding the type does not run the type guard."""
        self.aci_lipg_pc.group_type = LeafInterfacePolicyGroupTypeChoices.TYPE_VPC
        self.aci_lipg_pc.description = "Updated description"
        self.aci_lipg_pc.save(update_fields={"description"})
        self.aci_lipg_pc.refresh_from_db()
        self.assertEqual(
            self.aci_lipg_pc.group_type,
            LeafInterfacePolicyGroupTypeChoices.TYPE_PC,
        )

    def test_aci_leaf_interface_policy_group_generator_update_fields(
        self,
    ) -> None:
        """Test a single-use update_fields iterable persists the field."""
        self.aci_lipg_pc.description = "Updated via a single-use iterable"
        self.aci_lipg_pc.save(update_fields=(field for field in ("description",)))

        self.aci_lipg_pc.refresh_from_db()
        self.assertEqual(
            self.aci_lipg_pc.description, "Updated via a single-use iterable"
        )

    def test_invalid_aci_leaf_interface_policy_group_type_change_generator(
        self,
    ) -> None:
        """Test the type guard still runs for a single-use iterable."""
        self.aci_lipg_pc.group_type = LeafInterfacePolicyGroupTypeChoices.TYPE_VPC
        with self.assertRaises(ValidationError):
            self.aci_lipg_pc.save(update_fields=(field for field in ("group_type",)))

    def test_aci_leaf_interface_policy_group_edit_without_type_change_allowed(
        self,
    ) -> None:
        """Test full_clean accepts an edit that leaves the type unchanged."""
        self.aci_lipg_pc.description = "Updated description"
        self.aci_lipg_pc.full_clean()

    def test_invalid_aci_leaf_interface_policy_group_fabric_move_with_selector(
        self,
    ) -> None:
        """Test clean rejects a Fabric move away from assigned Selectors."""
        profile = ACILeafInterfaceProfile.objects.create(
            name="ACITestLIPGMoveProfile",
            aci_fabric=self.aci_fabric,
        )
        ACILeafInterfaceSelector.objects.create(
            name="ACITestLIPGMoveSelector",
            aci_leaf_interface_profile=profile,
            aci_leaf_interface_policy_group=self.aci_lipg_pc,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACITestLIPGMoveOtherFabric",
            fabric_id=131,
            infra_vlan_vid=3904,
        )
        self.aci_lipg_pc.aci_fabric = other_fabric
        with self.assertRaises(ValidationError) as cm:
            self.aci_lipg_pc.full_clean()
        self.assertIn("aci_fabric", cm.exception.error_dict)

    def test_aci_leaf_interface_policy_group_fabric_move_without_selector(
        self,
    ) -> None:
        """Test a Fabric move is allowed when no Selector is assigned."""
        other_fabric = ACIFabric.objects.create(
            name="ACITestLIPGFreeMoveOtherFabric",
            fabric_id=132,
            infra_vlan_vid=3905,
        )
        self.aci_lipg_pc.aci_fabric = other_fabric
        self.aci_lipg_pc.full_clean()

    def test_aci_leaf_interface_policy_group_fabric_move_with_selector_in_target(
        self,
    ) -> None:
        """Test a Fabric move is allowed when the Selector is already there.

        Pins the guard's `.exclude()` half. A bare `.exists()` would
        reject this move, and the no-Selector case above cannot tell the
        two apart.
        """
        other_fabric = ACIFabric.objects.create(
            name="ACITestLIPGMoveTargetFabric",
            fabric_id=143,
            infra_vlan_vid=3913,
        )
        profile_in_target = ACILeafInterfaceProfile.objects.create(
            name="ACITestLIPGMoveTargetProfile",
            aci_fabric=other_fabric,
        )
        # Created directly, since the Selector's own clean() rejects the
        # cross-Fabric pair this scenario has to start from
        ACILeafInterfaceSelector.objects.create(
            name="ACITestLIPGMoveTargetSelector",
            aci_leaf_interface_profile=profile_in_target,
            aci_leaf_interface_policy_group=self.aci_lipg_pc,
        )
        self.aci_lipg_pc.aci_fabric = other_fabric
        self.aci_lipg_pc.full_clean()

    def test_invalid_aci_leaf_interface_policy_group_name(self) -> None:
        """Test validation of ACI Leaf Interface Policy Group naming."""
        lipg = ACILeafInterfacePolicyGroup(name="Invalid Name With Spaces")
        with self.assertRaises(ValidationError):
            lipg.full_clean()

    def test_invalid_aci_leaf_interface_policy_group_name_length(self) -> None:
        """Test validation of ACI Leaf Interface Policy Group name length."""
        lipg = ACILeafInterfacePolicyGroup(name="A" * 65)
        with self.assertRaises(ValidationError):
            lipg.full_clean()

    def test_invalid_aci_leaf_interface_policy_group_name_alias(self) -> None:
        """Test validation of ACI Leaf Interface Policy Group name alias."""
        lipg = ACILeafInterfacePolicyGroup(
            name="ACILIPGTest1", name_alias="Invalid Alias"
        )
        with self.assertRaises(ValidationError):
            lipg.full_clean()

    def test_invalid_aci_leaf_interface_policy_group_name_alias_length(self) -> None:
        """Test validation of Leaf Interface Policy Group alias length."""
        lipg = ACILeafInterfacePolicyGroup(name="ACILIPGTest1", name_alias="A" * 65)
        with self.assertRaises(ValidationError):
            lipg.full_clean()

    def test_invalid_aci_leaf_interface_policy_group_description(self) -> None:
        """Test validation of ACI Leaf Interface Policy Group description."""
        lipg = ACILeafInterfacePolicyGroup(
            name="ACILIPGTest1", description="Invalid Description: ö"
        )
        with self.assertRaises(ValidationError):
            lipg.full_clean()

    def test_invalid_aci_leaf_interface_policy_group_description_length(
        self,
    ) -> None:
        """Test validation of Policy Group description length."""
        lipg = ACILeafInterfacePolicyGroup(name="ACILIPGTest1", description="A" * 129)
        with self.assertRaises(ValidationError):
            lipg.full_clean()

    def test_default_ordering_queryset_evaluates(self) -> None:
        """Test that the default-ordered queryset evaluates without error."""
        self.assertIsNotNone(list(ACILeafInterfacePolicyGroup.objects.all()))

    def test_invalid_policy_group_fabric_move_strands_override(self) -> None:
        """Test clean rejects a Fabric move stranding an assigned override."""
        policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACILIPGOverrideMove",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        node_interface = ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=1, port=41
        )
        ACILeafInterfaceOverride.objects.create(
            aci_node_interface=node_interface,
            aci_leaf_interface_policy_group=policy_group,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACILIPGOverrideMoveOtherFabric",
            fabric_id=140,
            infra_vlan_vid=3910,
        )
        policy_group.aci_fabric = other_fabric
        with self.assertRaises(ValidationError) as cm:
            policy_group.full_clean()
        self.assertIn("aci_fabric", cm.exception.error_dict)

    def test_policy_group_fabric_move_without_override(self) -> None:
        """Test a Fabric move is allowed when no override is assigned."""
        policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACILIPGOverrideMoveFree",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACILIPGOverrideMoveFreeFabric",
            fabric_id=141,
            infra_vlan_vid=3911,
        )
        policy_group.aci_fabric = other_fabric
        policy_group.full_clean()

    def test_policy_group_fabric_move_with_override_in_target(self) -> None:
        """Test a Fabric move is allowed when the Override is already there.

        Pins the guard's `.exclude()` half. A bare `.exists()` would
        reject this move, and the zero-override case above cannot tell
        the two apart.
        """
        policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACILIPGOverrideMoveTarget",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACILIPGOverrideMoveTargetFabric",
            fabric_id=142,
            infra_vlan_vid=3912,
        )
        other_pod = ACIPod.objects.create(
            name="ACILIPGOverrideMoveTargetPod",
            aci_fabric=other_fabric,
            pod_id=1,
        )
        other_node = ACINode.objects.create(
            name="ACILIPGOverrideMoveTargetNode", aci_pod=other_pod, node_id=101
        )
        interface_in_target = ACINodeInterface.objects.create(
            aci_node=other_node, module=1, port=1
        )
        # Created directly, since the Override's own clean() rejects the
        # cross-Fabric pair this scenario has to start from
        ACILeafInterfaceOverride.objects.create(
            aci_node_interface=interface_in_target,
            aci_leaf_interface_policy_group=policy_group,
        )
        policy_group.aci_fabric = other_fabric
        policy_group.full_clean()

    def test_aci_aaep_deletion_is_protected(self) -> None:
        """Test deleting a referenced ACI AAEP is refused."""
        with self.assertRaises(ProtectedError):
            self.aci_aaep.delete()
