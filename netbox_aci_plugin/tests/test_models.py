# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.test import TestCase
from tenancy.models import Tenant

from ..models.tenants import ACITenant


class ACITenantTestCase(TestCase):
    """Test case for ACITenant model."""

    def setUp(self) -> None:
        """Set up an ACI Tenant for testing."""
        acitenant_name = "ACITestTenant1"
        acitenant_alias = "TestingTenant"
        acitenant_description = "Tenant for NetBox ACI Plugin testing"
        acitenant_comments = """
        Tenant for NetBox ACI Plugin testing.
        """
        nb_tenant = Tenant.objects.create(name="NetBox Tenant")

        self.aci_tenant = ACITenant.objects.create(
            name=acitenant_name,
            alias=acitenant_alias,
            description=acitenant_description,
            comments=acitenant_comments,
            nb_tenant=nb_tenant,
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
        self.assertTrue(isinstance(self.aci_tenant.nb_tenant, Tenant))
        self.assertEqual(self.aci_tenant.nb_tenant.name, "NetBox Tenant")

    def test_invalid_aci_tenant_name(self) -> None:
        """Test validation of ACI Tenant naming."""
        tenant = ACITenant(name="ACI Test Tenant 1")
        self.assertRaises(ValidationError, tenant.full_clean)

    def test_invalid_aci_tenant_alias(self) -> None:
        """Test validation of ACI Tenant aliasing."""
        tenant = ACITenant(name="ACITestTenant1", alias="Invalid Alias")
        self.assertRaises(ValidationError, tenant.full_clean)

    def test_invalid_aci_tenant_description(self) -> None:
        """Test validation of ACI Tenant description."""
        tenant = ACITenant(
            name="ACITestTenant1", description="Invalid Description: ö"
        )
        self.assertRaises(ValidationError, tenant.full_clean)
