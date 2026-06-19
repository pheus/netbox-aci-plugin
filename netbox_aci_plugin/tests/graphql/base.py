# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.test import override_settings
from django.urls import reverse

from utilities.testing import APITestCase

from ...models.fabric.fabrics import ACIFabric
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF

__all__ = ("ACIBaseGraphQLTestCase",)


@override_settings(LOGIN_REQUIRED=True)
class ACIBaseGraphQLTestCase(APITestCase):
    """Base test case driving the plugin GraphQL endpoint over HTTP."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up shared ACI objects for GraphQL tests."""
        cls.aci_fabric1 = ACIFabric.objects.create(
            name="ACIGraphQLTestFabric1", fabric_id=1, infra_vlan_vid=3901
        )
        cls.aci_fabric2 = ACIFabric.objects.create(
            name="ACIGraphQLTestFabric2", fabric_id=2, infra_vlan_vid=3902
        )
        cls.aci_tenant1 = ACITenant.objects.create(
            name="ACIGraphQLTestTenant1", aci_fabric=cls.aci_fabric1
        )
        cls.aci_tenant2 = ACITenant.objects.create(
            name="ACIGraphQLTestTenant2", aci_fabric=cls.aci_fabric2
        )
        cls.aci_vrf1 = ACIVRF.objects.create(
            name="ACIGraphQLTestVRF1", aci_tenant=cls.aci_tenant1
        )

    def query(self, query_str: str) -> dict:
        """POST a GraphQL query and return the parsed JSON body."""
        response = self.client.post(
            reverse("graphql"),
            data={"query": query_str},
            format="json",
            **self.header,
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()
