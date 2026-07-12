# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""API tests for the tenant ACI Endpoint Group Domain Binding model."""

from ipam.models import VRF
from tenancy.models import Tenant
from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....models.access_policies.domains import ACIPhysicalDomain
from ....models.access_policies.vlan_pools import ACIVLANPool
from ....models.fabric.fabrics import ACIFabric
from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.bridge_domains import ACIBridgeDomain
from ....models.tenant.endpoint_group_bindings import (
    ACIEndpointGroupDomainBinding,
)
from ....models.tenant.endpoint_groups import ACIEndpointGroup, ACIUSegEndpointGroup
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF


class ACIEndpointGroupDomainBindingAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Endpoint Group Domain Binding."""

    model = ACIEndpointGroupDomainBinding
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_domain_object",
        "aci_domain_object_id",
        "aci_domain_object_type",
        "aci_epg_object",
        "aci_epg_object_id",
        "aci_epg_object_type",
        "display",
        "id",
        "url",
    ]
    user_permissions = (
        "netbox_aci_plugin.view_aciendpointgroup",
        "netbox_aci_plugin.view_aciusegendpointgroup",
        "netbox_aci_plugin.view_aciphysicaldomain",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Endpoint Group Domain Binding for API view testing."""
        nb_tenant = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_vrf = VRF.objects.create(name="VRF1", tenant=nb_tenant)
        aci_fabric = ACIFabric.objects.create(
            name="ACITestFabricAPI",
            fabric_id=102,
            infra_vlan_vid=3900,
        )
        aci_tenant = ACITenant.objects.create(
            name="ACITestTenantAPI5", aci_fabric=aci_fabric
        )
        aci_app_profile = ACIAppProfile.objects.create(
            name="ACITestAppProfileAPI1",
            aci_tenant=aci_tenant,
        )
        aci_vrf = ACIVRF.objects.create(
            name="ACI-VRF-API-1",
            aci_tenant=aci_tenant,
            nb_tenant=nb_tenant,
            nb_vrf=nb_vrf,
        )
        aci_bd = ACIBridgeDomain.objects.create(
            name="ACI-BD-API-1",
            aci_tenant=aci_tenant,
            aci_vrf=aci_vrf,
            nb_tenant=nb_tenant,
        )
        aci_epg = ACIEndpointGroup.objects.create(
            name="ACIEndpointGroupTestAPI1",
            aci_app_profile=aci_app_profile,
            aci_bridge_domain=aci_bd,
        )
        aci_useg_epg = ACIUSegEndpointGroup.objects.create(
            name="ACIUSegEndpointGroupTestAPI1",
            aci_app_profile=aci_app_profile,
            aci_bridge_domain=aci_bd,
        )

        aci_vlan_pool = ACIVLANPool.objects.create(
            name="ACIEndpointGroupDomainBindingTestVLANPoolAPI",
            aci_fabric=aci_fabric,
        )
        aci_physical_domain1 = ACIPhysicalDomain.objects.create(
            name="ACIPhysicalDomainTestAPI1",
            aci_fabric=aci_fabric,
            aci_vlan_pool=aci_vlan_pool,
        )
        aci_physical_domain2 = ACIPhysicalDomain.objects.create(
            name="ACIPhysicalDomainTestAPI2",
            aci_fabric=aci_fabric,
            aci_vlan_pool=aci_vlan_pool,
        )
        aci_physical_domain3 = ACIPhysicalDomain.objects.create(
            name="ACIPhysicalDomainTestAPI3",
            aci_fabric=aci_fabric,
            aci_vlan_pool=aci_vlan_pool,
        )
        aci_physical_domain4 = ACIPhysicalDomain.objects.create(
            name="ACIPhysicalDomainTestAPI4",
            aci_fabric=aci_fabric,
            aci_vlan_pool=aci_vlan_pool,
        )

        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=aci_epg,
            aci_domain_object=aci_physical_domain1,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=aci_useg_epg,
            aci_domain_object=aci_physical_domain1,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=aci_epg,
            aci_domain_object=aci_physical_domain2,
        )

        cls.create_data: list[dict] = [
            {
                "aci_epg_object_id": aci_epg.id,
                "aci_epg_object_type": f"{app_name}.aciendpointgroup",
                "aci_domain_object_id": aci_physical_domain3.id,
                "aci_domain_object_type": f"{app_name}.aciphysicaldomain",
                "comments": "# ACI Test 4",
            },
            {
                "aci_epg_object_id": aci_useg_epg.id,
                "aci_epg_object_type": f"{app_name}.aciusegendpointgroup",
                "aci_domain_object_id": aci_physical_domain4.id,
                "aci_domain_object_type": f"{app_name}.aciphysicaldomain",
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "comments": "New comments",
        }
