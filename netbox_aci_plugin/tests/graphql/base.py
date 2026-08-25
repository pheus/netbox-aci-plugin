# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.test import override_settings
from django.urls import reverse

from utilities.testing import APITestCase

from ...choices import LeafInterfacePolicyGroupTypeChoices, NodeRoleChoices
from ...models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ...models.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverride,
)
from ...models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
    ACILeafInterfaceSelector,
    ACILeafPortBlock,
)
from ...models.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlock,
    ACILeafSelector,
    ACILeafSwitchProfile,
    ACILeafSwitchProfileInterfaceBinding,
)
from ...models.fabric.fabrics import ACIFabric
from ...models.fabric.node_interfaces import ACINodeInterface
from ...models.fabric.nodes import ACINode
from ...models.fabric.pods import ACIPod
from ...models.fabric.vpc_protection_groups import ACIVPCProtectionGroup
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
        cls.aci_pod1 = ACIPod.objects.create(
            name="ACIGraphQLTestPod1", aci_fabric=cls.aci_fabric1, pod_id=1
        )
        cls.aci_node1 = ACINode.objects.create(
            name="ACIGraphQLTestNode1",
            aci_pod=cls.aci_pod1,
            node_id=101,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.aci_node2 = ACINode.objects.create(
            name="ACIGraphQLTestNode2",
            aci_pod=cls.aci_pod1,
            node_id=102,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.aci_leaf_interface_policy_group1 = (
            ACILeafInterfacePolicyGroup.objects.create(
                name="ACIGraphQLTestLeafInterfacePolicyGroup1",
                aci_fabric=cls.aci_fabric1,
                group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            )
        )
        cls.aci_vpc_protection_group1 = ACIVPCProtectionGroup.objects.create(
            name="ACIGraphQLTestVPCProtectionGroup1",
            aci_fabric=cls.aci_fabric1,
            logical_pair_id=1,
            aci_node_a=cls.aci_node1,
            aci_node_b=cls.aci_node2,
        )
        cls.aci_leaf_switch_profile1 = ACILeafSwitchProfile.objects.create(
            name="ACIGraphQLTestLeafSwitchProfile1", aci_fabric=cls.aci_fabric1
        )
        cls.aci_leaf_selector1 = ACILeafSelector.objects.create(
            name="ACIGraphQLTestLeafSelector1",
            aci_leaf_switch_profile=cls.aci_leaf_switch_profile1,
        )
        cls.aci_leaf_node_block1 = ACILeafNodeBlock.objects.create(
            name="ACIGraphQLTestLeafNodeBlock1",
            aci_leaf_selector=cls.aci_leaf_selector1,
            node_id_from=101,
            node_id_to=102,
        )
        cls.aci_leaf_interface_profile1 = ACILeafInterfaceProfile.objects.create(
            name="ACIGraphQLTestLeafInterfaceProfile1", aci_fabric=cls.aci_fabric1
        )
        cls.aci_leaf_interface_selector1 = ACILeafInterfaceSelector.objects.create(
            name="ACIGraphQLTestLeafInterfaceSelector1",
            aci_leaf_interface_profile=cls.aci_leaf_interface_profile1,
            aci_leaf_interface_policy_group=cls.aci_leaf_interface_policy_group1,
        )
        cls.aci_leaf_port_block1 = ACILeafPortBlock.objects.create(
            name="ACIGraphQLTestLeafPortBlock1",
            aci_leaf_interface_selector=cls.aci_leaf_interface_selector1,
            module_from=1,
            module_to=1,
            port_from=1,
            port_to=1,
        )
        cls.aci_leaf_switch_profile_interface_binding1 = (
            ACILeafSwitchProfileInterfaceBinding.objects.create(
                aci_leaf_switch_profile=cls.aci_leaf_switch_profile1,
                aci_leaf_interface_profile=cls.aci_leaf_interface_profile1,
            )
        )
        cls.aci_node_interface1 = ACINodeInterface.objects.create(
            aci_node=cls.aci_node1, module=1, port=1
        )
        cls.aci_leaf_interface_override1 = ACILeafInterfaceOverride.objects.create(
            aci_node_interface=cls.aci_node_interface1,
            aci_leaf_interface_policy_group=cls.aci_leaf_interface_policy_group1,
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
