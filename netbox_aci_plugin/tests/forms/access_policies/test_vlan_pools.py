# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....choices import (
    VLANAllocationModeChoices,
    VLANPoolRangeAllocationModeChoices,
    VLANPoolRangeRoleChoices,
)
from ....forms.access_policies.vlan_pools import (
    ACIVLANPoolEditForm,
    ACIVLANPoolRangeEditForm,
)
from ....models.access_policies.vlan_pools import ACIVLANPool
from ..base import ACIBaseFormTestCase


class ACIVLANPoolFormTestCase(ACIBaseFormTestCase):
    """Test case for the ACIVLANPool form."""

    def test_invalid_aci_vlan_pool_field_values(self) -> None:
        """Test validation of invalid ACI VLAN Pool field values."""
        form = ACIVLANPoolEditForm(
            data={
                "name": "ACI VLAN Pool Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_fabric": self.aci_fabric,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], [self.name_error_message])
        self.assertEqual(form.errors["name_alias"], [self.name_error_message])
        self.assertEqual(form.errors["description"], [self.description_error_message])

    def test_valid_aci_vlan_pool_field_values(self) -> None:
        """Test validation of valid ACI VLAN Pool field values."""
        form = ACIVLANPoolEditForm(
            data={
                "name": "ACIVLANPool1",
                "name_alias": "Testing",
                "description": "ACI VLAN Pool for NetBox ACI Plugin",
                "aci_fabric": self.aci_fabric,
                "allocation_mode": VLANAllocationModeChoices.MODE_STATIC,
            }
        )
        self.assertTrue(form.is_valid())


class ACIVLANPoolRangeFormTestCase(ACIBaseFormTestCase):
    """Test case for the ACIVLANPoolRange form."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIVLANPoolRange form tests."""
        super().setUpTestData()
        cls.aci_vlan_pool = ACIVLANPool.objects.create(
            name="ACIVLANPoolFormTest",
            aci_fabric=cls.aci_fabric,
        )

    def test_valid_aci_vlan_pool_range_field_values(self) -> None:
        """Test validation of valid ACI VLAN Pool Range field values."""
        form = ACIVLANPoolRangeEditForm(
            data={
                "aci_vlan_pool": self.aci_vlan_pool,
                "vlan_id_from": 100,
                "vlan_id_to": 199,
                "allocation_mode": VLANPoolRangeAllocationModeChoices.MODE_INHERIT,
                "role": VLANPoolRangeRoleChoices.ROLE_EXTERNAL,
            }
        )
        self.assertTrue(form.is_valid())

    def test_inverted_range_is_invalid(self) -> None:
        """Test that a range with from greater than to is rejected."""
        form = ACIVLANPoolRangeEditForm(
            data={
                "aci_vlan_pool": self.aci_vlan_pool,
                "vlan_id_from": 199,
                "vlan_id_to": 100,
                "allocation_mode": VLANPoolRangeAllocationModeChoices.MODE_INHERIT,
                "role": VLANPoolRangeRoleChoices.ROLE_EXTERNAL,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("vlan_id_to", form.errors)
