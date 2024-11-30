# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from ipam.models import VRF, IPAddress
from tenancy.models import Tenant

from ..choices import (
    BDMultiDestinationFloodingChoices,
    BDUnknownMulticastChoices,
    BDUnknownUnicastChoices,
    ContractFilterARPOpenPeripheralCodesChoices,
    ContractFilterEtherTypeChoices,
    ContractFilterICMPv4TypesChoices,
    ContractFilterICMPv6TypesChoices,
    ContractFilterIPProtocolChoices,
    ContractFilterPortChoices,
    ContractFilterTCPRulesChoices,
    ContractScopeChoices,
    QualityOfServiceClassChoices,
    QualityOfServiceDSCPChoices,
    VRFPCEnforcementDirectionChoices,
    VRFPCEnforcementPreferenceChoices,
)
from ..models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup
from ..models.tenant_contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from ..models.tenant_contracts import ACIContract, ACIContractSubject
from ..models.tenant_networks import (
    ACIVRF,
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)
from ..models.tenants import ACITenant


class ACITenantTestCase(TestCase):
    """Test case for ACITenant model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACITenant model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_tenant_alias = "ACITestTenantAlias"
        cls.aci_tenant_description = "ACI Test Tenant for NetBox ACI Plugin"
        cls.aci_tenant_comments = """
        ACI Tenant for NetBox ACI Plugin testing.
        """
        cls.nb_tenant_name = "NetBoxTestTenant"

        # Create objects
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.aci_tenant = ACITenant.objects.create(
            name=cls.aci_tenant_name,
            name_alias=cls.aci_tenant_alias,
            description=cls.aci_tenant_description,
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
        self.assertEqual(
            self.aci_tenant.description, self.aci_tenant_description
        )

    def test_aci_tenant_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant associated with ACI Tenant."""
        self.assertTrue(isinstance(self.aci_tenant.nb_tenant, Tenant))

    def test_aci_tenant_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ACI Tenant."""
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
        tenant = ACITenant(
            name="ACITestTenant1", description="Invalid Description: ö"
        )
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
        duplicate_tenant = ACITenant(name=self.aci_tenant_name)
        with self.assertRaises(IntegrityError):
            duplicate_tenant.save()


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
        self.assertEqual(
            self.aci_app_profile.__str__(), self.aci_app_profile.name
        )

    def test_aci_app_profile_alias(self) -> None:
        """Test alias of ACI Application Profile."""
        self.assertEqual(
            self.aci_app_profile.name_alias, self.aci_app_profile_alias
        )

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
        self.assertEqual(
            self.aci_app_profile.aci_tenant.name, self.aci_tenant_name
        )

    def test_aci_app_profile_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant associated with ACI Application Profile."""
        self.assertTrue(isinstance(self.aci_app_profile.nb_tenant, Tenant))

    def test_aci_app_profile_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ACI App Profile."""
        self.assertEqual(
            self.aci_app_profile.nb_tenant.name, self.nb_tenant_name
        )

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
        cls.nb_vrf = VRF.objects.create(
            name=cls.nb_vrf_name, tenant=cls.nb_tenant
        )
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
        self.assertEqual(
            self.aci_vrf.pim_ipv4_enabled, self.aci_vrf_pim_ipv4_enabled
        )

    def test_aci_vrf_pim_ipv6_enabled(self) -> None:
        """Test the 'PIM IPv6 enabled' option of ACI VRF."""
        self.assertEqual(
            self.aci_vrf.pim_ipv6_enabled, self.aci_vrf_pim_ipv6_enabled
        )

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


class ACIBridgeDomainTestCase(TestCase):
    """Test case for ACIBridgeDomain model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIBridgeDomain model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_vrf_name = "ACITestVRF"
        cls.aci_bd_name = "ACITestBD"
        cls.aci_bd_alias = "ACITestBDAlias"
        cls.aci_bd_description = "ACI Test Bridge Domain for NetBox ACI Plugin"
        cls.aci_bd_comments = """
        ACI Bridge Domain for NetBox ACI Plugin testing.
        """
        cls.aci_bd_advertise_host_routes_enabled = False
        cls.aci_bd_arp_flooding_enabled = True
        cls.aci_bd_clear_remote_mac_enabled = True
        cls.aci_bd_dhcp_labels = ["DHCP1", "DHCP2"]
        cls.aci_bd_ep_move_detection_enabled = True
        cls.aci_bd_igmp_interface_policy_name = "IGMPInterfacePolicy1"
        cls.aci_bd_igmp_snooping_policy_name = "IGMPSnoopingPolicy1"
        cls.aci_bd_ip_dp_learning_enabled = True
        cls.aci_bd_limit_ip_learn_enabled = True
        cls.aci_bd_mac_address = "00:11:22:33:44:55"
        cls.aci_bd_multi_destination_flooding = (
            BDMultiDestinationFloodingChoices.FLOOD_BD
        )
        cls.aci_bd_pim_ipv4_enabled = False
        cls.aci_bd_pim_ipv4_destination_filter = "PIMDestinationFilter1"
        cls.aci_bd_pim_ipv4_source_filter = "PIMSourceFilter1"
        cls.aci_bd_pim_ipv6_enabled = False
        cls.aci_bd_unicast_routing_enabled = True
        cls.aci_bd_unknown_ipv4_multicast = (
            BDUnknownMulticastChoices.UNKNOWN_MULTI_FLOOD
        )
        cls.aci_bd_unknown_ipv6_multicast = (
            BDUnknownMulticastChoices.UNKNOWN_MULTI_FLOOD
        )
        cls.aci_bd_unknown_unicast = BDUnknownUnicastChoices.UNKNOWN_UNI_PROXY
        cls.aci_bd_virtual_mac_address = "00:11:22:33:44:55"

        cls.nb_tenant_name = "NetBoxTestTenant"

        # Create objects
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.aci_vrf = ACIVRF.objects.create(
            name=cls.aci_vrf_name, aci_tenant=cls.aci_tenant
        )
        cls.aci_bd = ACIBridgeDomain.objects.create(
            name=cls.aci_bd_name,
            name_alias=cls.aci_bd_alias,
            description=cls.aci_bd_description,
            comments=cls.aci_bd_comments,
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            nb_tenant=cls.nb_tenant,
            advertise_host_routes_enabled=(
                cls.aci_bd_advertise_host_routes_enabled
            ),
            arp_flooding_enabled=cls.aci_bd_arp_flooding_enabled,
            clear_remote_mac_enabled=cls.aci_bd_clear_remote_mac_enabled,
            dhcp_labels=cls.aci_bd_dhcp_labels,
            ep_move_detection_enabled=cls.aci_bd_ep_move_detection_enabled,
            igmp_interface_policy_name=cls.aci_bd_igmp_interface_policy_name,
            igmp_snooping_policy_name=cls.aci_bd_igmp_snooping_policy_name,
            ip_data_plane_learning_enabled=cls.aci_bd_ip_dp_learning_enabled,
            limit_ip_learn_enabled=cls.aci_bd_limit_ip_learn_enabled,
            mac_address=cls.aci_bd_mac_address,
            multi_destination_flooding=cls.aci_bd_multi_destination_flooding,
            pim_ipv4_enabled=cls.aci_bd_pim_ipv4_enabled,
            pim_ipv4_destination_filter=cls.aci_bd_pim_ipv4_destination_filter,
            pim_ipv4_source_filter=cls.aci_bd_pim_ipv4_source_filter,
            pim_ipv6_enabled=cls.aci_bd_pim_ipv6_enabled,
            unicast_routing_enabled=cls.aci_bd_unicast_routing_enabled,
            unknown_ipv4_multicast=cls.aci_bd_unknown_ipv4_multicast,
            unknown_ipv6_multicast=cls.aci_bd_unknown_ipv6_multicast,
            unknown_unicast=cls.aci_bd_unknown_unicast,
            virtual_mac_address=cls.aci_bd_virtual_mac_address,
        )

    def test_aci_bd_type(self) -> None:
        """Test type of ACI Bridge Domain."""
        self.assertTrue(isinstance(self.aci_bd, ACIBridgeDomain))

    def test_aci_bd_name(self) -> None:
        """Test string value of created ACI Bridge Domain."""
        self.assertEqual(self.aci_bd.__str__(), self.aci_bd.name)

    def test_aci_bd_name_alias(self) -> None:
        """Test alias of created ACI Bridge Domain."""
        self.assertEqual(self.aci_bd.name_alias, self.aci_bd_alias)

    def test_aci_bd_description(self) -> None:
        """Test description of created ACI Bridge Domain."""
        self.assertEqual(self.aci_bd.description, self.aci_bd_description)

    def test_aci_bd_aci_tenant_type(self) -> None:
        """Test the ACI Tenant instance associated with ACI Bridge Domain."""
        self.assertTrue(isinstance(self.aci_bd.aci_tenant, ACITenant))

    def test_aci_bd_aci_tenant_name(self) -> None:
        """Test the ACI Tenant name associated with ACI Bridge Domain."""
        self.assertEqual(self.aci_bd.aci_tenant.name, self.aci_tenant_name)

    def test_aci_bd_aci_vrf_type(self) -> None:
        """Test the ACI VRF instance associated with ACI Bridge Domain."""
        self.assertTrue(isinstance(self.aci_bd.aci_vrf, ACIVRF))

    def test_aci_bd_aci_vrf_name(self) -> None:
        """Test the ACI VRF name associated with ACI Bridge Domain."""
        self.assertEqual(self.aci_bd.aci_vrf.name, self.aci_vrf_name)

    def test_aci_bd_nb_tenant_type(self) -> None:
        """Test the NetBox tenant instance associated with ACI BD."""
        self.assertTrue(isinstance(self.aci_bd.nb_tenant, Tenant))

    def test_aci_bd_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ACI Bridge Domain."""
        self.assertEqual(self.aci_bd.nb_tenant.name, self.nb_tenant_name)

    def test_aci_bd_advertise_host_routes_enabled(self) -> None:
        """Test the 'advertise host routes enabled' option of ACI BD."""
        self.assertEqual(
            self.aci_bd.advertise_host_routes_enabled,
            self.aci_bd_advertise_host_routes_enabled,
        )

    def test_aci_bd_arp_flooding_enabled(self) -> None:
        """Test the 'ARP flooding enabled' option of ACI Bridge Domain."""
        self.assertEqual(
            self.aci_bd.arp_flooding_enabled, self.aci_bd_arp_flooding_enabled
        )

    def test_aci_bd_clear_remote_mac_enabled(self) -> None:
        """Test the 'clear remote MAC enabled' option of ACI BD."""
        self.assertEqual(
            self.aci_bd.clear_remote_mac_enabled,
            self.aci_bd_clear_remote_mac_enabled,
        )

    def test_aci_bd_dhcp_labels(self) -> None:
        """Test the 'DHCP labels' option of ACI Bridge Domain."""
        self.assertEqual(self.aci_bd.dhcp_labels, self.aci_bd_dhcp_labels)

    def test_aci_bd_ep_move_detection_enabled(self) -> None:
        """Test the 'EP move detection enabled' option of ACI BD."""
        self.assertEqual(
            self.aci_bd.ep_move_detection_enabled,
            self.aci_bd_ep_move_detection_enabled,
        )

    def test_aci_bd_igmp_interface_policy_name(self) -> None:
        """Test the 'IGMP interface policy name' option of ACI BD."""
        self.assertEqual(
            self.aci_bd.igmp_interface_policy_name,
            self.aci_bd_igmp_interface_policy_name,
        )

    def test_aci_bd_igmp_snooping_policy_name(self) -> None:
        """Test the 'IGMP snooping policy name' option of ACI BD."""
        self.assertEqual(
            self.aci_bd.igmp_snooping_policy_name,
            self.aci_bd_igmp_snooping_policy_name,
        )

    def test_aci_bd_ip_data_plane_learning_enabled(self) -> None:
        """Test the 'IP data-plane learning enabled' option of ACI BD."""
        self.assertEqual(
            self.aci_bd.ip_data_plane_learning_enabled,
            self.aci_bd_ip_dp_learning_enabled,
        )

    def test_aci_bd_limit_ip_learn_enabled(self) -> None:
        """Test the 'limit IP learn enabled' option of ACI BD."""
        self.assertEqual(
            self.aci_bd.limit_ip_learn_enabled,
            self.aci_bd_limit_ip_learn_enabled,
        )

    def test_aci_bd_mac_address(self) -> None:
        """Test ACI Bridge Domain's MAC address."""
        self.assertEqual(self.aci_bd.mac_address, self.aci_bd_mac_address)

    def test_aci_bd_multi_destination_flooding(self) -> None:
        """Test the 'multi-destination flooding' option of ACI BD."""
        self.assertEqual(
            self.aci_bd.multi_destination_flooding,
            self.aci_bd_multi_destination_flooding,
        )

    def test_aci_bd_pim_ipv4_enabled(self) -> None:
        """Test the 'PIM IPv4 enabled' option of ACI Bridge Domain."""
        self.assertEqual(
            self.aci_bd.pim_ipv4_enabled, self.aci_bd_pim_ipv4_enabled
        )

    def test_aci_bd_pim_ipv4_destination_filter(self) -> None:
        """Test the 'PIM IPv4 destination filter' option of ACI BD."""
        self.assertEqual(
            self.aci_bd.pim_ipv4_destination_filter,
            self.aci_bd_pim_ipv4_destination_filter,
        )

    def test_aci_bd_pim_ipv4_source_filter(self) -> None:
        """Test the 'PIM IPv4 source filter' option of ACI BD."""
        self.assertEqual(
            self.aci_bd.pim_ipv4_source_filter,
            self.aci_bd_pim_ipv4_source_filter,
        )

    def test_aci_bd_pim_ipv6_enabled(self) -> None:
        """Test the 'PIM IPv6 enabled' option of ACI Bridge Domain."""
        self.assertEqual(
            self.aci_bd.pim_ipv6_enabled, self.aci_bd_pim_ipv6_enabled
        )

    def test_aci_bd_unicast_routing_enabled(self) -> None:
        """Test the 'unicast routing enabled' option of ACI BD."""
        self.assertEqual(
            self.aci_bd.unicast_routing_enabled,
            self.aci_bd_unicast_routing_enabled,
        )

    def test_aci_bd_unknown_ipv4_multicast(self) -> None:
        """Test the 'unknown IPv4 multicast' option of ACI BD."""
        self.assertEqual(
            self.aci_bd.unknown_ipv4_multicast,
            self.aci_bd_unknown_ipv4_multicast,
        )

    def test_aci_bd_unknown_ipv6_multicast(self) -> None:
        """Test the 'unknown IPv6 multicast' option of ACI BD."""
        self.assertEqual(
            self.aci_bd.unknown_ipv6_multicast,
            self.aci_bd_unknown_ipv6_multicast,
        )

    def test_aci_bd_unknown_unicast(self) -> None:
        """Test the 'unknown unicast' option of ACI Bridge Domain."""
        self.assertEqual(
            self.aci_bd.unknown_unicast, self.aci_bd_unknown_unicast
        )

    def test_aci_bd_virtual_mac_address(self) -> None:
        """Test ACI Bridge Domain's virtual MAC address."""
        self.assertEqual(
            self.aci_bd.virtual_mac_address, self.aci_bd_virtual_mac_address
        )

    def test_aci_bridge_domain_get_multi_destination_flooding_color(
        self,
    ) -> None:
        """Test the 'get_multi_destination_flooding_color' method of ACI BD."""
        self.assertEqual(
            self.aci_bd.get_multi_destination_flooding_color(),
            BDMultiDestinationFloodingChoices.colors.get(
                BDMultiDestinationFloodingChoices.FLOOD_BD
            ),
        )

    def test_aci_bridge_domain_get_unknown_ipv4_multicast_color(self) -> None:
        """Test the 'get_unknown_ipv4_multicast_color' method of ACI BD."""
        self.assertEqual(
            self.aci_bd.get_unknown_ipv4_multicast_color(),
            BDUnknownMulticastChoices.colors.get(
                BDUnknownMulticastChoices.UNKNOWN_MULTI_FLOOD
            ),
        )

    def test_aci_bridge_domain_get_unknown_ipv6_multicast_color(self) -> None:
        """Test the 'get_unknown_ipv6_multicast_color' method of ACI BD."""
        self.assertEqual(
            self.aci_bd.get_unknown_ipv6_multicast_color(),
            BDUnknownMulticastChoices.colors.get(
                BDUnknownMulticastChoices.UNKNOWN_MULTI_FLOOD
            ),
        )

    def test_aci_bridge_domain_get_unknown_unicast_color(self) -> None:
        """Test the 'get_unknown_unicast_color' method of ACI BD."""
        self.assertEqual(
            self.aci_bd.get_unknown_unicast_color(),
            BDUnknownUnicastChoices.colors.get(
                BDUnknownUnicastChoices.UNKNOWN_UNI_PROXY
            ),
        )

    def test_invalid_aci_bridge_domain_name(self) -> None:
        """Test validation of ACI Bridge Domain naming."""
        bd = ACIBridgeDomain(
            name="ACI BD Test 1",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            bd.full_clean()

    def test_invalid_aci_bridge_domain_name_length(self) -> None:
        """Test validation of ACI Bridge Domain name length."""
        bd = ACIBridgeDomain(
            name="A" * 65,  # Exceeding the maximum length of 64
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            bd.full_clean()

    def test_invalid_aci_bridge_domain_name_alias(self) -> None:
        """Test validation of ACI Bridge Domain aliasing."""
        bd = ACIBridgeDomain(
            name="ACIBDTest1",
            name_alias="Invalid Alias",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            bd.full_clean()

    def test_invalid_aci_bridge_domain_name_alias_length(self) -> None:
        """Test validation of ACI Bridge Domain name alias length."""
        bd = ACIBridgeDomain(
            name="ACIBDTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            bd.full_clean()

    def test_invalid_aci_bridge_domain_description(self) -> None:
        """Test validation of ACI Bridge Domain description."""
        bd = ACIBridgeDomain(
            name="ACIBDTest1",
            description="Invalid Description: ö",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            bd.full_clean()

    def test_invalid_aci_bridge_domain_description_length(self) -> None:
        """Test validation of ACI Bridge Domain description length."""
        bd = ACIBridgeDomain(
            name="ACIBDTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            bd.full_clean()

    def test_valid_aci_bridge_domain_aci_vrf_assignment_form_tenant_common(
        self,
    ) -> None:
        """Test valid assignment of ACI VRF from ACI Tenant 'common'."""
        tenant_common = ACITenant.objects.get_or_create(name="common")[0]
        vrf_common = ACIVRF.objects.create(
            name="common_vrf", aci_tenant=tenant_common
        )
        bd = ACIBridgeDomain(
            name="ACIBDTest1",
            aci_tenant=self.aci_tenant,
            aci_vrf=vrf_common,
        )
        bd.full_clean()
        bd.save()
        self.assertEqual(bd.aci_vrf, vrf_common)

    def test_invalid_aci_bridge_domain_aci_vrf_assignment_from_tenant_other(
        self,
    ) -> None:
        """Test invalid assignment of ACI VRF from ACI Tenant 'other'."""
        tenant_other = ACITenant.objects.get_or_create(name="other")[0]
        vrf_other = ACIVRF.objects.create(
            name="other_vrf", aci_tenant=tenant_other
        )
        bd = ACIBridgeDomain(
            name="ACIBDTest1",
            aci_tenant=self.aci_tenant,
            aci_vrf=vrf_other,
        )
        with self.assertRaises(ValidationError):
            bd.full_clean()
            bd.save()

    def test_constraint_unique_aci_bridge_domain_name_per_aci_tenant(
        self,
    ) -> None:
        """Test unique constraint of ACI Bridge Domain name per ACI Tenant."""
        tenant = ACITenant.objects.get(name=self.aci_tenant_name)
        vrf = ACIVRF.objects.get(name=self.aci_vrf_name)
        duplicate_bd = ACIBridgeDomain(
            name=self.aci_bd_name, aci_tenant=tenant, aci_vrf=vrf
        )
        with self.assertRaises(IntegrityError):
            duplicate_bd.save()


class ACIBridgeDomainSubnetTestCase(TestCase):
    """Test case for ACIBridgeDomainSubnet model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIBridgeDomainSubnet model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_vrf_name = "ACITestVRF"
        cls.aci_bd_name = "ACITestBD"
        cls.aci_bd_subnet_name = "ACITestBDSubnet"
        cls.aci_bd_subnet_alias = "ACITestBDSubnetAlias"
        cls.aci_bd_subnet_description = (
            "ACI Test Bridge Domain Subnet for NetBox ACI Plugin"
        )
        cls.aci_bd_subnet_comments = """
        ACI Bridge Domain Subnet for NetBox ACI Plugin testing.
        """
        cls.aci_bd_subnet_gateway_ip_address = "10.0.0.1/24"
        cls.aci_bd_subnet_advertised_externally_enabled = False
        cls.aci_bd_subnet_igmp_querier_enabled = True
        cls.aci_bd_subnet_ip_dp_learning_enabled = True
        cls.aci_bd_subnet_no_default_gateway = False
        cls.aci_bd_subnet_nd_ra_enabled = True
        cls.aci_bd_subnet_nd_ra_prefix_policy_name = "NDRAPolicy1"
        cls.aci_bd_subnet_preferred_ip_address_enabled = True
        cls.aci_bd_subnet_shared_enabled = False
        cls.aci_bd_subnet_virtual_ip_enabled = False
        cls.nb_tenant_name = "NetBoxTestTenant"

        # Create objects
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.gateway_ip_address = IPAddress.objects.create(
            address=cls.aci_bd_subnet_gateway_ip_address,
        )
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.aci_vrf = ACIVRF.objects.create(
            name=cls.aci_vrf_name, aci_tenant=cls.aci_tenant
        )
        cls.aci_bd = ACIBridgeDomain.objects.create(
            name=cls.aci_bd_name,
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
        )
        cls.aci_bd_subnet = ACIBridgeDomainSubnet.objects.create(
            name=cls.aci_bd_subnet_name,
            name_alias=cls.aci_bd_subnet_alias,
            description=cls.aci_bd_subnet_description,
            comments=cls.aci_bd_subnet_comments,
            aci_bridge_domain=cls.aci_bd,
            gateway_ip_address=cls.gateway_ip_address,
            nb_tenant=cls.nb_tenant,
            advertised_externally_enabled=(
                cls.aci_bd_subnet_advertised_externally_enabled
            ),
            igmp_querier_enabled=cls.aci_bd_subnet_igmp_querier_enabled,
            ip_data_plane_learning_enabled=(
                cls.aci_bd_subnet_ip_dp_learning_enabled
            ),
            no_default_gateway=cls.aci_bd_subnet_no_default_gateway,
            nd_ra_enabled=cls.aci_bd_subnet_nd_ra_enabled,
            nd_ra_prefix_policy_name=(
                cls.aci_bd_subnet_nd_ra_prefix_policy_name
            ),
            preferred_ip_address_enabled=(
                cls.aci_bd_subnet_preferred_ip_address_enabled
            ),
            shared_enabled=cls.aci_bd_subnet_shared_enabled,
            virtual_ip_enabled=cls.aci_bd_subnet_virtual_ip_enabled,
        )

    def test_aci_bd_subnet_instance(self) -> None:
        """Test instance of created ACI Bridge Domain Subnet."""
        self.assertTrue(isinstance(self.aci_bd_subnet, ACIBridgeDomainSubnet))

    def test_aci_bd_subnet_str(self) -> None:
        """Test string representation of ACI Bridge Domain Subnet."""
        self.assertEqual(self.aci_bd_subnet.__str__(), self.aci_bd_subnet.name)

    def test_aci_bd_subnet_name_alias(self) -> None:
        """Test ACI Bridge Domain Subnet name alias."""
        self.assertEqual(
            self.aci_bd_subnet.name_alias, self.aci_bd_subnet_alias
        )

    def test_aci_bd_subnet_description(self) -> None:
        """Test ACI Bridge Domain Subnet description."""
        self.assertEqual(
            self.aci_bd_subnet.description, self.aci_bd_subnet_description
        )

    def test_aci_bd_subnet_aci_tenant_instance(self) -> None:
        """Test ACI Tenant instance in ACI Bridge Domain Subnet."""
        self.assertTrue(isinstance(self.aci_bd_subnet.aci_tenant, ACITenant))

    def test_aci_bd_subnet_aci_tenant_name(self) -> None:
        """Test ACI Tenant name of ACI Bridge Domain Subnet."""
        self.assertEqual(
            self.aci_bd_subnet.aci_tenant.name, self.aci_tenant_name
        )

    def test_aci_bd_subnet_aci_vrf_instance(self) -> None:
        """Test ACI VRF instance in ACI Bridge Domain Subnet."""
        self.assertTrue(isinstance(self.aci_bd_subnet.aci_vrf, ACIVRF))

    def test_aci_bd_subnet_aci_vrf_name(self) -> None:
        """Test ACI VRF name in ACI Bridge Domain Subnet."""
        self.assertEqual(self.aci_bd_subnet.aci_vrf.name, self.aci_vrf_name)

    def test_aci_bd_subnet_aci_bridge_domain_instance(self) -> None:
        """Test ACI Bridge Domain instance in ACI Bridge Domain Subnet."""
        self.assertTrue(
            isinstance(self.aci_bd_subnet.aci_bridge_domain, ACIBridgeDomain)
        )

    def test_aci_bd_subnet_aci_bridge_domain_name(self) -> None:
        """Test ACI Bridge Domain name of ACI Bridge Domain Subnet."""
        self.assertEqual(
            self.aci_bd_subnet.aci_bridge_domain.name, self.aci_bd_name
        )

    def test_aci_bd_subnet_gateway_ip_address_instance(self) -> None:
        """Test gateway IP address instance associated with ACI BD Subnet."""
        self.assertTrue(
            isinstance(self.aci_bd_subnet.gateway_ip_address, IPAddress)
        )

    def test_aci_bd_subnet_gateway_ip_address(self) -> None:
        """Test gateway IP address of ACI Bridge Domain Subnet."""
        self.assertEqual(
            self.aci_bd_subnet.gateway_ip_address.address,
            self.aci_bd_subnet_gateway_ip_address,
        )

    def test_aci_bd_subnet_nb_tenant_instance(self) -> None:
        """Test NetBox tenant instance in ACI Bridge Domain Subnet."""
        self.assertTrue(isinstance(self.aci_bd_subnet.nb_tenant, Tenant))

    def test_aci_bd_subnet_nb_tenant_name(self) -> None:
        """Test NetBox tenant name of ACI Bridge Domain Subnet."""
        self.assertEqual(
            self.aci_bd_subnet.nb_tenant.name, self.nb_tenant_name
        )

    def test_aci_bd_subnet_advertised_externally_enabled(self) -> None:
        """Test 'advertised externally enabled' option in ACI BD Subnet."""
        self.assertEqual(
            self.aci_bd_subnet.advertised_externally_enabled,
            self.aci_bd_subnet_advertised_externally_enabled,
        )

    def test_aci_bd_subnet_igmp_querier_enabled(self) -> None:
        """Test 'IGMP querier enabled' option in ACI Bridge Domain Subnet."""
        self.assertEqual(
            self.aci_bd_subnet.igmp_querier_enabled,
            self.aci_bd_subnet_igmp_querier_enabled,
        )

    def test_aci_bd_subnet_ip_data_plane_learning_enabled(self) -> None:
        """Test 'IP data plane learning enabled' option in ACI BD Subnet."""
        self.assertEqual(
            self.aci_bd_subnet.ip_data_plane_learning_enabled,
            self.aci_bd_subnet_ip_dp_learning_enabled,
        )

    def test_aci_bd_subnet_no_default_gateway(self) -> None:
        """Test 'no default gateway' option in ACI Bridge Domain Subnet."""
        self.assertEqual(
            self.aci_bd_subnet.no_default_gateway,
            self.aci_bd_subnet_no_default_gateway,
        )

    def test_aci_bd_subnet_nd_ra_enabled(self) -> None:
        """Test 'ND RA enabled' option in ACI Bridge Domain Subnet."""
        self.assertEqual(
            self.aci_bd_subnet.nd_ra_enabled, self.aci_bd_subnet_nd_ra_enabled
        )

    def test_aci_bd_subnet_nd_ra_prefix_policy_name(self) -> None:
        """Test 'ND RA prefix policy name' in ACI Bridge Domain Subnet."""
        self.assertEqual(
            self.aci_bd_subnet.nd_ra_prefix_policy_name,
            self.aci_bd_subnet_nd_ra_prefix_policy_name,
        )

    def test_aci_bd_subnet_preferred_ip_address_enabled(self) -> None:
        """Test the 'preferred IP address enabled' option in ACI BD Subnet."""
        self.assertEqual(
            self.aci_bd_subnet.preferred_ip_address_enabled,
            self.aci_bd_subnet_preferred_ip_address_enabled,
        )

    def test_aci_bd_subnet_shared_enabled(self) -> None:
        """Test 'shared enabled' option in ACI Bridge Domain Subnet."""
        self.assertEqual(
            self.aci_bd_subnet.shared_enabled,
            self.aci_bd_subnet_shared_enabled,
        )

    def test_aci_bd_subnet_virtual_ip_enabled(self) -> None:
        """Test 'virtual IP enabled' option in ACI Bridge Domain Subnet."""
        self.assertEqual(
            self.aci_bd_subnet.virtual_ip_enabled,
            self.aci_bd_subnet_virtual_ip_enabled,
        )

    def test_invalid_aci_bridge_domain_subnet_name(self) -> None:
        """Test validation of ACI Bridge Domain Subnet naming."""
        subnet = ACIBridgeDomainSubnet(name="ACI BDSubnet Test 1")
        with self.assertRaises(ValidationError):
            subnet.full_clean()

    def test_invalid_aci_bridge_domain_subnet_name_length(self) -> None:
        """Test validation of ACI Bridge Domain Subnet name length."""
        subnet = ACIBridgeDomainSubnet(
            name="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            subnet.full_clean()

    def test_invalid_aci_bridge_domain_subnet_name_alias(self) -> None:
        """Test validation of ACI Bridge Domain Subnet aliasing."""
        subnet = ACIBridgeDomainSubnet(
            name="ACIBDSubnetTest1", name_alias="Invalid Alias"
        )
        with self.assertRaises(ValidationError):
            subnet.full_clean()

    def test_invalid_aci_bridge_domain_subnet_name_alias_length(self) -> None:
        """Test validation of ACI Bridge Domain Subnet name alias length."""
        subnet = ACIBridgeDomainSubnet(
            name="ACIBDSubnetTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            subnet.full_clean()

    def test_invalid_aci_bridge_domain_subnet_description(self) -> None:
        """Test validation of ACI Bridge Domain Subnet description."""
        subnet = ACIBridgeDomainSubnet(
            name="ACIBDSubnetTest1", description="Invalid Description: ö"
        )
        with self.assertRaises(ValidationError):
            subnet.full_clean()

    def test_invalid_aci_bridge_domain_subnet_description_length(self) -> None:
        """Test validation of ACI Bridge Domain Subnet description length."""
        subnet = ACIBridgeDomainSubnet(
            name="ACIBDSubnetTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
        )
        with self.assertRaises(ValidationError):
            subnet.full_clean()

    def test_constraint_unique_aci_bd_subnet_name_per_aci_bridge_domain(
        self,
    ) -> None:
        """Test unique constraint of ACI BD Subnet name per ACI BD."""
        bd = ACIBridgeDomain.objects.get(name=self.aci_bd_name)
        gateway_ip = IPAddress.objects.create(address="10.0.1.1/24")
        duplicate_subnet = ACIBridgeDomainSubnet(
            name=self.aci_bd_subnet_name,
            aci_bridge_domain=bd,
            gateway_ip_address=gateway_ip,
        )
        with self.assertRaises(IntegrityError):
            duplicate_subnet.save()

    def test_constraint_unique_preferred_ip_per_bridge_domain(self) -> None:
        """Test unique constraint of one preferred ip address per ACI BD."""
        bd = ACIBridgeDomain.objects.get(name=self.aci_bd_name)
        gateway_ip = IPAddress.objects.create(address="10.0.2.1/24")
        second_preferred_ip_subnet = ACIBridgeDomainSubnet(
            name="ACIBDSubnetTest1",
            aci_bridge_domain=bd,
            gateway_ip_address=gateway_ip,
            preferred_ip_address_enabled=True,
        )
        with self.assertRaises(IntegrityError):
            second_preferred_ip_subnet.save()


class ACIEndpointGroupTestCase(TestCase):
    """Test case for ACIEndpointGroup model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIBridgeDomainSubnet model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_app_profile_name = "ACITestAppProfile"
        cls.aci_vrf_name = "ACITestVRF"
        cls.aci_bd_name = "ACITestBD"
        cls.aci_epg_name = "ACITestEPG"
        cls.aci_epg_alias = "ACITestEPGAlias"
        cls.aci_epg_description = (
            "ACI Test Endpoint Group for NetBox ACI Plugin"
        )
        cls.aci_epg_comments = """
        ACI Endpoint Group for NetBox ACI Plugin testing.
        """
        cls.aci_epg_admin_shutdown = False
        cls.aci_epg_custom_qos_policy_name = "CustomQoSPolicy1"
        cls.aci_epg_flood_in_encap_enabled = False
        cls.aci_epg_intra_epg_isolation_enabled = False
        cls.aci_epg_qos_class = QualityOfServiceClassChoices.CLASS_LEVEL_3
        cls.aci_epg_preferred_group_member_enabled = False
        cls.aci_epg_proxy_arp_enabled = False
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
        cls.aci_bd = ACIBridgeDomain.objects.create(
            name=cls.aci_bd_name,
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
        )
        cls.aci_epg = ACIEndpointGroup.objects.create(
            name=cls.aci_epg_name,
            name_alias=cls.aci_epg_alias,
            description=cls.aci_epg_description,
            comments=cls.aci_epg_comments,
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
            nb_tenant=cls.nb_tenant,
            admin_shutdown=cls.aci_epg_admin_shutdown,
            custom_qos_policy_name=cls.aci_epg_custom_qos_policy_name,
            flood_in_encap_enabled=cls.aci_epg_flood_in_encap_enabled,
            intra_epg_isolation_enabled=(
                cls.aci_epg_intra_epg_isolation_enabled
            ),
            qos_class=cls.aci_epg_qos_class,
            preferred_group_member_enabled=(
                cls.aci_epg_preferred_group_member_enabled
            ),
            proxy_arp_enabled=cls.aci_epg_proxy_arp_enabled,
        )

    def test_create_aci_endpoint_group_instance(self) -> None:
        """Test type of created ACI Endpoint Group."""
        self.assertTrue(isinstance(self.aci_epg, ACIEndpointGroup))

    def test_aci_endpoint_group_str(self) -> None:
        """Test string representation of ACI Endpoint Group."""
        self.assertEqual(self.aci_epg.__str__(), self.aci_epg.name)

    def test_aci_endpoint_group_name_alias(self) -> None:
        """Test name alias of ACI Endpoint Group."""
        self.assertEqual(self.aci_epg.name_alias, self.aci_epg_alias)

    def test_aci_endpoint_group_description(self) -> None:
        """Test description of ACI Endpoint Group."""
        self.assertEqual(self.aci_epg.description, self.aci_epg_description)

    def test_aci_endpoint_group_aci_tenant_instance(self) -> None:
        """Test the ACI Tenant instance associated with ACI EPG."""
        self.assertTrue(isinstance(self.aci_epg.aci_tenant, ACITenant))

    def test_aci_endpoint_group_aci_tenant_name(self) -> None:
        """Test the ACI Tenant name associated with ACI EPG."""
        self.assertEqual(self.aci_epg.aci_tenant.name, self.aci_tenant_name)

    def test_aci_endpoint_group_aci_app_profile_instance(self) -> None:
        """Test the ACI App Profile instance associated with ACI EPG."""
        self.assertTrue(
            isinstance(self.aci_epg.aci_app_profile, ACIAppProfile)
        )

    def test_aci_endpoint_group_aci_app_profile_name(self) -> None:
        """Test the ACI App Profile name associated with ACI EPG."""
        self.assertEqual(
            self.aci_epg.aci_app_profile.name, self.aci_app_profile_name
        )

    def test_aci_endpoint_group_aci_vrf_instance(self) -> None:
        """Test the ACI VRF instance associated with ACI EPG."""
        self.assertTrue(isinstance(self.aci_epg.aci_vrf, ACIVRF))

    def test_aci_endpoint_group_aci_vrf_name(self) -> None:
        """Test the ACI VRF name associated with ACI EPG."""
        self.assertEqual(self.aci_epg.aci_vrf.name, self.aci_vrf_name)

    def test_aci_endpoint_group_aci_bridge_domain_instance(self) -> None:
        """Test the ACI Bridge Domain instance associated with ACI EPG."""
        self.assertTrue(
            isinstance(self.aci_epg.aci_bridge_domain, ACIBridgeDomain)
        )

    def test_aci_endpoint_group_aci_bridge_domain_name(self) -> None:
        """Test the ACI Bridge Domain name associated with ACI EPG."""
        self.assertEqual(self.aci_epg.aci_bridge_domain.name, self.aci_bd_name)

    def test_aci_endpoint_group_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with ACI EPG."""
        self.assertTrue(isinstance(self.aci_epg.nb_tenant, Tenant))

    def test_aci_endpoint_group_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ACI EPG."""
        self.assertEqual(self.aci_epg.nb_tenant.name, self.nb_tenant_name)

    def test_aci_endpoint_group_admin_shutdown(self) -> None:
        """Test 'admin shutdown' option of ACI Endpoint Group."""
        self.assertEqual(
            self.aci_epg.admin_shutdown, self.aci_epg_admin_shutdown
        )

    def test_aci_endpoint_group_custom_qos_policy_name(self) -> None:
        """Test 'custom QOS policy name' of ACI Endpoint Group."""
        self.assertEqual(
            self.aci_epg.custom_qos_policy_name,
            self.aci_epg_custom_qos_policy_name,
        )

    def test_aci_endpoint_group_flood_in_encap_enabled(self) -> None:
        """Test 'flood in encap enabled' option of ACI Endpoint Group."""
        self.assertEqual(
            self.aci_epg.flood_in_encap_enabled,
            self.aci_epg_flood_in_encap_enabled,
        )

    def test_aci_endpoint_group_intra_epg_isolation_enabled(self) -> None:
        """Test 'intra EPG isolation enabled' option of ACI Endpoint Group."""
        self.assertEqual(
            self.aci_epg.intra_epg_isolation_enabled,
            self.aci_epg_intra_epg_isolation_enabled,
        )

    def test_aci_endpoint_group_qos_class(self) -> None:
        """Test 'QoS class' of ACI Endpoint Group."""
        self.assertEqual(self.aci_epg.qos_class, self.aci_epg_qos_class)

    def test_aci_endpoint_group_preferred_group_member_enabled(self) -> None:
        """Test 'preferred group member enabled' option of ACI EPG."""
        self.assertEqual(
            self.aci_epg.preferred_group_member_enabled,
            self.aci_epg_preferred_group_member_enabled,
        )

    def test_aci_endpoint_group_proxy_arp_enabled(self) -> None:
        """Test 'proxy ARP enabled' option of ACI Endpoint Group."""
        self.assertEqual(
            self.aci_epg.proxy_arp_enabled, self.aci_epg_proxy_arp_enabled
        )

    def test_aci_endpoint_group_get_qos_class_color(self) -> None:
        """Test the 'get_qos_class_color' method of ACI Endpoint Group."""
        self.assertEqual(
            self.aci_epg.get_qos_class_color(),
            QualityOfServiceClassChoices.colors.get(
                QualityOfServiceClassChoices.CLASS_LEVEL_3
            ),
        )

    def test_invalid_aci_endpoint_group_name(self) -> None:
        """Test validation of ACI Endpoint Group naming."""
        epg = ACIEndpointGroup(
            name="ACI EPG Test 1",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_endpoint_group_name_length(self) -> None:
        """Test validation of ACI Endpoint Group name length."""
        epg = ACIEndpointGroup(
            name="A" * 65,  # Exceeding the maximum length of 64
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_endpoint_group_name_alias(self) -> None:
        """Test validation of ACI Endpoint Group aliasing."""
        epg = ACIEndpointGroup(
            name="ACIEPGTest1",
            name_alias="Invalid Alias",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_endpoint_group_name_alias_length(self) -> None:
        """Test validation of ACI Endpoint Group name alias length."""
        epg = ACIEndpointGroup(
            name="ACIEPGTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_endpoint_group_description(self) -> None:
        """Test validation of ACI Endpoint Group description."""
        epg = ACIEndpointGroup(
            name="ACIEPGTest1",
            description="Invalid Description: ö",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_endpoint_group_description_length(self) -> None:
        """Test validation of ACI Endpoint Group description length."""
        epg = ACIEndpointGroup(
            name="ACIEPGTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_valid_aci_endpoint_group_aci_bd_assignment_from_tenant_common(
        self,
    ) -> None:
        """Test valid assignment of ACI BD from ACI Tenant 'common'."""
        tenant_common = ACITenant.objects.get_or_create(name="common")[0]
        vrf_common = ACIVRF.objects.create(
            name="common_vrf", aci_tenant=tenant_common
        )
        bd_common = ACIBridgeDomain.objects.create(
            name="common_bd", aci_tenant=tenant_common, aci_vrf=vrf_common
        )
        epg = ACIEndpointGroup.objects.create(
            name="ACIEPGTest1",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=bd_common,
        )
        epg.full_clean()
        epg.save()
        self.assertEqual(epg.aci_bridge_domain, bd_common)

    def test_invalid_aci_endpoint_group_aci_bd_assignment_from_tenant_other(
        self,
    ) -> None:
        """Test invalid assignment of ACI BD from ACI Tenant 'other'."""
        tenant_other = ACITenant.objects.get_or_create(name="other")[0]
        vrf_other = ACIVRF.objects.create(
            name="other_vrf", aci_tenant=tenant_other
        )
        bd_other = ACIBridgeDomain.objects.create(
            name="other_bd", aci_tenant=tenant_other, aci_vrf=vrf_other
        )
        epg = ACIEndpointGroup(
            name="ACIEPGTest1",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=bd_other,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()
            epg.save()

    def test_constraint_unique_aci_endpoint_group_name_per_aci_app_profile(
        self,
    ) -> None:
        """Test unique constraint of ACI EPG name per ACI App Profile."""
        app_profile = ACIAppProfile.objects.get(name=self.aci_app_profile_name)
        bd = ACIBridgeDomain.objects.get(name=self.aci_bd_name)
        duplicate_epg = ACIEndpointGroup(
            name=self.aci_epg_name,
            aci_app_profile=app_profile,
            aci_bridge_domain=bd,
        )
        with self.assertRaises(IntegrityError):
            duplicate_epg.save()


class ACIContractFilterTestCase(TestCase):
    """Test case for ACIContractFilter model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractFilter model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_contract_filter_name = "ACITestContractFilter"
        cls.aci_contract_filter_alias = "ACITestContractFilterAlias"
        cls.aci_contract_filter_description = (
            "ACI Test Contract Filter for NetBox ACI Plugin"
        )
        cls.aci_contract_filter_comments = """
        ACI Contract Filter for NetBox ACI Plugin testing.
        """
        cls.nb_tenant_name = "NetBoxTestTenant"

        # Create objects
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.aci_contract_filter = ACIContractFilter.objects.create(
            name=cls.aci_contract_filter_name,
            name_alias=cls.aci_contract_filter_alias,
            description=cls.aci_contract_filter_description,
            comments=cls.aci_contract_filter_comments,
            aci_tenant=cls.aci_tenant,
            nb_tenant=cls.nb_tenant,
        )

    def test_aci_contract_filter_instance(self) -> None:
        """Test type of created ACI Contract Filter."""
        self.assertTrue(
            isinstance(self.aci_contract_filter, ACIContractFilter)
        )

    def test_aci_contract_filter_str(self) -> None:
        """Test string value of created ACI Contract Filter."""
        self.assertEqual(
            self.aci_contract_filter.__str__(), self.aci_contract_filter.name
        )

    def test_aci_contract_filter_alias(self) -> None:
        """Test alias of ACI Contract Filter."""
        self.assertEqual(
            self.aci_contract_filter.name_alias, self.aci_contract_filter_alias
        )

    def test_aci_contract_filter_description(self) -> None:
        """Test description of ACI Contract Filter."""
        self.assertEqual(
            self.aci_contract_filter.description,
            self.aci_contract_filter_description,
        )

    def test_aci_contract_filter_aci_tenant_instance(self) -> None:
        """Test the ACI Tenant instance associated with ACI Contract Filter."""
        self.assertTrue(
            isinstance(self.aci_contract_filter.aci_tenant, ACITenant)
        )

    def test_aci_contract_filter_aci_tenant_name(self) -> None:
        """Test the ACI Tenant name associated with ACI Contract Filter."""
        self.assertEqual(
            self.aci_contract_filter.aci_tenant.name, self.aci_tenant_name
        )

    def test_aci_contract_filter_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with Contract Filter."""
        self.assertTrue(isinstance(self.aci_contract_filter.nb_tenant, Tenant))

    def test_aci_contract_filter_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ACI Contract Filter."""
        self.assertEqual(
            self.aci_contract_filter.nb_tenant.name, self.nb_tenant_name
        )

    def test_invalid_aci_contract_filter_name(self) -> None:
        """Test validation of ACI Contract Filter naming."""
        contract_filter = ACIContractFilter(name="ACI Contract Filter Test 1")
        with self.assertRaises(ValidationError):
            contract_filter.full_clean()

    def test_invalid_aci_contract_filter_name_length(self) -> None:
        """Test validation of ACI Contract Filter name length."""
        contract_filter = ACIContractFilter(
            name="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            contract_filter.full_clean()

    def test_invalid_aci_contract_filter_name_alias(self) -> None:
        """Test validation of ACI Contract Filter aliasing."""
        contract_filter = ACIContractFilter(
            name="ACIContractFilterTest1", name_alias="Invalid Alias"
        )
        with self.assertRaises(ValidationError):
            contract_filter.full_clean()

    def test_invalid_aci_contract_filter_name_alias_length(self) -> None:
        """Test validation of ACI Contract Filter name alias length."""
        contract_filter = ACIContractFilter(
            name="ACIContractFilterTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            contract_filter.full_clean()

    def test_invalid_aci_contract_filter_description(self) -> None:
        """Test validation of ACI Contract Filter description."""
        contract_filter = ACIContractFilter(
            name="ACIContractFilterTest1", description="Invalid Description: ö"
        )
        with self.assertRaises(ValidationError):
            contract_filter.full_clean()

    def test_invalid_aci_contract_filter_description_length(self) -> None:
        """Test validation of ACI Contract Filter description length."""
        contract_filter = ACIContractFilter(
            name="ACIContractFilterTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
        )
        with self.assertRaises(ValidationError):
            contract_filter.full_clean()

    def test_constraint_unique_aci_contract_filter_name_per_aci_tenant(
        self,
    ) -> None:
        """Test unique constraint of ACI ContractFilter name per ACI Tenant."""
        tenant = ACITenant.objects.get(name=self.aci_tenant_name)
        duplicate_contract_filter = ACIContractFilter(
            name=self.aci_contract_filter_name, aci_tenant=tenant
        )
        with self.assertRaises(IntegrityError):
            duplicate_contract_filter.save()


class ACIContractFilterEntryTestCase(TestCase):
    """Test case for ACIContractFilterEntry model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractFilterEntry model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_contract_filter_name = "ACITestContractFilter"
        cls.aci_contract_filter_entry_name = "ACITestContractFilterEntry"
        cls.aci_contract_filter_entry_alias = "ACITestContractFilterEntryAlias"
        cls.aci_contract_filter_entry_description = (
            "ACI Test Contract Filter Entry for NetBox ACI Plugin"
        )
        cls.aci_contract_filter_entry_comments = """
        ACI Contract Filter Entry for NetBox ACI Plugin testing.
        """
        cls.aci_contract_filter_entry_arp_opc = (
            ContractFilterARPOpenPeripheralCodesChoices.OPC_REQUEST
        )
        cls.aci_contract_filter_entry_dest_from_port = (
            ContractFilterPortChoices.PORT_SSH
        )
        cls.aci_contract_filter_entry_dest_to_port = (
            ContractFilterPortChoices.PORT_DNS
        )
        cls.aci_contract_filter_entry_ether_type = (
            ContractFilterEtherTypeChoices.TYPE_IP
        )
        cls.aci_contract_filter_entry_icmp_v4_type = (
            ContractFilterICMPv4TypesChoices.ICMP_V4_ECHO_REQUEST
        )
        cls.aci_contract_filter_entry_icmp_v6_type = (
            ContractFilterICMPv6TypesChoices.ICMP_V6_UNSPECIFIED
        )
        cls.aci_contract_filter_entry_ip_protocol = (
            ContractFilterIPProtocolChoices.PROT_TCP
        )
        cls.aci_contract_filter_entry_match_dscp = (
            QualityOfServiceDSCPChoices.DSCP_AF42
        )
        cls.aci_contract_filter_entry_match_only_fragments_enabled = False
        cls.aci_contract_filter_entry_src_from_port = 0
        cls.aci_contract_filter_entry_src_to_port = 65535
        cls.aci_contract_filter_entry_stateful_enabled = False
        cls.aci_contract_filter_entry_tcp_rules = [
            ContractFilterTCPRulesChoices.TCP_SYN,
            ContractFilterTCPRulesChoices.TCP_FINISH,
        ]

        # Create objects
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.aci_contract_filter = ACIContractFilter.objects.create(
            name=cls.aci_contract_filter_name,
            aci_tenant=cls.aci_tenant,
        )
        cls.aci_contract_filter_entry = ACIContractFilterEntry.objects.create(
            name=cls.aci_contract_filter_entry_name,
            name_alias=cls.aci_contract_filter_entry_alias,
            description=cls.aci_contract_filter_entry_description,
            comments=cls.aci_contract_filter_entry_comments,
            aci_contract_filter=cls.aci_contract_filter,
            arp_opc=cls.aci_contract_filter_entry_arp_opc,
            destination_from_port=cls.aci_contract_filter_entry_dest_from_port,
            destination_to_port=cls.aci_contract_filter_entry_dest_to_port,
            ether_type=cls.aci_contract_filter_entry_ether_type,
            icmp_v4_type=cls.aci_contract_filter_entry_icmp_v4_type,
            icmp_v6_type=cls.aci_contract_filter_entry_icmp_v6_type,
            ip_protocol=cls.aci_contract_filter_entry_ip_protocol,
            match_dscp=cls.aci_contract_filter_entry_match_dscp,
            match_only_fragments_enabled=(
                cls.aci_contract_filter_entry_match_only_fragments_enabled
            ),
            source_from_port=cls.aci_contract_filter_entry_src_from_port,
            source_to_port=cls.aci_contract_filter_entry_src_to_port,
            stateful_enabled=cls.aci_contract_filter_entry_stateful_enabled,
            tcp_rules=cls.aci_contract_filter_entry_tcp_rules,
        )

    def test_aci_contract_filter_entry_instance(self) -> None:
        """Test type of created ACI Contract Filter Entry."""
        self.assertTrue(
            isinstance(self.aci_contract_filter_entry, ACIContractFilterEntry)
        )

    def test_aci_contract_filter_entry_str(self) -> None:
        """Test string value of created ACI Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.__str__(),
            f"{self.aci_contract_filter_entry_name} "
            f"({self.aci_contract_filter_name})",
        )

    def test_aci_contract_filter_entry_alias(self) -> None:
        """Test alias of ACI Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.name_alias,
            self.aci_contract_filter_entry_alias,
        )

    def test_aci_contract_filter_entry_description(self) -> None:
        """Test description of ACI Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.description,
            self.aci_contract_filter_entry_description,
        )

    def test_aci_contract_filter_entry_aci_contract_filter_instance(
        self,
    ) -> None:
        """Test the Filter instance associated with Contract Filter Entry."""
        self.assertTrue(
            isinstance(
                self.aci_contract_filter_entry.aci_contract_filter,
                ACIContractFilter,
            )
        )

    def test_aci_contract_filter_entry_aci_contract_filter_name(self) -> None:
        """Test the Filter name associated with Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.aci_contract_filter.name,
            self.aci_contract_filter_name,
        )

    def test_aci_contract_filter_entry_arp_opc(self) -> None:
        """Test the 'arp_opc' option of ACI Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.arp_opc,
            self.aci_contract_filter_entry_arp_opc,
        )

    def test_aci_contract_filter_entry_destination_from_port(self) -> None:
        """Test the 'destination_from_port' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.destination_from_port,
            self.aci_contract_filter_entry_dest_from_port,
        )

    def test_aci_contract_filter_entry_destination_to_port(self) -> None:
        """Test the 'destination_to_port' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.destination_to_port,
            self.aci_contract_filter_entry_dest_to_port,
        )

    def test_aci_contract_filter_entry_ether_type(self) -> None:
        """Test the 'ether_type' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.ether_type,
            self.aci_contract_filter_entry_ether_type,
        )

    def test_aci_contract_filter_entry_icmp_v4_type(self) -> None:
        """Test the 'icmp_v4_type' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.icmp_v4_type,
            self.aci_contract_filter_entry_icmp_v4_type,
        )

    def test_aci_contract_filter_entry_icmp_v6_type(self) -> None:
        """Test the 'icmp_v6_type' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.icmp_v6_type,
            self.aci_contract_filter_entry_icmp_v6_type,
        )

    def test_aci_contract_filter_entry_ip_protocol(self) -> None:
        """Test the 'ip_protocol' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.ip_protocol,
            self.aci_contract_filter_entry_ip_protocol,
        )

    def test_aci_contract_filter_entry_match_dscp(self) -> None:
        """Test the 'match_dscp' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.match_dscp,
            self.aci_contract_filter_entry_match_dscp,
        )

    def test_aci_contract_filter_entry_match_only_fragments_enabled(
        self,
    ) -> None:
        """Test the 'match_only_fragments_enabled' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.match_only_fragments_enabled,
            self.aci_contract_filter_entry_match_only_fragments_enabled,
        )

    def test_aci_contract_filter_entry_source_from_port(self) -> None:
        """Test the 'source_from_port' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.source_from_port,
            self.aci_contract_filter_entry_src_from_port,
        )

    def test_aci_contract_filter_entry_source_to_port(self) -> None:
        """Test the 'source_to_port' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.source_to_port,
            self.aci_contract_filter_entry_src_to_port,
        )

    def test_aci_contract_filter_entry_stateful_enabled(self) -> None:
        """Test the 'stateful_enabled' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.stateful_enabled,
            self.aci_contract_filter_entry_stateful_enabled,
        )

    def test_aci_contract_filter_entry_tcp_rules(self) -> None:
        """Test the 'tcp_rules' option of Contract Filter Entry."""
        self.assertEqual(
            self.aci_contract_filter_entry.tcp_rules,
            self.aci_contract_filter_entry_tcp_rules,
        )

    def test_invalid_aci_contract_filter_entry_name(self) -> None:
        """Test validation of ACI Contract Filter Entry naming."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACI Contract Filter Entry Test 1"
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_name_length(self) -> None:
        """Test validation of ACI Contract Filter Entry name length."""
        contract_filter_entry = ACIContractFilterEntry(
            name="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_name_alias(self) -> None:
        """Test validation of ACI Contract Filter Entry aliasing."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1", name_alias="Invalid Alias"
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_name_alias_length(self) -> None:
        """Test validation of ACI Contract Filter Entry name alias length."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_description(self) -> None:
        """Test validation of ACI Contract Filter Entry description."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            description="Invalid Description: ö",
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_description_length(
        self,
    ) -> None:
        """Test validation of ACI Contract Filter Entry description length."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_ip_protocol_number(
        self,
    ) -> None:
        """Test validation of ACI Contract Filter Entry IP Protocol number."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="2200",
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_ip_protocol_choice(
        self,
    ) -> None:
        """Test validation of ACI Contract Filter Entry IP Protocol choice."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="chaos",
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_destination_from_port_number(
        self,
    ) -> None:
        """Test validation of Filter Entry Destination From Port number."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            destination_from_port=65536,
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_destination_from_port_choice(
        self,
    ) -> None:
        """Test validation of Filter Entry Destination From Port choice."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            destination_from_port="ftp",
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_destination_to_port_number(
        self,
    ) -> None:
        """Test validation of Filter Entry Destination To Port number."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            destination_to_port=65536,
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_destination_to_port_choice(
        self,
    ) -> None:
        """Test validation of Filter Entry Destination To Port choice."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            destination_to_port="ftp",
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_source_from_port_number(
        self,
    ) -> None:
        """Test validation of Filter Entry Destination From Port number."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            source_from_port=65536,
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_source_from_port_choice(
        self,
    ) -> None:
        """Test validation of Filter Entry Destination From Port choice."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            source_from_port="ftp",
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_source_to_port_number(
        self,
    ) -> None:
        """Test validation of Filter Entry Destination To Port number."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            source_to_port=65536,
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_source_to_port_choice(
        self,
    ) -> None:
        """Test validation of Filter Entry Destination To Port choice."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            source_to_port="ftp",
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_tcp_rules_established(
        self,
    ) -> None:
        """Test validation of the TCP rule combination with 'established'."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            tcp_rules=[
                ContractFilterTCPRulesChoices.TCP_ESTABLISHED,
                ContractFilterTCPRulesChoices.TCP_SYN,
            ],
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_tcp_rules_unspecified(
        self,
    ) -> None:
        """Test validation of the TCP rule combination with 'unspecified'."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ip_protocol="tcp",
            tcp_rules=[
                ContractFilterTCPRulesChoices.TCP_UNSPECIFIED,
                ContractFilterTCPRulesChoices.TCP_SYN,
            ],
        )
        with self.assertRaises(ValidationError):
            contract_filter_entry.full_clean()

    def test_invalid_aci_contract_filter_entry_ether_type_arp_opc(
        self,
    ) -> None:
        """Test validation of the ether_type and arp_opc combination."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ether_type="ip",
            arp_opc=ContractFilterARPOpenPeripheralCodesChoices.OPC_REQUEST,
        )
        with self.assertRaises(ValidationError) as context_manager:
            contract_filter_entry.full_clean()

        # Check if ValidationError contains only one error
        exception = context_manager.exception
        self.assertIn("arp_opc", exception.message_dict)
        self.assertEqual(len(exception.message_dict), 1)

    def test_invalid_aci_contract_filter_entry_ether_type_ip_protocol(
        self,
    ) -> None:
        """Test validation of the ether_type and ip_protocol combination."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ether_type="arp",
            ip_protocol="icmp",
        )
        with self.assertRaises(ValidationError) as context_manager:
            contract_filter_entry.full_clean()

        # Check if ValidationError contains only one error
        exception = context_manager.exception
        self.assertIn("ip_protocol", exception.message_dict)
        self.assertEqual(len(exception.message_dict), 1)

    def test_invalid_aci_contract_filter_entry_ether_type_ports(self) -> None:
        """Test validation of the ether_type and port combination."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ether_type="ip",
            ip_protocol="icmp",
            destination_from_port="443",
            destination_to_port="443",
            source_from_port="https",
            source_to_port="https",
        )
        with self.assertRaises(ValidationError) as context_manager:
            contract_filter_entry.full_clean()

        # Check if ValidationError contains only four errors
        exception = context_manager.exception
        self.assertIn("destination_from_port", exception.message_dict)
        self.assertIn("destination_to_port", exception.message_dict)
        self.assertIn("source_from_port", exception.message_dict)
        self.assertIn("source_to_port", exception.message_dict)
        self.assertEqual(len(exception.message_dict), 4)

    def test_invalid_aci_contract_filter_entry_icmp_v4_type(self) -> None:
        """Test validation of the ether_type, ip_protocol, and icmp."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ether_type="ip",
            ip_protocol="tcp",
            icmp_v4_type=ContractFilterICMPv4TypesChoices.ICMP_V4_ECHO_REQUEST,
        )
        with self.assertRaises(ValidationError) as context_manager:
            contract_filter_entry.full_clean()

        # Check if ValidationError contains only one error
        exception = context_manager.exception
        self.assertIn("icmp_v4_type", exception.message_dict)
        self.assertEqual(len(exception.message_dict), 1)

    def test_invalid_aci_contract_filter_entry_icmp_v6_type(self) -> None:
        """Test validation of the ether_type, ip_protocol, and icmp_v6."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ether_type="ip",
            ip_protocol="tcp",
            icmp_v6_type=ContractFilterICMPv6TypesChoices.ICMP_V6_ECHO_REQUEST,
        )
        with self.assertRaises(ValidationError) as context_manager:
            contract_filter_entry.full_clean()

        # Check if ValidationError contains only one error
        exception = context_manager.exception
        self.assertIn("icmp_v6_type", exception.message_dict)
        self.assertEqual(len(exception.message_dict), 1)

    def test_invalid_aci_contract_filter_entry_match_dscp(self) -> None:
        """Test validation of the ether_type, and match_dscp."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ether_type="arp",
            match_dscp=QualityOfServiceDSCPChoices.DSCP_EF,
        )
        with self.assertRaises(ValidationError) as context_manager:
            contract_filter_entry.full_clean()

        # Check if ValidationError contains only one error
        exception = context_manager.exception
        self.assertIn("match_dscp", exception.message_dict)
        self.assertEqual(len(exception.message_dict), 1)

    def test_invalid_aci_contract_filter_entry_match_fragments(self) -> None:
        """Test validation of the match_only_fragments_enabled."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ether_type="arp",
            match_only_fragments_enabled=True,
        )
        with self.assertRaises(ValidationError) as context_manager:
            contract_filter_entry.full_clean()

        # Check if ValidationError contains only one error
        exception = context_manager.exception
        self.assertIn("match_only_fragments_enabled", exception.message_dict)
        self.assertEqual(len(exception.message_dict), 1)

    def test_invalid_aci_contract_filter_entry_ip_protocol_tcp_only(
        self,
    ) -> None:
        """Test validation of the ip_protocol and tcp settings combination."""
        contract_filter_entry = ACIContractFilterEntry(
            name="ACIContractFilterEntryTest1",
            aci_contract_filter=self.aci_contract_filter,
            ether_type="ip",
            ip_protocol="udp",
            stateful_enabled=True,
            tcp_rules=[ContractFilterTCPRulesChoices.TCP_ESTABLISHED],
        )
        with self.assertRaises(ValidationError) as context_manager:
            contract_filter_entry.full_clean()

        # Check if ValidationError contains only four errors
        exception = context_manager.exception
        self.assertIn("stateful_enabled", exception.message_dict)
        self.assertIn("tcp_rules", exception.message_dict)
        self.assertEqual(len(exception.message_dict), 2)

    def test_constraint_unique_aci_filter_entry_name_per_aci_contract_filter(
        self,
    ) -> None:
        """Test unique constraint of ACI Contract Filter Entry name."""
        contract_filter = ACIContractFilter.objects.get(
            name=self.aci_contract_filter_name
        )
        duplicate_contract_filter_entry = ACIContractFilterEntry(
            name=self.aci_contract_filter_entry_name,
            aci_contract_filter=contract_filter,
        )
        with self.assertRaises(IntegrityError):
            duplicate_contract_filter_entry.save()


