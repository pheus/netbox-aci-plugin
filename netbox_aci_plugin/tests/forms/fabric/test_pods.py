# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ipam.models import Prefix

from ....forms.fabric.pods import ACIPodEditForm
from ..base import ACIBaseFormTestCase


class ACIPodFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIPod form."""

    @classmethod
    def setUp(cls):
        """Set up required objects for ACIPod tests."""
        super().setUp()

        # Invalid field values
        cls.invalid_tep_pool = Prefix.objects.create(prefix="10.0.0.0/27")

        # Valid field values
        cls.valid_tep_pool = Prefix.objects.create(prefix="10.0.0.0/16")

    def test_invalid_aci_pod_field_values(self) -> None:
        """Test validation of invalid ACI Pod field values."""
        aci_pod_form = ACIPodEditForm(
            data={
                "name": "ACI Pod Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_fabric": self.aci_fabric,
                "pod_id": 300,
                "tep_pool": self.invalid_tep_pool,
            }
        )
        self.assertFalse(aci_pod_form.is_valid())
        self.assertEqual(aci_pod_form.errors["name"], [self.name_error_message])
        self.assertEqual(aci_pod_form.errors["name_alias"], [self.name_error_message])
        self.assertEqual(
            aci_pod_form.errors["description"], [self.description_error_message]
        )
        self.assertIn("pod_id", aci_pod_form.errors)
        self.assertIn("tep_pool", aci_pod_form.errors)

    def test_valid_aci_pod_field_values(self) -> None:
        """Test validation of valid ACI Pod field values."""
        aci_pod_form = ACIPodEditForm(
            data={
                "name": "ACIPod1",
                "name_alias": "Testing",
                "description": "ACI Pod for NetBox ACI Plugin",
                "aci_fabric": self.aci_fabric,
                "pod_id": 120,
                "tep_pool": self.valid_tep_pool,
            }
        )
        self.assertTrue(aci_pod_form.is_valid())
        self.assertEqual(aci_pod_form.errors.get("name"), None)
        self.assertEqual(aci_pod_form.errors.get("name_alias"), None)
        self.assertEqual(aci_pod_form.errors.get("description"), None)
        self.assertEqual(aci_pod_form.errors.get("pod_id"), None)
        self.assertEqual(aci_pod_form.errors.get("tep_pool"), None)
