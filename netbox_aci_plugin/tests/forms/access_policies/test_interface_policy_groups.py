# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError

from ....choices import LeafInterfacePolicyGroupTypeChoices
from ....forms.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroupBulkEditForm,
    ACILeafInterfacePolicyGroupEditForm,
    ACILeafInterfacePolicyGroupFilterForm,
    ACILeafInterfacePolicyGroupImportForm,
)
from ....models.access_policies.aaep import ACIAttachableAccessEntityProfile
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ....models.fabric.fabrics import ACIFabric
from ..base import ACIBaseFormTestCase


class ACILeafInterfacePolicyGroupFormTestCase(ACIBaseFormTestCase):
    """Test case for ACILeafInterfacePolicyGroup forms."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up required objects for ACILeafInterfacePolicyGroup tests."""
        super().setUpTestData()

        cls.aci_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACILeafInterfacePolicyGroupFormTestAAEP",
            aci_fabric=cls.aci_fabric,
        )

        # A separate Fabric and its own AAEP, to prove cross-Fabric
        # assignment is rejected.
        cls.other_fabric = ACIFabric.objects.create(
            name="ACILeafInterfacePolicyGroupFormTestOtherFabric",
            fabric_id=cls.aci_fabric.fabric_id + 1,
            infra_vlan_vid=cls.aci_fabric.infra_vlan_vid + 1,
        )
        cls.other_aci_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACILeafInterfacePolicyGroupFormTestOtherAAEP",
            aci_fabric=cls.other_fabric,
        )

        cls.aci_policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACILeafInterfacePolicyGroupFormTest",
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )

        # A Policy Group with an ACI AAEP already assigned, for the
        # bulk-edit Fabric reassignment cases below.
        cls.aci_policy_group_with_aaep = ACILeafInterfacePolicyGroup.objects.create(
            name="ACILeafInterfacePolicyGroupFormTestWithAAEP",
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            aci_aaep=cls.aci_aaep,
        )

    #
    # EditForm tests
    #

    def test_invalid_aci_leaf_interface_policy_group_field_values(self) -> None:
        """Test invalid ACI Leaf Interface Policy Group field values."""
        form = ACILeafInterfacePolicyGroupEditForm(
            data={
                "name": "ACI Leaf Interface Policy Group Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_fabric": self.aci_fabric,
                "group_type": "invalid",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], [self.name_error_message])
        self.assertEqual(form.errors["name_alias"], [self.name_error_message])
        self.assertEqual(form.errors["description"], [self.description_error_message])
        self.assertIn("group_type", form.errors)

    def test_valid_aci_leaf_interface_policy_group_field_values(self) -> None:
        """Test valid ACI Leaf Interface Policy Group field values."""
        form = ACILeafInterfacePolicyGroupEditForm(
            data={
                "name": "ACILeafInterfacePolicyGroup1",
                "name_alias": "Testing",
                "description": "ACI Leaf Interface Policy Group for NetBox ACI Plugin",
                "aci_fabric": self.aci_fabric,
                "group_type": LeafInterfacePolicyGroupTypeChoices.TYPE_VPC,
                "aci_aaep": self.aci_aaep,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.errors.get("name"), None)
        self.assertEqual(form.errors.get("name_alias"), None)
        self.assertEqual(form.errors.get("description"), None)
        self.assertEqual(form.errors.get("group_type"), None)
        self.assertEqual(form.errors.get("aci_aaep"), None)

    def test_valid_aci_leaf_interface_policy_group_without_aaep(self) -> None:
        """Test the edit form accepts a Policy Group without an ACI AAEP."""
        form = ACILeafInterfacePolicyGroupEditForm(
            data={
                "name": "ACILeafInterfacePolicyGroupNoAAEP",
                "aci_fabric": self.aci_fabric,
                "group_type": LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.errors.get("aci_aaep"), None)

    def test_edit_form_rejects_cross_fabric_aaep(self) -> None:
        """Test the edit form rejects an ACI AAEP from another ACI Fabric."""
        form = ACILeafInterfacePolicyGroupEditForm(
            data={
                "name": "ACILeafInterfacePolicyGroupCrossFabric",
                "aci_fabric": self.aci_fabric,
                "group_type": LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
                "aci_aaep": self.other_aci_aaep,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("aci_aaep", form.errors)

    def test_edit_form_group_type_required_on_create(self) -> None:
        """Test the edit form requires group_type on a new instance."""
        form = ACILeafInterfacePolicyGroupEditForm(
            data={
                "name": "ACILeafInterfacePolicyGroupNoType",
                "aci_fabric": self.aci_fabric,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("group_type", form.errors)
        self.assertFalse(form.fields["group_type"].disabled)

    def test_edit_form_disables_group_type_on_edit(self) -> None:
        """Test the edit form disables group_type when editing an instance."""
        form = ACILeafInterfacePolicyGroupEditForm(instance=self.aci_policy_group)
        self.assertTrue(form.fields["group_type"].disabled)

    def test_edit_form_group_type_survives_edit_round_trip(self) -> None:
        """Test a submitted group_type change is ignored on an edit."""
        form = ACILeafInterfacePolicyGroupEditForm(
            instance=self.aci_policy_group,
            data={
                "name": self.aci_policy_group.name,
                "aci_fabric": self.aci_fabric,
                # A disabled field ignores whatever value is submitted here
                "group_type": LeafInterfacePolicyGroupTypeChoices.TYPE_VPC,
            },
        )
        self.assertTrue(form.is_valid(), form.errors)
        saved_instance = form.save()
        saved_instance.refresh_from_db()
        self.assertEqual(
            saved_instance.group_type, LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS
        )

    #
    # BulkEditForm / FilterForm sanity
    #

    def test_bulk_edit_form_nullable_fields_present(self) -> None:
        """Test the bulk edit form declares its nullable fields."""
        form = ACILeafInterfacePolicyGroupBulkEditForm(data={})
        self.assertIn("aci_fabric", form.fields)
        self.assertIn("aci_aaep", form.fields)
        self.assertIn("description", form.fields)
        self.assertIn("comments", form.fields)
        self.assertEqual(
            set(ACILeafInterfacePolicyGroupBulkEditForm.nullable_fields),
            {"aci_aaep", "comments", "description", "name_alias", "nb_tenant"},
        )

    def test_bulk_edit_form_reassigns_aci_fabric(self) -> None:
        """Test the bulk-edit validation path accepts a Fabric reassignment.

        cls.aci_policy_group carries no ACI AAEP, so reassigning
        aci_fabric alone leaves nothing pointing at the old Fabric.
        """
        form = ACILeafInterfacePolicyGroupBulkEditForm(
            data={
                "pk": [self.aci_policy_group.pk],
                "aci_fabric": self.other_fabric.pk,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

        policy_group = ACILeafInterfacePolicyGroup.objects.get(
            pk=self.aci_policy_group.pk
        )
        policy_group.aci_fabric = form.cleaned_data["aci_fabric"]
        policy_group.full_clean()

    def test_bulk_edit_form_rejects_fabric_reassignment_with_stale_aaep(self) -> None:
        """Test the bulk-edit path rejects a stale cross-Fabric AAEP.

        Matches the domain siblings (ACIPhysicalDomain/ACIRoutedDomain):
        the model's own clean() already rejects an aci_aaep whose Fabric
        no longer matches, so reassigning aci_fabric alone, without also
        reassigning or clearing aci_aaep, must surface that rejection.
        """
        form = ACILeafInterfacePolicyGroupBulkEditForm(
            data={
                "pk": [self.aci_policy_group_with_aaep.pk],
                "aci_fabric": self.other_fabric.pk,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

        policy_group = ACILeafInterfacePolicyGroup.objects.get(
            pk=self.aci_policy_group_with_aaep.pk
        )
        policy_group.aci_fabric = form.cleaned_data["aci_fabric"]
        with self.assertRaises(ValidationError) as cm:
            policy_group.full_clean()
        self.assertIn("aci_aaep", cm.exception.message_dict)

    def test_filter_form_accepts_empty_data(self) -> None:
        """Test the filter form validates with no filters applied."""
        form = ACILeafInterfacePolicyGroupFilterForm(data={})
        self.assertTrue(form.is_valid(), form.errors)

    #
    # Import form tests
    #

    def test_import_form_valid_row_resolves_scoped_aaep(self) -> None:
        """Test the import form resolves the ACI AAEP scoped by ACI Fabric."""
        form = ACILeafInterfacePolicyGroupImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "group_type": LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
                "name": "ACILeafInterfacePolicyGroupImportTest",
                "aci_aaep": self.aci_aaep.name,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.aci_aaep, self.aci_aaep)

    def test_import_form_no_data_returns_early(self) -> None:
        """Test an unbound import form leaves the AAEP queryset unnarrowed."""
        form = ACILeafInterfacePolicyGroupImportForm(data=None)
        self.assertEqual(
            form.fields["aci_aaep"].queryset.count(),
            ACIAttachableAccessEntityProfile.objects.count(),
        )

    def test_import_form_missing_aaep_leaves_queryset_unnarrowed(self) -> None:
        """Test a row with a Fabric but no ACI AAEP column skips narrowing."""
        form = ACILeafInterfacePolicyGroupImportForm(
            data={"aci_fabric": self.aci_fabric.name}
        )
        self.assertEqual(
            form.fields["aci_aaep"].queryset.count(),
            ACIAttachableAccessEntityProfile.objects.count(),
        )

    def test_import_form_update_row_narrows_from_stored_fabric(self) -> None:
        """Test a sparse update row narrows the AAEP by the stored Fabric.

        An update row carries an id plus only the changed columns, so
        aci_fabric is usually absent. AAEP names are only fabric-unique,
        so an unnarrowed queryset could resolve to a foreign Fabric.
        """
        other_fabric = ACIFabric.objects.create(
            name="ACILeafInterfacePolicyGroupImportOtherFabric",
            fabric_id=self.aci_fabric.fabric_id + 1,
            infra_vlan_vid=self.aci_fabric.infra_vlan_vid + 1,
        )
        ACIAttachableAccessEntityProfile.objects.create(
            name=self.aci_aaep.name,
            aci_fabric=other_fabric,
        )
        policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACILeafInterfacePolicyGroupImportUpdateTarget",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            aci_aaep=self.aci_aaep,
        )
        form = ACILeafInterfacePolicyGroupImportForm(
            data={"id": str(policy_group.pk), "aci_aaep": self.aci_aaep.name},
            instance=policy_group,
        )
        self.assertQuerySetEqual(
            form.fields["aci_aaep"].queryset.order_by("pk"),
            ACIAttachableAccessEntityProfile.objects.filter(
                aci_fabric=self.aci_fabric
            ).order_by("pk"),
        )
