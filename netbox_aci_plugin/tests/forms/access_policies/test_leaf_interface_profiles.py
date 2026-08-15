# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Form tests for access-policy Leaf Interface Profile models."""

from ....choices import LeafInterfacePolicyGroupTypeChoices
from ....forms.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfileEditForm,
    ACILeafInterfaceSelectorEditForm,
    ACILeafInterfaceSelectorFilterForm,
    ACILeafInterfaceSelectorImportForm,
    ACILeafPortBlockEditForm,
    ACILeafPortBlockFilterForm,
    ACILeafPortBlockImportForm,
)
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ....models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
    ACILeafInterfaceSelector,
    ACILeafPortBlock,
)
from ....models.fabric.fabrics import ACIFabric
from ..base import ACIBaseFormTestCase


class ACILeafInterfaceProfileFormTestCase(ACIBaseFormTestCase):
    """Test case for the ACILeafInterfaceProfile form."""

    def test_invalid_aci_leaf_interface_profile_field_values(self) -> None:
        """Test invalid ACI Leaf Interface Profile field values."""
        form = ACILeafInterfaceProfileEditForm(
            data={
                "name": "ACI Leaf Interface Profile Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_fabric": self.aci_fabric,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], [self.name_error_message])
        self.assertEqual(form.errors["name_alias"], [self.name_error_message])
        self.assertEqual(form.errors["description"], [self.description_error_message])

    def test_valid_aci_leaf_interface_profile_field_values(self) -> None:
        """Test validation of valid ACI Leaf Interface Profile field values."""
        form = ACILeafInterfaceProfileEditForm(
            data={
                "name": "ACILeafInterfaceProfile1",
                "name_alias": "Testing",
                "description": "ACI Leaf Interface Profile for NetBox ACI Plugin",
                "aci_fabric": self.aci_fabric,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)


class ACILeafInterfaceSelectorFormTestCase(ACIBaseFormTestCase):
    """Test case for the ACILeafInterfaceSelector forms."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up required objects for ACILeafInterfaceSelector form tests."""
        super().setUpTestData()
        cls.aci_leaf_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACILeafInterfaceSelectorFormTestProfile",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_interface_policy_group = (
            ACILeafInterfacePolicyGroup.objects.create(
                name="ACILeafInterfaceSelectorFormTestPolicyGroup",
                aci_fabric=cls.aci_fabric,
                group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            )
        )

        # A separate Fabric and its own Policy Group, to prove
        # cross-Fabric assignment is rejected.
        cls.other_fabric = ACIFabric.objects.create(
            name="ACILeafInterfaceSelectorFormTestOtherFabric",
            fabric_id=cls.aci_fabric.fabric_id + 1,
            infra_vlan_vid=cls.aci_fabric.infra_vlan_vid + 1,
        )
        cls.other_aci_leaf_interface_policy_group = (
            ACILeafInterfacePolicyGroup.objects.create(
                name="ACILeafInterfaceSelectorFormTestOtherPolicyGroup",
                aci_fabric=cls.other_fabric,
                group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            )
        )

        # An access and a bundle group may legally share one name per
        # Fabric, since each uniqueness constraint is type-scoped.
        cls.shared_name = "ACILeafInterfaceSelectorFormTestSharedName"
        cls.shared_access_policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name=cls.shared_name,
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        cls.shared_bundle_policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name=cls.shared_name,
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_PC,
        )

    #
    # EditForm tests
    #

    def test_invalid_aci_leaf_interface_selector_field_values(self) -> None:
        """Test invalid ACI Leaf Interface Selector field values."""
        form = ACILeafInterfaceSelectorEditForm(
            data={
                "name": "ACI Leaf Interface Selector Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_leaf_interface_profile": self.aci_leaf_interface_profile,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], [self.name_error_message])
        self.assertEqual(form.errors["name_alias"], [self.name_error_message])
        self.assertEqual(form.errors["description"], [self.description_error_message])

    def test_valid_aci_leaf_interface_selector_field_values(self) -> None:
        """Test valid ACI Leaf Interface Selector field values."""
        form = ACILeafInterfaceSelectorEditForm(
            data={
                "name": "ACILeafInterfaceSelector1",
                "name_alias": "Testing",
                "description": "ACI Leaf Interface Selector for NetBox ACI Plugin",
                "aci_leaf_interface_profile": self.aci_leaf_interface_profile,
                "aci_leaf_interface_policy_group": self.aci_leaf_interface_policy_group,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_aci_leaf_interface_selector_without_policy_group(self) -> None:
        """Test the edit form accepts a Selector without a Policy Group."""
        form = ACILeafInterfaceSelectorEditForm(
            data={
                "name": "ACILeafInterfaceSelectorNoPolicyGroup",
                "aci_leaf_interface_profile": self.aci_leaf_interface_profile,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_edit_form_rejects_cross_fabric_policy_group(self) -> None:
        """Test the edit form rejects a cross-fabric Policy Group."""
        form = ACILeafInterfaceSelectorEditForm(
            data={
                "name": "ACILeafInterfaceSelectorCrossFabric",
                "aci_leaf_interface_profile": self.aci_leaf_interface_profile,
                "aci_leaf_interface_policy_group": (
                    self.other_aci_leaf_interface_policy_group
                ),
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("aci_leaf_interface_policy_group", form.errors)

    #
    # FilterForm sanity
    #

    def test_filter_form_accepts_empty_data(self) -> None:
        """Test the filter form validates with no filters applied."""
        form = ACILeafInterfaceSelectorFilterForm(data={})
        self.assertTrue(form.is_valid(), form.errors)

    #
    # Import form tests
    #

    def test_import_form_valid_row_resolves_scoped_profile(self) -> None:
        """Test the import form resolves the Profile scoped by ACI Fabric."""
        form = ACILeafInterfaceSelectorImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_leaf_interface_profile": self.aci_leaf_interface_profile.name,
                "name": "ACILeafInterfaceSelectorImportTest",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(
            instance.aci_leaf_interface_profile, self.aci_leaf_interface_profile
        )

    def test_import_form_no_data_returns_early(self) -> None:
        """Test an unbound import form leaves the Profile queryset alone."""
        form = ACILeafInterfaceSelectorImportForm(data=None)
        self.assertEqual(
            form.fields["aci_leaf_interface_profile"].queryset.count(),
            ACILeafInterfaceProfile.objects.count(),
        )

    def test_import_form_missing_profile_leaves_queryset_unnarrowed(self) -> None:
        """Test a row with a Fabric but no Profile column skips narrowing."""
        form = ACILeafInterfaceSelectorImportForm(
            data={"aci_fabric": self.aci_fabric.name}
        )
        self.assertEqual(
            form.fields["aci_leaf_interface_profile"].queryset.count(),
            ACILeafInterfaceProfile.objects.count(),
        )

    def test_import_form_update_row_narrows_from_stored_fabric(self) -> None:
        """Test a sparse update row narrows the Profile by the stored Fabric.

        An update row carries an id plus only the changed columns, so
        aci_fabric is usually absent. Profile names are only
        fabric-unique, so an unnarrowed queryset could resolve to a
        foreign Fabric.
        """
        ACILeafInterfaceProfile.objects.create(
            name=self.aci_leaf_interface_profile.name,
            aci_fabric=self.other_fabric,
        )
        aci_leaf_interface_selector = ACILeafInterfaceSelector.objects.create(
            name="ACILeafInterfaceSelectorImportUpdateTarget",
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        form = ACILeafInterfaceSelectorImportForm(
            data={
                "id": str(aci_leaf_interface_selector.pk),
                "aci_leaf_interface_profile": self.aci_leaf_interface_profile.name,
            },
            instance=aci_leaf_interface_selector,
        )
        self.assertQuerySetEqual(
            form.fields["aci_leaf_interface_profile"].queryset.order_by("pk"),
            ACILeafInterfaceProfile.objects.filter(aci_fabric=self.aci_fabric).order_by(
                "pk"
            ),
        )

    def test_import_form_valid_row_resolves_scoped_policy_group(self) -> None:
        """Test the import form resolves the scoped Policy Group."""
        form = ACILeafInterfaceSelectorImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_leaf_interface_profile": self.aci_leaf_interface_profile.name,
                "name": "ACILeafInterfaceSelectorImportPolicyGroupTest",
                "aci_leaf_interface_policy_group": (
                    self.aci_leaf_interface_policy_group.name
                ),
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(
            instance.aci_leaf_interface_policy_group,
            self.aci_leaf_interface_policy_group,
        )

    def test_import_form_missing_policy_group_leaves_queryset_unnarrowed(
        self,
    ) -> None:
        """Test a row with no Policy Group column skips narrowing."""
        form = ACILeafInterfaceSelectorImportForm(
            data={"aci_fabric": self.aci_fabric.name}
        )
        self.assertEqual(
            form.fields["aci_leaf_interface_policy_group"].queryset.count(),
            ACILeafInterfacePolicyGroup.objects.count(),
        )

    def test_import_form_update_row_narrows_policy_group_from_stored_fabric(
        self,
    ) -> None:
        """Test a sparse update row narrows the Policy Group by stored Fabric.

        An update row carries an id plus only the changed columns, so
        aci_fabric is usually absent. Policy Group names repeat across
        Fabrics, so an unnarrowed queryset could resolve to a foreign
        Fabric.
        """
        ACILeafInterfacePolicyGroup.objects.create(
            name=self.aci_leaf_interface_policy_group.name,
            aci_fabric=self.other_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        aci_leaf_interface_selector = ACILeafInterfaceSelector.objects.create(
            name="ACILeafInterfaceSelectorImportPolicyGroupUpdateTarget",
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
            aci_leaf_interface_policy_group=self.aci_leaf_interface_policy_group,
        )
        form = ACILeafInterfaceSelectorImportForm(
            data={
                "id": str(aci_leaf_interface_selector.pk),
                "aci_leaf_interface_policy_group": (
                    self.aci_leaf_interface_policy_group.name
                ),
            },
            instance=aci_leaf_interface_selector,
        )
        self.assertQuerySetEqual(
            form.fields["aci_leaf_interface_policy_group"].queryset.order_by("pk"),
            ACILeafInterfacePolicyGroup.objects.filter(
                aci_fabric=self.aci_fabric
            ).order_by("pk"),
        )

    def test_import_form_narrows_policy_group_by_group_type(self) -> None:
        """Test the group type column disambiguates a shared name.

        An access and a bundle group may share one name per Fabric, so
        a row naming only the Fabric cannot resolve either.
        """
        form = ACILeafInterfaceSelectorImportForm(
            data={
                "name": "ACILeafInterfaceSelectorImportSharedNameRow",
                "aci_fabric": self.aci_fabric.name,
                "aci_leaf_interface_profile": (self.aci_leaf_interface_profile.name),
                "aci_leaf_interface_policy_group": self.shared_name,
                "aci_leaf_interface_policy_group_type": (
                    LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS
                ),
            },
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(
            instance.aci_leaf_interface_policy_group,
            self.shared_access_policy_group,
        )

    def test_import_form_shared_policy_group_name_without_type_is_ambiguous(
        self,
    ) -> None:
        """Test a shared name without the group type column is rejected."""
        form = ACILeafInterfaceSelectorImportForm(
            data={
                "name": "ACILeafInterfaceSelectorImportAmbiguousRow",
                "aci_fabric": self.aci_fabric.name,
                "aci_leaf_interface_profile": (self.aci_leaf_interface_profile.name),
                "aci_leaf_interface_policy_group": self.shared_name,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            "aci_leaf_interface_policy_group",
            form.errors,
        )


class ACILeafPortBlockFormTestCase(ACIBaseFormTestCase):
    """Test case for the ACILeafPortBlock forms."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up required objects for ACILeafPortBlock form tests."""
        super().setUpTestData()
        cls.aci_leaf_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACILeafPortBlockFormTestProfile",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_interface_selector = ACILeafInterfaceSelector.objects.create(
            name="ACILeafPortBlockFormTestSelector",
            aci_leaf_interface_profile=cls.aci_leaf_interface_profile,
        )

    #
    # EditForm tests
    #

    def test_valid_aci_leaf_port_block_field_values(self) -> None:
        """Test validation of valid ACI Leaf Port Block field values."""
        form = ACILeafPortBlockEditForm(
            data={
                "name": "ACILeafPortBlock1",
                "name_alias": "Testing",
                "description": "ACI Leaf Port Block for NetBox ACI Plugin",
                "aci_leaf_interface_selector": self.aci_leaf_interface_selector,
                "module_from": 1,
                "module_to": 2,
                "port_from": 1,
                "port_to": 48,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_inverted_module_range_is_invalid(self) -> None:
        """Test that a module range with from greater than to is rejected."""
        form = ACILeafPortBlockEditForm(
            data={
                "name": "ACILeafPortBlockModuleInverted",
                "aci_leaf_interface_selector": self.aci_leaf_interface_selector,
                "module_from": 2,
                "module_to": 1,
                "port_from": 1,
                "port_to": 48,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("module_to", form.errors)

    def test_inverted_port_range_is_invalid(self) -> None:
        """Test that a port range with from greater than to is rejected."""
        form = ACILeafPortBlockEditForm(
            data={
                "name": "ACILeafPortBlockPortInverted",
                "aci_leaf_interface_selector": self.aci_leaf_interface_selector,
                "module_from": 1,
                "module_to": 2,
                "port_from": 48,
                "port_to": 1,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("port_to", form.errors)

    #
    # FilterForm sanity
    #

    def test_filter_form_accepts_empty_data(self) -> None:
        """Test the filter form validates with no filters applied."""
        form = ACILeafPortBlockFilterForm(data={})
        self.assertTrue(form.is_valid(), form.errors)

    #
    # Import form tests
    #

    def test_import_form_valid_row_resolves_scoped_selector(self) -> None:
        """Test the import form resolves the scoped Selector."""
        form = ACILeafPortBlockImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_leaf_interface_profile": self.aci_leaf_interface_profile.name,
                "aci_leaf_interface_selector": self.aci_leaf_interface_selector.name,
                "name": "ACILeafPortBlockImportTest",
                "module_from": 1,
                "module_to": 2,
                "port_from": 1,
                "port_to": 48,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(
            instance.aci_leaf_interface_selector, self.aci_leaf_interface_selector
        )

    def test_import_form_no_data_returns_early(self) -> None:
        """Test an unbound import form leaves the Selector queryset alone."""
        form = ACILeafPortBlockImportForm(data=None)
        self.assertEqual(
            form.fields["aci_leaf_interface_selector"].queryset.count(),
            ACILeafInterfaceSelector.objects.count(),
        )

    def test_import_form_missing_selector_leaves_queryset_unnarrowed(self) -> None:
        """Test a row with no scoping columns at all skips narrowing."""
        form = ACILeafPortBlockImportForm(data={"aci_fabric": self.aci_fabric.name})
        self.assertEqual(
            form.fields["aci_leaf_interface_selector"].queryset.count(),
            ACILeafInterfaceSelector.objects.count(),
        )

    def test_import_form_update_row_narrows_from_stored_profile(self) -> None:
        """Test a sparse update row narrows the Selector by the stored Profile.

        An update row carries an id plus only the changed columns, so
        aci_fabric and aci_leaf_interface_profile are usually absent.
        Selector names are only Profile-unique, so an unnarrowed
        queryset could resolve to a foreign Profile.
        """
        other_fabric = ACIFabric.objects.create(
            name="ACILeafPortBlockImportOtherFabric",
            fabric_id=self.aci_fabric.fabric_id + 1,
            infra_vlan_vid=self.aci_fabric.infra_vlan_vid + 1,
        )
        other_profile = ACILeafInterfaceProfile.objects.create(
            name="ACILeafPortBlockImportOtherProfile",
            aci_fabric=other_fabric,
        )
        ACILeafInterfaceSelector.objects.create(
            name=self.aci_leaf_interface_selector.name,
            aci_leaf_interface_profile=other_profile,
        )
        aci_leaf_port_block = ACILeafPortBlock.objects.create(
            name="ACILeafPortBlockImportUpdateTarget",
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            module_from=1,
            module_to=2,
            port_from=1,
            port_to=48,
        )
        form = ACILeafPortBlockImportForm(
            data={
                "id": str(aci_leaf_port_block.pk),
                "aci_leaf_interface_selector": self.aci_leaf_interface_selector.name,
            },
            instance=aci_leaf_port_block,
        )
        self.assertQuerySetEqual(
            form.fields["aci_leaf_interface_selector"].queryset.order_by("pk"),
            ACILeafInterfaceSelector.objects.filter(
                aci_leaf_interface_profile=self.aci_leaf_interface_profile
            ).order_by("pk"),
        )

    def test_import_form_update_row_moves_to_named_profile(self) -> None:
        """Test a sparse update row honors an explicitly named Profile.

        A row naming both the target Profile and the target Selector
        moves the Port Block, so the Selector queryset is scoped to the
        named Profile rather than to the stored one.
        """
        target_profile = ACILeafInterfaceProfile.objects.create(
            name="ACILeafPortBlockImportTargetProfile",
            aci_fabric=self.aci_fabric,
        )
        target_selector = ACILeafInterfaceSelector.objects.create(
            name="ACILeafPortBlockImportTargetSelector",
            aci_leaf_interface_profile=target_profile,
        )
        # A same-named Selector under a third Profile of the same
        # ACIFabric: a Fabric-wide scope would resolve to both.
        decoy_profile = ACILeafInterfaceProfile.objects.create(
            name="ACILeafPortBlockImportDecoyProfile",
            aci_fabric=self.aci_fabric,
        )
        ACILeafInterfaceSelector.objects.create(
            name=target_selector.name,
            aci_leaf_interface_profile=decoy_profile,
        )
        aci_leaf_port_block = ACILeafPortBlock.objects.create(
            name="ACILeafPortBlockImportMoveTarget",
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            module_from=3,
            module_to=4,
            port_from=1,
            port_to=48,
        )
        form = ACILeafPortBlockImportForm(
            data={
                "id": str(aci_leaf_port_block.pk),
                "aci_leaf_interface_profile": target_profile.name,
                "aci_leaf_interface_selector": target_selector.name,
            },
            instance=aci_leaf_port_block,
        )
        self.assertQuerySetEqual(
            form.fields["aci_leaf_interface_profile"].queryset.order_by("pk"),
            ACILeafInterfaceProfile.objects.filter(aci_fabric=self.aci_fabric).order_by(
                "pk"
            ),
        )
        self.assertQuerySetEqual(
            form.fields["aci_leaf_interface_selector"].queryset.order_by("pk"),
            ACILeafInterfaceSelector.objects.filter(
                aci_leaf_interface_profile=target_profile
            ).order_by("pk"),
        )

    def test_import_form_update_row_moves_to_named_fabric(self) -> None:
        """Test a sparse update row honors an explicitly named Fabric.

        A row naming the target ACIFabric and the target
        ACILeafInterfaceSelector, but no ACILeafInterfaceProfile, scopes
        the Selector queryset to that Fabric rather than pinning it to
        the stored Profile.
        """
        target_fabric = ACIFabric.objects.create(
            name="ACILeafPortBlockImportFabricMoveFabric",
            fabric_id=self.aci_fabric.fabric_id + 2,
            infra_vlan_vid=self.aci_fabric.infra_vlan_vid + 2,
        )
        target_profile = ACILeafInterfaceProfile.objects.create(
            name="ACILeafPortBlockImportFabricMoveProfile",
            aci_fabric=target_fabric,
        )
        ACILeafInterfaceSelector.objects.create(
            name="ACILeafPortBlockImportFabricMoveSelector",
            aci_leaf_interface_profile=target_profile,
        )
        # A same-named Selector under the stored Profile: pinning to the
        # stored Profile resolves to this one instead.
        ACILeafInterfaceSelector.objects.create(
            name="ACILeafPortBlockImportFabricMoveSelector",
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        aci_leaf_port_block = ACILeafPortBlock.objects.create(
            name="ACILeafPortBlockImportFabricMoveBlock",
            aci_leaf_interface_selector=self.aci_leaf_interface_selector,
            module_from=5,
            module_to=6,
            port_from=1,
            port_to=48,
        )
        form = ACILeafPortBlockImportForm(
            data={
                "id": str(aci_leaf_port_block.pk),
                "aci_fabric": target_fabric.name,
                "aci_leaf_interface_selector": (
                    "ACILeafPortBlockImportFabricMoveSelector"
                ),
            },
            instance=aci_leaf_port_block,
        )
        self.assertQuerySetEqual(
            form.fields["aci_leaf_interface_selector"].queryset.order_by("pk"),
            ACILeafInterfaceSelector.objects.filter(
                aci_leaf_interface_profile__aci_fabric=target_fabric
            ).order_by("pk"),
        )

    def test_import_form_valid_row_scopes_profile_by_fabric(self) -> None:
        """Test the import form scopes the Profile by the named Fabric.

        Profile names are only Fabric-unique, so an unnarrowed queryset
        resolves a repeated name to multiple objects.
        """
        other_fabric = ACIFabric.objects.create(
            name="ACILeafPortBlockImportProfileScopeFabric",
            fabric_id=self.aci_fabric.fabric_id + 1,
            infra_vlan_vid=self.aci_fabric.infra_vlan_vid + 1,
        )
        ACILeafInterfaceProfile.objects.create(
            name=self.aci_leaf_interface_profile.name,
            aci_fabric=other_fabric,
        )
        form = ACILeafPortBlockImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_leaf_interface_profile": self.aci_leaf_interface_profile.name,
                "aci_leaf_interface_selector": self.aci_leaf_interface_selector.name,
                "name": "ACILeafPortBlockImportProfileScope",
                "module_from": 1,
                "module_to": 2,
                "port_from": 1,
                "port_to": 48,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(
            instance.aci_leaf_interface_selector, self.aci_leaf_interface_selector
        )
