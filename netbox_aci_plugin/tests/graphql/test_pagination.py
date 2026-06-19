# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from .base import ACIBaseGraphQLTestCase


class ACIPaginationGraphQLTestCase(ACIBaseGraphQLTestCase):
    """Test pagination on plugin GraphQL list queries."""

    def test_tenant_list_pagination(self):
        """The aci_tenant_list query honors a pagination limit and offset."""
        self.add_permissions("netbox_aci_plugin.view_acitenant")

        full = self.query("query { aci_tenant_list { id } }")
        self.assertNotIn("errors", full, full)
        self.assertGreaterEqual(len(full["data"]["aci_tenant_list"]), 2)

        page1 = self.query(
            "query { aci_tenant_list(pagination: {limit: 1, offset: 0}) { id } }"
        )
        self.assertNotIn("errors", page1, page1)
        self.assertEqual(len(page1["data"]["aci_tenant_list"]), 1)

        page2 = self.query(
            "query { aci_tenant_list(pagination: {limit: 1, offset: 1}) { id } }"
        )
        self.assertNotIn("errors", page2, page2)
        self.assertEqual(len(page2["data"]["aci_tenant_list"]), 1)
        self.assertNotEqual(
            page1["data"]["aci_tenant_list"][0]["id"],
            page2["data"]["aci_tenant_list"][0]["id"],
        )
