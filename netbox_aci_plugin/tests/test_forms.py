# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.test import TestCase

from ..forms.tenants import ACITenantForm


class ACITenantFormTestCase(TestCase):
    """Test case for ACITenant form."""

    name_error_message = (
        "Only alphanumeric characters, hyphens, periods and underscores are\
        allowed."
    )
    description_error_message = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are\
        allowed."
    )

    def test_invalid_aci_tenant_field_values(self) -> None:
        """Test validation of invalid ACI Tenant field values."""
        aci_tenant_form = ACITenantForm(
            data={
                "name": "ACI Test Tenant 1",
                "alias": "ACI Test Tenant Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(
            aci_tenant_form.errors["name"], [self.name_error_message]
        )
        self.assertEqual(
            aci_tenant_form.errors["alias"], [self.name_error_message]
        )
        self.assertEqual(
            aci_tenant_form.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_tenant_field_values(self) -> None:
        """Test validation of valid ACI Tenant field values."""
        aci_tenant_form = ACITenantForm(
            data={
                "name": "ACITestTenant1",
                "alias": "TestingTenant",
                "description": "Tenant for NetBox ACI Plugin testing",
            }
        )
        self.assertEqual(aci_tenant_form.errors.get("name"), None)
        self.assertEqual(aci_tenant_form.errors.get("alias"), None)
        self.assertEqual(aci_tenant_form.errors.get("description"), None)
