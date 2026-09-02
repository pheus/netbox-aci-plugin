# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""API tests for access-policy AAEP models."""

from utilities.testing import APIViewTestCases, GraphQLQueryTest

from ....api.urls import app_name
from ....models.access_policies.aaep import (
    ACIAAEPDomainBinding,
    ACIAttachableAccessEntityProfile,
)
from ....models.access_policies.domains import ACIPhysicalDomain, ACIRoutedDomain
from ....models.access_policies.vlan_pools import ACIVLANPool
from ....models.fabric.fabrics import ACIFabric


class ACIAttachableAccessEntityProfileAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Attachable Access Entity Profile."""

    model = ACIAttachableAccessEntityProfile
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
        """Set up ACI AAEP for API view testing."""
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

        aci_aaeps: tuple = (
            ACIAttachableAccessEntityProfile(
                name="ACIAAEPTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_fabric=aci_fabric1,
                infra_vlan=False,
            ),
            ACIAttachableAccessEntityProfile(
                name="ACIAAEPTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_fabric=aci_fabric1,
                infra_vlan=True,
            ),
            ACIAttachableAccessEntityProfile(
                name="ACIAAEPTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_fabric=aci_fabric2,
                infra_vlan=False,
            ),
        )
        ACIAttachableAccessEntityProfile.objects.bulk_create(aci_aaeps)

        cls.create_data: list[dict] = [
            {
                "name": "ACIAAEPTestAPI4",
                "name_alias": "Testing",
                "description": "Fourth ACI Test",
                "aci_fabric": aci_fabric1.id,
                "infra_vlan": False,
                "comments": "# ACI Test 4",
            },
            {
                "name": "ACIAAEPTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "aci_fabric": aci_fabric2.id,
                "infra_vlan": True,
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }
        cls.bulk_update_invalid_data = {
            "description": "Invalid description: ö",
        }


class ACIAAEPDomainBindingAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI AAEP Domain Binding."""

    model = ACIAAEPDomainBinding
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_aaep",
        "aci_domain_object",
        "aci_domain_object_id",
        "aci_domain_object_type",
        "display",
        "id",
        "url",
    ]
    user_permissions = (
        "netbox_aci_plugin.view_aciattachableaccessentityprofile",
        "netbox_aci_plugin.view_aciphysicaldomain",
        "netbox_aci_plugin.view_acirouteddomain",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI AAEP Domain Binding for API view testing."""
        aci_fabric = ACIFabric.objects.create(
            name="ACITestFabricAPI",
            fabric_id=102,
            infra_vlan_vid=3900,
        )
        aci_vlan_pool = ACIVLANPool.objects.create(
            name="ACIAAEPBindingTestVLANPoolAPI",
            aci_fabric=aci_fabric,
        )
        aci_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACIAAEPDomainBindingTestAPI",
            aci_fabric=aci_fabric,
        )
        aci_routed_domain1 = ACIRoutedDomain.objects.create(
            name="ACIRoutedDomainTestAPI1",
            aci_fabric=aci_fabric,
        )
        aci_routed_domain2 = ACIRoutedDomain.objects.create(
            name="ACIRoutedDomainTestAPI2",
            aci_fabric=aci_fabric,
        )
        aci_routed_domain3 = ACIRoutedDomain.objects.create(
            name="ACIRoutedDomainTestAPI3",
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

        aci_aaep_domain_bindings: tuple = (
            ACIAAEPDomainBinding(
                aci_aaep=aci_aaep,
                aci_domain_object=aci_routed_domain1,
                comments="# ACI Test 1",
            ),
            ACIAAEPDomainBinding(
                aci_aaep=aci_aaep,
                aci_domain_object=aci_routed_domain2,
                comments="# ACI Test 2",
            ),
            ACIAAEPDomainBinding(
                aci_aaep=aci_aaep,
                aci_domain_object=aci_routed_domain3,
                comments="# ACI Test 3",
            ),
        )
        ACIAAEPDomainBinding.objects.bulk_create(aci_aaep_domain_bindings)

        # A union, which the generated query cannot express
        aci_physical_domain_bound = ACIPhysicalDomain.objects.create(
            name="ACIPhysicalDomainTestAPIBound",
            aci_fabric=aci_fabric,
            aci_vlan_pool=aci_vlan_pool,
        )
        ACIAAEPDomainBinding.objects.create(
            aci_aaep=aci_aaep,
            aci_domain_object=aci_physical_domain_bound,
        )
        cls.graphql_query_tests = (
            GraphQLQueryTest(
                name="aci_domain_object_union",
                query=(
                    "{ aci_aaep_domain_binding_list { aci_domain_object "
                    "{ ... on ACIPhysicalDomainType { name } "
                    "... on ACIRoutedDomainType { name } } } }"
                ),
                assert_result=cls.assert_domain_object_resolves,
            ),
        )

        cls.create_data: list[dict] = [
            {
                "aci_aaep": aci_aaep.id,
                "aci_domain_object_id": aci_physical_domain1.id,
                "aci_domain_object_type": f"{app_name}.aciphysicaldomain",
                "comments": "# ACI Test 4",
            },
            {
                "aci_aaep": aci_aaep.id,
                "aci_domain_object_id": aci_physical_domain2.id,
                "aci_domain_object_type": f"{app_name}.aciphysicaldomain",
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "comments": "New comments",
        }
        cls.bulk_update_invalid_data = {
            "aci_aaep": 99999999,
        }

    def assert_domain_object_resolves(self, data) -> None:
        """The domain union resolves both a physical and a routed domain."""
        names = {
            row["aci_domain_object"]["name"]
            for row in data["aci_aaep_domain_binding_list"]
        }
        self.assertIn("ACIPhysicalDomainTestAPIBound", names)
        self.assertIn("ACIRoutedDomainTestAPI1", names)
