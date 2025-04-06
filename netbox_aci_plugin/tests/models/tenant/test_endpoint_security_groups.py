# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from tenancy.models import Tenant

from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.endpoint_security_groups import ACIEndpointSecurityGroup
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF


class ACIEndpointSecurityGroupTestCase(TestCase):
    """Test case for ACIEndpointSecurityGroup model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEndpointSecurityGroup model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_app_profile_name = "ACITestAppProfile"
        cls.aci_vrf_name = "ACITestVRF"
        cls.aci_esg_name = "ACITestESG"
        cls.aci_esg_alias = "ACITestESGAlias"
        cls.aci_esg_description = (
            "ACI Test Endpoint Security Group for NetBox ACI Plugin"
        )
        cls.aci_esg_comments = """
        ACI Endpoint Security Group for NetBox ACI Plugin testing.
        """
        cls.aci_esg_admin_shutdown = False
        cls.aci_esg_intra_esg_isolation_enabled = False
        cls.aci_esg_preferred_group_member_enabled = False
        cls.nb_tenant_name = "NetBoxTestTenant"

        # Create objects
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.aci_app_profile = ACIAppProfile.objects.create(
            name=cls.aci_app_profile_name, aci_tenant=cls.aci_tenant
        )
        cls.aci_vrf = ACIVRF.objects.create(
            name=cls.aci_vrf_name, aci_tenant=cls.aci_tenant
        )
        cls.aci_esg = ACIEndpointSecurityGroup.objects.create(
            name=cls.aci_esg_name,
            name_alias=cls.aci_esg_alias,
            description=cls.aci_esg_description,
            comments=cls.aci_esg_comments,
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
            nb_tenant=cls.nb_tenant,
            admin_shutdown=cls.aci_esg_admin_shutdown,
            intra_esg_isolation_enabled=(
                cls.aci_esg_intra_esg_isolation_enabled
            ),
            preferred_group_member_enabled=(
                cls.aci_esg_preferred_group_member_enabled
            ),
        )

    def test_create_aci_endpoint_security_group_instance(self) -> None:
        """Test type of created ACI Endpoint Security Group."""
        self.assertTrue(isinstance(self.aci_esg, ACIEndpointSecurityGroup))

    def test_aci_endpoint_security_group_str(self) -> None:
        """Test string representation of ACI Endpoint Security Group."""
        self.assertEqual(self.aci_esg.__str__(), self.aci_esg.name)

    def test_aci_endpoint_security_group_name_alias(self) -> None:
        """Test name alias of ACI Endpoint Security Group."""
        self.assertEqual(self.aci_esg.name_alias, self.aci_esg_alias)

    def test_aci_endpoint_security_group_description(self) -> None:
        """Test description of ACI Endpoint Security Group."""
        self.assertEqual(self.aci_esg.description, self.aci_esg_description)

    def test_aci_endpoint_security_group_aci_tenant_instance(self) -> None:
        """Test the ACI Tenant instance associated with ACI ESG."""
        self.assertTrue(isinstance(self.aci_esg.aci_tenant, ACITenant))

    def test_aci_endpoint_security_group_aci_tenant_name(self) -> None:
        """Test the ACI Tenant name associated with ACI ESG."""
        self.assertEqual(self.aci_esg.aci_tenant.name, self.aci_tenant_name)

    def test_aci_endpoint_security_group_aci_app_profile_instance(
        self,
    ) -> None:
        """Test the ACI App Profile instance associated with ACI ESG."""
        self.assertTrue(
            isinstance(self.aci_esg.aci_app_profile, ACIAppProfile)
        )

    def test_aci_endpoint_security_group_aci_app_profile_name(self) -> None:
        """Test the ACI App Profile name associated with ACI ESG."""
        self.assertEqual(
            self.aci_esg.aci_app_profile.name, self.aci_app_profile_name
        )

    def test_aci_endpoint_security_group_aci_vrf_instance(self) -> None:
        """Test the ACI VRF instance associated with ACI ESG."""
        self.assertTrue(isinstance(self.aci_esg.aci_vrf, ACIVRF))

    def test_aci_endpoint_security_group_aci_vrf_name(self) -> None:
        """Test the ACI VRF name associated with ACI ESG."""
        self.assertEqual(self.aci_esg.aci_vrf.name, self.aci_vrf_name)

    def test_aci_endpoint_security_group_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with ACI ESG."""
        self.assertTrue(isinstance(self.aci_esg.nb_tenant, Tenant))

    def test_aci_endpoint_security_group_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ACI ESG."""
        self.assertEqual(self.aci_esg.nb_tenant.name, self.nb_tenant_name)

    def test_aci_endpoint_security_group_admin_shutdown(self) -> None:
        """Test 'admin shutdown' option of ACI Endpoint Security Group."""
        self.assertEqual(
            self.aci_esg.admin_shutdown, self.aci_esg_admin_shutdown
        )

    def test_aci_endpoint_security_group_intra_esg_isolation_enabled(
        self,
    ) -> None:
        """Test 'intra ESG isolation enabled' option of ACI ESG."""
        self.assertEqual(
            self.aci_esg.intra_esg_isolation_enabled,
            self.aci_esg_intra_esg_isolation_enabled,
        )

    def test_aci_endpoint_security_group_preferred_group_member_enabled(
        self,
    ) -> None:
        """Test 'preferred group member enabled' option of ACI ESG."""
        self.assertEqual(
            self.aci_esg.preferred_group_member_enabled,
            self.aci_esg_preferred_group_member_enabled,
        )

    def test_invalid_aci_endpoint_security_group_name(self) -> None:
        """Test validation of ACI Endpoint Security Group naming."""
        esg = ACIEndpointSecurityGroup(
            name="ACI ESG Test 1",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            esg.full_clean()

    def test_invalid_aci_endpoint_security_group_name_length(self) -> None:
        """Test validation of ACI Endpoint Security Group name length."""
        esg = ACIEndpointSecurityGroup(
            name="A" * 65,  # Exceeding the maximum length of 64
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            esg.full_clean()

    def test_invalid_aci_endpoint_security_group_name_alias(self) -> None:
        """Test validation of ACI Endpoint Security Group aliasing."""
        esg = ACIEndpointSecurityGroup(
            name="ACIESGTest1",
            name_alias="Invalid Alias",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            esg.full_clean()

    def test_invalid_aci_endpoint_security_group_name_alias_length(
        self,
    ) -> None:
        """Test validation of ACI Endpoint Security Group name alias length."""
        esg = ACIEndpointSecurityGroup(
            name="ACIESGTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            esg.full_clean()

    def test_invalid_aci_endpoint_security_group_description(self) -> None:
        """Test validation of ACI Endpoint Security Group description."""
        esg = ACIEndpointSecurityGroup(
            name="ACIESGTest1",
            description="Invalid Description: ö",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            esg.full_clean()

    def test_invalid_aci_endpoint_security_group_description_length(
        self,
    ) -> None:
        """Test validation of ACI ESG description length."""
        esg = ACIEndpointSecurityGroup(
            name="ACIESGTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            esg.full_clean()

    def test_valid_aci_esg_aci_vrf_assignment_from_tenant_common(
        self,
    ) -> None:
        """Test valid assignment of ACI VRF from ACI Tenant 'common'."""
        tenant_common = ACITenant.objects.get_or_create(name="common")[0]
        vrf_common = ACIVRF.objects.create(
            name="common_vrf", aci_tenant=tenant_common
        )
        esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIESGTest1",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=vrf_common,
        )
        esg.full_clean()
        esg.save()
        self.assertEqual(esg.aci_vrf, vrf_common)

    def test_invalid_aci_esg_aci_vrf_assignment_from_tenant_other(
        self,
    ) -> None:
        """Test invalid assignment of ACI VRF from ACI Tenant 'other'."""
        tenant_other = ACITenant.objects.get_or_create(name="other")[0]
        vrf_other = ACIVRF.objects.create(
            name="other_vrf", aci_tenant=tenant_other
        )
        esg = ACIEndpointSecurityGroup(
            name="ACIESGTest1",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=vrf_other,
        )
        with self.assertRaises(ValidationError):
            esg.full_clean()
            esg.save()

    def test_constraint_unique_aci_esg_name_per_aci_app_profile(
        self,
    ) -> None:
        """Test unique constraint of ACI ESG name per ACI App Profile."""
        app_profile = ACIAppProfile.objects.get(name=self.aci_app_profile_name)
        vrf = ACIVRF.objects.get(name=self.aci_vrf_name)
        duplicate_esg = ACIEndpointSecurityGroup(
            name=self.aci_esg_name,
            aci_app_profile=app_profile,
            aci_vrf=vrf,
        )
        with self.assertRaises(IntegrityError):
            duplicate_esg.save()
