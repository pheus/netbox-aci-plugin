# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ipam.models import VRF, IPAddress
from tenancy.models import Tenant
from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....models.tenant.bridge_domains import (
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF


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
        gw_ip5 = IPAddress.objects.create(address="192.168.0.1/24", vrf=nb_vrf2)

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
