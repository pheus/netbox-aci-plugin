# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ipam.models import VRF
from tenancy.models import Tenant
from utilities.testing import APIViewTestCases

from ...api.urls import app_name
from ...models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup
from ...models.tenant_networks import ACIVRF, ACIBridgeDomain
from ...models.tenants import ACITenant


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
