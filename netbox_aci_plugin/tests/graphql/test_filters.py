# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.graphql.schema import schema

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


class ACISchemaGraphQLTestCase(ACIBaseGraphQLTestCase):
    """Test the plugin GraphQL schema shape for the Access Interface types."""

    def test_node_type_excludes_cached_fabric_field(self):
        """The ACINode type does not expose its cached fabric field."""
        self.assertIsNone(schema.get_field_for_type("_aci_fabric", "ACINodeType"))

    def test_fabric_type_includes_access_interface_reverse_lists(self):
        """The ACIFabric type exposes the two new reverse list fields."""
        self.assertIsNotNone(
            schema.get_field_for_type(
                "aci_leaf_interface_policy_groups", "ACIFabricType"
            )
        )
        self.assertIsNotNone(
            schema.get_field_for_type("aci_vpc_protection_groups", "ACIFabricType")
        )

    def test_fabric_list_query_returns_access_interface_reverse_lists(self):
        """The aci_fabric_list query resolves both new reverse list fields."""
        self.add_permissions(
            "netbox_aci_plugin.view_acifabric",
            "netbox_aci_plugin.view_acileafinterfacepolicygroup",
            "netbox_aci_plugin.view_acivpcprotectiongroup",
        )

        result = self.query(
            "query { aci_fabric_list(filters: {id: {in_list: ["
            f'"{self.aci_fabric1.pk}"'
            "]}}) { id "
            "aci_leaf_interface_policy_groups { id } "
            "aci_vpc_protection_groups { id } } }"
        )

        self.assertNotIn("errors", result, result)
        fabric_row = result["data"]["aci_fabric_list"][0]
        self.assertEqual(
            {row["id"] for row in fabric_row["aci_leaf_interface_policy_groups"]},
            {str(self.aci_leaf_interface_policy_group1.pk)},
        )
        self.assertEqual(
            {row["id"] for row in fabric_row["aci_vpc_protection_groups"]},
            {str(self.aci_vpc_protection_group1.pk)},
        )

    def test_fabric_type_includes_leaf_switch_profile_reverse_list(self):
        """The ACIFabric type exposes the leaf switch profile reverse list."""
        self.assertIsNotNone(
            schema.get_field_for_type("aci_leaf_switch_profiles", "ACIFabricType")
        )

    def test_leaf_switch_profile_type_includes_leaf_selector_reverse_list(self):
        """The Profile type exposes the leaf selector reverse list."""
        self.assertIsNotNone(
            schema.get_field_for_type("aci_leaf_selectors", "ACILeafSwitchProfileType")
        )

    def test_leaf_selector_type_includes_leaf_node_block_reverse_list(self):
        """The Leaf Selector type exposes the leaf node block reverse list."""
        self.assertIsNotNone(
            schema.get_field_for_type("aci_leaf_node_blocks", "ACILeafSelectorType")
        )

    def test_fabric_list_query_returns_leaf_switch_profile_reverse_chain(self):
        """The aci_fabric_list query resolves the three-level reverse chain."""
        self.add_permissions(
            "netbox_aci_plugin.view_acifabric",
            "netbox_aci_plugin.view_acileafswitchprofile",
            "netbox_aci_plugin.view_acileafselector",
            "netbox_aci_plugin.view_acileafnodeblock",
        )

        result = self.query(
            "query { aci_fabric_list(filters: {id: {in_list: ["
            f'"{self.aci_fabric1.pk}"'
            "]}}) { id "
            "aci_leaf_switch_profiles { id "
            "aci_leaf_selectors { id "
            "aci_leaf_node_blocks { id } } } } }"
        )

        self.assertNotIn("errors", result, result)
        fabric_row = result["data"]["aci_fabric_list"][0]
        profile_row = fabric_row["aci_leaf_switch_profiles"][0]
        self.assertEqual(profile_row["id"], str(self.aci_leaf_switch_profile1.pk))
        selector_row = profile_row["aci_leaf_selectors"][0]
        self.assertEqual(selector_row["id"], str(self.aci_leaf_selector1.pk))
        self.assertEqual(
            {row["id"] for row in selector_row["aci_leaf_node_blocks"]},
            {str(self.aci_leaf_node_block1.pk)},
        )
