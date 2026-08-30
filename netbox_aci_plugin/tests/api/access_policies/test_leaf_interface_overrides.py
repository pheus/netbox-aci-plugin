# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""API tests for the access-policy Leaf Interface Override model."""

from tenancy.models import Tenant
from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....choices import LeafInterfacePolicyGroupTypeChoices
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ....models.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverride,
)
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.node_interfaces import ACINodeInterface
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod


class ACILeafInterfaceOverrideAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Leaf Interface Override.

    The override has no ``name``, so ``brief_fields`` carries only its
    Node Interface and Policy Group references plus description.
    """

    model = ACILeafInterfaceOverride
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_leaf_interface_policy_group",
        "aci_node_interface",
        "description",
        "display",
        "id",
        "url",
    ]
    user_permissions = (
        "netbox_aci_plugin.view_acifabric",
        "netbox_aci_plugin.view_acileafinterfacepolicygroup",
        "netbox_aci_plugin.view_acinode",
        "netbox_aci_plugin.view_acinodeinterface",
        "netbox_aci_plugin.view_acipod",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Leaf Interface Override for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_fabric = ACIFabric.objects.create(
            name="ACILeafInterfaceOverrideTestFabricAPI",
            fabric_id=118,
            infra_vlan_vid=3900,
        )

        # nb_tenant is set on every walked parent (Pod, Node, Node
        # Interface, Policy Group) so the API viewset's four nb_tenant
        # joins are genuinely exercised, not just present in
        # select_related()
        aci_pod = ACIPod.objects.create(
            name="ACILeafInterfaceOverrideTestPodAPI",
            aci_fabric=aci_fabric,
            pod_id=1,
            nb_tenant=nb_tenant1,
        )
        aci_node = ACINode.objects.create(
            name="ACILeafInterfaceOverrideTestNodeAPI",
            aci_pod=aci_pod,
            node_id=101,
            nb_tenant=nb_tenant2,
        )

        policy_group1 = ACILeafInterfacePolicyGroup.objects.create(
            name="ACILeafInterfaceOverrideTestPolicyGroupAPI1",
            aci_fabric=aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            nb_tenant=nb_tenant1,
        )
        policy_group2 = ACILeafInterfacePolicyGroup.objects.create(
            name="ACILeafInterfaceOverrideTestPolicyGroupAPI2",
            aci_fabric=aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            nb_tenant=nb_tenant2,
        )
        policy_group3 = ACILeafInterfacePolicyGroup.objects.create(
            name="ACILeafInterfaceOverrideTestPolicyGroupAPI3",
            aci_fabric=aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            nb_tenant=nb_tenant1,
        )
        policy_group4 = ACILeafInterfacePolicyGroup.objects.create(
            name="ACILeafInterfaceOverrideTestPolicyGroupAPI4",
            aci_fabric=aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        policy_group5 = ACILeafInterfacePolicyGroup.objects.create(
            name="ACILeafInterfaceOverrideTestPolicyGroupAPI5",
            aci_fabric=aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )

        node_interface1 = ACINodeInterface.objects.create(
            aci_node=aci_node, module=1, port=1, nb_tenant=nb_tenant1
        )
        node_interface2 = ACINodeInterface.objects.create(
            aci_node=aci_node, module=1, port=2, nb_tenant=nb_tenant2
        )
        node_interface3 = ACINodeInterface.objects.create(
            aci_node=aci_node, module=1, port=3, nb_tenant=nb_tenant1
        )
        node_interface4 = ACINodeInterface.objects.create(
            aci_node=aci_node, module=1, port=4
        )
        node_interface5 = ACINodeInterface.objects.create(
            aci_node=aci_node, module=1, port=5
        )

        overrides: tuple = (
            ACILeafInterfaceOverride(
                aci_node_interface=node_interface1,
                aci_leaf_interface_policy_group=policy_group1,
                description="First ACI Test",
                comments="# ACI Test 1",
            ),
            ACILeafInterfaceOverride(
                aci_node_interface=node_interface2,
                aci_leaf_interface_policy_group=policy_group2,
                description="Second ACI Test",
                comments="# ACI Test 2",
            ),
            ACILeafInterfaceOverride(
                aci_node_interface=node_interface3,
                aci_leaf_interface_policy_group=policy_group3,
                description="Third ACI Test",
                comments="# ACI Test 3",
            ),
        )
        ACILeafInterfaceOverride.objects.bulk_create(overrides)

        cls.create_data: list[dict] = [
            {
                "aci_node_interface": node_interface4.id,
                "aci_leaf_interface_policy_group": policy_group4.id,
                "description": "Fourth ACI Test",
                "comments": "# ACI Test 4",
            },
            {
                "aci_node_interface": node_interface5.id,
                "aci_leaf_interface_policy_group": policy_group5.id,
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }
        cls.bulk_update_invalid_data = {
            "description": "Invalid description: ö",
        }
