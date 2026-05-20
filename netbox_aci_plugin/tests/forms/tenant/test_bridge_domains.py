# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....forms.tenant.bridge_domains import (
    ACIBridgeDomainEditForm,
    ACIBridgeDomainL3OutBindingEditForm,
    ACIBridgeDomainSubnetEditForm,
)
from ....models.access_policies.domains import ACIRoutedDomain
from ....models.tenant.l3outs import ACIL3Out
from ....models.tenant.vrfs import ACIVRF
from ..base import ACIBaseFormTestCase


class ACIBridgeDomainFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIBridgeDomain form."""

    def test_invalid_aci_bridge_domain_field_values(self) -> None:
        """Test validation of invalid ACI Bridge Domain field values."""
        aci_bd_form = ACIBridgeDomainEditForm(
            data={
                "name": "ACI BD Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_tenant": self.aci_tenant,
                "aci_vrf": self.aci_vrf,
            }
        )
        self.assertEqual(aci_bd_form.errors["name"], [self.name_error_message])
        self.assertEqual(aci_bd_form.errors["name_alias"], [self.name_error_message])
        self.assertEqual(
            aci_bd_form.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_bridge_domain_field_values(self) -> None:
        """Test validation of valid ACI Bridge Domain field values."""
        aci_bd_form = ACIBridgeDomainEditForm(
            data={
                "name": "ACIBD1",
                "name_alias": "Testing",
                "description": "BD for NetBox ACI Plugin",
                "aci_tenant": self.aci_tenant,
                "aci_vrf": self.aci_vrf,
            }
        )
        self.assertEqual(aci_bd_form.errors.get("name"), None)
        self.assertEqual(aci_bd_form.errors.get("name_alias"), None)
        self.assertEqual(aci_bd_form.errors.get("description"), None)


class ACIBridgeDomainSubnetFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIBridgeDomainSubnet form."""

    def test_invalid_aci_bridge_domain_subnet_field_values(self) -> None:
        """Test validation of invalid ACI Bridge Domain Subnet field values."""
        aci_bd_subnet_form = ACIBridgeDomainSubnetEditForm(
            data={
                "name": "ACI BDSubnet Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(aci_bd_subnet_form.errors["name"], [self.name_error_message])
        self.assertEqual(
            aci_bd_subnet_form.errors["name_alias"], [self.name_error_message]
        )
        self.assertEqual(
            aci_bd_subnet_form.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_bridge_domain_subnet_field_values(self) -> None:
        """Test validation of valid ACI Bridge Domain Subnet field values."""
        aci_bd_subnet_form = ACIBridgeDomainSubnetEditForm(
            data={
                "name": "ACIBDSubnet1",
                "name_alias": "Testing",
                "description": "BDSubnet for NetBox ACI Plugin",
            }
        )
        self.assertEqual(aci_bd_subnet_form.errors.get("name"), None)
        self.assertEqual(aci_bd_subnet_form.errors.get("name_alias"), None)
        self.assertEqual(aci_bd_subnet_form.errors.get("description"), None)


class ACIBridgeDomainL3OutBindingFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIBridgeDomainL3OutBinding form."""

    @classmethod
    def setUpTestData(cls):
        """Set up required objects for BD L3Out Relation form tests."""
        super().setUpTestData()
        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIBaseFormTestRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_l3out = ACIL3Out.objects.create(
            name="ACIBaseFormTestL3Out",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.aci_vrf2 = ACIVRF.objects.create(
            name="ACIBaseFormTestVRF2",
            aci_tenant=cls.aci_tenant,
        )
        cls.aci_l3out_vrf2 = ACIL3Out.objects.create(
            name="ACIBaseFormTestL3OutVRF2",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf2,
            aci_routed_domain=cls.aci_routed_domain,
        )

    def test_invalid_aci_bridge_domain_l3out_binding_values(self) -> None:
        """Test validation of invalid ACI BD L3Out Relation values."""
        form = ACIBridgeDomainL3OutBindingEditForm(
            data={
                "aci_bridge_domain": self.aci_bd,
                "aci_l3out": self.aci_l3out_vrf2,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("aci_l3out", form.errors)

    def test_valid_aci_bridge_domain_l3out_binding_values(self) -> None:
        """Test validation of valid ACI Bridge Domain L3Out Relation values."""
        form = ACIBridgeDomainL3OutBindingEditForm(
            data={
                "aci_bridge_domain": self.aci_bd,
                "aci_l3out": self.aci_l3out,
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors.get("aci_bridge_domain"), None)
        self.assertEqual(form.errors.get("aci_l3out"), None)
