# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....choices import NodeRoleChoices
from ....forms.fabric.vpc_protection_groups import (
    ACIVPCProtectionGroupBulkEditForm,
    ACIVPCProtectionGroupEditForm,
    ACIVPCProtectionGroupFilterForm,
    ACIVPCProtectionGroupImportForm,
)
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ....models.fabric.vpc_protection_groups import ACIVPCProtectionGroup
from ..base import ACIBaseFormTestCase


class ACIVPCProtectionGroupFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIVPCProtectionGroup forms."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up required objects for ACIVPCProtectionGroup tests."""
        super().setUpTestData()

        cls.aci_node_a = ACINode.objects.create(
            name="ACIVPCProtectionGroupFormTestNodeA",
            aci_pod=cls.aci_pod,
            node_id=101,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.aci_node_b = ACINode.objects.create(
            name="ACIVPCProtectionGroupFormTestNodeB",
            aci_pod=cls.aci_pod,
            node_id=102,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.aci_spine_node = ACINode.objects.create(
            name="ACIVPCProtectionGroupFormTestSpine",
            aci_pod=cls.aci_pod,
            node_id=103,
            role=NodeRoleChoices.ROLE_SPINE,
        )

        # A separate Fabric, to prove the CSV Node narrowing excludes it
        # even when a Node ID collides (Node IDs are unique per
        # Fabric, not globally).
        cls.other_fabric = ACIFabric.objects.create(
            name="ACIVPCProtectionGroupFormTestOtherFabric",
            fabric_id=cls.aci_fabric.fabric_id + 1,
            infra_vlan_vid=cls.aci_fabric.infra_vlan_vid + 1,
        )
        cls.other_fabric_pod = ACIPod.objects.create(
            name="ACIVPCProtectionGroupFormTestOtherFabricPod",
            aci_fabric=cls.other_fabric,
            pod_id=1,
        )

    #
    # EditForm tests
    #

    def test_invalid_aci_vpc_protection_group_field_values(self) -> None:
        """Test validation of invalid ACI VPC Protection Group field values."""
        form = ACIVPCProtectionGroupEditForm(
            data={
                "name": "ACI VPC Protection Group Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_fabric": self.aci_fabric,
                "logical_pair_id": 2000,
                "aci_node_a": self.aci_spine_node,
                "aci_node_b": self.aci_node_b,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], [self.name_error_message])
        self.assertEqual(form.errors["name_alias"], [self.name_error_message])
        self.assertEqual(form.errors["description"], [self.description_error_message])
        self.assertIn("logical_pair_id", form.errors)
        self.assertIn("aci_node_a", form.errors)

    def test_valid_aci_vpc_protection_group_field_values(self) -> None:
        """Test validation of valid ACI VPC Protection Group field values."""
        form = ACIVPCProtectionGroupEditForm(
            data={
                "name": "ACIVPCProtectionGroup1",
                "name_alias": "Testing",
                "description": "ACI VPC Protection Group for NetBox ACI Plugin",
                "aci_fabric": self.aci_fabric,
                "logical_pair_id": 1,
                "aci_node_a": self.aci_node_a,
                "aci_node_b": self.aci_node_b,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.errors.get("name"), None)
        self.assertEqual(form.errors.get("name_alias"), None)
        self.assertEqual(form.errors.get("description"), None)
        self.assertEqual(form.errors.get("logical_pair_id"), None)
        self.assertEqual(form.errors.get("aci_node_a"), None)
        self.assertEqual(form.errors.get("aci_node_b"), None)

    #
    # BulkEditForm / FilterForm sanity
    #

    def test_bulk_edit_form_nullable_fields_present(self) -> None:
        """Test the bulk edit form declares its nullable fields."""
        form = ACIVPCProtectionGroupBulkEditForm(data={})
        self.assertIn("description", form.fields)
        self.assertIn("comments", form.fields)
        self.assertEqual(
            set(ACIVPCProtectionGroupBulkEditForm.nullable_fields),
            {"comments", "description", "name_alias", "nb_tenant"},
        )

    def test_filter_form_accepts_empty_data(self) -> None:
        """Test the filter form validates with no filters applied."""
        form = ACIVPCProtectionGroupFilterForm(data={})
        self.assertTrue(form.is_valid(), form.errors)

    #
    # Import form tests (Node ID resolution scoped to its Fabric)
    #

    def test_import_form_valid_row_resolves_nodes_by_node_id(self) -> None:
        """Test the import form resolves both Nodes scoped by ACI Fabric."""
        form = ACIVPCProtectionGroupImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "name": "ACIVPCProtectionGroupImportTest",
                "logical_pair_id": "1",
                "aci_node_a": str(self.aci_node_a.node_id),
                "aci_node_b": str(self.aci_node_b.node_id),
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.aci_node_a, self.aci_node_a)
        self.assertEqual(instance.aci_node_b, self.aci_node_b)

    def test_import_form_resolves_node_scoped_when_id_shared_across_fabrics(
        self,
    ) -> None:
        """Test the import form resolves the Node ID scoped to its own Fabric.

        Node IDs are unique per ACI Fabric, not globally, so an
        unscoped lookup by Node ID alone could match more than one row
        once another Fabric reuses the same Node ID.
        """
        ACINode.objects.create(
            name="ACIVPCProtectionGroupFormTestOtherFabricNode",
            aci_pod=self.other_fabric_pod,
            node_id=self.aci_node_a.node_id,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        form = ACIVPCProtectionGroupImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "name": "ACIVPCProtectionGroupImportScoped",
                "logical_pair_id": "2",
                "aci_node_a": str(self.aci_node_a.node_id),
                "aci_node_b": str(self.aci_node_b.node_id),
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.aci_node_a, self.aci_node_a)

    def test_import_form_no_data_returns_early(self) -> None:
        """Test an unbound import form leaves the Node querysets unnarrowed."""
        form = ACIVPCProtectionGroupImportForm(data=None)
        self.assertEqual(
            form.fields["aci_node_a"].queryset.count(), ACINode.objects.count()
        )
        self.assertEqual(
            form.fields["aci_node_b"].queryset.count(), ACINode.objects.count()
        )

    def test_import_form_missing_fabric_leaves_querysets_unnarrowed(self) -> None:
        """Test a row without an ACI Fabric column skips the Node narrowing."""
        form = ACIVPCProtectionGroupImportForm(
            data={"name": "ACIVPCProtectionGroupImportTestNoFabric"}
        )
        self.assertEqual(
            form.fields["aci_node_a"].queryset.count(), ACINode.objects.count()
        )
        self.assertEqual(
            form.fields["aci_node_b"].queryset.count(), ACINode.objects.count()
        )

    def test_import_form_update_row_narrows_from_stored_fabric(self) -> None:
        """Test a sparse update row narrows Nodes by the stored ACI Fabric.

        An update row carries an id plus only the changed columns, so
        aci_fabric is usually absent. Node IDs are only fabric-unique,
        so an unnarrowed queryset could resolve to a foreign Fabric.
        """
        ACINode.objects.create(
            name="ACIVPCProtectionGroupFormTestUpdateOtherNode",
            aci_pod=self.other_fabric_pod,
            node_id=self.aci_node_a.node_id,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        group = ACIVPCProtectionGroup.objects.create(
            name="ACIVPCProtectionGroupImportUpdateTarget",
            aci_fabric=self.aci_fabric,
            logical_pair_id=3,
            aci_node_a=self.aci_node_a,
            aci_node_b=self.aci_node_b,
        )
        form = ACIVPCProtectionGroupImportForm(
            data={"id": str(group.pk), "description": "Updated"},
            instance=group,
        )
        for field_name in ("aci_node_a", "aci_node_b"):
            self.assertQuerySetEqual(
                form.fields[field_name].queryset.order_by("pk"),
                ACINode.objects.filter(_aci_fabric=self.aci_fabric).order_by("pk"),
            )
