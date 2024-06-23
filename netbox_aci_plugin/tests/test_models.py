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

    def setUp(self) -> None:
        """Set up an ACI Tenant for testing."""
        acitenant_name = "ACITestTenant1"
        acitenant_name_alias = "TestingTenant"
        acitenant_description = "Tenant for NetBox ACI Plugin testing"
        acitenant_comments = """
        Tenant for NetBox ACI Plugin testing.
        """
        nb_tenant = Tenant.objects.create(name="NetBox Tenant")

        self.aci_tenant = ACITenant.objects.create(
            name=acitenant_name,
            name_alias=acitenant_name_alias,
            description=acitenant_description,
            comments=acitenant_comments,
            nb_tenant=nb_tenant,
        )
        super().setUp()

    def test_create_aci_tenant(self) -> None:
        """Test type and values of created ACI Tenant."""
        self.assertTrue(isinstance(self.aci_tenant, ACITenant))
        self.assertEqual(self.aci_tenant.__str__(), self.aci_tenant.name)
        self.assertEqual(self.aci_tenant.name_alias, "TestingTenant")
        self.assertEqual(
            self.aci_tenant.description, "Tenant for NetBox ACI Plugin testing"
        )
        self.assertTrue(isinstance(self.aci_tenant.nb_tenant, Tenant))
        self.assertEqual(self.aci_tenant.nb_tenant.name, "NetBox Tenant")

    def test_invalid_aci_tenant_name(self) -> None:
        """Test validation of ACI Tenant naming."""
        tenant = ACITenant(name="ACI Test Tenant 1")
        self.assertRaises(ValidationError, tenant.full_clean)

    def test_invalid_aci_tenant_name_alias(self) -> None:
        """Test validation of ACI Tenant aliasing."""
        tenant = ACITenant(name="ACITestTenant1", name_alias="Invalid Alias")
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
        aciappprofile_name_alias = "TestingAppProfile"
        aciappprofile_description = "AppProfile for NetBox ACI Plugin testing"
        aciappprofile_comments = """
        AppProfile for NetBox ACI Plugin testing.
        """
        aci_tenant = ACITenant.objects.create(name=acitenant_name)
        nb_tenant = Tenant.objects.create(name="NetBox Tenant")

        self.aci_app_profile = ACIAppProfile.objects.create(
            name=aciappprofile_name,
            name_alias=aciappprofile_name_alias,
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
        self.assertEqual(self.aci_app_profile.name_alias, "TestingAppProfile")
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

    def test_invalid_aci_app_profile_name_alias(self) -> None:
        """Test validation of ACI AppProfile aliasing."""
        app_profile = ACIAppProfile(
            name="ACIAppProfileTest1", name_alias="Invalid Alias"
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
        acivrf_name_alias = "TestingVRF"
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
            name_alias=acivrf_name_alias,
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
        self.assertEqual(self.aci_vrf.name_alias, "TestingVRF")
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

    def test_invalid_aci_vrf_name_alias(self) -> None:
        """Test validation of ACI VRF aliasing."""
        vrf = ACIVRF(name="ACIVRFTest1", name_alias="Invalid Alias")
        self.assertRaises(ValidationError, vrf.full_clean)

    def test_invalid_aci_vrf_description(self) -> None:
        """Test validation of ACI VRF description."""
        vrf = ACIVRF(name="ACIVRFTest1", description="Invalid Description: ö")
        self.assertRaises(ValidationError, vrf.full_clean)


class ACIBridgeDomainTestCase(TestCase):
    """Test case for ACIBridgeDomain model."""

    def setUp(self) -> None:
        """Set up an ACI Bridge Domain for testing."""
        acitenant_name = "ACITestTenant1"
        acivrf_name = "VRFTest1"
        acibd_name = "BDTest1"
        acibd_name_alias = "TestingBD"
        acibd_description = "BD for NetBox ACI Plugin testing"
        acibd_comments = """
        BD for NetBox ACI Plugin testing.
        """
        acibd_advertise_host_routes_enabled = False
        acibd_arp_flooding_enabled = True
        acibd_clear_remote_mac_enabled = True
        acibd_dhcp_labels = ["DHCP1", "DHCP2"]
        acibd_ep_move_detection_enabled = True
        acibd_igmp_interface_policy_name = "IGMPInterfacePolicy1"
        acibd_igmp_snooping_policy_name = "IGMPSnoopingPolicy1"
        acibd_ip_dp_learning_enabled = True
        acibd_limit_ip_learn_enabled = True
        acibd_mac_address = "00:11:22:33:44:55"
        acibd_multi_destination_flooding = (
            BDMultiDestinationFloodingChoices.FLOOD_BD
        )
        acibd_pim_ipv4_enabled = False
        acibd_pim_ipv4_destination_filter = "PIMDestinationFilter1"
        acibd_pim_ipv4_source_filter = "PIMSourceFilter1"
        acibd_pim_ipv6_enabled = False
        acibd_unicast_routing_enabled = True
        acibd_unknown_ipv4_multicast = (
            BDUnknownMulticastChoices.UNKNOWN_MULTI_FLOOD
        )
        acibd_unknown_ipv6_multicast = (
            BDUnknownMulticastChoices.UNKNOWN_MULTI_FLOOD
        )
        acibd_unknown_unicast = BDUnknownUnicastChoices.UNKNOWN_UNI_PROXY
        acibd_virtual_mac_address = "00:11:22:33:44:55"

        aci_tenant = ACITenant.objects.create(name=acitenant_name)
        aci_vrf = ACIVRF.objects.create(
            name=acivrf_name, aci_tenant=aci_tenant
        )
        nb_tenant = Tenant.objects.create(name="NetBox Tenant")

        self.aci_bd = ACIBridgeDomain.objects.create(
            name=acibd_name,
            name_alias=acibd_name_alias,
            description=acibd_description,
            comments=acibd_comments,
            aci_vrf=aci_vrf,
            nb_tenant=nb_tenant,
            advertise_host_routes_enabled=acibd_advertise_host_routes_enabled,
            arp_flooding_enabled=acibd_arp_flooding_enabled,
            clear_remote_mac_enabled=acibd_clear_remote_mac_enabled,
            dhcp_labels=acibd_dhcp_labels,
            ep_move_detection_enabled=acibd_ep_move_detection_enabled,
            igmp_interface_policy_name=acibd_igmp_interface_policy_name,
            igmp_snooping_policy_name=acibd_igmp_snooping_policy_name,
            ip_data_plane_learning_enabled=acibd_ip_dp_learning_enabled,
            limit_ip_learn_enabled=acibd_limit_ip_learn_enabled,
            mac_address=acibd_mac_address,
            multi_destination_flooding=acibd_multi_destination_flooding,
            pim_ipv4_enabled=acibd_pim_ipv4_enabled,
            pim_ipv4_destination_filter=acibd_pim_ipv4_destination_filter,
            pim_ipv4_source_filter=acibd_pim_ipv4_source_filter,
            pim_ipv6_enabled=acibd_pim_ipv6_enabled,
            unicast_routing_enabled=acibd_unicast_routing_enabled,
            unknown_ipv4_multicast=acibd_unknown_ipv4_multicast,
            unknown_ipv6_multicast=acibd_unknown_ipv6_multicast,
            unknown_unicast=acibd_unknown_unicast,
            virtual_mac_address=acibd_virtual_mac_address,
        )
        super().setUp()

    def test_create_aci_bridge_domain(self) -> None:
        """Test type and values of created ACI Bridge Domain."""
        self.assertTrue(isinstance(self.aci_bd, ACIBridgeDomain))
        self.assertEqual(self.aci_bd.__str__(), self.aci_bd.name)
        self.assertEqual(self.aci_bd.name_alias, "TestingBD")
        self.assertEqual(
            self.aci_bd.description, "BD for NetBox ACI Plugin testing"
        )
        self.assertTrue(isinstance(self.aci_bd.aci_tenant, ACITenant))
        self.assertEqual(self.aci_bd.aci_tenant.name, "ACITestTenant1")
        self.assertTrue(isinstance(self.aci_bd.aci_vrf, ACIVRF))
        self.assertEqual(self.aci_bd.aci_vrf.name, "VRFTest1")
        self.assertTrue(isinstance(self.aci_bd.nb_tenant, Tenant))
        self.assertEqual(self.aci_bd.nb_tenant.name, "NetBox Tenant")
        self.assertEqual(self.aci_bd.advertise_host_routes_enabled, False)
        self.assertEqual(self.aci_bd.arp_flooding_enabled, True)
        self.assertEqual(self.aci_bd.clear_remote_mac_enabled, True)
        self.assertEqual(self.aci_bd.dhcp_labels, ["DHCP1", "DHCP2"])
        self.assertEqual(self.aci_bd.ep_move_detection_enabled, True)
        self.assertEqual(
            self.aci_bd.igmp_interface_policy_name, "IGMPInterfacePolicy1"
        )
        self.assertEqual(
            self.aci_bd.igmp_snooping_policy_name, "IGMPSnoopingPolicy1"
        )
        self.assertEqual(self.aci_bd.ip_data_plane_learning_enabled, True)
        self.assertEqual(self.aci_bd.limit_ip_learn_enabled, True)
        self.assertEqual(self.aci_bd.mac_address, "00:11:22:33:44:55")
        self.assertEqual(self.aci_bd.multi_destination_flooding, "bd-flood")
        self.assertEqual(self.aci_bd.pim_ipv4_enabled, False)
        self.assertEqual(
            self.aci_bd.pim_ipv4_destination_filter, "PIMDestinationFilter1"
        )
        self.assertEqual(
            self.aci_bd.pim_ipv4_source_filter, "PIMSourceFilter1"
        )
        self.assertEqual(self.aci_bd.pim_ipv6_enabled, False)
        self.assertEqual(self.aci_bd.unicast_routing_enabled, True)
        self.assertEqual(self.aci_bd.unknown_ipv4_multicast, "flood")
        self.assertEqual(self.aci_bd.unknown_ipv6_multicast, "flood")
        self.assertEqual(self.aci_bd.unknown_unicast, "proxy")
        self.assertEqual(self.aci_bd.virtual_mac_address, "00:11:22:33:44:55")

    def test_invalid_aci_bridge_domain_name(self) -> None:
        """Test validation of ACI Bridge Domain naming."""
        bd = ACIBridgeDomain(name="ACI BD Test 1")
        self.assertRaises(ValidationError, bd.full_clean)

    def test_invalid_aci_bridge_domain_name_alias(self) -> None:
        """Test validation of ACI Bridge Domain aliasing."""
        bd = ACIBridgeDomain(name="ACIBDTest1", name_alias="Invalid Alias")
        self.assertRaises(ValidationError, bd.full_clean)

    def test_invalid_aci_bridge_domain_description(self) -> None:
        """Test validation of ACI Bridge Domain description."""
        bd = ACIBridgeDomain(
            name="ACIBDTest1", description="Invalid Description: ö"
        )
        self.assertRaises(ValidationError, bd.full_clean)


class ACIBridgeDomainSubnetTestCase(TestCase):
    """Test case for ACIBridgeDomainSubnet model."""

    def setUp(self) -> None:
        """Set up an ACI Bridge Domain Subnet for testing."""
        acitenant_name = "ACITestTenant1"
        acivrf_name = "VRFTest1"
        acibd_name = "BDTest1"
        acisnet_name = "BDSubnetTest1"
        acisnet_name_alias = "TestingBDSubnet"
        acisnet_description = "BDSubnet for NetBox ACI Plugin testing"
        acisnet_comments = """
        BDSubnet for NetBox ACI Plugin testing.
        """
        acisnet_gateway_ip_address = "10.0.0.1/24"
        acisnet_advertised_externally_enabled = False
        acisnet_igmp_querier_enabled = True
        acisnet_ip_dp_learning_enabled = True
        acisnet_no_default_gateway = False
        acisnet_nd_ra_enabled = True
        acisnet_nd_ra_prefix_policy_name = "NDRAPolicy1"
        acisnet_preferred_ip_address_enabled = True
        acisnet_shared_enabled = False
        acisnet_virtual_ip_enabled = False

        aci_tenant = ACITenant.objects.create(name=acitenant_name)
        aci_vrf = ACIVRF.objects.create(
            name=acivrf_name, aci_tenant=aci_tenant
        )
        aci_bridge_domain = ACIBridgeDomain.objects.create(
            name=acibd_name, aci_vrf=aci_vrf
        )
        aci_bd_gateway = IPAddress.objects.create(
            address=acisnet_gateway_ip_address
        )
        nb_tenant = Tenant.objects.create(name="NetBox Tenant")

        self.aci_bd_subnet = ACIBridgeDomainSubnet.objects.create(
            name=acisnet_name,
            name_alias=acisnet_name_alias,
            description=acisnet_description,
            comments=acisnet_comments,
            aci_bridge_domain=aci_bridge_domain,
            gateway_ip_address=aci_bd_gateway,
            nb_tenant=nb_tenant,
            advertised_externally_enabled=acisnet_advertised_externally_enabled,
            igmp_querier_enabled=acisnet_igmp_querier_enabled,
            ip_data_plane_learning_enabled=acisnet_ip_dp_learning_enabled,
            no_default_gateway=acisnet_no_default_gateway,
            nd_ra_enabled=acisnet_nd_ra_enabled,
            nd_ra_prefix_policy_name=acisnet_nd_ra_prefix_policy_name,
            preferred_ip_address_enabled=acisnet_preferred_ip_address_enabled,
            shared_enabled=acisnet_shared_enabled,
            virtual_ip_enabled=acisnet_virtual_ip_enabled,
        )
        super().setUp()

    def test_create_aci_bridge_domain(self) -> None:
        """Test type and values of created ACI Bridge Domain."""
        self.assertTrue(isinstance(self.aci_bd_subnet, ACIBridgeDomainSubnet))
        self.assertEqual(self.aci_bd_subnet.__str__(), self.aci_bd_subnet.name)
        self.assertEqual(self.aci_bd_subnet.name_alias, "TestingBDSubnet")
        self.assertEqual(
            self.aci_bd_subnet.description,
            "BDSubnet for NetBox ACI Plugin testing",
        )
        self.assertTrue(isinstance(self.aci_bd_subnet.aci_tenant, ACITenant))
        self.assertEqual(self.aci_bd_subnet.aci_tenant.name, "ACITestTenant1")
        self.assertTrue(isinstance(self.aci_bd_subnet.aci_vrf, ACIVRF))
        self.assertEqual(self.aci_bd_subnet.aci_vrf.name, "VRFTest1")
        self.assertTrue(
            isinstance(self.aci_bd_subnet.aci_bridge_domain, ACIBridgeDomain)
        )
        self.assertEqual(self.aci_bd_subnet.aci_bridge_domain.name, "BDTest1")
        self.assertTrue(
            isinstance(self.aci_bd_subnet.gateway_ip_address, IPAddress)
        )
        self.assertEqual(
            self.aci_bd_subnet.gateway_ip_address.address, "10.0.0.1/24"
        )
        self.assertTrue(isinstance(self.aci_bd_subnet.nb_tenant, Tenant))
        self.assertEqual(self.aci_bd_subnet.nb_tenant.name, "NetBox Tenant")
        self.assertEqual(
            self.aci_bd_subnet.advertised_externally_enabled, False
        )
        self.assertEqual(self.aci_bd_subnet.igmp_querier_enabled, True)
        self.assertEqual(
            self.aci_bd_subnet.ip_data_plane_learning_enabled, True
        )
        self.assertEqual(self.aci_bd_subnet.no_default_gateway, False)
        self.assertEqual(self.aci_bd_subnet.nd_ra_enabled, True)
        self.assertEqual(
            self.aci_bd_subnet.nd_ra_prefix_policy_name, "NDRAPolicy1"
        )
        self.assertEqual(self.aci_bd_subnet.preferred_ip_address_enabled, True)
        self.assertEqual(self.aci_bd_subnet.shared_enabled, False)
        self.assertEqual(self.aci_bd_subnet.virtual_ip_enabled, False)

    def test_invalid_aci_bridge_domain_subnet_name(self) -> None:
        """Test validation of ACI Bridge Domain Subnet naming."""
        subnet = ACIBridgeDomainSubnet(name="ACI BDSubnet Test 1")
        self.assertRaises(ValidationError, subnet.full_clean)

    def test_invalid_aci_bridge_domain_subnet_name_alias(self) -> None:
        """Test validation of ACI Bridge Domain Subnet aliasing."""
        subnet = ACIBridgeDomainSubnet(
            name="ACIBDSubnetTest1", name_alias="Invalid Alias"
        )
        self.assertRaises(ValidationError, subnet.full_clean)

    def test_invalid_aci_bridge_domain_subnet_description(self) -> None:
        """Test validation of ACI Bridge Domain Subnet description."""
        subnet = ACIBridgeDomainSubnet(
            name="ACIBDSubnetTest1", description="Invalid Description: ö"
        )
        self.assertRaises(ValidationError, subnet.full_clean)

    def test_constraint_one_preferred_ip_address_per_bridge_domain(
        self,
    ) -> None:
        """Test unique constraint of one preferred ip address per ACI BD."""
        bd = ACIBridgeDomain.objects.get(name="BDTest1")
        gateway_ip = IPAddress.objects.create(address="10.0.1.1/24")
        subnet = ACIBridgeDomainSubnet(
            name="ACIBDSubnetTest1",
            aci_bridge_domain=bd,
            gateway_ip_address=gateway_ip,
            preferred_ip_address_enabled=True,
        )
        self.assertRaises(IntegrityError, subnet.save)


class ACIEndpointGroupTestCase(TestCase):
    """Test case for ACIEndpointGroup model."""

    def setUp(self) -> None:
        """Set up an ACI Endpoint Group for testing."""
        acitenant_name = "ACITestTenant1"
        aciappprofile_name = "AppProfileTest1"
        acivrf_name = "VRFTest1"
        acibd_name = "BDTest1"
        aciepg_name = "EPGTest1"
        aciepg_name_alias = "TestingEPG"
        aciepg_description = "EPG for NetBox ACI Plugin testing"
        aciepg_comments = """
        EPG for NetBox ACI Plugin testing.
        """
        aciepg_admin_shutdown = False
        aciepg_custom_qos_policy_name = "CustomQoSPolicy1"
        aciepg_flood_in_encap_enabled = False
        aciepg_intra_epg_isolation_enabled = False
        aciepg_qos_class = EPGQualityOfServiceClassChoices.CLASS_LEVEL_3
        aciepg_preferred_group_member_enabled = False
        aciepg_proxy_arp_enabled = False

        aci_tenant = ACITenant.objects.create(name=acitenant_name)
        aci_app_profile = ACIAppProfile.objects.create(
            name=aciappprofile_name, aci_tenant=aci_tenant
        )
        aci_vrf = ACIVRF.objects.create(
            name=acivrf_name, aci_tenant=aci_tenant
        )
        aci_bd = ACIBridgeDomain.objects.create(
            name=acibd_name, aci_vrf=aci_vrf
        )
        nb_tenant = Tenant.objects.create(name="NetBox Tenant")

        self.aci_epg = ACIEndpointGroup.objects.create(
            name=aciepg_name,
            name_alias=aciepg_name_alias,
            description=aciepg_description,
            comments=aciepg_comments,
            aci_app_profile=aci_app_profile,
            aci_bridge_domain=aci_bd,
            nb_tenant=nb_tenant,
            admin_shutdown=aciepg_admin_shutdown,
            custom_qos_policy_name=aciepg_custom_qos_policy_name,
            flood_in_encap_enabled=aciepg_flood_in_encap_enabled,
            intra_epg_isolation_enabled=aciepg_intra_epg_isolation_enabled,
            qos_class=aciepg_qos_class,
            preferred_group_member_enabled=aciepg_preferred_group_member_enabled,
            proxy_arp_enabled=aciepg_proxy_arp_enabled,
        )
        super().setUp()

    def test_create_aci_endpoint_group(self) -> None:
        """Test type and values of created ACI Endpoint Group."""
        self.assertTrue(isinstance(self.aci_epg, ACIEndpointGroup))
        self.assertEqual(self.aci_epg.__str__(), self.aci_epg.name)
        self.assertEqual(self.aci_epg.name_alias, "TestingEPG")
        self.assertEqual(
            self.aci_epg.description, "EPG for NetBox ACI Plugin testing"
        )
        self.assertTrue(isinstance(self.aci_epg.aci_tenant, ACITenant))
        self.assertEqual(self.aci_epg.aci_tenant.name, "ACITestTenant1")
        self.assertTrue(
            isinstance(self.aci_epg.aci_app_profile, ACIAppProfile)
        )
        self.assertEqual(self.aci_epg.aci_app_profile.name, "AppProfileTest1")
        self.assertTrue(isinstance(self.aci_epg.aci_vrf, ACIVRF))
        self.assertEqual(self.aci_epg.aci_vrf.name, "VRFTest1")
        self.assertTrue(
            isinstance(self.aci_epg.aci_bridge_domain, ACIBridgeDomain)
        )
        self.assertEqual(self.aci_epg.aci_bridge_domain.name, "BDTest1")
        self.assertTrue(isinstance(self.aci_epg.nb_tenant, Tenant))
        self.assertEqual(self.aci_epg.nb_tenant.name, "NetBox Tenant")
        self.assertEqual(self.aci_epg.admin_shutdown, False)
        self.assertEqual(
            self.aci_epg.custom_qos_policy_name, "CustomQoSPolicy1"
        )
        self.assertEqual(self.aci_epg.flood_in_encap_enabled, False)
        self.assertEqual(self.aci_epg.intra_epg_isolation_enabled, False)
        self.assertEqual(self.aci_epg.qos_class, "level3")
        self.assertEqual(self.aci_epg.preferred_group_member_enabled, False)
        self.assertEqual(self.aci_epg.proxy_arp_enabled, False)

    def test_invalid_aci_endpoint_group_name(self) -> None:
        """Test validation of ACI Endpoint Group naming."""
        epg = ACIEndpointGroup(name="ACI EPG Test 1")
        self.assertRaises(ValidationError, epg.full_clean)

    def test_invalid_aci_endpoint_group_name_alias(self) -> None:
        """Test validation of ACI Endpoint Group aliasing."""
        epg = ACIEndpointGroup(name="ACIEPGTest1", name_alias="Invalid Alias")
        self.assertRaises(ValidationError, epg.full_clean)

    def test_invalid_aci_endpoint_group_description(self) -> None:
        """Test validation of ACI Endpoint Group description."""
        epg = ACIEndpointGroup(
            name="ACIEPGTest1", description="Invalid Description: ö"
        )
        self.assertRaises(ValidationError, epg.full_clean)
