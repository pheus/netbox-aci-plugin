# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the ACI Leaf Interface Profile models."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from core.choices import ObjectChangeActionChoices
from tenancy.models import Tenant

from ....choices import LeafInterfacePolicyGroupTypeChoices
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ....models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
    ACILeafInterfaceSelector,
    ACILeafPortBlock,
)
from ....models.access_policies.leaf_switch_profiles import (
    ACILeafSwitchProfile,
    ACILeafSwitchProfileInterfaceBinding,
)
from ....models.fabric.fabrics import ACIFabric
from ..base import ACIBaseTestCase


class ACILeafInterfaceProfileTestCase(ACIBaseTestCase):
    """Test case for the ACILeafInterfaceProfile model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACILeafInterfaceProfile model."""
        super().setUpTestData()

        cls.aci_leaf_interface_profile_name = "ACITestLeafInterfaceProfile"
        cls.aci_leaf_interface_profile_alias = "ACITestLeafInterfaceProfileAlias"
        cls.aci_leaf_interface_profile_description = (
            "ACI Test Leaf Interface Profile for NetBox ACI Plugin"
        )
        cls.aci_leaf_interface_profile_comments = """
        ACI Leaf Interface Profile for NetBox ACI Plugin testing.
        """

        # Create objects
        cls.aci_leaf_interface_profile = ACILeafInterfaceProfile.objects.create(
            name=cls.aci_leaf_interface_profile_name,
            name_alias=cls.aci_leaf_interface_profile_alias,
            description=cls.aci_leaf_interface_profile_description,
            comments=cls.aci_leaf_interface_profile_comments,
            aci_fabric=cls.aci_fabric,
            nb_tenant=cls.nb_tenant,
        )

    def test_aci_leaf_interface_profile_instance(self) -> None:
        """Test type of created ACI Leaf Interface Profile."""
        self.assertTrue(
            isinstance(self.aci_leaf_interface_profile, ACILeafInterfaceProfile)
        )

    def test_aci_leaf_interface_profile_str(self) -> None:
        """Test string value of created ACI Leaf Interface Profile."""
        self.assertEqual(
            self.aci_leaf_interface_profile.__str__(),
            self.aci_leaf_interface_profile.name,
        )

    def test_aci_leaf_interface_profile_name_alias(self) -> None:
        """Test alias of created ACI Leaf Interface Profile."""
        self.assertEqual(
            self.aci_leaf_interface_profile.name_alias,
            self.aci_leaf_interface_profile_alias,
        )

    def test_aci_leaf_interface_profile_description(self) -> None:
        """Test description of created ACI Leaf Interface Profile."""
        self.assertEqual(
            self.aci_leaf_interface_profile.description,
            self.aci_leaf_interface_profile_description,
        )

    def test_aci_leaf_interface_profile_aci_fabric_instance(self) -> None:
        """Test the ACI Fabric instance associated with the profile."""
        self.assertTrue(
            isinstance(self.aci_leaf_interface_profile.aci_fabric, ACIFabric)
        )
        self.assertEqual(
            self.aci_leaf_interface_profile.aci_fabric.name, self.aci_fabric_name
        )

    def test_aci_leaf_interface_profile_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with the profile."""
        self.assertTrue(isinstance(self.aci_leaf_interface_profile.nb_tenant, Tenant))
        self.assertEqual(
            self.aci_leaf_interface_profile.nb_tenant.name, self.nb_tenant_name
        )

    def test_aci_leaf_interface_profile_parent_object(self) -> None:
        """Test parent object of ACI Leaf Interface Profile is the Fabric."""
        self.assertEqual(self.aci_leaf_interface_profile.parent_object, self.aci_fabric)

    def test_invalid_aci_leaf_interface_profile_name(self) -> None:
        """Test validation of ACI Leaf Interface Profile naming."""
        profile = ACILeafInterfaceProfile(
            name="Invalid Name With Spaces", aci_fabric=self.aci_fabric
        )
        with self.assertRaises(ValidationError) as cm:
            profile.full_clean()
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_leaf_interface_profile_name_length(self) -> None:
        """Test validation of ACI Leaf Interface Profile name length."""
        profile = ACILeafInterfaceProfile(name="A" * 65, aci_fabric=self.aci_fabric)
        with self.assertRaises(ValidationError) as cm:
            profile.full_clean()
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_leaf_interface_profile_name_alias(self) -> None:
        """Test validation of ACI Leaf Interface Profile name alias."""
        profile = ACILeafInterfaceProfile(
            name="ACILeafInterfaceProfileTest1",
            name_alias="Invalid Alias",
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(ValidationError) as cm:
            profile.full_clean()
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_leaf_interface_profile_name_alias_length(self) -> None:
        """Test validation of ACI Leaf Interface Profile name alias length."""
        profile = ACILeafInterfaceProfile(
            name="ACILeafInterfaceProfileTest1",
            name_alias="A" * 65,
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(ValidationError) as cm:
            profile.full_clean()
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_leaf_interface_profile_description(self) -> None:
        """Test validation of ACI Leaf Interface Profile description."""
        profile = ACILeafInterfaceProfile(
            name="ACILeafInterfaceProfileTest1",
            description="Invalid Description: ö",
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(ValidationError) as cm:
            profile.full_clean()
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_leaf_interface_profile_description_length(self) -> None:
        """Test validation of ACI Leaf Interface Profile description length."""
        profile = ACILeafInterfaceProfile(
            name="ACILeafInterfaceProfileTest1",
            description="A" * 129,
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(ValidationError) as cm:
            profile.full_clean()
        self.assertIn("description", cm.exception.error_dict)

    def test_constraint_unique_aci_leaf_interface_profile_name_per_fabric(
        self,
    ) -> None:
        """Test unique constraint of profile name per ACI Fabric."""
        duplicate_profile = ACILeafInterfaceProfile(
            name=self.aci_leaf_interface_profile_name,
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_profile.save()

    def test_aci_leaf_interface_profile_name_reusable_in_another_fabric(
        self,
    ) -> None:
        """Test the same profile name is allowed in a second ACI Fabric."""
        other_fabric = ACIFabric.objects.create(
            name="ACITestLeafInterfaceProfileOtherFabric",
            fabric_id=128,
            infra_vlan_vid=3901,
        )
        profile = ACILeafInterfaceProfile.objects.create(
            name=self.aci_leaf_interface_profile_name,
            aci_fabric=other_fabric,
        )
        self.assertEqual(profile.name, self.aci_leaf_interface_profile_name)

    def test_invalid_aci_leaf_interface_profile_fabric_move_strands_group(
        self,
    ) -> None:
        """Test clean rejects a Fabric move stranding an assigned group."""
        policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACITestLeafInterfaceProfileMovePolicyGroup",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        ACILeafInterfaceSelector.objects.create(
            name="ACITestLeafInterfaceProfileMoveSelector",
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
            aci_leaf_interface_policy_group=policy_group,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACITestLeafInterfaceProfileMoveOtherFabric",
            fabric_id=129,
            infra_vlan_vid=3902,
        )
        self.aci_leaf_interface_profile.aci_fabric = other_fabric
        with self.assertRaises(ValidationError) as cm:
            self.aci_leaf_interface_profile.full_clean()
        self.assertIn("aci_fabric", cm.exception.error_dict)

    def test_aci_leaf_interface_profile_fabric_move_without_group(self) -> None:
        """Test a Fabric move is allowed when no group is assigned."""
        ACILeafInterfaceSelector.objects.create(
            name="ACITestLeafInterfaceProfileMoveFreeSelector",
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACITestLeafInterfaceProfileMoveFreeFabric",
            fabric_id=130,
            infra_vlan_vid=3903,
        )
        self.aci_leaf_interface_profile.aci_fabric = other_fabric
        self.aci_leaf_interface_profile.full_clean()

    def test_aci_leaf_interface_profile_fabric_move_with_group_in_target(
        self,
    ) -> None:
        """Test a Fabric move is allowed when the group is already there.

        Pins the guard's `.exclude()` half. A bare `.exists()` would
        reject this move, and the no-group case above cannot tell the
        two apart.
        """
        other_fabric = ACIFabric.objects.create(
            name="ACITestLeafInterfaceProfileMoveTargetFabric",
            fabric_id=134,
            infra_vlan_vid=3906,
        )
        policy_group_in_target = ACILeafInterfacePolicyGroup.objects.create(
            name="ACITestLeafInterfaceProfileMoveTargetPolicyGroup",
            aci_fabric=other_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        # Created directly, since the Selector's own clean() rejects the
        # cross-Fabric pair this scenario has to start from
        ACILeafInterfaceSelector.objects.create(
            name="ACITestLeafInterfaceProfileMoveTargetSelector",
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
            aci_leaf_interface_policy_group=policy_group_in_target,
        )
        self.aci_leaf_interface_profile.aci_fabric = other_fabric
        self.aci_leaf_interface_profile.full_clean()

    def test_invalid_interface_profile_fabric_move_strands_binding(self) -> None:
        """Test clean rejects a Fabric move stranding an assigned binding."""
        switch_profile = ACILeafSwitchProfile.objects.create(
            name="ACILIPMoveSwitchProfile", aci_fabric=self.aci_fabric
        )
        ACILeafSwitchProfileInterfaceBinding.objects.create(
            aci_leaf_switch_profile=switch_profile,
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACILIPMoveOtherFabric", fabric_id=152, infra_vlan_vid=3922
        )
        self.aci_leaf_interface_profile.aci_fabric = other_fabric
        with self.assertRaises(ValidationError) as cm:
            self.aci_leaf_interface_profile.full_clean()
        self.assertIn("aci_fabric", cm.exception.error_dict)

    def test_interface_profile_fabric_move_with_binding_in_target(self) -> None:
        """Test a Fabric move is allowed when the binding is already there.

        Pins the guard's `.exclude()` half. A bare `.exists()` would
        reject this move.
        """
        other_fabric = ACIFabric.objects.create(
            name="ACILIPMoveTargetFabric",
            fabric_id=133,
            infra_vlan_vid=3905,
        )
        switch_profile_in_target = ACILeafSwitchProfile.objects.create(
            name="ACILIPMoveTargetSwitchProfile", aci_fabric=other_fabric
        )
        # Created directly, since the Binding's own clean() rejects the
        # cross-Fabric pair this scenario has to start from
        ACILeafSwitchProfileInterfaceBinding.objects.create(
            aci_leaf_switch_profile=switch_profile_in_target,
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        self.aci_leaf_interface_profile.aci_fabric = other_fabric
        self.aci_leaf_interface_profile.full_clean()

    def test_aci_leaf_interface_profile_selector_count_zero(self) -> None:
        """Test selector_count is 0 for a profile with no Selectors."""
        self.assertEqual(self.aci_leaf_interface_profile.selector_count, 0)

    def test_aci_leaf_interface_profile_selector_count_nonzero(self) -> None:
        """Test selector_count counts the profile's Selectors."""
        ACILeafInterfaceSelector.objects.create(
            name="ACILIPSelectorCount1",
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        ACILeafInterfaceSelector.objects.create(
            name="ACILIPSelectorCount2",
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        self.assertEqual(self.aci_leaf_interface_profile.selector_count, 2)


class ACILeafInterfaceSelectorTestCase(ACIBaseTestCase):
    """Test case for the ACILeafInterfaceSelector model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACILeafInterfaceSelector model."""
        super().setUpTestData()

        cls.aci_leaf_interface_selector_name = "ACITestLeafInterfaceSelector"
        cls.aci_leaf_interface_selector_alias = "ACITestLeafInterfaceSelectorAlias"
        cls.aci_leaf_interface_selector_description = (
            "ACI Test Leaf Interface Selector for NetBox ACI Plugin"
        )

        # Create objects
        cls.aci_leaf_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACITestLeafInterfaceSelectorProfile",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_interface_policy_group_name = (
            "ACITestLeafInterfaceSelectorPolicyGroup"
        )
        cls.aci_leaf_interface_policy_group = (
            ACILeafInterfacePolicyGroup.objects.create(
                name=cls.aci_leaf_interface_policy_group_name,
                aci_fabric=cls.aci_fabric,
                group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            )
        )
        cls.aci_leaf_interface_selector = ACILeafInterfaceSelector.objects.create(
            name=cls.aci_leaf_interface_selector_name,
            name_alias=cls.aci_leaf_interface_selector_alias,
            description=cls.aci_leaf_interface_selector_description,
            aci_leaf_interface_profile=cls.aci_leaf_interface_profile,
            aci_leaf_interface_policy_group=cls.aci_leaf_interface_policy_group,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_leaf_interface_selector_no_policy_group = (
            ACILeafInterfaceSelector.objects.create(
                name="ACITestLeafInterfaceSelectorNoPolicyGroup",
                aci_leaf_interface_profile=cls.aci_leaf_interface_profile,
            )
        )

    def test_aci_leaf_interface_selector_instance(self) -> None:
        """Test type of created ACI Leaf Interface Selector."""
        self.assertTrue(
            isinstance(self.aci_leaf_interface_selector, ACILeafInterfaceSelector)
        )

    def test_aci_leaf_interface_selector_str(self) -> None:
        """Test string value of created ACI Leaf Interface Selector."""
        self.assertEqual(
            self.aci_leaf_interface_selector.__str__(),
            self.aci_leaf_interface_selector.name,
        )

    def test_aci_leaf_interface_selector_name_alias(self) -> None:
        """Test alias of created ACI Leaf Interface Selector."""
        self.assertEqual(
            self.aci_leaf_interface_selector.name_alias,
            self.aci_leaf_interface_selector_alias,
        )

    def test_aci_leaf_interface_selector_description(self) -> None:
        """Test description of created ACI Leaf Interface Selector."""
        self.assertEqual(
            self.aci_leaf_interface_selector.description,
            self.aci_leaf_interface_selector_description,
        )

    def test_aci_leaf_interface_selector_parent_object(self) -> None:
        """Test parent object of ACI Leaf Interface Selector is the profile."""
        self.assertEqual(
            self.aci_leaf_interface_selector.parent_object,
            self.aci_leaf_interface_profile,
        )

    def test_aci_leaf_interface_selector_aci_fabric(self) -> None:
        """Test aci_fabric returns the ACI Fabric of the related profile."""
        self.assertTrue(
            isinstance(self.aci_leaf_interface_selector.aci_fabric, ACIFabric)
        )
        self.assertEqual(self.aci_leaf_interface_selector.aci_fabric, self.aci_fabric)

    def test_aci_leaf_interface_selector_to_objectchange(self) -> None:
        """Test to_objectchange sets the profile as the related object."""
        objectchange = self.aci_leaf_interface_selector.to_objectchange(
            ObjectChangeActionChoices.ACTION_UPDATE
        )
        self.assertEqual(objectchange.related_object, self.aci_leaf_interface_profile)

    def test_aci_leaf_interface_selector_aci_leaf_interface_policy_group_instance(
        self,
    ) -> None:
        """Test the policy group instance associated with the selector."""
        self.assertTrue(
            isinstance(
                self.aci_leaf_interface_selector.aci_leaf_interface_policy_group,
                ACILeafInterfacePolicyGroup,
            )
        )
        self.assertEqual(
            self.aci_leaf_interface_selector.aci_leaf_interface_policy_group.name,
            self.aci_leaf_interface_policy_group_name,
        )

    def test_aci_leaf_interface_selector_without_policy_group(self) -> None:
        """Test a selector may be saved without a policy group assigned."""
        self.assertIsNone(
            self.aci_leaf_interface_selector_no_policy_group.aci_leaf_interface_policy_group
        )

    def test_aci_leaf_interface_selector_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with the selector."""
        self.assertTrue(isinstance(self.aci_leaf_interface_selector.nb_tenant, Tenant))
        self.assertEqual(
            self.aci_leaf_interface_selector.nb_tenant.name, self.nb_tenant_name
        )

    def test_aci_leaf_interface_selector_valid_same_fabric_policy_group(
        self,
    ) -> None:
        """Test clean accepts a policy group from the same ACI Fabric."""
        selector = ACILeafInterfaceSelector(
            name="ACITestLeafInterfaceSelectorValidPolicyGroup",
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
            aci_leaf_interface_policy_group=self.aci_leaf_interface_policy_group,
        )
        selector.full_clean()

    def test_aci_leaf_interface_selector_valid_without_policy_group(self) -> None:
        """Test clean accepts a selector without a policy group."""
        selector = ACILeafInterfaceSelector(
            name="ACITestLeafInterfaceSelectorValidNoPolicyGroup",
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        selector.full_clean()

    def test_invalid_aci_leaf_interface_selector_cross_fabric_policy_group(
        self,
    ) -> None:
        """Test clean rejects a policy group from a different ACI Fabric."""
        other_fabric = ACIFabric.objects.create(
            name="ACITestLeafInterfaceSelectorOtherFabric",
            fabric_id=128,
            infra_vlan_vid=3901,
        )
        other_policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACITestLeafInterfaceSelectorOtherPolicyGroup",
            aci_fabric=other_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        selector = ACILeafInterfaceSelector(
            name="ACITestLeafInterfaceSelectorCrossFabric",
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
            aci_leaf_interface_policy_group=other_policy_group,
        )
        with self.assertRaises(ValidationError) as cm:
            selector.full_clean()
        self.assertIn("aci_leaf_interface_policy_group", cm.exception.error_dict)

    def test_invalid_aci_leaf_interface_selector_name(self) -> None:
        """Test validation of ACI Leaf Interface Selector naming."""
        selector = ACILeafInterfaceSelector(
            name="Invalid Name With Spaces",
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        with self.assertRaises(ValidationError) as cm:
            selector.full_clean()
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_leaf_interface_selector_name_length(self) -> None:
        """Test validation of ACI Leaf Interface Selector name length."""
        selector = ACILeafInterfaceSelector(
            name="A" * 65,
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        with self.assertRaises(ValidationError) as cm:
            selector.full_clean()
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_leaf_interface_selector_name_alias(self) -> None:
        """Test validation of ACI Leaf Interface Selector name alias."""
        selector = ACILeafInterfaceSelector(
            name="ACILeafInterfaceSelectorTest1",
            name_alias="Invalid Alias",
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        with self.assertRaises(ValidationError) as cm:
            selector.full_clean()
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_leaf_interface_selector_name_alias_length(self) -> None:
        """Test validation of ACI Leaf Interface Selector name alias length."""
        selector = ACILeafInterfaceSelector(
            name="ACILeafInterfaceSelectorTest1",
            name_alias="A" * 65,
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        with self.assertRaises(ValidationError) as cm:
            selector.full_clean()
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_leaf_interface_selector_description(self) -> None:
        """Test validation of ACI Leaf Interface Selector description."""
        selector = ACILeafInterfaceSelector(
            name="ACILeafInterfaceSelectorTest1",
            description="Invalid Description: ö",
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        with self.assertRaises(ValidationError) as cm:
            selector.full_clean()
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_leaf_interface_selector_description_length(self) -> None:
        """Test ACI Leaf Interface Selector description length validation."""
        selector = ACILeafInterfaceSelector(
            name="ACILeafInterfaceSelectorTest1",
            description="A" * 129,
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        with self.assertRaises(ValidationError) as cm:
            selector.full_clean()
        self.assertIn("description", cm.exception.error_dict)

    def test_constraint_unique_aci_leaf_interface_selector_name(self) -> None:
        """Test unique constraint of selector name per profile."""
        duplicate_selector = ACILeafInterfaceSelector(
            name=self.aci_leaf_interface_selector_name,
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_selector.save()

    def test_aci_leaf_interface_selector_name_reusable_in_another_profile(
        self,
    ) -> None:
        """Test the same selector name is allowed in a second profile."""
        other_profile = ACILeafInterfaceProfile.objects.create(
            name="ACITestLeafInterfaceSelectorOtherProfile",
            aci_fabric=self.aci_fabric,
        )
        selector = ACILeafInterfaceSelector.objects.create(
            name=self.aci_leaf_interface_selector_name,
            aci_leaf_interface_profile=other_profile,
        )
        self.assertEqual(selector.name, self.aci_leaf_interface_selector_name)

    def test_aci_leaf_interface_selector_port_block_count_zero(self) -> None:
        """Test port_block_count is 0 for a selector with no Port Blocks."""
        self.assertEqual(self.aci_leaf_interface_selector.port_block_count, 0)

    def test_aci_leaf_interface_selector_port_block_count_nonzero(self) -> None:
        """Test port_block_count counts the selector's Port Blocks."""
        ACILeafPortBlock.objects.create(
            name="ACILISPortBlockCount1",
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            module_from=1,
            module_to=1,
            port_from=1,
            port_to=1,
        )
        ACILeafPortBlock.objects.create(
            name="ACILISPortBlockCount2",
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            module_from=2,
            module_to=2,
            port_from=1,
            port_to=1,
        )
        self.assertEqual(self.aci_leaf_interface_selector.port_block_count, 2)


class ACILeafPortBlockTestCase(ACIBaseTestCase):
    """Test case for the ACILeafPortBlock model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACILeafPortBlock model."""
        super().setUpTestData()

        cls.aci_leaf_port_block_name = "ACITestLeafPortBlock"
        cls.aci_leaf_port_block_alias = "ACITestLeafPortBlockAlias"
        cls.aci_leaf_port_block_description = (
            "ACI Test Leaf Port Block for NetBox ACI Plugin"
        )

        # Create objects
        cls.aci_leaf_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACITestLeafPortBlockProfile",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_interface_selector = ACILeafInterfaceSelector.objects.create(
            name="ACITestLeafPortBlockSelector",
            aci_leaf_interface_profile=cls.aci_leaf_interface_profile,
        )
        cls.aci_leaf_port_block = ACILeafPortBlock.objects.create(
            name=cls.aci_leaf_port_block_name,
            name_alias=cls.aci_leaf_port_block_alias,
            description=cls.aci_leaf_port_block_description,
            aci_leaf_interface_selector=cls.aci_leaf_interface_selector,
            module_from=1,
            module_to=2,
            port_from=1,
            port_to=48,
            nb_tenant=cls.nb_tenant,
        )

    def test_aci_leaf_port_block_instance(self) -> None:
        """Test type of created ACI Leaf Port Block."""
        self.assertTrue(isinstance(self.aci_leaf_port_block, ACILeafPortBlock))

    def test_aci_leaf_port_block_str(self) -> None:
        """Test string value of created ACI Leaf Port Block."""
        self.assertEqual(
            self.aci_leaf_port_block.__str__(), self.aci_leaf_port_block.name
        )

    def test_aci_leaf_port_block_name_alias(self) -> None:
        """Test alias of created ACI Leaf Port Block."""
        self.assertEqual(
            self.aci_leaf_port_block.name_alias, self.aci_leaf_port_block_alias
        )

    def test_aci_leaf_port_block_description(self) -> None:
        """Test description of created ACI Leaf Port Block."""
        self.assertEqual(
            self.aci_leaf_port_block.description,
            self.aci_leaf_port_block_description,
        )

    def test_aci_leaf_port_block_module_range(self) -> None:
        """Test the module range of created ACI Leaf Port Block."""
        self.assertEqual(self.aci_leaf_port_block.module_from, 1)
        self.assertEqual(self.aci_leaf_port_block.module_to, 2)

    def test_aci_leaf_port_block_port_range(self) -> None:
        """Test the port range of created ACI Leaf Port Block."""
        self.assertEqual(self.aci_leaf_port_block.port_from, 1)
        self.assertEqual(self.aci_leaf_port_block.port_to, 48)

    def test_aci_leaf_port_block_parent_object(self) -> None:
        """Test parent object of ACI Leaf Port Block is the selector."""
        self.assertEqual(
            self.aci_leaf_port_block.parent_object, self.aci_leaf_interface_selector
        )

    def test_aci_leaf_port_block_aci_fabric(self) -> None:
        """Test aci_fabric returns the ACI Fabric of the related selector."""
        self.assertTrue(isinstance(self.aci_leaf_port_block.aci_fabric, ACIFabric))
        self.assertEqual(self.aci_leaf_port_block.aci_fabric, self.aci_fabric)

    def test_aci_leaf_port_block_to_objectchange(self) -> None:
        """Test to_objectchange sets the selector as the related object."""
        objectchange = self.aci_leaf_port_block.to_objectchange(
            ObjectChangeActionChoices.ACTION_UPDATE
        )
        self.assertEqual(objectchange.related_object, self.aci_leaf_interface_selector)

    def test_aci_leaf_port_block_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with the block."""
        self.assertTrue(isinstance(self.aci_leaf_port_block.nb_tenant, Tenant))
        self.assertEqual(self.aci_leaf_port_block.nb_tenant.name, self.nb_tenant_name)

    def test_aci_leaf_port_block_valid_ranges(self) -> None:
        """Test clean accepts a block whose ranges each start at their end."""
        block = ACILeafPortBlock(
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            name="ACITestLeafPortBlockSingle",
            module_from=1,
            module_to=1,
            port_from=1,
            port_to=1,
        )
        block.full_clean()

    def test_invalid_aci_leaf_port_block_module_from_greater_than_to(
        self,
    ) -> None:
        """Test clean rejects a block whose module range is reversed."""
        block = ACILeafPortBlock(
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            name="ACITestLeafPortBlockModuleReversed",
            module_from=2,
            module_to=1,
            port_from=1,
            port_to=48,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("module_to", cm.exception.error_dict)

    def test_invalid_aci_leaf_port_block_port_from_greater_than_to(
        self,
    ) -> None:
        """Test clean rejects a block whose port range is reversed."""
        block = ACILeafPortBlock(
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            name="ACITestLeafPortBlockPortReversed",
            module_from=1,
            module_to=2,
            port_from=10,
            port_to=5,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("port_to", cm.exception.error_dict)

    def test_invalid_aci_leaf_port_block_module_and_port_from_greater_than_to(
        self,
    ) -> None:
        """Test clean rejects a block with both ranges reversed at once."""
        block = ACILeafPortBlock(
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            name="ACITestLeafPortBlockBothReversed",
            module_from=3,
            module_to=2,
            port_from=10,
            port_to=5,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("module_to", cm.exception.error_dict)
        self.assertIn("port_to", cm.exception.error_dict)

    def test_invalid_aci_leaf_port_block_name(self) -> None:
        """Test validation of ACI Leaf Port Block naming."""
        block = ACILeafPortBlock(
            name="Invalid Name With Spaces",
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            module_from=1,
            module_to=2,
            port_from=1,
            port_to=48,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_leaf_port_block_name_length(self) -> None:
        """Test validation of ACI Leaf Port Block name length."""
        block = ACILeafPortBlock(
            name="A" * 65,
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            module_from=1,
            module_to=2,
            port_from=1,
            port_to=48,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_leaf_port_block_name_alias(self) -> None:
        """Test validation of ACI Leaf Port Block name alias."""
        block = ACILeafPortBlock(
            name="ACILeafPortBlockTest1",
            name_alias="Invalid Alias",
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            module_from=1,
            module_to=2,
            port_from=1,
            port_to=48,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_leaf_port_block_name_alias_length(self) -> None:
        """Test validation of ACI Leaf Port Block name alias length."""
        block = ACILeafPortBlock(
            name="ACILeafPortBlockTest1",
            name_alias="A" * 65,
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            module_from=1,
            module_to=2,
            port_from=1,
            port_to=48,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_leaf_port_block_description(self) -> None:
        """Test validation of ACI Leaf Port Block description."""
        block = ACILeafPortBlock(
            name="ACILeafPortBlockTest1",
            description="Invalid Description: ö",
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            module_from=1,
            module_to=2,
            port_from=1,
            port_to=48,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_leaf_port_block_description_length(self) -> None:
        """Test validation of ACI Leaf Port Block description length."""
        block = ACILeafPortBlock(
            name="ACILeafPortBlockTest1",
            description="A" * 129,
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            module_from=1,
            module_to=2,
            port_from=1,
            port_to=48,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_leaf_port_block_module_from_bound(self) -> None:
        """Test validation of ACI Leaf Port Block module lower bound."""
        block = ACILeafPortBlock(
            name="ACILeafPortBlockBoundModuleFrom",
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            module_from=0,
            module_to=2,
            port_from=1,
            port_to=48,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("module_from", cm.exception.error_dict)

    def test_invalid_aci_leaf_port_block_module_to_bound(self) -> None:
        """Test validation of ACI Leaf Port Block module upper bound."""
        block = ACILeafPortBlock(
            name="ACILeafPortBlockBoundModuleTo",
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            module_from=1,
            module_to=101,
            port_from=1,
            port_to=48,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("module_to", cm.exception.error_dict)

    def test_invalid_aci_leaf_port_block_port_from_bound(self) -> None:
        """Test validation of ACI Leaf Port Block port lower bound."""
        block = ACILeafPortBlock(
            name="ACILeafPortBlockBoundPortFrom",
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            module_from=1,
            module_to=2,
            port_from=0,
            port_to=48,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("port_from", cm.exception.error_dict)

    def test_invalid_aci_leaf_port_block_port_to_bound(self) -> None:
        """Test validation of ACI Leaf Port Block port upper bound."""
        block = ACILeafPortBlock(
            name="ACILeafPortBlockBoundPortTo",
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            module_from=1,
            module_to=2,
            port_from=1,
            port_to=128,
        )
        with self.assertRaises(ValidationError) as cm:
            block.full_clean()
        self.assertIn("port_to", cm.exception.error_dict)

    def test_constraint_unique_aci_leaf_port_block_name_per_selector(
        self,
    ) -> None:
        """Test unique constraint of block name per selector."""
        duplicate_block = ACILeafPortBlock(
            name=self.aci_leaf_port_block_name,
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            module_from=3,
            module_to=4,
            port_from=1,
            port_to=48,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_block.save()

    def test_aci_leaf_port_block_name_reusable_in_another_selector(self) -> None:
        """Test the same block name is allowed in a second selector."""
        other_selector = ACILeafInterfaceSelector.objects.create(
            name="ACITestLeafPortBlockOtherSelector",
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        block = ACILeafPortBlock.objects.create(
            name=self.aci_leaf_port_block_name,
            aci_leaf_interface_selector=other_selector,
            module_from=1,
            module_to=2,
            port_from=1,
            port_to=48,
        )
        self.assertEqual(block.name, self.aci_leaf_port_block_name)
