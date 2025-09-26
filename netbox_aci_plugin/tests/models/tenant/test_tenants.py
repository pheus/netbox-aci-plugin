# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from tenancy.models import Tenant

from ....models.fabric.fabrics import ACIFabric
from ....models.tenant.tenants import ACITenant
from ..base import ACIBaseTestCase


class ACITenantTestCase(ACIBaseTestCase):
    """Test case for ACITenant model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACITenant model."""
        super().setUpTestData()

        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_tenant_alias = "ACITestTenantAlias"
        cls.aci_tenant_description = "ACI Test Tenant for NetBox ACI Plugin"
        cls.aci_tenant_comments = """
        ACI Tenant for NetBox ACI Plugin testing.
        """

        # Create objects
        cls.aci_tenant = ACITenant.objects.create(
            name=cls.aci_tenant_name,
            name_alias=cls.aci_tenant_alias,
            description=cls.aci_tenant_description,
            aci_fabric=cls.aci_fabric,
            comments=cls.aci_tenant_comments,
            nb_tenant=cls.nb_tenant,
        )

    def test_aci_tenant_instance(self) -> None:
        """Test type of created ACI Tenant."""
        self.assertTrue(isinstance(self.aci_tenant, ACITenant))

    def test_aci_tenant_str_return_value(self) -> None:
        """Test string value of created ACI Tenant."""
        self.assertEqual(self.aci_tenant.__str__(), self.aci_tenant.name)

    def test_aci_tenant_name_alias(self) -> None:
        """Test alias of ACI Tenant."""
        self.assertEqual(self.aci_tenant.name_alias, self.aci_tenant_alias)

    def test_aci_tenant_description(self) -> None:
        """Test description of ACI Tenant."""
        self.assertEqual(self.aci_tenant.description, self.aci_tenant_description)

    def test_aci_tenant_aci_fabric_instance(self) -> None:
        """Test the ACI Fabric associated with ACI Tenant."""
        self.assertTrue(isinstance(self.aci_tenant.aci_fabric, ACIFabric))
        self.assertEqual(self.aci_tenant.aci_fabric.name, self.aci_fabric_name)

    def test_aci_tenant_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant associated with ACI Tenant."""
        self.assertTrue(isinstance(self.aci_tenant.nb_tenant, Tenant))
        self.assertEqual(self.aci_tenant.nb_tenant.name, self.nb_tenant_name)

    def test_invalid_aci_tenant_name(self) -> None:
        """Test validation of ACI Tenant naming."""
        tenant = ACITenant(name="ACI Test Tenant 1")
        with self.assertRaises(ValidationError):
            tenant.full_clean()

    def test_invalid_aci_tenant_name_length(self) -> None:
        """Test validation of ACI Tenant name length."""
        tenant = ACITenant(
            name="T" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            tenant.full_clean()

    def test_invalid_aci_tenant_name_alias(self) -> None:
        """Test validation of ACI Tenant alias."""
        tenant = ACITenant(name="ACITestTenant1", name_alias="Invalid Alias")
        with self.assertRaises(ValidationError):
            tenant.full_clean()

    def test_invalid_aci_tenant_name_alias_length(self) -> None:
        """Test validation of ACI Tenant name alias length."""
        tenant = ACITenant(
            name="ACITestTenant1",
            name_alias="T" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            tenant.full_clean()

    def test_invalid_aci_tenant_description(self) -> None:
        """Test validation of ACI Tenant description."""
        tenant = ACITenant(name="ACITestTenant1", description="Invalid Description: ö")
        with self.assertRaises(ValidationError):
            tenant.full_clean()

    def test_invalid_aci_tenant_description_length(self) -> None:
        """Test validation of ACI Tenant description length."""
        tenant = ACITenant(
            name="ACITestTenant1",
            description="T" * 129,  # Exceeding the maximum length of 128
        )
        with self.assertRaises(ValidationError):
            tenant.full_clean()

    def test_constraint_unique_aci_tenant_name(self) -> None:
        """Test unique constraint of ACI Tenant name."""
        duplicate_tenant = ACITenant(
            name=self.aci_tenant_name,
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(IntegrityError):
            duplicate_tenant.save()
