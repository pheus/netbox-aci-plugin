# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""API tests for fabric Pod models."""

from dcim.models import Site
from ipam.models import Prefix
from tenancy.models import Tenant
from utilities.testing import APIViewTestCases, GraphQLQueryTest

from ....api.urls import app_name
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.pods import ACIPod


class ACIPodAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Pod."""

    model = ACIPod
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_fabric",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "pod_id",
        "url",
    ]
    user_permissions = (
        "ipam.view_prefix",
        "ipam.view_vlan",
        "netbox_aci_plugin.view_acifabric",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Pod for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        tep_pool_fab1_pod1 = Prefix.objects.create(prefix="10.1.0.0/19")
        tep_pool_fab1_pod2 = Prefix.objects.create(prefix="10.1.32.0/19")
        tep_pool_fab1_pod3 = Prefix.objects.create(prefix="10.1.64.0/19")
        tep_pool_fab2_pod1 = Prefix.objects.create(prefix="10.2.0.0/19")
        tep_pool_fab2_pod2 = Prefix.objects.create(prefix="10.2.32.0/19")

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

        aci_pods: tuple = (
            ACIPod(
                name="ACIPodTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                aci_fabric=aci_fabric1,
                pod_id="1",
                tep_pool=tep_pool_fab1_pod1,
                nb_tenant=nb_tenant1,
                comments="# ACI Test 1",
            ),
            ACIPod(
                name="ACIPodTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                aci_fabric=aci_fabric1,
                pod_id="2",
                tep_pool=tep_pool_fab1_pod2,
                nb_tenant=nb_tenant2,
                comments="# ACI Test 2",
            ),
            ACIPod(
                name="ACIPodTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                aci_fabric=aci_fabric2,
                pod_id="1",
                tep_pool=tep_pool_fab2_pod1,
                nb_tenant=nb_tenant2,
                comments="# ACI Test 3",
            ),
        )
        ACIPod.objects.bulk_create(aci_pods)

        # A union, which the generated query cannot express
        cls.scope_site = Site.objects.create(
            name="ACIPodTestAPISite", slug="acipodtestapisite"
        )
        scoped_pod = ACIPod.objects.first()
        scoped_pod.scope = cls.scope_site
        scoped_pod.save()

        cls.graphql_query_tests = (
            GraphQLQueryTest(
                name="scope_union",
                query="{ aci_pod_list { scope { ... on SiteType { name } } } }",
                assert_result=cls.assert_scope_resolves,
            ),
        )

        cls.create_data: list[dict] = [
            {
                "name": "ACIPodTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "aci_fabric": aci_fabric1.id,
                "pod_id": 3,
                "tep_pool": tep_pool_fab1_pod3.id,
                "nb_tenant": nb_tenant1.id,
                "comments": "# ACI Test 4",
            },
            {
                "name": "ACIPodTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "aci_fabric": aci_fabric2.id,
                "pod_id": 2,
                "tep_pool": tep_pool_fab2_pod2.id,
                "nb_tenant": nb_tenant2.id,
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }
        cls.bulk_update_invalid_data = {
            "description": "Invalid description: ö",
        }

    def assert_scope_resolves(self, data) -> None:
        """The scope union resolves to the assigned NetBox Site."""
        scopes = [row["scope"] for row in data["aci_pod_list"] if row["scope"]]
        self.assertEqual(scopes, [{"name": self.scope_site.name}])
