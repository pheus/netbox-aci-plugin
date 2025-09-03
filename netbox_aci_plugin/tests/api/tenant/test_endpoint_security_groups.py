# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ipam.models import VRF, IPAddress, Prefix
from tenancy.models import Tenant
from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.bridge_domains import ACIBridgeDomain
from ....models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
)
from ....models.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroup,
    ACIEsgEndpointGroupSelector,
    ACIEsgEndpointSelector,
)
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF


class ACIEndpointSecurityGroupAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Endpoint Security Group."""

    model = ACIEndpointSecurityGroup
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_app_profile",
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
        "netbox_aci_plugin.view_aciappprofile",
        "netbox_aci_plugin.view_acivrf",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Endpoint Security Group for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        nb_vrf1 = VRF.objects.create(name="VRF1", tenant=nb_tenant1)
        nb_vrf2 = VRF.objects.create(name="VRF2", tenant=nb_tenant2)
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI1")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI2")
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

        aci_esgs: tuple = (
            ACIEndpointSecurityGroup(
                name="ACIEndpointSecurityGroupTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_app_profile=aci_app_profile1,
                aci_vrf=aci_vrf1,
                nb_tenant=nb_tenant1,
                admin_shutdown=False,
                intra_esg_isolation_enabled=False,
                preferred_group_member_enabled=False,
            ),
            ACIEndpointSecurityGroup(
                name="ACIEndpointSecurityGroupTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_app_profile=aci_app_profile2,
                aci_vrf=aci_vrf2,
                nb_tenant=nb_tenant2,
            ),
            ACIEndpointSecurityGroup(
                name="ACIEndpointSecurityGroupTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_app_profile=aci_app_profile2,
                aci_vrf=aci_vrf2,
                nb_tenant=nb_tenant2,
                admin_shutdown=True,
                intra_esg_isolation_enabled=True,
                preferred_group_member_enabled=True,
            ),
        )
        ACIEndpointSecurityGroup.objects.bulk_create(aci_esgs)

        cls.create_data: list[dict] = [
            {
                "name": "ACIEndpointSecurityGroupTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_app_profile": aci_app_profile2.id,
                "aci_vrf": aci_vrf2.id,
                "nb_tenant": nb_tenant1.id,
                "admin_shutdown": False,
                "intra_esg_isolation_enabled": True,
                "preferred_group_member_enabled": True,
            },
            {
                "name": "ACIEndpointSecurityGroupTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_app_profile": aci_app_profile1.id,
                "aci_vrf": aci_vrf1.id,
                "nb_tenant": nb_tenant2.id,
                "admin_shutdown": True,
                "intra_esg_isolation_enabled": False,
                "preferred_group_member_enabled": False,
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIEsgEndpointGroupSelectorAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI ESG Endpoint Group Selector."""

    model = ACIEsgEndpointGroupSelector
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_endpoint_security_group",
        "aci_epg_object",
        "aci_epg_object_id",
        "aci_epg_object_type",
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
        "netbox_aci_plugin.view_acibridgedomain",
        "netbox_aci_plugin.view_aciendpointgroup",
        "netbox_aci_plugin.view_aciendpointsecuritygroup",
        "netbox_aci_plugin.view_aciusegendpointgroup",
        "netbox_aci_plugin.view_acivrf",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI ESG Endpoint Group Selector for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        nb_vrf1 = VRF.objects.create(name="VRF1", tenant=nb_tenant1)
        nb_vrf2 = VRF.objects.create(name="VRF2", tenant=nb_tenant2)
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI1")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI2")
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
        aci_esg1 = ACIEndpointSecurityGroup.objects.create(
            name="ACIEndpointSecurityGroupTestAPI1",
            aci_app_profile=aci_app_profile1,
            aci_vrf=aci_vrf1,
            nb_tenant=nb_tenant1,
        )
        aci_esg2 = ACIEndpointSecurityGroup.objects.create(
            name="ACIEndpointSecurityGroupTestAPI2",
            aci_app_profile=aci_app_profile2,
            aci_vrf=aci_vrf2,
            nb_tenant=nb_tenant2,
        )

        # Create attribute objects
        aci_epg1 = ACIEndpointGroup.objects.create(
            name="ACIEndpointGroupTestAPI1",
            aci_app_profile=aci_app_profile1,
            aci_bridge_domain=aci_bd1,
            nb_tenant=nb_tenant1,
        )
        aci_epg2 = ACIEndpointGroup.objects.create(
            name="ACIEndpointGroupTestAPI2",
            aci_app_profile=aci_app_profile2,
            aci_bridge_domain=aci_bd2,
            nb_tenant=nb_tenant2,
        )
        aci_epg3 = ACIEndpointGroup.objects.create(
            name="ACIEndpointGroupTestAPI3",
            aci_app_profile=aci_app_profile1,
            aci_bridge_domain=aci_bd1,
            nb_tenant=nb_tenant1,
        )
        aci_useg_epg1 = ACIUSegEndpointGroup.objects.create(
            name="ACIUSegEndpointGroupTestAPI1",
            aci_app_profile=aci_app_profile1,
            aci_bridge_domain=aci_bd1,
            nb_tenant=nb_tenant1,
        )
        aci_useg_epg2 = ACIUSegEndpointGroup.objects.create(
            name="ACIUSegEndpointGroupTestAPI2",
            aci_app_profile=aci_app_profile2,
            aci_bridge_domain=aci_bd2,
            nb_tenant=nb_tenant2,
        )

        aci_esg_epg_selectors: tuple = (
            ACIEsgEndpointGroupSelector(
                name="ACIEsgEndpointGroupSelectorTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_endpoint_security_group=aci_esg1,
                aci_epg_object=aci_epg1,
                nb_tenant=nb_tenant1,
            ),
            ACIEsgEndpointGroupSelector(
                name="ACIEsgEndpointGroupSelectorTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_endpoint_security_group=aci_esg2,
                aci_epg_object=aci_epg2,
                nb_tenant=nb_tenant2,
            ),
            ACIEsgEndpointGroupSelector(
                name="ACIEsgEndpointGroupSelectorTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_endpoint_security_group=aci_esg1,
                aci_epg_object=aci_useg_epg1,
                nb_tenant=nb_tenant2,
            ),
        )
        ACIEsgEndpointGroupSelector.objects.bulk_create(aci_esg_epg_selectors)

        cls.create_data: list[dict] = [
            {
                "name": "ACIEsgEndpointGroupSelectorTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_endpoint_security_group": aci_esg1.id,
                "aci_epg_object_type": "netbox_aci_plugin.aciendpointgroup",
                "aci_epg_object_id": aci_epg3.id,
                "nb_tenant": nb_tenant1.id,
            },
            {
                "name": "ACIEsgEndpointGroupSelectorTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_endpoint_security_group": aci_esg2.id,
                "aci_epg_object_type": "netbox_aci_plugin.aciusegendpointgroup",
                "aci_epg_object_id": aci_useg_epg2.id,
                "nb_tenant": nb_tenant2.id,
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIEsgEndpointSelectorAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI ESG Endpoint Selector."""

    model = ACIEsgEndpointSelector
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_endpoint_security_group",
        "description",
        "display",
        "ep_object",
        "ep_object_id",
        "ep_object_type",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]
    user_permissions = (
        "ipam.view_ipaddress",
        "ipam.view_prefix",
        "netbox_aci_plugin.view_acitenant",
        "netbox_aci_plugin.view_aciappprofile",
        "netbox_aci_plugin.view_aciendpointsecuritygroup",
        "netbox_aci_plugin.view_acivrf",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI ESG Endpoint Selector for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        nb_vrf1 = VRF.objects.create(name="VRF1", tenant=nb_tenant1)
        nb_vrf2 = VRF.objects.create(name="VRF2", tenant=nb_tenant2)
        aci_tenant1 = ACITenant.objects.create(name="ACITestTenantAPI1")
        aci_tenant2 = ACITenant.objects.create(name="ACITestTenantAPI2")
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
        aci_esg1 = ACIEndpointSecurityGroup.objects.create(
            name="ACIEndpointSecurityGroupTestAPI1",
            aci_app_profile=aci_app_profile1,
            aci_vrf=aci_vrf1,
            nb_tenant=nb_tenant1,
        )
        aci_esg2 = ACIEndpointSecurityGroup.objects.create(
            name="ACIEndpointSecurityGroupTestAPI2",
            aci_app_profile=aci_app_profile2,
            aci_vrf=aci_vrf2,
            nb_tenant=nb_tenant2,
        )

        # Create attribute objects
        ip_address1 = IPAddress.objects.create(address="192.168.1.1/24")
        ip_address2 = IPAddress.objects.create(address="192.168.1.2/24")
        prefix1 = Prefix.objects.create(prefix="192.168.1.0/24")
        prefix2 = Prefix.objects.create(prefix="192.168.2.0/24")

        aci_esg_ep_selectors: tuple = (
            ACIEsgEndpointSelector(
                name="ACIEsgEndpointSelectorTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_endpoint_security_group=aci_esg1,
                ep_object=ip_address1,
                nb_tenant=nb_tenant1,
            ),
            ACIEsgEndpointSelector(
                name="ACIEsgEndpointSelectorTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_endpoint_security_group=aci_esg2,
                ep_object=ip_address2,
                nb_tenant=nb_tenant2,
            ),
            ACIEsgEndpointSelector(
                name="ACIEsgEndpointSelectorTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_endpoint_security_group=aci_esg1,
                ep_object=prefix1,
                nb_tenant=nb_tenant2,
            ),
        )
        ACIEsgEndpointSelector.objects.bulk_create(aci_esg_ep_selectors)

        cls.create_data: list[dict] = [
            {
                "name": "ACIEsgEndpointSelectorTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "comments": "# ACI Test 4",
                "aci_endpoint_security_group": aci_esg1.id,
                "ep_object_type": "ipam.prefix",
                "ep_object_id": prefix2.id,
                "nb_tenant": nb_tenant1.id,
            },
            {
                "name": "ACIEsgEndpointSelectorTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_endpoint_security_group": aci_esg2.id,
                "ep_object_type": "ipam.ipaddress",
                "ep_object_id": ip_address1.id,
                "nb_tenant": nb_tenant2.id,
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }
