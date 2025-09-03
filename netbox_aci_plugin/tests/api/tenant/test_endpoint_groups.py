# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.models import MACAddress
from ipam.models import VRF, IPAddress, Prefix
from tenancy.models import Tenant
from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.bridge_domains import ACIBridgeDomain
from ....models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
    ACIUSegNetworkAttribute,
)
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF


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


class ACIUSegEndpointGroupAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI uSeg Endpoint Group."""

    model = ACIUSegEndpointGroup
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
        """Set up ACI uSeg Endpoint Group for API view testing."""
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

        aci_useg_epgs: tuple = (
            ACIUSegEndpointGroup(
                name="ACIUSegEndpointGroupTestAPI1",
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
                match_operator="any",
                qos_class="unspecified",
                preferred_group_member_enabled=False,
            ),
            ACIUSegEndpointGroup(
                name="ACIUSegEndpointGroupTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_app_profile=aci_app_profile2,
                aci_bridge_domain=aci_bd2,
                nb_tenant=nb_tenant2,
            ),
            ACIUSegEndpointGroup(
                name="ACIUSegEndpointGroupTestAPI3",
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
                match_operator="all",
                qos_class="level1",
                preferred_group_member_enabled=True,
            ),
        )
        ACIUSegEndpointGroup.objects.bulk_create(aci_useg_epgs)

        cls.create_data: list[dict] = [
            {
                "name": "ACIUSegEndpointGroupTestAPI4",
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
                "match_operator": "any",
                "qos_class": "level3",
                "preferred_group_member_enabled": True,
            },
            {
                "name": "ACIUSegEndpointGroupTestAPI5",
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
                "match_operator": "all",
                "qos_class": "level2",
                "preferred_group_member_enabled": False,
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIUSegNetworkAttributeAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI uSeg Network Attribute."""

    model = ACIUSegNetworkAttribute
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_useg_endpoint_group",
        "attr_object",
        "attr_object_id",
        "attr_object_type",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "url",
        "use_epg_subnet",
    ]
    user_permissions = (
        "dcim.view_macaddress",
        "ipam.view_ipaddress",
        "ipam.view_iprange",
        "ipam.view_prefix",
        "netbox_aci_plugin.view_acitenant",
        "netbox_aci_plugin.view_aciappprofile",
        "netbox_aci_plugin.view_acivrf",
        "netbox_aci_plugin.view_acibridgedomain",
        "netbox_aci_plugin.view_aciusegendpointgroup",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI uSeg Endpoint Group for API view testing."""
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
        aci_useg_epg1 = ACIUSegEndpointGroup.objects.create(
            name="ACIUSegEndpointGroupTestAPI1",
            name_alias="Testing",
            description="First ACI Test",
            comments="# ACI Test 1",
            aci_app_profile=aci_app_profile1,
            aci_bridge_domain=aci_bd1,
            nb_tenant=nb_tenant1,
            match_operator="any",
        )
        aci_useg_epg2 = ACIUSegEndpointGroup.objects.create(
            name="ACIUSegEndpointGroupTestAPI2",
            name_alias="Testing",
            description="Second ACI Test",
            comments="# ACI Test 2",
            aci_app_profile=aci_app_profile2,
            aci_bridge_domain=aci_bd2,
            nb_tenant=nb_tenant2,
            match_operator="all",
        )

        # Create attribute objects
        ip_address1 = IPAddress.objects.create(address="192.168.1.1/24")
        ip_address2 = IPAddress.objects.create(address="192.168.1.2/24")
        mac_address1 = MACAddress.objects.create(mac_address="00:00:00:00:00:01")
        mac_address2 = MACAddress.objects.create(mac_address="00:00:00:00:00:02")
        prefix1 = Prefix.objects.create(prefix="192.168.1.0/24")
        prefix2 = Prefix.objects.create(prefix="192.168.2.0/24")

        aci_useg_network_attributes: tuple = (
            ACIUSegNetworkAttribute(
                name="ACIUSegNetworkAttributeTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_useg_endpoint_group=aci_useg_epg1,
                attr_object=ip_address1,
                nb_tenant=nb_tenant1,
                use_epg_subnet=False,
            ),
            ACIUSegNetworkAttribute(
                name="ACIUSegNetworkAttributeTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_useg_endpoint_group=aci_useg_epg1,
                attr_object=prefix1,
                nb_tenant=nb_tenant2,
            ),
            ACIUSegNetworkAttribute(
                name="ACIUSegNetworkAttributeTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_useg_endpoint_group=aci_useg_epg1,
                attr_object=mac_address1,
                nb_tenant=nb_tenant2,
            ),
            ACIUSegNetworkAttribute(
                name="ACIUSegNetworkAttributeTestAPI4",
                name_alias="Testing",
                description="Forth ACI Test",
                comments="# ACI Test 4",
                aci_useg_endpoint_group=aci_useg_epg2,
                nb_tenant=nb_tenant1,
                use_epg_subnet=True,
            ),
        )
        ACIUSegNetworkAttribute.objects.bulk_create(aci_useg_network_attributes)

        cls.create_data: list[dict] = [
            {
                "name": "ACIUSegNetworkAttributeTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_useg_endpoint_group": aci_useg_epg1.id,
                "attr_object_type": "ipam.ipaddress",
                "attr_object_id": ip_address2.id,
                "nb_tenant": nb_tenant1.id,
                "use_epg_subnet": False,
            },
            {
                "name": "ACIUSegNetworkAttributeTestAPI6",
                "name_alias": "Testing",
                "description": "Sixth ACI Test",
                "comments": "# ACI Test 6",
                "aci_useg_endpoint_group": aci_useg_epg2.id,
                "attr_object_type": "dcim.macaddress",
                "attr_object_id": mac_address2.id,
                "nb_tenant": nb_tenant2.id,
            },
            {
                "name": "ACIUSegNetworkAttributeTestAPI7",
                "name_alias": "Testing",
                "description": "Seventh ACI Test",
                "comments": "# ACI Test 7",
                "aci_useg_endpoint_group": aci_useg_epg2.id,
                "attr_object_type": "ipam.prefix",
                "attr_object_id": prefix2.id,
                "nb_tenant": nb_tenant2.id,
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }
