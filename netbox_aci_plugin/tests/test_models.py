# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.test import TestCase
from ipam.models import VRF
from tenancy.models import Tenant

from ..choices import (
    VRFPCEnforcementDirectionChoices,
    VRFPCEnforcementPreferenceChoices,
)
from ..models.tenant_app_profiles import ACIAppProfile
from ..models.tenant_networks import ACIVRF
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


class ACIAppProfileTestCase(TestCase):
    """Test case for ACIAppProfile model."""

    def setUp(self) -> None:
        """Set up an ACI AppProfile for testing."""
        acitenant_name = "ACITestTenant1"
        aciappprofile_name = "AppProfileTest1"
        aciappprofile_alias = "TestingAppProfile"
        aciappprofile_description = "AppProfile for NetBox ACI Plugin testing"
        aciappprofile_comments = """
        AppProfile for NetBox ACI Plugin testing.
        """
        aci_tenant = ACITenant.objects.create(name=acitenant_name)
        nb_tenant = Tenant.objects.create(name="NetBox Tenant")

        self.aci_app_profile = ACIAppProfile.objects.create(
            name=aciappprofile_name,
            alias=aciappprofile_alias,
            description=aciappprofile_description,
            comments=aciappprofile_comments,
            aci_tenant=aci_tenant,
            nb_tenant=nb_tenant,
        )
        super().setUp()

    def test_create_aci_app_profile(self) -> None:
        """Test type and values of created ACI Application Profile."""
        self.assertTrue(isinstance(self.aci_app_profile, ACIAppProfile))
        self.assertEqual(
            self.aci_app_profile.__str__(), self.aci_app_profile.name
        )
        self.assertEqual(self.aci_app_profile.alias, "TestingAppProfile")
        self.assertEqual(
            self.aci_app_profile.description,
            "AppProfile for NetBox ACI Plugin testing",
        )
        self.assertTrue(isinstance(self.aci_app_profile.aci_tenant, ACITenant))
        self.assertEqual(
            self.aci_app_profile.aci_tenant.name, "ACITestTenant1"
        )
        self.assertTrue(isinstance(self.aci_app_profile.nb_tenant, Tenant))
        self.assertEqual(self.aci_app_profile.nb_tenant.name, "NetBox Tenant")

    def test_invalid_aci_app_profile_name(self) -> None:
        """Test validation of ACI AppProfile naming."""
        app_profile = ACIAppProfile(name="ACI App Profile Test 1")
        self.assertRaises(ValidationError, app_profile.full_clean)

    def test_invalid_aci_app_profile_alias(self) -> None:
        """Test validation of ACI AppProfile aliasing."""
        app_profile = ACIAppProfile(
            name="ACIAppProfileTest1", alias="Invalid Alias"
        )
        self.assertRaises(ValidationError, app_profile.full_clean)

    def test_invalid_aci_app_profile_description(self) -> None:
        """Test validation of ACI AppProfile description."""
        app_profile = ACIAppProfile(
            name="ACIAppProfileTest1", description="Invalid Description: ö"
        )
        self.assertRaises(ValidationError, app_profile.full_clean)


