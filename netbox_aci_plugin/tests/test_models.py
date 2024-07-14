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
    EPGQualityOfServiceClassChoices,
    VRFPCEnforcementDirectionChoices,
    VRFPCEnforcementPreferenceChoices,
)
from ..models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup
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

    def test_create_aci_tenant(self) -> None:
        """Test type and values of created ACI Tenant."""
        self.assertTrue(isinstance(self.aci_tenant, ACITenant))
        self.assertEqual(self.aci_tenant.__str__(), self.aci_tenant.name)
        self.assertEqual(self.aci_tenant.name_alias, self.aci_tenant_alias)
        self.assertEqual(
            self.aci_tenant.description, self.aci_tenant_description
        )
        self.assertTrue(isinstance(self.aci_tenant.nb_tenant, Tenant))
        self.assertEqual(self.aci_tenant.nb_tenant.name, self.nb_tenant_name)

    def test_invalid_aci_tenant_name(self) -> None:
        """Test validation of ACI Tenant naming."""
        tenant = ACITenant(name="ACI Test Tenant 1")
        with self.assertRaises(ValidationError):
            tenant.full_clean()

    def test_invalid_aci_tenant_name_alias(self) -> None:
        """Test validation of ACI Tenant aliasing."""
        tenant = ACITenant(name="ACITestTenant1", name_alias="Invalid Alias")
        with self.assertRaises(ValidationError):
            tenant.full_clean()

    def test_invalid_aci_tenant_description(self) -> None:
        """Test validation of ACI Tenant description."""
        tenant = ACITenant(
            name="ACITestTenant1", description="Invalid Description: ö"
        )
        with self.assertRaises(ValidationError):
            tenant.full_clean()

    def test_constraint_unique_aci_tenant_name(self) -> None:
        """Test unique constraint of ACI Tenant name."""
        tenant = ACITenant(name=self.aci_tenant_name)
        with self.assertRaises(IntegrityError):
            tenant.save()


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

    def test_create_aci_app_profile(self) -> None:
        """Test type and values of created ACI Application Profile."""
        self.assertTrue(isinstance(self.aci_app_profile, ACIAppProfile))
        self.assertEqual(
            self.aci_app_profile.__str__(), self.aci_app_profile.name
        )
        self.assertEqual(
            self.aci_app_profile.name_alias, self.aci_app_profile_alias
        )
        self.assertEqual(
            self.aci_app_profile.description,
            self.aci_app_profile_description,
        )
        self.assertTrue(isinstance(self.aci_app_profile.aci_tenant, ACITenant))
        self.assertEqual(
            self.aci_app_profile.aci_tenant.name, self.aci_tenant_name
        )
        self.assertTrue(isinstance(self.aci_app_profile.nb_tenant, Tenant))
        self.assertEqual(
            self.aci_app_profile.nb_tenant.name, self.nb_tenant_name
        )

    def test_invalid_aci_app_profile_name(self) -> None:
        """Test validation of ACI AppProfile naming."""
        app_profile = ACIAppProfile(name="ACI App Profile Test 1")
        with self.assertRaises(ValidationError):
            app_profile.full_clean()

    def test_invalid_aci_app_profile_name_alias(self) -> None:
        """Test validation of ACI AppProfile aliasing."""
        app_profile = ACIAppProfile(
            name="ACIAppProfileTest1", name_alias="Invalid Alias"
        )
        with self.assertRaises(ValidationError):
            app_profile.full_clean()

    def test_invalid_aci_app_profile_description(self) -> None:
        """Test validation of ACI AppProfile description."""
        app_profile = ACIAppProfile(
            name="ACIAppProfileTest1", description="Invalid Description: ö"
        )
        with self.assertRaises(ValidationError):
            app_profile.full_clean()

    def test_constraint_unique_aci_app_profile_name_per_aci_tenant(
        self,
    ) -> None:
        """Test unique constraint of ACI AppProfile name per ACI Tenant."""
        tenant = ACITenant.objects.get(name=self.aci_tenant_name)
        app_profile = ACIAppProfile(
            name=self.aci_app_profile_name, aci_tenant=tenant
        )
        with self.assertRaises(IntegrityError):
            app_profile.save()


