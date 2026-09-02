# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""API tests for tenant ACI Endpoint Group binding models."""

from ipam.models import VRF
from tenancy.models import Tenant
from utilities.testing import APIViewTestCases, GraphQLQueryTest

from ....api.urls import app_name
from ....models.access_policies.aaep import (
    ACIAAEPDomainBinding,
    ACIAttachableAccessEntityProfile,
)
from ....models.access_policies.domains import ACIPhysicalDomain
from ....models.access_policies.vlan_pools import ACIVLANPool, ACIVLANPoolRange
from ....models.fabric.fabrics import ACIFabric
from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.bridge_domains import ACIBridgeDomain
from ....models.tenant.endpoint_group_bindings import (
    ACIEndpointGroupAAEPBinding,
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

        # A union, which the generated query cannot express
        cls.graphql_query_tests = (
            GraphQLQueryTest(
                name="aci_epg_object_union",
                query=(
                    "{ aci_endpoint_group_domain_binding_list { aci_epg_object "
                    "{ ... on ACIEndpointGroupType { name } "
                    "... on ACIUSegEndpointGroupType { name } } } }"
                ),
                assert_result=cls.assert_epg_object_resolves,
            ),
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
        cls.bulk_update_invalid_data = {
            "deployment_immediacy": "invalid-immediacy",
        }

    def assert_epg_object_resolves(self, data) -> None:
        """The endpoint group union resolves a regular and a uSeg group."""
        names = {
            row["aci_epg_object"]["name"]
            for row in data["aci_endpoint_group_domain_binding_list"]
        }
        self.assertEqual(
            names,
            {
                ACIEndpointGroup.objects.first().name,
                ACIUSegEndpointGroup.objects.first().name,
            },
        )


class ACIEndpointGroupAAEPBindingAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Endpoint Group AAEP Binding."""

    model = ACIEndpointGroupAAEPBinding
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_aaep",
        "aci_endpoint_group",
        "display",
        "id",
        "url",
    ]
    user_permissions = (
        "netbox_aci_plugin.view_aciattachableaccessentityprofile",
        "netbox_aci_plugin.view_aciendpointgroup",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Endpoint Group AAEP Binding for API view testing."""
        nb_tenant = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        nb_vrf = VRF.objects.create(name="VRF2", tenant=nb_tenant)
        aci_fabric = ACIFabric.objects.create(
            name="ACITestFabricAAEPBindingAPI",
            fabric_id=104,
            infra_vlan_vid=3900,
        )
        aci_tenant = ACITenant.objects.create(
            name="ACITestTenantAAEPBindingAPI", aci_fabric=aci_fabric
        )
        aci_app_profile = ACIAppProfile.objects.create(
            name="ACITestAppProfileAAEPBindingAPI",
            aci_tenant=aci_tenant,
        )
        aci_vrf = ACIVRF.objects.create(
            name="ACI-VRF-AAEPBinding-API",
            aci_tenant=aci_tenant,
            nb_tenant=nb_tenant,
            nb_vrf=nb_vrf,
        )
        aci_bd = ACIBridgeDomain.objects.create(
            name="ACI-BD-AAEPBinding-API",
            aci_tenant=aci_tenant,
            aci_vrf=aci_vrf,
            nb_tenant=nb_tenant,
        )
        aci_epg1 = ACIEndpointGroup.objects.create(
            name="ACIEndpointGroupAAEPBindingTestAPI1",
            aci_app_profile=aci_app_profile,
            aci_bridge_domain=aci_bd,
        )
        aci_epg2 = ACIEndpointGroup.objects.create(
            name="ACIEndpointGroupAAEPBindingTestAPI2",
            aci_app_profile=aci_app_profile,
            aci_bridge_domain=aci_bd,
        )
        aci_epg3 = ACIEndpointGroup.objects.create(
            name="ACIEndpointGroupAAEPBindingTestAPI3",
            aci_app_profile=aci_app_profile,
            aci_bridge_domain=aci_bd,
        )

        aci_vlan_pool = ACIVLANPool.objects.create(
            name="ACIEndpointGroupAAEPBindingTestVLANPoolAPI",
            aci_fabric=aci_fabric,
        )
        ACIVLANPoolRange.objects.create(
            aci_vlan_pool=aci_vlan_pool,
            vlan_id_from=100,
            vlan_id_to=299,
        )
        aci_physical_domain = ACIPhysicalDomain.objects.create(
            name="ACIPhysicalDomainAAEPBindingTestAPI",
            aci_fabric=aci_fabric,
            aci_vlan_pool=aci_vlan_pool,
        )

        aci_aaep1 = ACIAttachableAccessEntityProfile.objects.create(
            name="ACIAAEPBindingTestAAEPAPI1",
            aci_fabric=aci_fabric,
        )
        aci_aaep2 = ACIAttachableAccessEntityProfile.objects.create(
            name="ACIAAEPBindingTestAAEPAPI2",
            aci_fabric=aci_fabric,
        )
        ACIAAEPDomainBinding.objects.create(
            aci_aaep=aci_aaep1,
            aci_domain_object=aci_physical_domain,
        )
        ACIAAEPDomainBinding.objects.create(
            aci_aaep=aci_aaep2,
            aci_domain_object=aci_physical_domain,
        )

        # Prerequisite domain bindings for the F0467 shared-domain validation:
        # the EPG and the AAEP must each be bound to the same ACI domain.
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=aci_epg1,
            aci_domain_object=aci_physical_domain,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=aci_epg2,
            aci_domain_object=aci_physical_domain,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=aci_epg3,
            aci_domain_object=aci_physical_domain,
        )

        ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=aci_epg1,
            aci_aaep=aci_aaep1,
            encap_vlan_id=150,
        )
        ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=aci_epg2,
            aci_aaep=aci_aaep1,
            encap_vlan_id=151,
        )
        ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=aci_epg3,
            aci_aaep=aci_aaep1,
            encap_vlan_id=152,
        )

        cls.create_data: list[dict] = [
            {
                "aci_endpoint_group": aci_epg1.id,
                "aci_aaep": aci_aaep2.id,
                "encap_vlan_id": 160,
                "comments": "# ACI Test 4",
            },
            {
                "aci_endpoint_group": aci_epg2.id,
                "aci_aaep": aci_aaep2.id,
                "encap_vlan_id": 161,
                "comments": "# ACI Test 5",
            },
            {
                "aci_endpoint_group": aci_epg3.id,
                "aci_aaep": aci_aaep2.id,
                "encap_vlan_id": 162,
                "comments": "# ACI Test 6",
            },
        ]
        cls.bulk_update_data = {
            "comments": "New comments",
        }
        cls.bulk_update_invalid_data = {
            "aci_endpoint_group": 99999999,
        }
