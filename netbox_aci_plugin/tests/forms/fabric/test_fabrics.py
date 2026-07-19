# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db.backends.postgresql.psycopg_any import NumericRange

from ipam.models import VLAN, Prefix, VLANGroup

from ....forms.fabric.fabrics import ACIFabricEditForm, ACIFabricImportForm
from ..base import ACIBaseFormTestCase


class ACIFabricFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIFabric form."""

    @classmethod
    def setUpTestData(cls):
        """Set up required objects for ACIFabric tests."""
        super().setUpTestData()

        # Invalid field values
        cls.invalid_infra_vlan = VLAN.objects.create(vid=100, name="Invalid-Infra-Vlan")
        cls.invalid_gipo_pool = Prefix.objects.create(prefix="192.168.0.0/16")

        # Valid field values
        cls.valid_infra_vlan = VLAN.objects.create(vid=3900, name="ACI-Infra-Vlan")
        cls.valid_gipo_pool = Prefix.objects.create(prefix="225.0.0.0/15")

    def test_invalid_aci_fabric_field_values(self) -> None:
        """Test validation of invalid ACI Fabric field values."""
        aci_fabric_form = ACIFabricEditForm(
            data={
                "name": "ACI Fabric Test 1",
                "description": "Invalid Description: ö",
                "fabric_id": 200,
                "infra_vlan_vid": 4200,
                "infra_vlan": self.invalid_infra_vlan,
                "gipo_pool": self.invalid_gipo_pool,
            }
        )
        self.assertFalse(aci_fabric_form.is_valid())
        self.assertEqual(aci_fabric_form.errors["name"], [self.name_error_message])
        self.assertEqual(
            aci_fabric_form.errors["description"], [self.description_error_message]
        )
        self.assertIn("fabric_id", aci_fabric_form.errors)
        self.assertIn("infra_vlan_vid", aci_fabric_form.errors)
        self.assertIn("infra_vlan", aci_fabric_form.errors)
        self.assertIn("gipo_pool", aci_fabric_form.errors)

    def test_valid_aci_fabric_field_values(self) -> None:
        """Test validation of valid ACI Fabric field values."""
        aci_fabric_form = ACIFabricEditForm(
            data={
                "name": "ACIFabric1",
                "description": "ACI Fabric for NetBox ACI Plugin",
                "fabric_id": 120,
                "infra_vlan_vid": 3900,
                "infra_vlan": self.valid_infra_vlan,
                "gipo_pool": self.valid_gipo_pool,
            }
        )
        self.assertTrue(aci_fabric_form.is_valid())
        self.assertEqual(aci_fabric_form.errors.get("name"), None)
        self.assertEqual(aci_fabric_form.errors.get("description"), None)
        self.assertEqual(aci_fabric_form.errors.get("fabric_id"), None)
        self.assertEqual(aci_fabric_form.errors.get("infra_vlan_vid"), None)
        self.assertEqual(aci_fabric_form.errors.get("infra_vlan"), None)
        self.assertEqual(aci_fabric_form.errors.get("gipo_pool"), None)

    def test_import_form_resolves_duplicate_vid_via_vlan_group(self) -> None:
        """Test import disambiguates a duplicated VID by the VLAN group."""
        group_a = VLANGroup.objects.create(
            name="ACIFabricFormTestGroupA",
            slug="aci-fabric-form-test-group-a",
            vid_ranges=[NumericRange(3900, 3999)],
        )
        group_b = VLANGroup.objects.create(
            name="ACIFabricFormTestGroupB",
            slug="aci-fabric-form-test-group-b",
            vid_ranges=[NumericRange(3900, 3999)],
        )
        VLAN.objects.create(vid=3900, name="ACIFabricDupVIDGroupA", group=group_a)
        vlan_b = VLAN.objects.create(
            vid=3900, name="ACIFabricDupVIDGroupB", group=group_b
        )

        form = ACIFabricImportForm(
            data={
                "name": "ACIFabricImportTest1",
                "fabric_id": 120,
                "infra_vlan_vid": 3900,
                "infra_vlan": 3900,
                "infra_vlan_group": group_b.name,
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["infra_vlan"], vlan_b)
