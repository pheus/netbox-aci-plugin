# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models.tenants import ACITenant


class ACITenantTestCase(TestCase):
    """Test case for ACITenant model."""

    def setUp(self) -> None:
        """Set up an ACI Tenant for testing."""

        tenant_name = "ACITestTenant1"
        tenant_alias = "TestingTenant"
        tenant_description = "Tenant for NetBox ACI Plugin testing"
        tenant_comments = """
        Tenant for NetBox ACI Plugin testing.
        """

        self.aci_tenant = ACITenant.objects.create(
            name=tenant_name,
            alias=tenant_alias,
            description=tenant_description,
            comments=tenant_comments,
        )
        super().setUp()

    def test_create_aci_tenant(self) -> None:
        """Test type and values of created ACI Tenant."""

        self.assertTrue(isinstance(self.aci_tenant, ACITenant))
        self.assertEqual(self.aci_tenant.__str__(), self.aci_tenant.name)
        self.assertEqual(self.aci_tenant.alias, "TestingTenant")
        self.assertEqual(
            self.aci_tenant.description, "Tenant for NetBox ACI Plugin testing"
        )

    def test_invalid_aci_tenant_name(self) -> None:
        """Test validation of ACI Tenant naming, description and aliasing."""
        tenant = ACITenant(name="ACI Test Tenant 1")
        self.assertRaises(ValidationError, tenant.full_clean)
