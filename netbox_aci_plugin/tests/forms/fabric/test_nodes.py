# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.models import Device
from django.contrib.contenttypes.models import ContentType
from ipam.models import IPAddress

from ....choices import NodeRoleChoices, NodeTypeChoices
from ....forms.fabric.nodes import ACINodeEditForm
from ..base import ACIBaseFormTestCase


class ACINodeFormTestCase(ACIBaseFormTestCase):
    """Test case for ACINode form."""

    @classmethod
    def setUp(cls):
        """Set up required objects for ACINode tests."""
        super().setUp()

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

    def test_invalid_aci_node_field_values(self) -> None:
        """Test validation of invalid ACI Node field values."""
        aci_node_form = ACINodeEditForm(
            data={
                "name": "ACI Node Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_pod": self.aci_pod,
                "node_id": 5000,
                "node_object_type": ContentType.objects.get_for_model(
                    self.aci_bd._meta.model
                ).id,
                "node_object": self.aci_bd,
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
        self.assertIn("node_object_type", aci_node_form.errors)
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
                "node_object_type": ContentType.objects.get_for_model(
                    self.valid_node_object._meta.model
                ).id,
                "node_object": self.valid_node_object,
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
        self.assertEqual(aci_node_form.errors.get("node_object_type"), None)
        self.assertEqual(aci_node_form.errors.get("role"), None)
        self.assertEqual(aci_node_form.errors.get("node_type"), None)
        self.assertEqual(aci_node_form.errors.get("tep_ip_address"), None)
