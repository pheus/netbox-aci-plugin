# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from dcim.models import Device
from ipam.models import IPAddress

from ....choices import NodeRoleChoices, NodeTypeChoices
from ....forms.fabric.nodes import ACINodeBulkEditForm, ACINodeEditForm
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ....models.fabric.vpc_protection_groups import ACIVPCProtectionGroup
from ..base import ACIBaseFormTestCase


class ACINodeFormTestCase(ACIBaseFormTestCase):
    """Test case for ACINode form."""

    @classmethod
    def setUpTestData(cls):
        """Set up required objects for ACINode tests."""
        super().setUpTestData()

        # Invalid field values
        cls.invalid_tep_ip = IPAddress(address="192.168.1.1/32")
        cls.invalid_tep_ip.full_clean()
        cls.invalid_tep_ip.save()

        # Valid field values
        cls.valid_tep_ip = IPAddress(address="10.0.32.9/19")
        cls.valid_tep_ip.full_clean()
        cls.valid_tep_ip.save()
        cls.valid_node_object = Device.objects.create(
            name="ValidACINode1",
            device_type=cls.device_type1,
            role=cls.device_role1,
            site=cls.site,
        )

        # A second Pod in the same Fabric, for the cross-Pod cases below
        cls.aci_pod2 = ACIPod.objects.create(
            name="ACINodeFormTestPod2",
            aci_fabric=cls.aci_fabric,
            pod_id=102,
        )

        # An existing Node, for the duplicate Node ID case
        cls.existing_node = ACINode.objects.create(
            name="ACINodeFormTestExistingNode",
            aci_pod=cls.aci_pod,
            node_id=160,
            role=NodeRoleChoices.ROLE_LEAF,
        )

        # A Node pair already forming a VPC Protection Group, used by
        # the tests below that reject moving a paired Node to another
        # Pod
        cls.paired_node_a = ACINode.objects.create(
            name="ACINodeFormTestPairedNodeA",
            aci_pod=cls.aci_pod,
            node_id=161,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.paired_node_b = ACINode.objects.create(
            name="ACINodeFormTestPairedNodeB",
            aci_pod=cls.aci_pod,
            node_id=162,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        ACIVPCProtectionGroup.objects.create(
            name="ACINodeFormTestProtectionGroup",
            aci_fabric=cls.aci_fabric,
            logical_pair_id=1,
            aci_node_a=cls.paired_node_a,
            aci_node_b=cls.paired_node_b,
        )

    def test_invalid_aci_node_field_values(self) -> None:
        """Test validation of invalid ACI Node field values."""
        aci_node_form = ACINodeEditForm(
            data={
                "name": "ACI Node Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_pod": self.aci_pod,
                "node_id": 5000,
                "node_object_content_type": ContentType.objects.get_for_model(
                    self.aci_bd._meta.model
                ).id,
                "node_object_object_id": self.aci_bd.pk,
                "role": "invalid",
                "node_type": "invalid",
                "tep_ip_address": self.invalid_tep_ip,
            }
        )
        self.assertFalse(aci_node_form.is_valid())
        self.assertEqual(aci_node_form.errors["name"], [self.name_error_message])
        self.assertEqual(aci_node_form.errors["name_alias"], [self.name_error_message])
        self.assertEqual(
            aci_node_form.errors["description"], [self.description_error_message]
        )
        self.assertIn("node_id", aci_node_form.errors)
        self.assertIn("node_object", aci_node_form.errors)
        self.assertIn("role", aci_node_form.errors)
        self.assertIn("node_type", aci_node_form.errors)
        self.assertIn("tep_ip_address", aci_node_form.errors)

    def test_valid_aci_node_field_values(self) -> None:
        """Test validation of valid ACI Node field values."""
        aci_node_form = ACINodeEditForm(
            data={
                "name": "ACINode1",
                "name_alias": "Testing",
                "description": "ACI Node for NetBox ACI Plugin",
                "aci_pod": self.aci_pod,
                "node_id": 120,
                "node_object_content_type": ContentType.objects.get_for_model(
                    self.valid_node_object._meta.model
                ).id,
                "node_object_object_id": self.valid_node_object.pk,
                "role": NodeRoleChoices.ROLE_LEAF,
                "node_type": NodeTypeChoices.TYPE_UNKNOWN,
                "tep_ip_address": self.valid_tep_ip,
            }
        )
        self.assertTrue(aci_node_form.is_valid())
        self.assertEqual(aci_node_form.errors.get("name"), None)
        self.assertEqual(aci_node_form.errors.get("name_alias"), None)
        self.assertEqual(aci_node_form.errors.get("description"), None)
        self.assertEqual(aci_node_form.errors.get("node_id"), None)
        self.assertEqual(aci_node_form.errors.get("node_object"), None)
        self.assertEqual(aci_node_form.errors.get("role"), None)
        self.assertEqual(aci_node_form.errors.get("node_type"), None)
        self.assertEqual(aci_node_form.errors.get("tep_ip_address"), None)

    def test_edit_form_node_object_type_unknown(self) -> None:
        """Test the edit form tolerates an unknown node object type."""
        form = ACINodeEditForm(data={"node_object_content_type": 99999999})
        self.assertIsNone(form.fields["node_object"].selected_model)

    def test_bulk_edit_form_node_object_type_configures_field(self) -> None:
        """Test the bulk edit form configures node_object for a valid type."""
        node_object_type = ContentType.objects.get_for_model(Device)
        form = ACINodeBulkEditForm(
            data={"node_object_content_type": node_object_type.pk}
        )
        self.assertIs(form.fields["node_object"].selected_model, Device)

    def test_bulk_edit_form_node_object_type_unknown(self) -> None:
        """Test the bulk edit form tolerates an unknown node object type."""
        form = ACINodeBulkEditForm(data={"node_object_content_type": 99999999})
        self.assertIsNone(form.fields["node_object"].selected_model)

    def test_edit_form_rejects_duplicate_node_id_across_pods(self) -> None:
        """Test the edit form rejects a Node ID already used in the Fabric."""
        aci_node_form = ACINodeEditForm(
            data={
                "name": "ACINodeFormTestDuplicateNodeId",
                "aci_pod": self.aci_pod2,
                "node_id": self.existing_node.node_id,
                "role": NodeRoleChoices.ROLE_LEAF,
                "node_type": NodeTypeChoices.TYPE_UNKNOWN,
            }
        )
        self.assertFalse(aci_node_form.is_valid())
        self.assertIn("node_id", aci_node_form.errors)

    def test_edit_form_rejects_moving_paired_node_to_another_pod(self) -> None:
        """Test the edit form rejects moving a paired Node to another Pod."""
        aci_node_form = ACINodeEditForm(
            instance=self.paired_node_a,
            data={
                "name": self.paired_node_a.name,
                "aci_pod": self.aci_pod2,
                "node_id": self.paired_node_a.node_id,
                "role": NodeRoleChoices.ROLE_LEAF,
                "node_type": NodeTypeChoices.TYPE_UNKNOWN,
            },
        )
        self.assertFalse(aci_node_form.is_valid())
        self.assertIn("aci_pod", aci_node_form.errors)

    def test_bulk_edit_form_rejects_moving_paired_node_to_another_pod(self) -> None:
        """Test the bulk-edit validation path rejects moving a paired Node.

        NetBox's bulk edit view applies each cleaned field onto the
        fetched object and then calls full_clean() before save(). The
        form itself carries no aci_pod-specific validation, so this
        mirrors that view-level sequence directly against the model.
        """
        form = ACINodeBulkEditForm(
            data={"pk": [self.paired_node_a.pk], "aci_pod": self.aci_pod2.pk}
        )
        self.assertTrue(form.is_valid(), form.errors)

        node = ACINode.objects.get(pk=self.paired_node_a.pk)
        node.aci_pod = form.cleaned_data["aci_pod"]
        with self.assertRaises(ValidationError) as cm:
            node.full_clean()
        self.assertIn("aci_pod", cm.exception.message_dict)