class ACIVRFTestCase(TestCase):
    """Test case for ACIVRF model."""

    def setUp(self) -> None:
        """Set up an ACI VRF for testing."""
        acitenant_name = "ACITestTenant1"
        acivrf_name = "VRFTest1"
        acivrf_alias = "TestingVRF"
        acivrf_description = "VRF for NetBox ACI Plugin testing"
        acivrf_comments = """
        VRF for NetBox ACI Plugin testing.
        """
        acivrf_bd_enforcement_enabled = False
        acivrf_dns_labels = ["DNS1", "DNS2"]
        acivrf_ip_dp_learning_enabled = False
        acivrf_pc_enforcement_direction = (
            VRFPCEnforcementDirectionChoices.DIR_EGRESS
        )
        acivrf_pc_enforcement_preference = (
            VRFPCEnforcementPreferenceChoices.PREF_UNENFORCED
        )
        acivrf_pim_ipv4_enabled = False
        acivrf_pim_ipv6_enabled = False
        acivrf_preferred_group_enabled = True
        aci_tenant = ACITenant.objects.create(name=acitenant_name)
        nb_tenant = Tenant.objects.create(name="NetBox Tenant")
        nb_vrf = VRF.objects.create(name="NetBox-VRF", tenant=nb_tenant)

        self.aci_vrf = ACIVRF.objects.create(
            name=acivrf_name,
            alias=acivrf_alias,
            description=acivrf_description,
            comments=acivrf_comments,
            aci_tenant=aci_tenant,
            nb_tenant=nb_tenant,
            nb_vrf=nb_vrf,
            bd_enforcement_enabled=acivrf_bd_enforcement_enabled,
            dns_labels=acivrf_dns_labels,
            ip_data_plane_learning_enabled=acivrf_ip_dp_learning_enabled,
            pc_enforcement_direction=acivrf_pc_enforcement_direction,
            pc_enforcement_preference=acivrf_pc_enforcement_preference,
            pim_ipv4_enabled=acivrf_pim_ipv4_enabled,
            pim_ipv6_enabled=acivrf_pim_ipv6_enabled,
            preferred_group_enabled=acivrf_preferred_group_enabled,
        )
        super().setUp()

    def test_create_aci_vrf(self) -> None:
        """Test type and values of created ACI VRF."""
        self.assertTrue(isinstance(self.aci_vrf, ACIVRF))
        self.assertEqual(self.aci_vrf.__str__(), self.aci_vrf.name)
        self.assertEqual(self.aci_vrf.alias, "TestingVRF")
        self.assertEqual(
            self.aci_vrf.description, "VRF for NetBox ACI Plugin testing"
        )
        self.assertTrue(isinstance(self.aci_vrf.aci_tenant, ACITenant))
        self.assertEqual(self.aci_vrf.aci_tenant.name, "ACITestTenant1")
        self.assertTrue(isinstance(self.aci_vrf.nb_tenant, Tenant))
        self.assertEqual(self.aci_vrf.nb_tenant.name, "NetBox Tenant")
        self.assertTrue(isinstance(self.aci_vrf.nb_vrf, VRF))
        self.assertEqual(self.aci_vrf.nb_vrf.name, "NetBox-VRF")
        self.assertEqual(self.aci_vrf.bd_enforcement_enabled, False)
        self.assertEqual(self.aci_vrf.dns_labels, ["DNS1", "DNS2"])
        self.assertEqual(self.aci_vrf.ip_data_plane_learning_enabled, False)
        self.assertEqual(self.aci_vrf.pc_enforcement_direction, "egress")
        self.assertEqual(self.aci_vrf.pc_enforcement_preference, "unenforced")
        self.assertEqual(self.aci_vrf.pim_ipv4_enabled, False)
        self.assertEqual(self.aci_vrf.pim_ipv6_enabled, False)
        self.assertEqual(self.aci_vrf.preferred_group_enabled, True)

    def test_invalid_aci_vrf_name(self) -> None:
        """Test validation of ACI VRF naming."""
        vrf = ACIVRF(name="ACI VRF Test 1")
        self.assertRaises(ValidationError, vrf.full_clean)

    def test_invalid_aci_vrf_alias(self) -> None:
        """Test validation of ACI VRF aliasing."""
        vrf = ACIVRF(name="ACIVRFTest1", alias="Invalid Alias")
        self.assertRaises(ValidationError, vrf.full_clean)

    def test_invalid_aci_vrf_description(self) -> None:
        """Test validation of ACI VRF description."""
        vrf = ACIVRF(name="ACIVRFTest1", description="Invalid Description: ö")
        self.assertRaises(ValidationError, vrf.full_clean)
