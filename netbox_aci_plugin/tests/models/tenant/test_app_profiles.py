# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from tenancy.models import Tenant

from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.tenants import ACITenant


class ACIAppProfileTestCase(TestCase):
    """Test case for ACIAppProfile model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIAppProfile model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_app_profile_name = "ACITestAppProfile"
        cls.aci_app_profile_alias = "ACITestAppProfileAlias"
        cls.aci_app_profile_description = (
            "ACI Test Application Profile for NetBox ACI Plugin"
        )
        cls.aci_app_profile_comments = """
        ACI Application Profile for NetBox ACI Plugin testing.
        """
        cls.nb_tenant_name = "NetBoxTestTenant"

        # Create objects
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.aci_app_profile = ACIAppProfile.objects.create(
            name=cls.aci_app_profile_name,
            name_alias=cls.aci_app_profile_alias,
            description=cls.aci_app_profile_description,
            comments=cls.aci_app_profile_comments,
            aci_tenant=cls.aci_tenant,
            nb_tenant=cls.nb_tenant,
        )

    def test_aci_app_profile_instance(self) -> None:
        """Test type of created ACI Application Profile."""
        self.assertTrue(isinstance(self.aci_app_profile, ACIAppProfile))

    def test_aci_app_profile_str(self) -> None:
        """Test string value of created ACI Application Profile."""
        self.assertEqual(self.aci_app_profile.__str__(), self.aci_app_profile.name)

    def test_aci_app_profile_alias(self) -> None:
        """Test alias of ACI Application Profile."""
        self.assertEqual(self.aci_app_profile.name_alias, self.aci_app_profile_alias)

    def test_aci_app_profile_description(self) -> None:
        """Test description of ACI Application Profile."""
        self.assertEqual(
            self.aci_app_profile.description, self.aci_app_profile_description
        )

    def test_aci_app_profile_aci_tenant_instance(self) -> None:
        """Test the ACI Tenant instance associated with ACI App Profile."""
        self.assertTrue(isinstance(self.aci_app_profile.aci_tenant, ACITenant))

    def test_aci_app_profile_aci_tenant_name(self) -> None:
        """Test the ACI Tenant name associated with ACI Application Profile."""
        self.assertEqual(self.aci_app_profile.aci_tenant.name, self.aci_tenant_name)

    def test_aci_app_profile_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant associated with ACI Application Profile."""
        self.assertTrue(isinstance(self.aci_app_profile.nb_tenant, Tenant))

    def test_aci_app_profile_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ACI App Profile."""
        self.assertEqual(self.aci_app_profile.nb_tenant.name, self.nb_tenant_name)

    def test_invalid_aci_app_profile_name(self) -> None:
        """Test validation of ACI Application Profile naming."""
        app_profile = ACIAppProfile(name="ACI App Profile Test 1")
        with self.assertRaises(ValidationError):
            app_profile.full_clean()

    def test_invalid_aci_app_profile_name_length(self) -> None:
        """Test validation of ACI Application Profile name length."""
        app_profile = ACIAppProfile(
            name="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            app_profile.full_clean()

    def test_invalid_aci_app_profile_name_alias(self) -> None:
        """Test validation of ACI Application Profile aliasing."""
        app_profile = ACIAppProfile(
            name="ACIAppProfileTest1", name_alias="Invalid Alias"
        )
        with self.assertRaises(ValidationError):
            app_profile.full_clean()

    def test_invalid_aci_app_profile_name_alias_length(self) -> None:
        """Test validation of ACI Application Profile name alias length."""
        app_profile = ACIAppProfile(
            name="ACIAppProfileTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            app_profile.full_clean()

    def test_invalid_aci_app_profile_description(self) -> None:
        """Test validation of ACI Application Profile description."""
        app_profile = ACIAppProfile(
            name="ACIAppProfileTest1", description="Invalid Description: ö"
        )
        with self.assertRaises(ValidationError):
            app_profile.full_clean()

    def test_invalid_aci_app_profile_description_length(self) -> None:
        """Test validation of ACI Application Profile description length."""
        app_profile = ACIAppProfile(
            name="ACIAppProfileTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
        )
        with self.assertRaises(ValidationError):
            app_profile.full_clean()

    def test_constraint_unique_aci_app_profile_name_per_aci_tenant(
        self,
    ) -> None:
        """Test unique constraint of ACI AppProfile name per ACI Tenant."""
        tenant = ACITenant.objects.get(name=self.aci_tenant_name)
        duplicate_app_profile = ACIAppProfile(
            name=self.aci_app_profile_name, aci_tenant=tenant
        )
        with self.assertRaises(IntegrityError):
            duplicate_app_profile.save()
