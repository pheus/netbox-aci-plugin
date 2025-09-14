# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....forms.tenant.bridge_domains import (
    ACIBridgeDomainEditForm,
    ACIBridgeDomainSubnetEditForm,
)
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
