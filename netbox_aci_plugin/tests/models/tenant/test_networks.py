# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from ipam.models import VRF, IPAddress
from tenancy.models import Tenant

from ....choices import (
    BDMultiDestinationFloodingChoices,
    BDUnknownMulticastChoices,
    BDUnknownUnicastChoices,
    VRFPCEnforcementDirectionChoices,
    VRFPCEnforcementPreferenceChoices,
)
from ....models.tenant.networks import (
    ACIVRF,
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)
from ....models.tenant.tenants import ACITenant


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
