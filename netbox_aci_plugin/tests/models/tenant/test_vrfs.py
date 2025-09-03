# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from ipam.models import VRF
from tenancy.models import Tenant

from ....choices import (
    VRFPCEnforcementDirectionChoices,
    VRFPCEnforcementPreferenceChoices,
)
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF


class ACIVRFTestCase(TestCase):
    """Test case for ACIVRF model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACIVRF model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_vrf_name = "ACITestVRF"
        cls.aci_vrf_alias = "ACITestVRFAlias"
        cls.aci_vrf_description = "ACI Test VRF for NetBox ACI Plugin"
        cls.aci_vrf_comments = """
        ACI VRF for NetBox ACI Plugin testing.
        """
        cls.aci_vrf_bd_enforcement_enabled = False
        cls.aci_vrf_dns_labels = ["DNS1", "DNS2"]
        cls.aci_vrf_ip_dp_learning_enabled = False
        cls.aci_vrf_pc_enforcement_direction = (
            VRFPCEnforcementDirectionChoices.DIR_EGRESS
        )
        cls.aci_vrf_pc_enforcement_preference = (
            VRFPCEnforcementPreferenceChoices.PREF_UNENFORCED
        )
        cls.aci_vrf_pim_ipv4_enabled = False
        cls.aci_vrf_pim_ipv6_enabled = False
        cls.aci_vrf_preferred_group_enabled = True
        cls.nb_tenant_name = "NetBoxTestTenant"
        cls.nb_vrf_name = "NetBoxTestVRF"

        # Create objects
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.nb_vrf = VRF.objects.create(name=cls.nb_vrf_name, tenant=cls.nb_tenant)
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.aci_vrf = ACIVRF.objects.create(
            name=cls.aci_vrf_name,
            name_alias=cls.aci_vrf_alias,
            description=cls.aci_vrf_description,
            comments=cls.aci_vrf_comments,
            aci_tenant=cls.aci_tenant,
            nb_tenant=cls.nb_tenant,
            nb_vrf=cls.nb_vrf,
            bd_enforcement_enabled=cls.aci_vrf_bd_enforcement_enabled,
            dns_labels=cls.aci_vrf_dns_labels,
            ip_data_plane_learning_enabled=cls.aci_vrf_ip_dp_learning_enabled,
            pc_enforcement_direction=cls.aci_vrf_pc_enforcement_direction,
            pc_enforcement_preference=cls.aci_vrf_pc_enforcement_preference,
            pim_ipv4_enabled=cls.aci_vrf_pim_ipv4_enabled,
            pim_ipv6_enabled=cls.aci_vrf_pim_ipv6_enabled,
            preferred_group_enabled=cls.aci_vrf_preferred_group_enabled,
        )

    def test_aci_vrf_instance(self) -> None:
        """Test type of created ACI VRF."""
        self.assertTrue(isinstance(self.aci_vrf, ACIVRF))

    def test_aci_vrf_str(self) -> None:
        """Test string value of created ACI VRF."""
        self.assertEqual(self.aci_vrf.__str__(), self.aci_vrf.name)

    def test_aci_vrf_alias(self) -> None:
        """Test alias of ACI VRF."""
        self.assertEqual(self.aci_vrf.name_alias, self.aci_vrf_alias)

    def test_aci_vrf_description(self) -> None:
        """Test description of ACI VRF."""
        self.assertEqual(self.aci_vrf.description, self.aci_vrf_description)

    def test_aci_vrf_aci_tenant_instance(self) -> None:
        """Test the ACI Tenant instance associated with ACI VRF."""
        self.assertTrue(isinstance(self.aci_vrf.aci_tenant, ACITenant))

    def test_aci_vrf_aci_tenant_name(self) -> None:
        """Test the ACI Tenant name associated with ACI VRF."""
        self.assertEqual(self.aci_vrf.aci_tenant.name, self.aci_tenant_name)

    def test_aci_vrf_nb_tenant_instance(self) -> None:
        """Test the NetBox Tenant instance associated with ACI VRF."""
        self.assertTrue(isinstance(self.aci_vrf.nb_tenant, Tenant))

    def test_aci_vrf_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ACI VRF."""
        self.assertEqual(self.aci_vrf.nb_tenant.name, self.nb_tenant_name)

    def test_aci_vrf_nb_vrf_instance(self) -> None:
        """Test the NetBox VRF instance associated with ACI VRF."""
        self.assertTrue(isinstance(self.aci_vrf.nb_vrf, VRF))

    def test_aci_vrf_nb_vrf_name(self) -> None:
        """Test the NetBox VRF name associated with ACI VRF."""
        self.assertEqual(self.aci_vrf.nb_vrf.name, self.nb_vrf_name)

    def test_aci_vrf_bd_enforcement_enabled(self) -> None:
        """Test the 'Bridge Domain enforcement enabled' option of ACI VRF."""
        self.assertEqual(
            self.aci_vrf.bd_enforcement_enabled,
            self.aci_vrf.bd_enforcement_enabled,
        )

    def test_aci_vrf_dns_labels(self) -> None:
        """Test the 'DNS labels' option of ACI VRF."""
        self.assertEqual(self.aci_vrf.dns_labels, self.aci_vrf_dns_labels)

    def test_aci_vrf_ip_data_plane_learning_enabled(self) -> None:
        """Test the 'IP data plane learning enabled' option of ACI VRF."""
        self.assertEqual(
            self.aci_vrf.ip_data_plane_learning_enabled,
            self.aci_vrf_ip_dp_learning_enabled,
        )

    def test_aci_vrf_pc_enforcement_direction(self) -> None:
        """Test the 'PC enforcement direction' option of ACI VRF."""
        self.assertEqual(
            self.aci_vrf.pc_enforcement_direction,
            self.aci_vrf_pc_enforcement_direction,
        )

    def test_aci_vrf_pc_enforcement_preference(self) -> None:
        """Test the 'PC enforcement preference' option of ACI VRF."""
        self.assertEqual(
            self.aci_vrf.pc_enforcement_preference,
            self.aci_vrf_pc_enforcement_preference,
        )

    def test_aci_vrf_pim_ipv4_enabled(self) -> None:
        """Test the 'PIM IPv4 enabled' option of ACI VRF."""
        self.assertEqual(self.aci_vrf.pim_ipv4_enabled, self.aci_vrf_pim_ipv4_enabled)

    def test_aci_vrf_pim_ipv6_enabled(self) -> None:
        """Test the 'PIM IPv6 enabled' option of ACI VRF."""
        self.assertEqual(self.aci_vrf.pim_ipv6_enabled, self.aci_vrf_pim_ipv6_enabled)

    def test_aci_vrf_preferred_group_enabled(self) -> None:
        """Test the 'preferred group enabled' option of ACI VRF."""
        self.assertEqual(
            self.aci_vrf.preferred_group_enabled,
            self.aci_vrf_preferred_group_enabled,
        )

    def test_aci_vrf_get_pc_enforcement_direction_color(self) -> None:
        """Test the 'get_pc_enforcement_direction_color' method of ACI VRF."""
        self.assertEqual(
            self.aci_vrf.get_pc_enforcement_direction_color(),
            VRFPCEnforcementDirectionChoices.colors.get(
                VRFPCEnforcementDirectionChoices.DIR_EGRESS
            ),
        )

    def test_aci_vrf_get_pc_enforcement_preference_color(self) -> None:
        """Test the 'get_pc_enforcement_preference_color' method of ACI VRF."""
        self.assertEqual(
            self.aci_vrf.get_pc_enforcement_preference_color(),
            VRFPCEnforcementPreferenceChoices.colors.get(
                VRFPCEnforcementPreferenceChoices.PREF_UNENFORCED
            ),
        )

    def test_invalid_aci_vrf_name(self) -> None:
        """Test validation of ACI VRF naming."""
        vrf = ACIVRF(name="ACI VRF Test 1")
        with self.assertRaises(ValidationError):
            vrf.full_clean()

    def test_invalid_aci_vrf_name_length(self) -> None:
        """Test validation of ACI VRF name length."""
        vrf = ACIVRF(
            name="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            vrf.full_clean()

    def test_invalid_aci_vrf_name_alias(self) -> None:
        """Test validation of ACI VRF aliasing."""
        vrf = ACIVRF(name="ACIVRFTest1", name_alias="Invalid Alias")
        with self.assertRaises(ValidationError):
            vrf.full_clean()

    def test_invalid_aci_vrf_name_alias_length(self) -> None:
        """Test validation of ACI VRF name alias length."""
        vrf = ACIVRF(
            name="ACIVRFTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            vrf.full_clean()

    def test_invalid_aci_vrf_description(self) -> None:
        """Test validation of ACI VRF description."""
        vrf = ACIVRF(name="ACIVRFTest1", description="Invalid Description: ö")
        with self.assertRaises(ValidationError):
            vrf.full_clean()

    def test_invalid_aci_vrf_description_length(self) -> None:
        """Test validation of ACI VRF description length."""
        vrf = ACIVRF(
            name="ACIVRFTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
        )
        with self.assertRaises(ValidationError):
            vrf.full_clean()

    def test_constraint_unique_aci_vrf_name_per_aci_tenant(self) -> None:
        """Test unique constraint of ACI VRF name per ACI Tenant."""
        tenant = ACITenant.objects.get(name=self.aci_tenant_name)
        duplicate_vrf = ACIVRF(name=self.aci_vrf_name, aci_tenant=tenant)
        with self.assertRaises(IntegrityError):
            duplicate_vrf.save()
