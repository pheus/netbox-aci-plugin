# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Form tests for the access-policy Leaf Interface Override model."""

from ....choices import LeafInterfacePolicyGroupTypeChoices
from ....forms.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverrideEditForm,
    ACILeafInterfaceOverrideFilterForm,
    ACILeafInterfaceOverrideImportForm,
)
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ....models.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverride,
)
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.node_interfaces import ACINodeInterface
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ..base import ACIBaseFormTestCase


class ACILeafInterfaceOverrideFormTestCase(ACIBaseFormTestCase):
    """Test case for the ACILeafInterfaceOverride forms."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up required objects for the Leaf Interface Override tests."""
        super().setUpTestData()
        cls.aci_node = ACINode.objects.create(
            name="ACILeafInterfaceOverrideFormTestNode",
            aci_pod=cls.aci_pod,
            node_id=101,
        )
        cls.aci_node_interface = ACINodeInterface.objects.create(
            aci_node=cls.aci_node, module=1, port=1
        )
        cls.aci_policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACILeafInterfaceOverrideFormTestPolicyGroup",
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        cls.aci_pc_policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACILeafInterfaceOverrideFormTestPCPolicyGroup",
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_PC,
        )
        cls.other_fabric = ACIFabric.objects.create(
            name="ACILeafInterfaceOverrideFormTestOtherFabric",
            fabric_id=cls.aci_fabric.fabric_id + 1,
            infra_vlan_vid=cls.aci_fabric.infra_vlan_vid + 1,
        )
        cls.other_aci_policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACILeafInterfaceOverrideFormTestOtherPolicyGroup",
            aci_fabric=cls.other_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )

    def free_node_interface(self, port: int) -> ACINodeInterface:
        """Return an unbound ACI Node Interface on the shared test Node."""
        return ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=1, port=port
        )

    @staticmethod
    def _delete_unused_import_fields(form, record: dict) -> None:
        """Delete fields BulkImportView would delete for an update row.

        Mirrors bulk_views.py's own _process_import_records: for a row
        carrying an id, every field whose column is absent from the
        record is removed before validation, so no field is required
        to modify an existing object. The plugin's own tests construct
        the form directly rather than driving the view, so this must
        be replicated by hand to reproduce the real update contract.
        """
        for field_name in [name for name in form.fields if name not in record]:
            del form.fields[field_name]

    #
    # EditForm tests
    #

    def test_invalid_aci_leaf_interface_override_field_values(self) -> None:
        """Test invalid ACI Leaf Interface Override field values."""
        form = ACILeafInterfaceOverrideEditForm(
            data={
                "aci_node_interface": self.free_node_interface(2),
                "aci_leaf_interface_policy_group": self.aci_policy_group,
                "description": "Invalid Description: ö",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["description"], [self.description_error_message])

    def test_valid_aci_leaf_interface_override_field_values(self) -> None:
        """Test valid ACI Leaf Interface Override field values."""
        form = ACILeafInterfaceOverrideEditForm(
            data={
                "aci_node_interface": self.aci_node_interface,
                "aci_leaf_interface_policy_group": self.aci_policy_group,
                "description": "ACI Leaf Interface Override for NetBox ACI Plugin",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_edit_form_rejects_cross_fabric_policy_group(self) -> None:
        """Test the edit form rejects a cross-fabric Policy Group."""
        form = ACILeafInterfaceOverrideEditForm(
            data={
                "aci_node_interface": self.free_node_interface(3),
                "aci_leaf_interface_policy_group": self.other_aci_policy_group,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("aci_leaf_interface_policy_group", form.errors)

    def test_edit_form_rejects_non_access_policy_group(self) -> None:
        """Test the edit form rejects a non-Access Policy Group."""
        form = ACILeafInterfaceOverrideEditForm(
            data={
                "aci_node_interface": self.free_node_interface(4),
                "aci_leaf_interface_policy_group": self.aci_pc_policy_group,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("aci_leaf_interface_policy_group", form.errors)

    #
    # FilterForm sanity
    #

    def test_filter_form_accepts_empty_data(self) -> None:
        """Test the filter form validates with no filters applied."""
        form = ACILeafInterfaceOverrideFilterForm(data={})
        self.assertTrue(form.is_valid(), form.errors)

    #
    # Import form tests
    #

    def test_import_form_valid_row_resolves_scoped_node_interface(self) -> None:
        """Test the import form resolves the Node Interface by coordinates."""
        form = ACILeafInterfaceOverrideImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node.name,
                "module": 1,
                "port": 1,
                "aci_leaf_interface_policy_group": self.aci_policy_group.name,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.aci_node_interface, self.aci_node_interface)

    def test_import_form_no_data_returns_early(self) -> None:
        """Test an unbound import form leaves the Pod queryset alone."""
        form = ACILeafInterfaceOverrideImportForm(data=None)
        self.assertEqual(
            form.fields["aci_pod"].queryset.count(), ACIPod.objects.count()
        )

    def test_import_form_missing_parent_leaves_queryset_unnarrowed(self) -> None:
        """Test a row with no Fabric column skips narrowing the Pod."""
        form = ACILeafInterfaceOverrideImportForm(data={"aci_pod": self.aci_pod.name})
        self.assertEqual(
            form.fields["aci_pod"].queryset.count(), ACIPod.objects.count()
        )

    def test_import_form_update_row_narrows_pod_from_stored_fabric(self) -> None:
        """Test a sparse update row narrows the Pod queryset.

        An update row carries an id plus only the changed columns, so
        aci_fabric is usually absent.
        """
        aci_override = ACILeafInterfaceOverride.objects.create(
            aci_node_interface=self.aci_node_interface,
            aci_leaf_interface_policy_group=self.aci_policy_group,
        )
        form = ACILeafInterfaceOverrideImportForm(
            data={
                "id": str(aci_override.pk),
                "aci_pod": self.aci_pod.name,
            },
            instance=aci_override,
        )
        self.assertQuerySetEqual(
            form.fields["aci_pod"].queryset.order_by("pk"),
            ACIPod.objects.filter(aci_fabric=self.aci_fabric).order_by("pk"),
        )

    def test_import_form_rejects_row_with_no_matching_port(self) -> None:
        """Test the import form rejects coordinates matching no port."""
        form = ACILeafInterfaceOverrideImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node.name,
                "module": 1,
                "port": 99,
                "aci_leaf_interface_policy_group": self.aci_policy_group.name,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("port", form.errors)

    def test_import_form_rejects_row_with_duplicate_override(self) -> None:
        """Test the import form rejects a port that already has an Override."""
        ACILeafInterfaceOverride.objects.create(
            aci_node_interface=self.aci_node_interface,
            aci_leaf_interface_policy_group=self.aci_policy_group,
        )
        form = ACILeafInterfaceOverrideImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node.name,
                "module": 1,
                "port": 1,
                "aci_leaf_interface_policy_group": self.aci_policy_group.name,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("port", form.errors)

    def test_import_form_update_row_reresolves_own_port(self) -> None:
        """Test an update row re-resolves its own port."""
        aci_override = ACILeafInterfaceOverride.objects.create(
            aci_node_interface=self.aci_node_interface,
            aci_leaf_interface_policy_group=self.aci_policy_group,
        )
        form = ACILeafInterfaceOverrideImportForm(
            data={
                "id": str(aci_override.pk),
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node.name,
                "module": 1,
                "port": 1,
                "sub_port": 0,
                "description": "Updated",
                "aci_leaf_interface_policy_group": self.aci_policy_group.name,
            },
            instance=aci_override,
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.aci_node_interface, self.aci_node_interface)
        self.assertEqual(instance.description, "Updated")

    def test_import_form_applies_module_and_sub_port_defaults(self) -> None:
        """Test the import form applies the module and sub port defaults."""
        free_interface = ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=1, port=5
        )
        form = ACILeafInterfaceOverrideImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node.name,
                "port": 5,
                "aci_leaf_interface_policy_group": self.aci_policy_group.name,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.aci_node_interface, free_interface)

    def test_import_form_update_row_rejects_blank_module(self) -> None:
        """Test a blank module on an update row is rejected, not defaulted.

        Defaulting it would silently re-point the Override at module 1,
        which is a different port.
        """
        aci_override = ACILeafInterfaceOverride.objects.create(
            aci_node_interface=self.aci_node_interface,
            aci_leaf_interface_policy_group=self.aci_policy_group,
        )
        record = {
            "id": str(aci_override.pk),
            "aci_fabric": self.aci_fabric.name,
            "aci_pod": self.aci_pod.name,
            "aci_node": self.aci_node.name,
            "module": "",
            "port": 1,
            "sub_port": 0,
            "aci_leaf_interface_policy_group": self.aci_policy_group.name,
        }
        form = ACILeafInterfaceOverrideImportForm(data=record, instance=aci_override)
        self._delete_unused_import_fields(form, record)

        self.assertFalse(form.is_valid())
        self.assertIn("module", form.errors)

    def test_import_form_update_row_rejects_blank_sub_port(self) -> None:
        """Test a blank sub port on an update row is not defaulted."""
        aci_override = ACILeafInterfaceOverride.objects.create(
            aci_node_interface=self.aci_node_interface,
            aci_leaf_interface_policy_group=self.aci_policy_group,
        )
        record = {
            "id": str(aci_override.pk),
            "aci_fabric": self.aci_fabric.name,
            "aci_pod": self.aci_pod.name,
            "aci_node": self.aci_node.name,
            "module": 1,
            "port": 1,
            "sub_port": "",
            "aci_leaf_interface_policy_group": self.aci_policy_group.name,
        }
        form = ACILeafInterfaceOverrideImportForm(data=record, instance=aci_override)
        self._delete_unused_import_fields(form, record)

        self.assertFalse(form.is_valid())
        self.assertIn("sub_port", form.errors)

    def test_import_form_update_row_rejects_partial_coordinates(self) -> None:
        """Test an update row omitting only some coordinate columns fails.

        The import view deletes the fields of absent columns, so the
        interface cannot be re-resolved and the row would otherwise save
        unchanged while being reported as updated.
        """
        aci_override = ACILeafInterfaceOverride.objects.create(
            aci_node_interface=self.aci_node_interface,
            aci_leaf_interface_policy_group=self.aci_policy_group,
        )
        self.free_node_interface(port=7)
        record = {
            "id": str(aci_override.pk),
            "aci_fabric": self.aci_fabric.name,
            "aci_pod": self.aci_pod.name,
            "aci_node": self.aci_node.name,
            "port": 7,
            "aci_leaf_interface_policy_group": self.aci_policy_group.name,
        }
        form = ACILeafInterfaceOverrideImportForm(data=record, instance=aci_override)
        self._delete_unused_import_fields(form, record)

        self.assertFalse(form.is_valid())
        self.assertIn("module", form.non_field_errors()[0])
        self.assertIn("sub_port", form.non_field_errors()[0])
        aci_override.refresh_from_db()
        self.assertEqual(aci_override.aci_node_interface, self.aci_node_interface)

    def test_import_form_update_row_omitting_all_coordinates_is_allowed(
        self,
    ) -> None:
        """Test a sparse update row leaves the linked port untouched."""
        aci_override = ACILeafInterfaceOverride.objects.create(
            aci_node_interface=self.aci_node_interface,
            aci_leaf_interface_policy_group=self.aci_policy_group,
        )
        record = {"id": str(aci_override.pk), "description": "Updated via CSV"}
        form = ACILeafInterfaceOverrideImportForm(data=record, instance=aci_override)
        self._delete_unused_import_fields(form, record)

        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        instance.refresh_from_db()
        self.assertEqual(instance.aci_node_interface, self.aci_node_interface)
        self.assertEqual(instance.description, "Updated via CSV")

    def test_import_form_rejects_unparsable_sub_port(self) -> None:
        """Test an unparsable sub port is reported as a field error."""
        form = ACILeafInterfaceOverrideImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node.name,
                "module": 1,
                "port": 1,
                "sub_port": "not-a-number",
                "aci_leaf_interface_policy_group": self.aci_policy_group.name,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("sub_port", form.errors)

    def test_import_form_rejects_unparsable_module(self) -> None:
        """Test an unparsable module is reported as a field error."""
        form = ACILeafInterfaceOverrideImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_pod": self.aci_pod.name,
                "aci_node": self.aci_node.name,
                "module": "not-a-number",
                "port": 1,
                "aci_leaf_interface_policy_group": self.aci_policy_group.name,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("module", form.errors)