class ACIContractTestCase(TestCase):
    """Test case for ACIContract model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContract model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_contract_name = "ACITestContract"
        cls.aci_contract_alias = "ACITestContractAlias"
        cls.aci_contract_description = (
            "ACI Test Contract for NetBox ACI Plugin"
        )
        cls.aci_contract_comments = """
        ACI Contract for NetBox ACI Plugin testing.
        """
        cls.nb_tenant_name = "NetBoxTestTenant"
        cls.aci_contract_qos_class = (
            QualityOfServiceClassChoices.CLASS_UNSPECIFIED
        )
        cls.aci_contract_scope = ContractScopeChoices.SCOPE_VRF
        cls.aci_contract_target_dscp = QualityOfServiceDSCPChoices.DSCP_EF

        # Create objects
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.aci_contract = ACIContract.objects.create(
            name=cls.aci_contract_name,
            name_alias=cls.aci_contract_alias,
            description=cls.aci_contract_description,
            comments=cls.aci_contract_comments,
            aci_tenant=cls.aci_tenant,
            nb_tenant=cls.nb_tenant,
            qos_class=cls.aci_contract_qos_class,
            scope=cls.aci_contract_scope,
            target_dscp=cls.aci_contract_target_dscp,
        )

    def test_aci_contract_instance(self) -> None:
        """Test type of created ACI Contract."""
        self.assertTrue(isinstance(self.aci_contract, ACIContract))

    def test_aci_contract_str(self) -> None:
        """Test string value of created ACI Contract."""
        self.assertEqual(self.aci_contract.__str__(), self.aci_contract.name)

    def test_aci_contract_alias(self) -> None:
        """Test alias of ACI Contract."""
        self.assertEqual(self.aci_contract.name_alias, self.aci_contract_alias)

    def test_aci_contract_description(self) -> None:
        """Test description of ACI Contract."""
        self.assertEqual(
            self.aci_contract.description,
            self.aci_contract_description,
        )

    def test_aci_contract_aci_tenant_instance(self) -> None:
        """Test the ACI Tenant instance associated with ACI Contract."""
        self.assertTrue(isinstance(self.aci_contract.aci_tenant, ACITenant))

    def test_aci_contract_aci_tenant_name(self) -> None:
        """Test the ACI Tenant name associated with ACI Contract."""
        self.assertEqual(
            self.aci_contract.aci_tenant.name, self.aci_tenant_name
        )

    def test_aci_contract_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with ACI Contract."""
        self.assertTrue(isinstance(self.aci_contract.nb_tenant, Tenant))

    def test_aci_contract_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ACI Contract."""
        self.assertEqual(self.aci_contract.nb_tenant.name, self.nb_tenant_name)

    def test_aci_contract_qos_class(self) -> None:
        """Test 'qos_class' choice of ACI Contract."""
        self.assertEqual(
            self.aci_contract.qos_class, self.aci_contract_qos_class
        )

    def test_aci_contract_get_qos_class_color(self) -> None:
        """Test the 'get_qos_class_color' method of ACI Contract."""
        self.assertEqual(
            self.aci_contract.get_qos_class_color(),
            QualityOfServiceClassChoices.colors.get(
                self.aci_contract_qos_class
            ),
        )

    def test_aci_contract_scope(self) -> None:
        """Test 'scope' choice of ACI Contract."""
        self.assertEqual(self.aci_contract.scope, self.aci_contract_scope)

    def test_aci_contract_get_scope_color(self) -> None:
        """Test the 'get_scope_color' method of ACI Contract."""
        self.assertEqual(
            self.aci_contract.get_scope_color(),
            ContractScopeChoices.colors.get(self.aci_contract_scope),
        )

    def test_aci_contract_target_dscp(self) -> None:
        """Test 'target_dscp' choice of ACI Contract."""
        self.assertEqual(
            self.aci_contract.target_dscp, self.aci_contract_target_dscp
        )

    def test_invalid_aci_contract_name(self) -> None:
        """Test validation of ACI Contract naming."""
        contract = ACIContract(name="ACI Contract Test 1")
        with self.assertRaises(ValidationError):
            contract.full_clean()

    def test_invalid_aci_contract_name_length(self) -> None:
        """Test validation of ACI Contract name length."""
        contract = ACIContract(
            name="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            contract.full_clean()

    def test_invalid_aci_contract_name_alias(self) -> None:
        """Test validation of ACI Contract Filter aliasing."""
        contract = ACIContract(
            name="ACIContractTest1", name_alias="Invalid Alias"
        )
        with self.assertRaises(ValidationError):
            contract.full_clean()

    def test_invalid_aci_contract_name_alias_length(self) -> None:
        """Test validation of ACI Contract Filter name alias length."""
        contract = ACIContract(
            name="ACIContractTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            contract.full_clean()

    def test_invalid_aci_contract_description(self) -> None:
        """Test validation of ACI Contract description."""
        contract = ACIContract(
            name="ACIContractTest1", description="Invalid Description: ö"
        )
        with self.assertRaises(ValidationError):
            contract.full_clean()

    def test_invalid_aci_contract_description_length(self) -> None:
        """Test validation of ACI Contract description length."""
        contract = ACIContract(
            name="ACIContractTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
        )
        with self.assertRaises(ValidationError):
            contract.full_clean()

    def test_constraint_unique_aci_contract_name_per_aci_tenant(
        self,
    ) -> None:
        """Test unique constraint of ACI Contract name per ACI Tenant."""
        tenant = ACITenant.objects.get(name=self.aci_tenant_name)
        duplicate_contract = ACIContract(
            name=self.aci_contract_name, aci_tenant=tenant
        )
        with self.assertRaises(IntegrityError):
            duplicate_contract.save()


class ACIContractSubjectTestCase(TestCase):
    """Test case for ACIContractSubject model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractSubject model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_contract_name = "ACITestContract"
        cls.aci_contract_qos_class = (
            QualityOfServiceClassChoices.CLASS_UNSPECIFIED
        )
        cls.aci_contract_scope = ContractScopeChoices.SCOPE_VRF
        cls.aci_contract_target_dscp = QualityOfServiceDSCPChoices.DSCP_EF
        cls.aci_contract_subject_name = "ACITestContractSubject"
        cls.aci_contract_subject_alias = "ACITestContractSubjectAlias"
        cls.aci_contract_subject_description = (
            "ACI Test Contract Subject for NetBox ACI Plugin"
        )
        cls.aci_contract_subject_comments = """
        ACI Contract Subject for NetBox ACI Plugin testing.
        """
        cls.nb_tenant_name = "NetBoxTestTenant"
        cls.aci_contract_subject_apply_both_directions_enabled = True
        cls.aci_contract_subject_qos_class = (
            QualityOfServiceClassChoices.CLASS_UNSPECIFIED
        )
        cls.aci_contract_subject_qos_class_cons_to_prov = (
            QualityOfServiceClassChoices.CLASS_UNSPECIFIED
        )
        cls.aci_contract_subject_qos_class_prov_to_cons = (
            QualityOfServiceClassChoices.CLASS_UNSPECIFIED
        )
        cls.aci_contract_subject_reverse_filter_ports_enabled = True
        cls.aci_contract_subject_service_graph_name = "ACITestServiceGraph"
        cls.aci_contract_subject_service_graph_name_cons_to_prov = (
            "ACITestServiceGraph"
        )
        cls.aci_contract_subject_service_graph_name_prov_to_cons = (
            "ACITestServiceGraph"
        )
        cls.aci_contract_subject_target_dscp = (
            QualityOfServiceDSCPChoices.DSCP_EF
        )
        cls.aci_contract_subject_target_dscp_cons_to_prov = (
            QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED
        )
        cls.aci_contract_subject_target_dscp_prov_to_cons = (
            QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED
        )

        # Create objects
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.aci_contract = ACIContract.objects.create(
            name=cls.aci_contract_name,
            aci_tenant=cls.aci_tenant,
            nb_tenant=cls.nb_tenant,
            qos_class=cls.aci_contract_qos_class,
            scope=cls.aci_contract_scope,
            target_dscp=cls.aci_contract_target_dscp,
        )
        cls.aci_contract_subject = ACIContractSubject.objects.create(
            name=cls.aci_contract_subject_name,
            name_alias=cls.aci_contract_subject_alias,
            description=cls.aci_contract_subject_description,
            comments=cls.aci_contract_subject_comments,
            aci_contract=cls.aci_contract,
            nb_tenant=cls.nb_tenant,
            apply_both_directions_enabled=(
                cls.aci_contract_subject_apply_both_directions_enabled
            ),
            qos_class=cls.aci_contract_subject_qos_class,
            qos_class_cons_to_prov=(
                cls.aci_contract_subject_qos_class_cons_to_prov
            ),
            qos_class_prov_to_cons=(
                cls.aci_contract_subject_qos_class_prov_to_cons
            ),
            reverse_filter_ports_enabled=(
                cls.aci_contract_subject_reverse_filter_ports_enabled
            ),
            service_graph_name=cls.aci_contract_subject_service_graph_name,
            service_graph_name_cons_to_prov=(
                cls.aci_contract_subject_service_graph_name_cons_to_prov
            ),
            service_graph_name_prov_to_cons=(
                cls.aci_contract_subject_service_graph_name_prov_to_cons
            ),
            target_dscp=cls.aci_contract_subject_target_dscp,
            target_dscp_cons_to_prov=(
                cls.aci_contract_subject_target_dscp_cons_to_prov
            ),
            target_dscp_prov_to_cons=(
                cls.aci_contract_subject_target_dscp_prov_to_cons
            ),
        )

    def test_aci_contract_subject_instance(self) -> None:
        """Test type of created ACI Contract Subject."""
        self.assertTrue(
            isinstance(self.aci_contract_subject, ACIContractSubject)
        )

    def test_aci_contract_subject_str(self) -> None:
        """Test string value of created ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.__str__(),
            f"{self.aci_contract_subject_name}",
        )

    def test_aci_contract_subject_alias(self) -> None:
        """Test alias of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.name_alias,
            self.aci_contract_subject_alias,
        )

    def test_aci_contract_subject_description(self) -> None:
        """Test description of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.description,
            self.aci_contract_subject_description,
        )

    def test_aci_contract_subject_aci_contract_instance(
        self,
    ) -> None:
        """Test the Contract instance associated with Contract Subject."""
        self.assertTrue(
            isinstance(self.aci_contract_subject.aci_contract, ACIContract)
        )

    def test_aci_contract_subject_aci_contract_name(self) -> None:
        """Test the Contract name associated with Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.aci_contract.name,
            self.aci_contract_name,
        )

    def test_aci_contract_subject_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with Contract Subject."""
        self.assertTrue(
            isinstance(self.aci_contract_subject.nb_tenant, Tenant)
        )

    def test_aci_contract_subject_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.nb_tenant.name, self.nb_tenant_name
        )

    def test_aci_contract_subject_apply_both_directions_enabled(self) -> None:
        """Test the 'apply_both_directions_enabled' of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.apply_both_directions_enabled,
            self.aci_contract_subject_apply_both_directions_enabled,
        )

    def test_aci_contract_subject_qos_class(self) -> None:
        """Test 'qos_class' choice of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.qos_class,
            self.aci_contract_subject_qos_class,
        )

    def test_aci_contract_subject_get_qos_class_color(self) -> None:
        """Test the 'get_qos_class_color' method of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.get_qos_class_color(),
            QualityOfServiceClassChoices.colors.get(
                self.aci_contract_subject_qos_class
            ),
        )

    def test_aci_contract_subject_qos_class_cons_to_prov(self) -> None:
        """Test 'qos_class_cons_to_prov' choice of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.qos_class_cons_to_prov,
            self.aci_contract_subject_qos_class_cons_to_prov,
        )

    def test_aci_contract_subject_get_qos_class_cons_to_prov_color(
        self,
    ) -> None:
        """Test the 'get_qos_class_cons_to_prov_color' method of Subject."""
        self.assertEqual(
            self.aci_contract_subject.get_qos_class_cons_to_prov_color(),
            QualityOfServiceClassChoices.colors.get(
                self.aci_contract_subject_qos_class_cons_to_prov
            ),
        )

    def test_aci_contract_subject_qos_class_prov_to_cons(self) -> None:
        """Test 'qos_class_prov_to_cons' choice of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.qos_class_prov_to_cons,
            self.aci_contract_subject_qos_class_prov_to_cons,
        )

    def test_aci_contract_subject_get_qos_class_prov_to_cons_color(
        self,
    ) -> None:
        """Test the 'get_qos_class_prov_to_cons_color' method of Subject."""
        self.assertEqual(
            self.aci_contract_subject.get_qos_class_prov_to_cons_color(),
            QualityOfServiceClassChoices.colors.get(
                self.aci_contract_subject_qos_class_prov_to_cons
            ),
        )

    def test_aci_contract_subject_reverse_filter_ports_enabled(self) -> None:
        """Test the 'reverse_filter_ports_enabled' of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.reverse_filter_ports_enabled,
            self.aci_contract_subject_reverse_filter_ports_enabled,
        )

    def test_aci_contract_subject_service_graph_name(self) -> None:
        """Test the 'service_graph_name' of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.service_graph_name,
            self.aci_contract_subject_service_graph_name,
        )

    def test_aci_contract_subject_service_graph_name_cons_to_prov(
        self,
    ) -> None:
        """Test the 'service_graph_name_cons_to_prov' of Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.service_graph_name_cons_to_prov,
            self.aci_contract_subject_service_graph_name_cons_to_prov,
        )

    def test_aci_contract_subject_service_graph_name_prov_to_cons(
        self,
    ) -> None:
        """Test the 'service_graph_name_prov_to_cons' of Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.service_graph_name_prov_to_cons,
            self.aci_contract_subject_service_graph_name_prov_to_cons,
        )

    def test_aci_contract_subject_target_dscp(self) -> None:
        """Test 'target_dscp' choice of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.target_dscp,
            self.aci_contract_subject_target_dscp,
        )

    def test_aci_contract_subject_target_dscp_cons_to_prov(self) -> None:
        """Test 'target_dscp_cons_to_prov' choice of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.target_dscp_cons_to_prov,
            self.aci_contract_subject_target_dscp_cons_to_prov,
        )

    def test_aci_contract_subject_target_dscp_prov_to_cons(self) -> None:
        """Test 'target_dscp_prov_to_cons' choice of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.target_dscp_prov_to_cons,
            self.aci_contract_subject_target_dscp_prov_to_cons,
        )

    def test_invalid_aci_contract_subject_name(self) -> None:
        """Test validation of ACI Contract Subject naming."""
        contract_subject = ACIContractSubject(
            name="ACI Contract Filter Entry Test 1"
        )
        with self.assertRaises(ValidationError):
            contract_subject.full_clean()

    def test_invalid_aci_contract_subject_name_length(self) -> None:
        """Test validation of ACI Contract Subject name length."""
        contract_subject = ACIContractSubject(
            name="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            contract_subject.full_clean()

    def test_invalid_aci_contract_subject_name_alias(self) -> None:
        """Test validation of ACI Contract Subject aliasing."""
        contract_subject = ACIContractSubject(
            name="ACIContractSubjectTest1", name_alias="Invalid Alias"
        )
        with self.assertRaises(ValidationError):
            contract_subject.full_clean()

    def test_invalid_aci_contract_subject_name_alias_length(self) -> None:
        """Test validation of ACI Contract Subject name alias length."""
        contract_subject = ACIContractSubject(
            name="ACIContractSubjectTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            contract_subject.full_clean()

    def test_invalid_aci_contract_subject_description(self) -> None:
        """Test validation of ACI Contract Subject description."""
        contract_subject = ACIContractSubject(
            name="ACIContractSubjectTest1",
            description="Invalid Description: ö",
        )
        with self.assertRaises(ValidationError):
            contract_subject.full_clean()

    def test_invalid_aci_contract_subject_description_length(
        self,
    ) -> None:
        """Test validation of ACI Contract Subject description length."""
        contract_subject = ACIContractSubject(
            name="ACIContractSubjectTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
        )
        with self.assertRaises(ValidationError):
            contract_subject.full_clean()

    def test_constraint_unique_aci_contract_subject_name_per_aci_contract(
        self,
    ) -> None:
        """Test unique constraint of ACI Contract Subject name."""
        contract = ACIContract.objects.get(name=self.aci_contract_name)
        duplicate_contract_subject = ACIContractSubject(
            name=self.aci_contract_subject_name,
            aci_contract=contract,
        )
        with self.assertRaises(IntegrityError):
            duplicate_contract_subject.save()