class ACIVRFTestCase(TestCase):
    """Test case for ACIVRF model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIVRF model."""
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

    def test_create_aci_vrf(self) -> None:
        """Test type and values of created ACI VRF."""
        self.assertTrue(isinstance(self.aci_vrf, ACIVRF))
        self.assertEqual(self.aci_vrf.__str__(), self.aci_vrf.name)
        self.assertEqual(self.aci_vrf.name_alias, self.aci_vrf_alias)
        self.assertEqual(self.aci_vrf.description, self.aci_vrf_description)
        self.assertTrue(isinstance(self.aci_vrf.aci_tenant, ACITenant))
        self.assertEqual(self.aci_vrf.aci_tenant.name, self.aci_tenant_name)
        self.assertTrue(isinstance(self.aci_vrf.nb_tenant, Tenant))
        self.assertEqual(self.aci_vrf.nb_tenant.name, self.nb_tenant_name)
        self.assertTrue(isinstance(self.aci_vrf.nb_vrf, VRF))
        self.assertEqual(self.aci_vrf.nb_vrf.name, self.nb_vrf_name)
        self.assertEqual(
            self.aci_vrf.bd_enforcement_enabled,
            self.aci_vrf.bd_enforcement_enabled,
        )
        self.assertEqual(self.aci_vrf.dns_labels, self.aci_vrf_dns_labels)
        self.assertEqual(
            self.aci_vrf.ip_data_plane_learning_enabled,
            self.aci_vrf_ip_dp_learning_enabled,
        )
        self.assertEqual(
            self.aci_vrf.pc_enforcement_direction,
            self.aci_vrf_pc_enforcement_direction,
        )
        self.assertEqual(
            self.aci_vrf.pc_enforcement_preference,
            self.aci_vrf_pc_enforcement_preference,
        )
        self.assertEqual(
            self.aci_vrf.pim_ipv4_enabled, self.aci_vrf_pim_ipv4_enabled
        )
        self.assertEqual(
            self.aci_vrf.pim_ipv6_enabled, self.aci_vrf_pim_ipv6_enabled
        )
        self.assertEqual(
            self.aci_vrf.preferred_group_enabled,
            self.aci_vrf_preferred_group_enabled,
        )

    def test_invalid_aci_vrf_name(self) -> None:
        """Test validation of ACI VRF naming."""
        vrf = ACIVRF(name="ACI VRF Test 1")
        with self.assertRaises(ValidationError):
            vrf.full_clean()

    def test_invalid_aci_vrf_name_alias(self) -> None:
        """Test validation of ACI VRF aliasing."""
        vrf = ACIVRF(name="ACIVRFTest1", name_alias="Invalid Alias")
        with self.assertRaises(ValidationError):
            vrf.full_clean()

    def test_invalid_aci_vrf_description(self) -> None:
        """Test validation of ACI VRF description."""
        vrf = ACIVRF(name="ACIVRFTest1", description="Invalid Description: ö")
        with self.assertRaises(ValidationError):
            vrf.full_clean()

    def test_constraint_unique_aci_vrf_name_per_aci_tenant(self) -> None:
        """Test unique constraint of ACI VRF name per ACI Tenant."""
        tenant = ACITenant.objects.get(name=self.aci_tenant_name)
        vrf = ACIVRF(name=self.aci_vrf_name, aci_tenant=tenant)
        with self.assertRaises(IntegrityError):
            vrf.save()


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

    def test_create_aci_bridge_domain(self) -> None:
        """Test type and values of created ACI Bridge Domain."""
        self.assertTrue(isinstance(self.aci_bd, ACIBridgeDomain))
        self.assertEqual(self.aci_bd.__str__(), self.aci_bd.name)
        self.assertEqual(self.aci_bd.name_alias, self.aci_bd_alias)
        self.assertEqual(self.aci_bd.description, self.aci_bd_description)
        self.assertTrue(isinstance(self.aci_bd.aci_tenant, ACITenant))
        self.assertEqual(self.aci_bd.aci_tenant.name, self.aci_tenant_name)
        self.assertTrue(isinstance(self.aci_bd.aci_vrf, ACIVRF))
        self.assertEqual(self.aci_bd.aci_vrf.name, self.aci_vrf_name)
        self.assertTrue(isinstance(self.aci_bd.nb_tenant, Tenant))
        self.assertEqual(self.aci_bd.nb_tenant.name, self.nb_tenant_name)
        self.assertEqual(
            self.aci_bd.advertise_host_routes_enabled,
            self.aci_bd_advertise_host_routes_enabled,
        )
        self.assertEqual(
            self.aci_bd.arp_flooding_enabled, self.aci_bd_arp_flooding_enabled
        )
        self.assertEqual(
            self.aci_bd.clear_remote_mac_enabled,
            self.aci_bd_clear_remote_mac_enabled,
        )
        self.assertEqual(self.aci_bd.dhcp_labels, self.aci_bd_dhcp_labels)
        self.assertEqual(
            self.aci_bd.ep_move_detection_enabled,
            self.aci_bd_ep_move_detection_enabled,
        )
        self.assertEqual(
            self.aci_bd.igmp_interface_policy_name,
            self.aci_bd_igmp_interface_policy_name,
        )
        self.assertEqual(
            self.aci_bd.igmp_snooping_policy_name,
            self.aci_bd_igmp_snooping_policy_name,
        )
        self.assertEqual(
            self.aci_bd.ip_data_plane_learning_enabled,
            self.aci_bd_ip_dp_learning_enabled,
        )
        self.assertEqual(
            self.aci_bd.limit_ip_learn_enabled,
            self.aci_bd_limit_ip_learn_enabled,
        )
        self.assertEqual(self.aci_bd.mac_address, self.aci_bd_mac_address)
        self.assertEqual(
            self.aci_bd.multi_destination_flooding,
            self.aci_bd_multi_destination_flooding,
        )
        self.assertEqual(
            self.aci_bd.pim_ipv4_enabled, self.aci_bd_pim_ipv4_enabled
        )
        self.assertEqual(
            self.aci_bd.pim_ipv4_destination_filter,
            self.aci_bd_pim_ipv4_destination_filter,
        )
        self.assertEqual(
            self.aci_bd.pim_ipv4_source_filter,
            self.aci_bd_pim_ipv4_source_filter,
        )
        self.assertEqual(
            self.aci_bd.pim_ipv6_enabled, self.aci_bd_pim_ipv6_enabled
        )
        self.assertEqual(
            self.aci_bd.unicast_routing_enabled,
            self.aci_bd_unicast_routing_enabled,
        )
        self.assertEqual(
            self.aci_bd.unknown_ipv4_multicast,
            self.aci_bd_unknown_ipv4_multicast,
        )
        self.assertEqual(
            self.aci_bd.unknown_ipv6_multicast,
            self.aci_bd_unknown_ipv6_multicast,
        )
        self.assertEqual(
            self.aci_bd.unknown_unicast, self.aci_bd_unknown_unicast
        )
        self.assertEqual(
            self.aci_bd.virtual_mac_address, self.aci_bd_virtual_mac_address
        )

    def test_invalid_aci_bridge_domain_name(self) -> None:
        """Test validation of ACI Bridge Domain naming."""
        bd = ACIBridgeDomain(name="ACI BD Test 1")
        with self.assertRaises(ValidationError):
            bd.full_clean()

    def test_invalid_aci_bridge_domain_name_alias(self) -> None:
        """Test validation of ACI Bridge Domain aliasing."""
        bd = ACIBridgeDomain(name="ACIBDTest1", name_alias="Invalid Alias")
        with self.assertRaises(ValidationError):
            bd.full_clean()

    def test_invalid_aci_bridge_domain_description(self) -> None:
        """Test validation of ACI Bridge Domain description."""
        bd = ACIBridgeDomain(
            name="ACIBDTest1", description="Invalid Description: ö"
        )
        with self.assertRaises(ValidationError):
            bd.full_clean()

    def test_constraint_unique_aci_bridge_domain_name_per_aci_tenant(
        self,
    ) -> None:
        """Test unique constraint of ACI Bridge Domain name per ACI Tenant."""
        tenant = ACITenant.objects.get(name=self.aci_tenant_name)
        vrf = ACIVRF.objects.get(name=self.aci_vrf_name)
        bd = ACIBridgeDomain(
            name=self.aci_bd_name, aci_tenant=tenant, aci_vrf=vrf
        )
        with self.assertRaises(IntegrityError):
            bd.save()


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

    def test_create_aci_bridge_domain(self) -> None:
        """Test type and values of created ACI Bridge Domain."""
        self.assertTrue(isinstance(self.aci_bd_subnet, ACIBridgeDomainSubnet))
        self.assertEqual(self.aci_bd_subnet.__str__(), self.aci_bd_subnet.name)
        self.assertEqual(
            self.aci_bd_subnet.name_alias, self.aci_bd_subnet_alias
        )
        self.assertEqual(
            self.aci_bd_subnet.description,
            self.aci_bd_subnet_description,
        )
        self.assertTrue(isinstance(self.aci_bd_subnet.aci_tenant, ACITenant))
        self.assertEqual(
            self.aci_bd_subnet.aci_tenant.name, self.aci_tenant_name
        )
        self.assertTrue(isinstance(self.aci_bd_subnet.aci_vrf, ACIVRF))
        self.assertEqual(self.aci_bd_subnet.aci_vrf.name, self.aci_vrf_name)
        self.assertTrue(
            isinstance(self.aci_bd_subnet.aci_bridge_domain, ACIBridgeDomain)
        )
        self.assertEqual(
            self.aci_bd_subnet.aci_bridge_domain.name, self.aci_bd_name
        )
        self.assertTrue(
            isinstance(self.aci_bd_subnet.gateway_ip_address, IPAddress)
        )
        self.assertEqual(
            self.aci_bd_subnet.gateway_ip_address.address,
            self.aci_bd_subnet_gateway_ip_address,
        )
        self.assertTrue(isinstance(self.aci_bd_subnet.nb_tenant, Tenant))
        self.assertEqual(
            self.aci_bd_subnet.nb_tenant.name, self.nb_tenant_name
        )
        self.assertEqual(
            self.aci_bd_subnet.advertised_externally_enabled,
            self.aci_bd_subnet_advertised_externally_enabled,
        )
        self.assertEqual(
            self.aci_bd_subnet.igmp_querier_enabled,
            self.aci_bd_subnet_igmp_querier_enabled,
        )
        self.assertEqual(
            self.aci_bd_subnet.ip_data_plane_learning_enabled,
            self.aci_bd_subnet_ip_dp_learning_enabled,
        )
        self.assertEqual(
            self.aci_bd_subnet.no_default_gateway,
            self.aci_bd_subnet_no_default_gateway,
        )
        self.assertEqual(
            self.aci_bd_subnet.nd_ra_enabled, self.aci_bd_subnet_nd_ra_enabled
        )
        self.assertEqual(
            self.aci_bd_subnet.nd_ra_prefix_policy_name,
            self.aci_bd_subnet_nd_ra_prefix_policy_name,
        )
        self.assertEqual(
            self.aci_bd_subnet.preferred_ip_address_enabled,
            self.aci_bd_subnet_preferred_ip_address_enabled,
        )
        self.assertEqual(
            self.aci_bd_subnet.shared_enabled,
            self.aci_bd_subnet_shared_enabled,
        )
        self.assertEqual(
            self.aci_bd_subnet.virtual_ip_enabled,
            self.aci_bd_subnet_virtual_ip_enabled,
        )

    def test_invalid_aci_bridge_domain_subnet_name(self) -> None:
        """Test validation of ACI Bridge Domain Subnet naming."""
        subnet = ACIBridgeDomainSubnet(name="ACI BDSubnet Test 1")
        with self.assertRaises(ValidationError):
            subnet.full_clean()

    def test_invalid_aci_bridge_domain_subnet_name_alias(self) -> None:
        """Test validation of ACI Bridge Domain Subnet aliasing."""
        subnet = ACIBridgeDomainSubnet(
            name="ACIBDSubnetTest1", name_alias="Invalid Alias"
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

    def test_constraint_unique_aci_bd_subnet_name_per_aci_bridge_domain(
        self,
    ) -> None:
        """Test unique constraint of ACI BD Subnet name per ACI BD."""
        bd = ACIBridgeDomain.objects.get(name=self.aci_bd_name)
        gateway_ip = IPAddress.objects.create(address="10.0.1.1/24")
        subnet = ACIBridgeDomainSubnet(
            name=self.aci_bd_subnet_name,
            aci_bridge_domain=bd,
            gateway_ip_address=gateway_ip,
        )
        with self.assertRaises(IntegrityError):
            subnet.save()

    def test_constraint_unique_preferred_ip_per_bridge_domain(self) -> None:
        """Test unique constraint of one preferred ip address per ACI BD."""
        bd = ACIBridgeDomain.objects.get(name=self.aci_bd_name)
        gateway_ip = IPAddress.objects.create(address="10.0.2.1/24")
        subnet = ACIBridgeDomainSubnet(
            name="ACIBDSubnetTest1",
            aci_bridge_domain=bd,
            gateway_ip_address=gateway_ip,
            preferred_ip_address_enabled=True,
        )
        with self.assertRaises(IntegrityError):
            subnet.save()


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
        cls.aci_epg_qos_class = EPGQualityOfServiceClassChoices.CLASS_LEVEL_3
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

    def test_create_aci_endpoint_group(self) -> None:
        """Test type and values of created ACI Endpoint Group."""
        self.assertTrue(isinstance(self.aci_epg, ACIEndpointGroup))
        self.assertEqual(self.aci_epg.__str__(), self.aci_epg.name)
        self.assertEqual(self.aci_epg.name_alias, self.aci_epg_alias)
        self.assertEqual(self.aci_epg.description, self.aci_epg_description)
        self.assertTrue(isinstance(self.aci_epg.aci_tenant, ACITenant))
        self.assertEqual(self.aci_epg.aci_tenant.name, self.aci_tenant_name)
        self.assertTrue(
            isinstance(self.aci_epg.aci_app_profile, ACIAppProfile)
        )
        self.assertEqual(
            self.aci_epg.aci_app_profile.name, self.aci_app_profile_name
        )
        self.assertTrue(isinstance(self.aci_epg.aci_vrf, ACIVRF))
        self.assertEqual(self.aci_epg.aci_vrf.name, self.aci_vrf_name)
        self.assertTrue(
            isinstance(self.aci_epg.aci_bridge_domain, ACIBridgeDomain)
        )
        self.assertEqual(self.aci_epg.aci_bridge_domain.name, self.aci_bd_name)
        self.assertTrue(isinstance(self.aci_epg.nb_tenant, Tenant))
        self.assertEqual(self.aci_epg.nb_tenant.name, self.nb_tenant_name)
        self.assertEqual(
            self.aci_epg.admin_shutdown, self.aci_epg_admin_shutdown
        )
        self.assertEqual(
            self.aci_epg.custom_qos_policy_name,
            self.aci_epg_custom_qos_policy_name,
        )
        self.assertEqual(
            self.aci_epg.flood_in_encap_enabled,
            self.aci_epg_flood_in_encap_enabled,
        )
        self.assertEqual(
            self.aci_epg.intra_epg_isolation_enabled,
            self.aci_epg_intra_epg_isolation_enabled,
        )
        self.assertEqual(self.aci_epg.qos_class, self.aci_epg_qos_class)
        self.assertEqual(
            self.aci_epg.preferred_group_member_enabled,
            self.aci_epg_preferred_group_member_enabled,
        )
        self.assertEqual(
            self.aci_epg.proxy_arp_enabled, self.aci_epg_proxy_arp_enabled
        )

    def test_invalid_aci_endpoint_group_name(self) -> None:
        """Test validation of ACI Endpoint Group naming."""
        epg = ACIEndpointGroup(name="ACI EPG Test 1")
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_endpoint_group_name_alias(self) -> None:
        """Test validation of ACI Endpoint Group aliasing."""
        epg = ACIEndpointGroup(name="ACIEPGTest1", name_alias="Invalid Alias")
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_endpoint_group_description(self) -> None:
        """Test validation of ACI Endpoint Group description."""
        epg = ACIEndpointGroup(
            name="ACIEPGTest1", description="Invalid Description: ö"
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_constraint_unique_aci_endpoint_group_name_per_aci_app_profile(
        self,
    ) -> None:
        """Test unique constraint of ACI EPG name per ACI App Profile."""
        app_profile = ACIAppProfile.objects.get(name=self.aci_app_profile_name)
        bd = ACIBridgeDomain.objects.get(name=self.aci_bd_name)
        epg = ACIEndpointGroup(
            name=self.aci_epg_name,
            aci_app_profile=app_profile,
            aci_bridge_domain=bd,
        )
        with self.assertRaises(IntegrityError):
            epg.save()
