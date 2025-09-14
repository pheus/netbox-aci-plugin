# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....forms.tenant.tenants import ACITenantEditForm
from ..base import ACIBaseFormTestCase


class ACITenantFormTestCase(ACIBaseFormTestCase):
    """Test case for ACITenant form."""

    def test_invalid_aci_tenant_field_values(self) -> None:
        """Test validation of invalid ACI Tenant field values."""
        aci_tenant_form = ACITenantEditForm(
            data={
                "name": "ACI Test Tenant 1",
                "name_alias": "ACI Test Tenant Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(aci_tenant_form.errors["name"], [self.name_error_message])
        self.assertEqual(
            aci_tenant_form.errors["name_alias"], [self.name_error_message]
        )
        self.assertEqual(
            aci_tenant_form.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_tenant_field_values(self) -> None:
        """Test validation of valid ACI Tenant field values."""
        aci_tenant_form = ACITenantEditForm(
            data={
                "name": "ACITestTenant1",
                "name_alias": "TestingTenant",
                "description": "Tenant for NetBox ACI Plugin testing",
            }
        )
        self.assertEqual(aci_tenant_form.errors.get("name"), None)
        self.assertEqual(aci_tenant_form.errors.get("name_alias"), None)
        self.assertEqual(aci_tenant_form.errors.get("description"), None)
