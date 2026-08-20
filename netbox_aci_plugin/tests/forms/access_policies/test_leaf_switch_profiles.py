# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Form tests for access-policy Leaf Switch Profile models."""

from ....forms.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlockEditForm,
    ACILeafNodeBlockFilterForm,
    ACILeafNodeBlockImportForm,
    ACILeafSelectorEditForm,
    ACILeafSelectorFilterForm,
    ACILeafSelectorImportForm,
    ACILeafSwitchProfileEditForm,
    ACILeafSwitchProfileInterfaceBindingEditForm,
    ACILeafSwitchProfileInterfaceBindingFilterForm,
    ACILeafSwitchProfileInterfaceBindingImportForm,
)
from ....models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
)
from ....models.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlock,
    ACILeafSelector,
    ACILeafSwitchProfile,
    ACILeafSwitchProfileInterfaceBinding,
)
from ....models.fabric.fabrics import ACIFabric
from ..base import ACIBaseFormTestCase


class ACILeafSwitchProfileFormTestCase(ACIBaseFormTestCase):
    """Test case for the ACILeafSwitchProfile form."""

    def test_invalid_aci_leaf_switch_profile_field_values(self) -> None:
        """Test validation of invalid ACI Leaf Switch Profile field values."""
        form = ACILeafSwitchProfileEditForm(
            data={
                "name": "ACI Leaf Switch Profile Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_fabric": self.aci_fabric,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], [self.name_error_message])
        self.assertEqual(form.errors["name_alias"], [self.name_error_message])
        self.assertEqual(form.errors["description"], [self.description_error_message])

    def test_valid_aci_leaf_switch_profile_field_values(self) -> None:
        """Test validation of valid ACI Leaf Switch Profile field values."""
        form = ACILeafSwitchProfileEditForm(
            data={
                "name": "ACILeafSwitchProfile1",
                "name_alias": "Testing",
                "description": "ACI Leaf Switch Profile for NetBox ACI Plugin",
                "aci_fabric": self.aci_fabric,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)


class ACILeafSelectorFormTestCase(ACIBaseFormTestCase):
    """Test case for the ACILeafSelector forms."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up required objects for ACILeafSelector form tests."""
        super().setUpTestData()
        cls.aci_leaf_switch_profile = ACILeafSwitchProfile.objects.create(
            name="ACILeafSelectorFormTestProfile",
            aci_fabric=cls.aci_fabric,
        )

    #
    # EditForm tests
    #

    def test_invalid_aci_leaf_selector_field_values(self) -> None:
        """Test validation of invalid ACI Leaf Selector field values."""
        form = ACILeafSelectorEditForm(
            data={
                "name": "ACI Leaf Selector Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_leaf_switch_profile": self.aci_leaf_switch_profile,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], [self.name_error_message])
        self.assertEqual(form.errors["name_alias"], [self.name_error_message])
        self.assertEqual(form.errors["description"], [self.description_error_message])

    def test_valid_aci_leaf_selector_field_values(self) -> None:
        """Test validation of valid ACI Leaf Selector field values."""
        form = ACILeafSelectorEditForm(
            data={
                "name": "ACILeafSelector1",
                "name_alias": "Testing",
                "description": "ACI Leaf Selector for NetBox ACI Plugin",
                "aci_leaf_switch_profile": self.aci_leaf_switch_profile,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    #
    # FilterForm sanity
    #

    def test_filter_form_accepts_empty_data(self) -> None:
        """Test the filter form validates with no filters applied."""
        form = ACILeafSelectorFilterForm(data={})
        self.assertTrue(form.is_valid(), form.errors)

    #
    # Import form tests
    #

    def test_import_form_valid_row_resolves_scoped_profile(self) -> None:
        """Test the import form resolves the Profile scoped by ACI Fabric."""
        form = ACILeafSelectorImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_leaf_switch_profile": self.aci_leaf_switch_profile.name,
                "name": "ACILeafSelectorImportTest",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.aci_leaf_switch_profile, self.aci_leaf_switch_profile)

    def test_import_form_no_data_returns_early(self) -> None:
        """Test an unbound import form leaves the Profile queryset alone."""
        form = ACILeafSelectorImportForm(data=None)
        self.assertEqual(
            form.fields["aci_leaf_switch_profile"].queryset.count(),
            ACILeafSwitchProfile.objects.count(),
        )

    def test_import_form_missing_profile_leaves_queryset_unnarrowed(self) -> None:
        """Test a row with a Fabric but no Profile column skips narrowing."""
        form = ACILeafSelectorImportForm(data={"aci_fabric": self.aci_fabric.name})
        self.assertEqual(
            form.fields["aci_leaf_switch_profile"].queryset.count(),
            ACILeafSwitchProfile.objects.count(),
        )

    def test_import_form_update_row_narrows_from_stored_fabric(self) -> None:
        """Test a sparse update row narrows the Profile by the stored Fabric.

        An update row carries an id plus only the changed columns, so
        aci_fabric is usually absent. Profile names are only
        fabric-unique, so an unnarrowed queryset could resolve to a
        foreign Fabric.
        """
        other_fabric = ACIFabric.objects.create(
            name="ACILeafSelectorImportOtherFabric",
            fabric_id=self.aci_fabric.fabric_id + 1,
            infra_vlan_vid=self.aci_fabric.infra_vlan_vid + 1,
        )
        ACILeafSwitchProfile.objects.create(
            name=self.aci_leaf_switch_profile.name,
            aci_fabric=other_fabric,
        )
        aci_leaf_selector = ACILeafSelector.objects.create(
            name="ACILeafSelectorImportUpdateTarget",
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
        )
        form = ACILeafSelectorImportForm(
            data={
                "id": str(aci_leaf_selector.pk),
                "aci_leaf_switch_profile": self.aci_leaf_switch_profile.name,
            },
            instance=aci_leaf_selector,
        )
        self.assertQuerySetEqual(
            form.fields["aci_leaf_switch_profile"].queryset.order_by("pk"),
            ACILeafSwitchProfile.objects.filter(aci_fabric=self.aci_fabric).order_by(
                "pk"
            ),
        )


class ACILeafNodeBlockFormTestCase(ACIBaseFormTestCase):
    """Test case for the ACILeafNodeBlock forms."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up required objects for ACILeafNodeBlock form tests."""
        super().setUpTestData()
        cls.aci_leaf_switch_profile = ACILeafSwitchProfile.objects.create(
            name="ACILeafNodeBlockFormTestProfile",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_selector = ACILeafSelector.objects.create(
            name="ACILeafNodeBlockFormTestSelector",
            aci_leaf_switch_profile=cls.aci_leaf_switch_profile,
        )

    #
    # EditForm tests
    #

    def test_valid_aci_leaf_node_block_field_values(self) -> None:
        """Test validation of valid ACI Leaf Node Block field values."""
        form = ACILeafNodeBlockEditForm(
            data={
                "name": "ACILeafNodeBlock1",
                "name_alias": "Testing",
                "description": "ACI Leaf Node Block for NetBox ACI Plugin",
                "aci_leaf_selector": self.aci_leaf_selector,
                "node_id_from": 101,
                "node_id_to": 104,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_inverted_range_is_invalid(self) -> None:
        """Test that a range with from greater than to is rejected."""
        form = ACILeafNodeBlockEditForm(
            data={
                "name": "ACILeafNodeBlockInverted",
                "aci_leaf_selector": self.aci_leaf_selector,
                "node_id_from": 104,
                "node_id_to": 101,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("node_id_to", form.errors)

    #
    # FilterForm sanity
    #

    def test_filter_form_accepts_empty_data(self) -> None:
        """Test the filter form validates with no filters applied."""
        form = ACILeafNodeBlockFilterForm(data={})
        self.assertTrue(form.is_valid(), form.errors)

    #
    # Import form tests
    #

    def test_import_form_valid_row_resolves_scoped_selector(self) -> None:
        """Test the import form resolves the scoped Selector."""
        form = ACILeafNodeBlockImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_leaf_switch_profile": self.aci_leaf_switch_profile.name,
                "aci_leaf_selector": self.aci_leaf_selector.name,
                "name": "ACILeafNodeBlockImportTest",
                "node_id_from": 201,
                "node_id_to": 204,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.aci_leaf_selector, self.aci_leaf_selector)

    def test_import_form_no_data_returns_early(self) -> None:
        """Test an unbound import form leaves the Selector queryset alone."""
        form = ACILeafNodeBlockImportForm(data=None)
        self.assertEqual(
            form.fields["aci_leaf_selector"].queryset.count(),
            ACILeafSelector.objects.count(),
        )

    def test_import_form_missing_selector_leaves_queryset_unnarrowed(self) -> None:
        """Test a row with no scoping columns at all skips narrowing."""
        form = ACILeafNodeBlockImportForm(data={"aci_fabric": self.aci_fabric.name})
        self.assertEqual(
            form.fields["aci_leaf_selector"].queryset.count(),
            ACILeafSelector.objects.count(),
        )

    def test_import_form_update_row_narrows_from_stored_profile(self) -> None:
        """Test a sparse update row narrows the Selector by the stored Profile.

        An update row carries an id plus only the changed columns, so
        aci_fabric and aci_leaf_switch_profile are usually absent.
        Selector names are only Profile-unique, so an unnarrowed
        queryset could resolve to a foreign Profile.
        """
        other_fabric = ACIFabric.objects.create(
            name="ACILeafNodeBlockImportOtherFabric",
            fabric_id=self.aci_fabric.fabric_id + 1,
            infra_vlan_vid=self.aci_fabric.infra_vlan_vid + 1,
        )
        other_profile = ACILeafSwitchProfile.objects.create(
            name="ACILeafNodeBlockImportOtherProfile",
            aci_fabric=other_fabric,
        )
        ACILeafSelector.objects.create(
            name=self.aci_leaf_selector.name,
            aci_leaf_switch_profile=other_profile,
        )
        aci_leaf_node_block = ACILeafNodeBlock.objects.create(
            name="ACILeafNodeBlockImportUpdateTarget",
            aci_leaf_selector=self.aci_leaf_selector,
            node_id_from=301,
            node_id_to=304,
        )
        form = ACILeafNodeBlockImportForm(
            data={
                "id": str(aci_leaf_node_block.pk),
                "aci_leaf_selector": self.aci_leaf_selector.name,
            },
            instance=aci_leaf_node_block,
        )
        self.assertQuerySetEqual(
            form.fields["aci_leaf_selector"].queryset.order_by("pk"),
            ACILeafSelector.objects.filter(
                aci_leaf_switch_profile=self.aci_leaf_switch_profile
            ).order_by("pk"),
        )

    def test_import_form_update_row_moves_to_named_profile(self) -> None:
        """Test a sparse update row honors an explicitly named Profile.

        A row naming both the target Profile and the target Selector
        moves the Node Block, so the Selector queryset is scoped to the
        named Profile rather than to the stored one.
        """
        target_profile = ACILeafSwitchProfile.objects.create(
            name="ACILeafNodeBlockImportTargetProfile",
            aci_fabric=self.aci_fabric,
        )
        target_selector = ACILeafSelector.objects.create(
            name="ACILeafNodeBlockImportTargetSelector",
            aci_leaf_switch_profile=target_profile,
        )
        # A same-named Selector under a third Profile of the same
        # ACIFabric: a Fabric-wide scope would resolve to both.
        decoy_profile = ACILeafSwitchProfile.objects.create(
            name="ACILeafNodeBlockImportDecoyProfile",
            aci_fabric=self.aci_fabric,
        )
        ACILeafSelector.objects.create(
            name=target_selector.name,
            aci_leaf_switch_profile=decoy_profile,
        )
        aci_leaf_node_block = ACILeafNodeBlock.objects.create(
            name="ACILeafNodeBlockImportMoveTarget",
            aci_leaf_selector=self.aci_leaf_selector,
            node_id_from=311,
            node_id_to=314,
        )
        form = ACILeafNodeBlockImportForm(
            data={
                "id": str(aci_leaf_node_block.pk),
                "aci_leaf_switch_profile": target_profile.name,
                "aci_leaf_selector": target_selector.name,
            },
            instance=aci_leaf_node_block,
        )
        self.assertQuerySetEqual(
            form.fields["aci_leaf_switch_profile"].queryset.order_by("pk"),
            ACILeafSwitchProfile.objects.filter(aci_fabric=self.aci_fabric).order_by(
                "pk"
            ),
        )
        self.assertQuerySetEqual(
            form.fields["aci_leaf_selector"].queryset.order_by("pk"),
            ACILeafSelector.objects.filter(
                aci_leaf_switch_profile=target_profile
            ).order_by("pk"),
        )

    def test_import_form_update_row_moves_to_named_fabric(self) -> None:
        """Test a sparse update row honors an explicitly named Fabric.

        A row naming the target ACIFabric and the target ACILeafSelector,
        but no ACILeafSwitchProfile, scopes the Selector queryset to that
        Fabric rather than pinning it to the stored Profile.
        """
        target_fabric = ACIFabric.objects.create(
            name="ACILeafNodeBlockImportFabricMoveFabric",
            fabric_id=self.aci_fabric.fabric_id + 2,
            infra_vlan_vid=self.aci_fabric.infra_vlan_vid + 2,
        )
        target_profile = ACILeafSwitchProfile.objects.create(
            name="ACILeafNodeBlockImportFabricMoveProfile",
            aci_fabric=target_fabric,
        )
        ACILeafSelector.objects.create(
            name="ACILeafNodeBlockImportFabricMoveSelector",
            aci_leaf_switch_profile=target_profile,
        )
        # A same-named Selector under the stored Profile: pinning to the
        # stored Profile resolves to this one instead.
        ACILeafSelector.objects.create(
            name="ACILeafNodeBlockImportFabricMoveSelector",
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
        )
        aci_leaf_node_block = ACILeafNodeBlock.objects.create(
            name="ACILeafNodeBlockImportFabricMoveBlock",
            aci_leaf_selector=self.aci_leaf_selector,
            node_id_from=331,
            node_id_to=334,
        )
        form = ACILeafNodeBlockImportForm(
            data={
                "id": str(aci_leaf_node_block.pk),
                "aci_fabric": target_fabric.name,
                "aci_leaf_selector": "ACILeafNodeBlockImportFabricMoveSelector",
            },
            instance=aci_leaf_node_block,
        )
        self.assertQuerySetEqual(
            form.fields["aci_leaf_selector"].queryset.order_by("pk"),
            ACILeafSelector.objects.filter(
                aci_leaf_switch_profile__aci_fabric=target_fabric
            ).order_by("pk"),
        )

    def test_import_form_valid_row_scopes_profile_by_fabric(self) -> None:
        """Test the import form scopes the Profile by the named Fabric.

        Profile names are only Fabric-unique, so an unnarrowed queryset
        resolves a repeated name to multiple objects.
        """
        other_fabric = ACIFabric.objects.create(
            name="ACILeafNodeBlockImportProfileScopeFabric",
            fabric_id=self.aci_fabric.fabric_id + 1,
            infra_vlan_vid=self.aci_fabric.infra_vlan_vid + 1,
        )
        ACILeafSwitchProfile.objects.create(
            name=self.aci_leaf_switch_profile.name,
            aci_fabric=other_fabric,
        )
        form = ACILeafNodeBlockImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_leaf_switch_profile": self.aci_leaf_switch_profile.name,
                "aci_leaf_selector": self.aci_leaf_selector.name,
                "name": "ACILeafNodeBlockImportProfileScope",
                "node_id_from": 321,
                "node_id_to": 324,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.aci_leaf_selector, self.aci_leaf_selector)


class ACILeafSwitchProfileInterfaceBindingFormTestCase(ACIBaseFormTestCase):
    """Test case for the ACILeafSwitchProfileInterfaceBinding forms."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up required objects for the Interface Binding form tests."""
        super().setUpTestData()
        cls.aci_leaf_switch_profile = ACILeafSwitchProfile.objects.create(
            name="ACILeafSwitchProfileInterfaceBindingFormTestProfile",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_leaf_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACILeafSwitchProfileInterfaceBindingFormTestIfProfile",
            aci_fabric=cls.aci_fabric,
        )
        cls.other_fabric = ACIFabric.objects.create(
            name="ACILeafSwitchProfileInterfaceBindingFormTestOtherFabric",
            fabric_id=cls.aci_fabric.fabric_id + 1,
            infra_vlan_vid=cls.aci_fabric.infra_vlan_vid + 1,
        )
        cls.other_aci_leaf_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACILeafSwitchProfileInterfaceBindingFormTestOtherIfProfile",
            aci_fabric=cls.other_fabric,
        )

    #
    # EditForm tests
    #

    def test_valid_aci_leaf_switch_profile_interface_binding_field_values(
        self,
    ) -> None:
        """Test valid Interface Binding field values."""
        form = ACILeafSwitchProfileInterfaceBindingEditForm(
            data={
                "aci_leaf_switch_profile": self.aci_leaf_switch_profile,
                "aci_leaf_interface_profile": self.aci_leaf_interface_profile,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_edit_form_rejects_cross_fabric_profiles(self) -> None:
        """Test the edit form rejects Profiles from different ACI Fabrics."""
        form = ACILeafSwitchProfileInterfaceBindingEditForm(
            data={
                "aci_leaf_switch_profile": self.aci_leaf_switch_profile,
                "aci_leaf_interface_profile": self.other_aci_leaf_interface_profile,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("aci_leaf_interface_profile", form.errors)

    #
    # FilterForm sanity
    #

    def test_filter_form_accepts_empty_data(self) -> None:
        """Test the filter form validates with no filters applied."""
        form = ACILeafSwitchProfileInterfaceBindingFilterForm(data={})
        self.assertTrue(form.is_valid(), form.errors)

    #
    # Import form tests
    #

    def test_import_form_valid_row_resolves_scoped_profiles(self) -> None:
        """Test the import form resolves both Profiles scoped by ACI Fabric."""
        form = ACILeafSwitchProfileInterfaceBindingImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_leaf_switch_profile": self.aci_leaf_switch_profile.name,
                "aci_leaf_interface_profile": self.aci_leaf_interface_profile.name,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.aci_leaf_switch_profile, self.aci_leaf_switch_profile)
        self.assertEqual(
            instance.aci_leaf_interface_profile, self.aci_leaf_interface_profile
        )

    def test_import_form_no_data_returns_early(self) -> None:
        """Test an unbound import form leaves both Profile querysets alone."""
        form = ACILeafSwitchProfileInterfaceBindingImportForm(data=None)
        self.assertEqual(
            form.fields["aci_leaf_switch_profile"].queryset.count(),
            ACILeafSwitchProfile.objects.count(),
        )
        self.assertEqual(
            form.fields["aci_leaf_interface_profile"].queryset.count(),
            ACILeafInterfaceProfile.objects.count(),
        )

    def test_import_form_missing_profiles_leave_querysets_unnarrowed(self) -> None:
        """Test a row with a Fabric but no Profile columns skips narrowing."""
        form = ACILeafSwitchProfileInterfaceBindingImportForm(
            data={"aci_fabric": self.aci_fabric.name}
        )
        self.assertEqual(
            form.fields["aci_leaf_switch_profile"].queryset.count(),
            ACILeafSwitchProfile.objects.count(),
        )
        self.assertEqual(
            form.fields["aci_leaf_interface_profile"].queryset.count(),
            ACILeafInterfaceProfile.objects.count(),
        )

    def test_import_form_update_row_narrows_switch_profile_from_stored_fabric(
        self,
    ) -> None:
        """Test a sparse update row narrows the Switch Profile queryset.

        An update row carries an id plus only the changed columns, so
        aci_fabric is usually absent. Profile names are only
        fabric-unique, so an unnarrowed queryset could resolve to a
        foreign Fabric.
        """
        aci_binding = ACILeafSwitchProfileInterfaceBinding.objects.create(
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        form = ACILeafSwitchProfileInterfaceBindingImportForm(
            data={
                "id": str(aci_binding.pk),
                "aci_leaf_switch_profile": self.aci_leaf_switch_profile.name,
            },
            instance=aci_binding,
        )
        self.assertQuerySetEqual(
            form.fields["aci_leaf_switch_profile"].queryset.order_by("pk"),
            ACILeafSwitchProfile.objects.filter(aci_fabric=self.aci_fabric).order_by(
                "pk"
            ),
        )

    def test_import_form_update_row_narrows_interface_profile_from_stored_fabric(
        self,
    ) -> None:
        """Test a sparse update row narrows the Interface Profile queryset."""
        aci_binding = ACILeafSwitchProfileInterfaceBinding.objects.create(
            aci_leaf_switch_profile=self.aci_leaf_switch_profile,
            aci_leaf_interface_profile=self.aci_leaf_interface_profile,
        )
        form = ACILeafSwitchProfileInterfaceBindingImportForm(
            data={
                "id": str(aci_binding.pk),
                "aci_leaf_interface_profile": self.aci_leaf_interface_profile.name,
            },
            instance=aci_binding,
        )
        self.assertQuerySetEqual(
            form.fields["aci_leaf_interface_profile"].queryset.order_by("pk"),
            ACILeafInterfaceProfile.objects.filter(aci_fabric=self.aci_fabric).order_by(
                "pk"
            ),
        )
