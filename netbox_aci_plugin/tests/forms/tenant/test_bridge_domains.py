# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.test import TestCase

from ....forms.tenant.bridge_domains import (
    ACIBridgeDomainEditForm,
    ACIBridgeDomainSubnetEditForm,
)
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF


class ACIBridgeDomainFormTestCase(TestCase):
    """Test case for ACIBridgeDomain form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

    @classmethod
    def setUp(cls):
        """Set up required objects for ACIBridgeDomainForm tests."""
        cls.aci_tenant = ACITenant.objects.create(name="ACITestTenant")
        cls.aci_vrf = ACIVRF.objects.create(
            name="ACITestVRF", aci_tenant=cls.aci_tenant
        )

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


class ACIBridgeDomainSubnetFormTestCase(TestCase):
    """Test case for ACIBridgeDomainSubnet form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

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
