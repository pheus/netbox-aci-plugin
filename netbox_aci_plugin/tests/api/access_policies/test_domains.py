# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from tenancy.models import Tenant
from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....models.access_policies.domains import ACIPhysicalDomain, ACIRoutedDomain
from ....models.access_policies.vlan_pools import ACIVLANPool
from ....models.fabric.fabrics import ACIFabric


class ACIPhysicalDomainAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Physical Domain."""

    model = ACIPhysicalDomain
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_fabric",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acifabric",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Physical Domain for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1",
            slug="netbox-tenant-api-1",
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2",
            slug="netbox-tenant-api-2",
        )
        aci_fabric1 = ACIFabric.objects.create(
            name="ACITestFabricAPI1",
            fabric_id=111,
            infra_vlan_vid=3900,
        )
        aci_fabric2 = ACIFabric.objects.create(
            name="ACITestFabricAPI2",
            fabric_id=112,
            infra_vlan_vid=3900,
        )
        aci_vlan_pool1 = ACIVLANPool.objects.create(
            name="ACIVLANPoolTestAPI1",
            aci_fabric=aci_fabric1,
        )
        aci_vlan_pool2 = ACIVLANPool.objects.create(
            name="ACIVLANPoolTestAPI2",
            aci_fabric=aci_fabric2,
        )
        physical_domains: tuple = (
            ACIPhysicalDomain(
                name="ACIPhysicalDomainTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                aci_fabric=aci_fabric1,
                aci_vlan_pool=aci_vlan_pool1,
                security_domains=["all"],
                nb_tenant=nb_tenant1,
                comments="# ACI Test 1",
            ),
            ACIPhysicalDomain(
                name="ACIPhysicalDomainTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                aci_fabric=aci_fabric1,
                aci_vlan_pool=aci_vlan_pool1,
                security_domains=["netops"],
                nb_tenant=nb_tenant2,
                comments="# ACI Test 2",
            ),
            ACIPhysicalDomain(
                name="ACIPhysicalDomainTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                aci_fabric=aci_fabric2,
                aci_vlan_pool=aci_vlan_pool2,
                security_domains=["secops"],
                nb_tenant=nb_tenant2,
                comments="# ACI Test 3",
            ),
        )
        ACIPhysicalDomain.objects.bulk_create(physical_domains)

        cls.create_data: list[dict] = [
            {
                "name": "ACIPhysicalDomainTestAPI4",
                "name_alias": "Testing",
                "description": "Fourth ACI Test",
                "aci_fabric": aci_fabric1.id,
                "aci_vlan_pool": aci_vlan_pool1.id,
                "security_domains": ["all", "netops"],
                "nb_tenant": nb_tenant1.id,
                "comments": "# ACI Test 4",
            },
            {
                "name": "ACIPhysicalDomainTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "aci_fabric": aci_fabric2.id,
                "aci_vlan_pool": aci_vlan_pool2.id,
                "security_domains": ["all"],
                "nb_tenant": nb_tenant2.id,
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIRoutedDomainAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Routed Domain."""

    model = ACIRoutedDomain
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_fabric",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]
    user_permissions = ("netbox_aci_plugin.view_acifabric",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Routed Domain for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1",
            slug="netbox-tenant-api-1",
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2",
            slug="netbox-tenant-api-2",
        )
        aci_fabric1 = ACIFabric.objects.create(
            name="ACITestFabricAPI1",
            fabric_id=111,
            infra_vlan_vid=3900,
        )
        aci_fabric2 = ACIFabric.objects.create(
            name="ACITestFabricAPI2",
            fabric_id=112,
            infra_vlan_vid=3900,
        )
        aci_vlan_pool1 = ACIVLANPool.objects.create(
            name="ACIVLANPoolTestAPI1",
            aci_fabric=aci_fabric1,
        )
        aci_vlan_pool2 = ACIVLANPool.objects.create(
            name="ACIVLANPoolTestAPI2",
            aci_fabric=aci_fabric2,
        )
        routed_domains: tuple = (
            ACIRoutedDomain(
                name="ACIRoutedDomainTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                aci_fabric=aci_fabric1,
                security_domains=["all"],
                nb_tenant=nb_tenant1,
                comments="# ACI Test 1",
            ),
            ACIRoutedDomain(
                name="ACIRoutedDomainTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                aci_fabric=aci_fabric1,
                security_domains=["netops"],
                nb_tenant=nb_tenant2,
                comments="# ACI Test 2",
            ),
            ACIRoutedDomain(
                name="ACIRoutedDomainTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                aci_fabric=aci_fabric2,
                security_domains=["secops"],
                nb_tenant=nb_tenant2,
                comments="# ACI Test 3",
            ),
        )
        ACIRoutedDomain.objects.bulk_create(routed_domains)

        cls.create_data: list[dict] = [
            {
                "name": "ACIRoutedDomainTestAPI4",
                "name_alias": "Testing",
                "description": "Fourth ACI Test",
                "aci_fabric": aci_fabric1.id,
                "aci_vlan_pool": aci_vlan_pool1.id,
                "security_domains": ["all", "netops"],
                "nb_tenant": nb_tenant1.id,
                "comments": "# ACI Test 4",
            },
            {
                "name": "ACIRoutedDomainTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "aci_fabric": aci_fabric2.id,
                "aci_vlan_pool": aci_vlan_pool2.id,
                "security_domains": ["all"],
                "nb_tenant": nb_tenant2.id,
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }
