# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from .base import ACIBaseGraphQLTestCase


class ACIFilterGraphQLTestCase(ACIBaseGraphQLTestCase):
    """Test id list filtering on plugin GraphQL list queries."""

    def test_tenant_list_filter_by_id_in_list(self):
        """The aci_tenant_list query filters by a list of object ids."""
        self.add_permissions("netbox_aci_plugin.view_acitenant")

        id_list = ", ".join(
            f'"{pk}"' for pk in (self.aci_tenant1.pk, self.aci_tenant2.pk)
        )
        result = self.query(
            "query { aci_tenant_list(filters: {id: {in_list: ["
            + id_list
            + "]}}) { id } }"
        )

        self.assertNotIn("errors", result, result)
        returned_ids = {row["id"] for row in result["data"]["aci_tenant_list"]}
        self.assertEqual(
            returned_ids,
            {str(self.aci_tenant1.pk), str(self.aci_tenant2.pk)},
        )

    def test_tenant_list_filter_by_related_fabric_id_in_list(self):
        """The aci_tenant_list query filters by related fabric ids."""
        self.add_permissions("netbox_aci_plugin.view_acitenant")

        result = self.query(
            "query { aci_tenant_list(filters: {aci_fabric: {id: {in_list: ["
            f'"{self.aci_fabric1.pk}"'
            "]}}}) { id } }"
        )

        self.assertNotIn("errors", result, result)
        returned_ids = {row["id"] for row in result["data"]["aci_tenant_list"]}
        self.assertEqual(returned_ids, {str(self.aci_tenant1.pk)})
