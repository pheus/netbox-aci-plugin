# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.urls import reverse
from ipam.models import VRF, IPAddress
from rest_framework import status
from tenancy.models import Tenant
from utilities.testing import APITestCase, APIViewTestCases

from ..api.urls import app_name
from ..models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup
from ..models.tenant_contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from ..models.tenant_contracts import (
    ACIContract,
    ACIContractSubject,
    ACIContractSubjectFilter,
)
from ..models.tenant_networks import (
    ACIVRF,
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)
from ..models.tenants import ACITenant


class AppTest(APITestCase):
    """API test case for NetBox ACI plugin."""

    def test_root(self) -> None:
        """Test API root access of the plugin."""
        url = reverse("plugins-api:netbox_aci_plugin-api:api-root")
        response = self.client.get(f"{url}?format=api", **self.header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ACITenantAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Tenant."""

    model = ACITenant
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Tenants for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_tenants = (
            ACITenant(
                name="ACITestTenantAPI1",
                name_alias="TestingTenant1",
                description="First ACI Test Tenant",
                comments="# ACI Test Tenant 1",
                nb_tenant=nb_tenant1,
            ),
            ACITenant(
                name="ACITestTenantAPI2",
                name_alias="TestingTenant2",
                description="Second ACI Test Tenant",
                comments="# ACI Test Tenant 2",
                nb_tenant=nb_tenant1,
            ),
            ACITenant(
                name="ACITestTenantAPI3",
                name_alias="TestingTenant3",
                description="Third ACI Test Tenant",
                comments="# ACI Test Tenant 3",
                nb_tenant=nb_tenant2,
            ),
        )
        ACITenant.objects.bulk_create(aci_tenants)

        cls.create_data = [
            {
                "name": "ACITestTenantAPI4",
                "name_alias": "TestingTenant4",
                "description": "Forth ACI Test Tenant",
                "comments": "# ACI Test Tenant 4",
                "nb_tenant": nb_tenant1.id,
            },
            {
                "name": "ACITestTenantAPI5",
                "name_alias": "TestingTenant5",
                "description": "Fifth ACI Test Tenant",
                "comments": "# ACI Test Tenant 5",
                "nb_tenant": nb_tenant2.id,
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIAppProfileAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI AppProfile."""

    model = ACIAppProfile
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_tenant",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acitenant",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI AppProfile for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI1")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI2")

        aci_app_profiles = (
            ACIAppProfile(
                name="ACIAppProfileTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_tenant=aci_tenant1,
                nb_tenant=nb_tenant1,
            ),
            ACIAppProfile(
                name="ACIAppProfileTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_tenant=aci_tenant2,
                nb_tenant=nb_tenant1,
            ),
            ACIAppProfile(
                name="ACIAppProfileTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_tenant=aci_tenant1,
                nb_tenant=nb_tenant2,
            ),
        )
        ACIAppProfile.objects.bulk_create(aci_app_profiles)

        cls.create_data: list[dict] = [
            {
                "name": "ACIAppProfileTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_tenant": aci_tenant2.id,
                "nb_tenant": nb_tenant1.id,
            },
            {
                "name": "ACIAppProfileTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_tenant": aci_tenant1.id,
                "nb_tenant": nb_tenant2.id,
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIVRFAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI VRF."""

    model = ACIVRF
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_tenant",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "nb_vrf",
        "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acitenant",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI VRF for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        nb_vrf1 = VRF.objects.create(
            name="NetBox-VRF-API-1", tenant=nb_tenant1
        )
        nb_vrf2 = VRF.objects.create(
            name="NetBox-VRF-API-2", tenant=nb_tenant2
        )
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI5")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI6")

        aci_vrfs: tuple = (
            ACIVRF(
                name="ACIVRFTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_tenant=aci_tenant1,
                nb_tenant=nb_tenant1,
                nb_vrf=nb_vrf1,
                bd_enforcement_enabled=False,
                dns_labels=["DNS1", "DNS2"],
                ip_data_plane_learning_enabled=True,
                pc_enforcement_direction="ingress",
                pc_enforcement_preference="unenforced",
                pim_ipv4_enabled=False,
                pim_ipv6_enabled=False,
                preferred_group_enabled=False,
            ),
            ACIVRF(
                name="ACIVRFTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_tenant=aci_tenant2,
                nb_tenant=nb_tenant1,
                nb_vrf=nb_vrf2,
            ),
            ACIVRF(
                name="ACIVRFTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_tenant=aci_tenant1,
                nb_tenant=nb_tenant2,
                bd_enforcement_enabled=True,
                ip_data_plane_learning_enabled=False,
                pc_enforcement_direction="egress",
                pc_enforcement_preference="enforced",
                pim_ipv4_enabled=True,
                pim_ipv6_enabled=True,
                preferred_group_enabled=True,
            ),
        )
        ACIVRF.objects.bulk_create(aci_vrfs)

        cls.create_data: list[dict] = [
            {
                "name": "ACIVRFTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_tenant": aci_tenant2.id,
                "nb_tenant": nb_tenant1.id,
                "nb_vrf": nb_vrf2.id,
                "bd_enforcement_enabled": False,
                "ip_data_plane_learning_enabled": True,
                "pc_enforcement_direction": "ingress",
                "pc_enforcement_preference": "unenforced",
                "pim_ipv4_enabled": True,
                "preferred_group_enabled": False,
            },
            {
                "name": "ACIVRFTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_tenant": aci_tenant1.id,
                "nb_tenant": nb_tenant2.id,
                "nb_vrf": nb_vrf1.id,
                "ip_data_plane_learning_enabled": False,
                "pc_enforcement_direction": "egress",
                "pc_enforcement_preference": "enforced",
                "pim_ipv6_enabled": True,
                "preferred_group_enabled": False,
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIBridgeDomainAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Bridge Domain."""

    model = ACIBridgeDomain
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_tenant",
        "aci_vrf",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]
    user_permissions = (
        "netbox_aci_plugin.view_acitenant",
        "netbox_aci_plugin.view_acivrf",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Bridge Domain for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI5")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI6")
        aci_vrf1 = ACIVRF.objects.create(
            name="ACI-VRF-API-1", aci_tenant=aci_tenant1, nb_tenant=nb_tenant1
        )
        aci_vrf2 = ACIVRF.objects.create(
            name="ACI-VRF-API-2", aci_tenant=aci_tenant2, nb_tenant=nb_tenant2
        )

        aci_bds: tuple = (
            ACIBridgeDomain(
                name="ACIBridgeDomainTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_tenant=aci_tenant1,
                aci_vrf=aci_vrf1,
                nb_tenant=nb_tenant1,
                advertise_host_routes_enabled=False,
                arp_flooding_enabled=True,
                clear_remote_mac_enabled=True,
                dhcp_labels=[
                    "DHCP1",
                    "DHCP2",
                ],
                ep_move_detection_enabled=True,
                igmp_interface_policy_name="IGMP-Interface-Policy1",
                igmp_snooping_policy_name="IGMP-Snooping-Policy1",
                ip_data_plane_learning_enabled=True,
                limit_ip_learn_enabled=True,
                mac_address="00:11:22:33:44:55",
                multi_destination_flooding="bd-flood",
                pim_ipv4_enabled=False,
                pim_ipv4_destination_filter="PIM-v4-Destination-Filter1",
                pim_ipv4_source_filter="PIM-v4-Source-Filter1",
                pim_ipv6_enabled=False,
                unicast_routing_enabled=True,
                unknown_ipv4_multicast="flood",
                unknown_ipv6_multicast="flood",
                unknown_unicast="proxy",
                virtual_mac_address="00:11:22:33:44:55",
            ),
            ACIBridgeDomain(
                name="ACIBridgeDomainTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_tenant=aci_tenant2,
                aci_vrf=aci_vrf2,
                nb_tenant=nb_tenant1,
            ),
            ACIBridgeDomain(
                name="ACIBridgeDomainTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_tenant=aci_tenant1,
                aci_vrf=aci_vrf1,
                nb_tenant=nb_tenant2,
                advertise_host_routes_enabled=True,
                arp_flooding_enabled=False,
                clear_remote_mac_enabled=False,
                dhcp_labels=[
                    "DHCP1",
                    "DHCP3",
                ],
                ep_move_detection_enabled=False,
                igmp_interface_policy_name="IGMP-Interface-Policy2",
                igmp_snooping_policy_name="IGMP-Snooping-Policy2",
                ip_data_plane_learning_enabled=False,
                limit_ip_learn_enabled=False,
                mac_address="AA:11:22:33:44:55",
                multi_destination_flooding="encap-flood",
                pim_ipv4_enabled=True,
                pim_ipv6_enabled=True,
                unicast_routing_enabled=False,
                unknown_ipv4_multicast="opt-flood",
                unknown_ipv6_multicast="opt-flood",
                unknown_unicast="flood",
                virtual_mac_address="00:11:22:33:44:55",
            ),
        )
        ACIBridgeDomain.objects.bulk_create(aci_bds)

        cls.create_data: list[dict] = [
            {
                "name": "ACIBridgeDomainTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_tenant": aci_tenant2.id,
                "aci_vrf": aci_vrf2.id,
                "nb_tenant": nb_tenant1.id,
                "advertise_host_routes_enabled": False,
                "arp_flooding_enabled": True,
                "clear_remote_mac_enabled": False,
                "dhcp_labels": ["DHCP3", "DHCP4"],
                "ep_move_detection_enabled": True,
                "igmp_interface_policy_name": "IGMP-Intf-Policy1",
                "igmp_snooping_policy_name": "IGMP-Snoop-Policy1",
                "ip_data_plane_learning_enabled": True,
                "limit_ip_learn_enabled": True,
                "mac_address": "00:BB:CC:DD:EE:05",
                "multi_destination_flooding": "bd-flood",
                "pim_ipv4_enabled": False,
                "pim_ipv4_destination_filter": "",
                "pim_ipv4_source_filter": "",
                "pim_ipv6_enabled": False,
                "unicast_routing_enabled": True,
                "unknown_ipv4_multicast": "flood",
                "unknown_ipv6_multicast": "flood",
                "unknown_unicast": "proxy",
                "virtual_mac_address": None,
            },
            {
                "name": "ACIBridgeDomainTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_tenant": aci_tenant1.id,
                "aci_vrf": aci_vrf1.id,
                "nb_tenant": nb_tenant2.id,
                "advertise_host_routes_enabled": True,
                "arp_flooding_enabled": False,
                "clear_remote_mac_enabled": True,
                "dhcp_labels": ["DHCP3", "DHCP5"],
                "ep_move_detection_enabled": False,
                "igmp_interface_policy_name": "IGMP-Intf-Policy2",
                "igmp_snooping_policy_name": "IGMP-Snoop-Policy2",
                "ip_data_plane_learning_enabled": False,
                "limit_ip_learn_enabled": False,
                "mac_address": "01:BB:CC:DD:FE:01",
                "multi_destination_flooding": "drop",
                "pim_ipv4_enabled": True,
                "pim_ipv4_destination_filter": "",
                "pim_ipv4_source_filter": "",
                "pim_ipv6_enabled": True,
                "unicast_routing_enabled": False,
                "unknown_ipv4_multicast": "opt-flood",
                "unknown_ipv6_multicast": "opt-flood",
                "unknown_unicast": "flood",
                "virtual_mac_address": "00:AB:CD:11:22:02",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIBridgeDomainSubnetAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Bridge Domain Subnet."""

    model = ACIBridgeDomainSubnet
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_bridge_domain",
        "description",
        "display",
        "gateway_ip_address",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]
    user_permissions = (
        "netbox_aci_plugin.view_acitenant",
        "netbox_aci_plugin.view_acivrf",
        "netbox_aci_plugin.view_acibridgedomain",
        "ipam.view_ipaddress",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Bridge Domain Subnet for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        nb_vrf1 = VRF.objects.create(name="VRF1", tenant=nb_tenant1)
        nb_vrf2 = VRF.objects.create(name="VRF2", tenant=nb_tenant2)
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI5")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI6")
        aci_vrf1 = ACIVRF.objects.create(
            name="ACI-VRF-API-1",
            aci_tenant=aci_tenant1,
            nb_tenant=nb_tenant1,
            nb_vrf=nb_vrf1,
        )
        aci_vrf2 = ACIVRF.objects.create(
            name="ACI-VRF-API-2",
            aci_tenant=aci_tenant2,
            nb_tenant=nb_tenant2,
            nb_vrf=nb_vrf2,
        )
        aci_bd1 = ACIBridgeDomain.objects.create(
            name="ACI-BD-API-1",
            aci_tenant=aci_tenant1,
            aci_vrf=aci_vrf1,
            nb_tenant=nb_tenant1,
        )
        aci_bd2 = ACIBridgeDomain.objects.create(
            name="ACI-BD-API-2",
            aci_tenant=aci_tenant2,
            aci_vrf=aci_vrf2,
            nb_tenant=nb_tenant2,
        )
        gw_ip1 = IPAddress.objects.create(address="10.0.0.1/24", vrf=nb_vrf1)
        gw_ip2 = IPAddress.objects.create(address="10.0.1.1/24", vrf=nb_vrf1)
        gw_ip3 = IPAddress.objects.create(address="172.16.0.1/24", vrf=nb_vrf2)
        gw_ip4 = IPAddress.objects.create(address="172.16.1.1/24", vrf=nb_vrf2)
        gw_ip5 = IPAddress.objects.create(
            address="192.168.0.1/24", vrf=nb_vrf2
        )

        aci_bd_subnets: tuple = (
            ACIBridgeDomainSubnet(
                name="ACIBridgeDomainSubnetTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_bridge_domain=aci_bd1,
                gateway_ip_address=gw_ip1,
                nb_tenant=nb_tenant1,
                advertised_externally_enabled=False,
                igmp_querier_enabled=False,
                ip_data_plane_learning_enabled=True,
                no_default_gateway=False,
                nd_ra_enabled=True,
                nd_ra_prefix_policy_name="NARD-Policy1",
                preferred_ip_address_enabled=True,
                shared_enabled=False,
                virtual_ip_enabled=False,
            ),
            ACIBridgeDomainSubnet(
                name="ACIBridgeDomainSubnetTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_bridge_domain=aci_bd1,
                gateway_ip_address=gw_ip2,
                nb_tenant=nb_tenant2,
            ),
            ACIBridgeDomainSubnet(
                name="ACIBridgeDomainSubnetTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_bridge_domain=aci_bd2,
                gateway_ip_address=gw_ip3,
                nb_tenant=nb_tenant2,
                advertised_externally_enabled=True,
                igmp_querier_enabled=True,
                ip_data_plane_learning_enabled=False,
                no_default_gateway=True,
                nd_ra_enabled=False,
                nd_ra_prefix_policy_name="NARD-Policy3",
                preferred_ip_address_enabled=True,
                shared_enabled=True,
                virtual_ip_enabled=True,
            ),
        )
        ACIBridgeDomainSubnet.objects.bulk_create(aci_bd_subnets)

        cls.create_data: list[dict] = [
            {
                "name": "ACIBridgeDomainSubnetTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_bridge_domain": aci_bd2.id,
                "gateway_ip_address": gw_ip4.id,
                "nb_tenant": nb_tenant1.id,
                "advertised_externally_enabled": False,
                "igmp_querier_enabled": True,
                "ip_data_plane_learning_enabled": False,
                "no_default_gateway": True,
                "nd_ra_enabled": True,
                "nd_ra_prefix_policy_name": "NARD-Policy1",
                "preferred_ip_address_enabled": False,
                "shared_enabled": True,
                "virtual_ip_enabled": False,
            },
            {
                "name": "ACIBridgeDomainSubnetTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_bridge_domain": aci_bd2.id,
                "gateway_ip_address": gw_ip5.id,
                "nb_tenant": nb_tenant2.id,
                "advertised_externally_enabled": True,
                "igmp_querier_enabled": True,
                "ip_data_plane_learning_enabled": True,
                "no_default_gateway": False,
                "nd_ra_enabled": True,
                "nd_ra_prefix_policy_name": "NARD-Policy1",
                "preferred_ip_address_enabled": False,
                "shared_enabled": True,
                "virtual_ip_enabled": False,
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIEndpointGroupAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Endpoint Group."""

    model = ACIEndpointGroup
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_app_profile",
        "aci_bridge_domain",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]
    user_permissions = (
        "netbox_aci_plugin.view_acitenant",
        "netbox_aci_plugin.view_aciappprofile",
        "netbox_aci_plugin.view_acivrf",
        "netbox_aci_plugin.view_acibridgedomain",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Endpoint Group for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        nb_vrf1 = VRF.objects.create(name="VRF1", tenant=nb_tenant1)
        nb_vrf2 = VRF.objects.create(name="VRF2", tenant=nb_tenant2)
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI5")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI6")
        aci_app_profile1 = ACIAppProfile.objects.create(
            name="ACITestAppProfileAPI1",
            aci_tenant=aci_tenant1,
        )
        aci_app_profile2 = ACIAppProfile.objects.create(
            name="ACITestAppProfileAPI2",
            aci_tenant=aci_tenant2,
        )
        aci_vrf1 = ACIVRF.objects.create(
            name="ACI-VRF-API-1",
            aci_tenant=aci_tenant1,
            nb_tenant=nb_tenant1,
            nb_vrf=nb_vrf1,
        )
        aci_vrf2 = ACIVRF.objects.create(
            name="ACI-VRF-API-2",
            aci_tenant=aci_tenant2,
            nb_tenant=nb_tenant2,
            nb_vrf=nb_vrf2,
        )
        aci_bd1 = ACIBridgeDomain.objects.create(
            name="ACI-BD-API-1",
            aci_tenant=aci_tenant1,
            aci_vrf=aci_vrf1,
            nb_tenant=nb_tenant1,
        )
        aci_bd2 = ACIBridgeDomain.objects.create(
            name="ACI-BD-API-2",
            aci_tenant=aci_tenant2,
            aci_vrf=aci_vrf2,
            nb_tenant=nb_tenant2,
        )

        aci_epgs: tuple = (
            ACIEndpointGroup(
                name="ACIEndpointGroupTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_app_profile=aci_app_profile1,
                aci_bridge_domain=aci_bd1,
                nb_tenant=nb_tenant1,
                admin_shutdown=False,
                custom_qos_policy_name="Custom-QoS-Policy1",
                flood_in_encap_enabled=False,
                intra_epg_isolation_enabled=False,
                qos_class="unspecified",
                preferred_group_member_enabled=False,
                proxy_arp_enabled=False,
            ),
            ACIEndpointGroup(
                name="ACIEndpointGroupTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_app_profile=aci_app_profile2,
                aci_bridge_domain=aci_bd2,
                nb_tenant=nb_tenant2,
            ),
            ACIEndpointGroup(
                name="ACIEndpointGroupTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_app_profile=aci_app_profile2,
                aci_bridge_domain=aci_bd2,
                nb_tenant=nb_tenant2,
                admin_shutdown=True,
                custom_qos_policy_name="Custom-QoS-Policy2",
                flood_in_encap_enabled=True,
                intra_epg_isolation_enabled=True,
                qos_class="level1",
                preferred_group_member_enabled=True,
                proxy_arp_enabled=True,
            ),
        )
        ACIEndpointGroup.objects.bulk_create(aci_epgs)

        cls.create_data: list[dict] = [
            {
                "name": "ACIEndpointGroupTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_app_profile": aci_app_profile2.id,
                "aci_bridge_domain": aci_bd2.id,
                "nb_tenant": nb_tenant1.id,
                "admin_shutdown": False,
                "custom_qos_policy_name": "Custom-QoS-Policy1",
                "flood_in_encap_enabled": False,
                "intra_epg_isolation_enabled": True,
                "qos_class": "level3",
                "preferred_group_member_enabled": True,
                "proxy_arp_enabled": False,
            },
            {
                "name": "ACIEndpointGroupTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_app_profile": aci_app_profile1.id,
                "aci_bridge_domain": aci_bd1.id,
                "nb_tenant": nb_tenant2.id,
                "admin_shutdown": True,
                "custom_qos_policy_name": "Custom-QoS-Policy3",
                "flood_in_encap_enabled": True,
                "intra_epg_isolation_enabled": False,
                "qos_class": "level2",
                "preferred_group_member_enabled": False,
                "proxy_arp_enabled": True,
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIContractFilterAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Contract Filter."""

    model = ACIContractFilter
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_tenant",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acitenant",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Contract Filter for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI5")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI6")

        aci_contract_filters = (
            ACIContractFilter(
                name="ACIContractFilterTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_tenant=aci_tenant1,
                nb_tenant=nb_tenant1,
            ),
            ACIContractFilter(
                name="ACIContractFilterTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_tenant=aci_tenant2,
                nb_tenant=nb_tenant1,
            ),
            ACIContractFilter(
                name="ACIContractFilterTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_tenant=aci_tenant1,
                nb_tenant=nb_tenant2,
            ),
        )
        ACIContractFilter.objects.bulk_create(aci_contract_filters)

        cls.create_data: list[dict] = [
            {
                "name": "ACIContractFilterTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_tenant": aci_tenant2.id,
                "nb_tenant": nb_tenant1.id,
            },
            {
                "name": "ACIContractFilterTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_tenant": aci_tenant1.id,
                "nb_tenant": nb_tenant2.id,
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIContractFilterEntryAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Contract Filter."""

    model = ACIContractFilterEntry
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_contract_filter",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "url",
    ]
    user_permissions = (
        "netbox_aci_plugin.view_acitenant",
        "netbox_aci_plugin.view_acicontractfilter",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Contract Filter for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI5")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI6")
        aci_contract_filter1 = ACIContractFilter.objects.create(
            name="ACIContractFilterTestAPI1",
            aci_tenant=aci_tenant1,
            nb_tenant=nb_tenant1,
        )
        aci_contract_filter2 = ACIContractFilter.objects.create(
            name="ACIContractFilterTestAPI2",
            aci_tenant=aci_tenant2,
            nb_tenant=nb_tenant2,
        )

        aci_contract_filter_entries = (
            ACIContractFilterEntry(
                name="ACIContractFilterEntryTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_contract_filter=aci_contract_filter1,
                ether_type="ip",
                arp_opc="unspecified",
                ip_protocol="tcp",
                match_dscp="unspecified",
                match_only_fragments_enabled=True,
                icmp_v4_type="unspecified",
                icmp_v6_type="unspecified",
                source_from_port="1024",
                source_to_port="65535",
                destination_from_port="http",
                destination_to_port="https",
                stateful_enabled=True,
                tcp_rules=["rst", "fin"],
            ),
            ACIContractFilterEntry(
                name="ACIContractFilterEntryTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_contract_filter=aci_contract_filter2,
            ),
            ACIContractFilterEntry(
                name="ACIContractFilterEntryTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_contract_filter=aci_contract_filter1,
                ether_type="arp",
                arp_opc="reply",
                ip_protocol="unspecified",
                match_dscp="unspecified",
                match_only_fragments_enabled=False,
                icmp_v4_type="unspecified",
                icmp_v6_type="unspecified",
                source_from_port="unspecified",
                source_to_port="unspecified",
                destination_from_port="unspecified",
                destination_to_port="unspecified",
                stateful_enabled=False,
                tcp_rules=["unspecified"],
            ),
        )
        ACIContractFilterEntry.objects.bulk_create(aci_contract_filter_entries)

        cls.create_data: list[dict] = [
            {
                "name": "ACIContractFilterEntryTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_contract_filter": aci_contract_filter2.id,
                "ether_type": "ip",
                "arp_opc": "unspecified",
                "ip_protocol": "tcp",
                "match_dscp": "unspecified",
                "match_only_fragments_enabled": True,
                "icmp_v4_type": "unspecified",
                "icmp_v6_type": "unspecified",
                "source_from_port": "1024",
                "source_to_port": "65535",
                "destination_from_port": "http",
                "destination_to_port": "https",
                "stateful_enabled": True,
                "tcp_rules": ["rst", "fin"],
            },
            {
                "name": "ACIContractFilterEntryTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_contract_filter": aci_contract_filter1.id,
                "ether_type": "ip",
                "arp_opc": "unspecified",
                "ip_protocol": "5",
                "match_dscp": "unspecified",
                "match_only_fragments_enabled": False,
                "icmp_v4_type": "unspecified",
                "icmp_v6_type": "unspecified",
                "source_from_port": "unspecified",
                "source_to_port": "unspecified",
                "destination_from_port": "unspecified",
                "destination_to_port": "unspecified",
                "stateful_enabled": False,
                "tcp_rules": ["unspecified"],
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIContractAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Contract."""

    model = ACIContract
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_tenant",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "scope",
        "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acitenant",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Contract for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI5")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI6")

        aci_contracts = (
            ACIContract(
                name="ACIContractTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_tenant=aci_tenant1,
                nb_tenant=nb_tenant1,
                qos_class="unspecified",
                scope="global",
                target_dscp="unspecified",
            ),
            ACIContract(
                name="ACIContractTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_tenant=aci_tenant2,
                nb_tenant=nb_tenant1,
                qos_class="level3",
                scope="tenant",
                target_dscp="EF",
            ),
            ACIContract(
                name="ACIContractTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_tenant=aci_tenant1,
                nb_tenant=nb_tenant2,
                qos_class="level6",
                scope="context",
                target_dscp="CS3",
            ),
        )
        ACIContract.objects.bulk_create(aci_contracts)

        cls.create_data: list[dict] = [
            {
                "name": "ACIContractTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_tenant": aci_tenant2.id,
                "nb_tenant": nb_tenant1.id,
                "qos_class": "level1",
                "scope": "global",
                "target_dscp": "unspecified",
            },
            {
                "name": "ACIContractTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_tenant": aci_tenant1.id,
                "nb_tenant": nb_tenant2.id,
                "qos_class": "level2",
                "scope": "context",
                "target_dscp": "VA",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIContractSubjectAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Contract Subject."""

    model = ACIContractSubject
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_contract",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acicontract",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Contract Subject for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI5")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI6")
        aci_contract1 = ACIContract.objects.create(
            name="ACIContractTestAPI1",
            aci_tenant=aci_tenant1,
            nb_tenant=nb_tenant1,
            qos_class="unspecified",
            scope="context",
            target_dscp="unspecified",
        )
        aci_contract2 = ACIContract.objects.create(
            name="ACIContractTestAPI2",
            aci_tenant=aci_tenant2,
            nb_tenant=nb_tenant2,
            qos_class="level1",
            scope="tenant",
            target_dscp="unspecified",
        )

        aci_contract_subjects = (
            ACIContractSubject(
                name="ACIContractSubjectTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_contract=aci_contract1,
                nb_tenant=nb_tenant1,
                apply_both_directions_enabled=True,
                qos_class="unspecified",
                reverse_filter_ports_enabled=True,
                service_graph_name="ServiceGraph1",
                target_dscp="unspecified",
            ),
            ACIContractSubject(
                name="ACIContractSubjectTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_contract=aci_contract2,
                nb_tenant=nb_tenant1,
                apply_both_directions_enabled=True,
                qos_class="level3",
                reverse_filter_ports_enabled=True,
                service_graph_name="ServiceGraph2",
                target_dscp="EF",
            ),
            ACIContractSubject(
                name="ACIContractSubjectTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_contract=aci_contract1,
                nb_tenant=nb_tenant2,
                apply_both_directions_enabled=True,
                qos_class="level6",
                reverse_filter_ports_enabled=True,
                service_graph_name="ServiceGraph3",
                target_dscp="CS3",
            ),
        )
        ACIContractSubject.objects.bulk_create(aci_contract_subjects)

        cls.create_data: list[dict] = [
            {
                "name": "ACIContractSubjectTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_contract": aci_contract1.id,
                "nb_tenant": nb_tenant1.id,
                "apply_both_directions_enabled": True,
                "qos_class": "level1",
                "reverse_filter_ports_enabled": True,
                "service_graph_name": "ServiceGraph4",
                "target_dscp": "unspecified",
            },
            {
                "name": "ACIContractSubjectTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_contract": aci_contract2.id,
                "nb_tenant": nb_tenant2.id,
                "apply_both_directions_enabled": True,
                "qos_class": "level2",
                "reverse_filter_ports_enabled": True,
                "service_graph_name": "ServiceGraph4",
                "target_dscp": "VA",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIContractSubjectFilterAPIViewTestCase(
    APIViewTestCases.APIViewTestCase
):
    """API view test case for ACI Contract Subject Filter."""

    model = ACIContractSubjectFilter
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_contract_filter",
        "aci_contract_subject",
        "action",
        "display",
        "id",
        "url",
    ]
    user_permissions = (
        "netbox_aci_plugin.view_acicontractfilter",
        "netbox_aci_plugin.view_acicontractsubject",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Contract Subject Filter for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI5")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI6")
        aci_contract_filter1 = ACIContractFilter.objects.create(
            name="ACIContractFilterTestAPI1",
            aci_tenant=aci_tenant1,
            nb_tenant=nb_tenant1,
        )
        aci_contract_filter2 = ACIContractFilter.objects.create(
            name="ACIContractFilterTestAPI2",
            aci_tenant=aci_tenant2,
            nb_tenant=nb_tenant2,
        )
        aci_contract_filter3 = ACIContractFilter.objects.create(
            name="ACIContractFilterTestAPI3",
            aci_tenant=aci_tenant1,
            nb_tenant=nb_tenant2,
        )
        aci_contract_filter4 = ACIContractFilter.objects.create(
            name="ACIContractFilterTestAPI4",
            aci_tenant=aci_tenant2,
            nb_tenant=nb_tenant1,
        )
        aci_contract1 = ACIContract.objects.create(
            name="ACIContractTestAPI1",
            aci_tenant=aci_tenant1,
            nb_tenant=nb_tenant1,
            qos_class="unspecified",
            scope="context",
            target_dscp="unspecified",
        )
        aci_contract2 = ACIContract.objects.create(
            name="ACIContractTestAPI2",
            aci_tenant=aci_tenant2,
            nb_tenant=nb_tenant2,
            qos_class="level1",
            scope="tenant",
            target_dscp="unspecified",
        )
        aci_contract_subject1 = ACIContractSubject.objects.create(
            name="ACIContractSubjectTestAPI1",
            aci_contract=aci_contract1,
            nb_tenant=nb_tenant1,
            apply_both_directions_enabled=True,
            qos_class="unspecified",
            reverse_filter_ports_enabled=True,
            target_dscp="unspecified",
        )
        aci_contract_subject2 = ACIContractSubject.objects.create(
            name="ACIContractSubjectTestAPI2",
            aci_contract=aci_contract2,
            nb_tenant=nb_tenant2,
            apply_both_directions_enabled=True,
            qos_class="unspecified",
            reverse_filter_ports_enabled=True,
            target_dscp="unspecified",
        )

        aci_contract_subject_filters = (
            ACIContractSubjectFilter(
                aci_contract_filter=aci_contract_filter1,
                aci_contract_subject=aci_contract_subject1,
                action="permit",
                apply_direction="both",
                log_enabled=True,
                policy_compression_enabled=False,
                priority="default",
            ),
            ACIContractSubjectFilter(
                aci_contract_filter=aci_contract_filter2,
                aci_contract_subject=aci_contract_subject2,
                action="permit",
                apply_direction="both",
                log_enabled=False,
                policy_compression_enabled=True,
                priority="level1",
            ),
            ACIContractSubjectFilter(
                aci_contract_filter=aci_contract_filter1,
                aci_contract_subject=aci_contract_subject2,
                action="deny",
                apply_direction="ctp",
                log_enabled=False,
                policy_compression_enabled=True,
                priority="level3",
            ),
        )
        ACIContractSubjectFilter.objects.bulk_create(
            aci_contract_subject_filters
        )

        cls.create_data: list[dict] = [
            {
                "aci_contract_filter": aci_contract_filter3.id,
                "aci_contract_subject": aci_contract_subject1.id,
                "action": "permit",
                "apply_direction": "both",
                "log_enabled": True,
                "policy_compression_enabled": False,
                "priority": "default",
            },
            {
                "aci_contract_filter": aci_contract_filter4.id,
                "aci_contract_subject": aci_contract_subject2.id,
                "action": "permit",
                "apply_direction": "both",
                "log_enabled": True,
                "policy_compression_enabled": False,
                "priority": "default",
            },
        ]
        cls.bulk_update_data = {
            "log_enabled": False,
        }
