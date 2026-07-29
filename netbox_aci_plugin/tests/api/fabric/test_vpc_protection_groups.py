# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""API tests for fabric VPC Protection Group models."""

from tenancy.models import Tenant
from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....choices import NodeRoleChoices
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ....models.fabric.vpc_protection_groups import ACIVPCProtectionGroup


class ACIVPCProtectionGroupAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI VPC Protection Group."""

    model = ACIVPCProtectionGroup
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_fabric",
        "aci_node_a",
        "aci_node_b",
        "description",
        "display",
        "id",
        "logical_pair_id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]
    user_permissions = (
        "netbox_aci_plugin.view_acifabric",
        "netbox_aci_plugin.view_acinode",
        "netbox_aci_plugin.view_acipod",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI VPC Protection Group for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_fabric = ACIFabric.objects.create(
            name="ACITestFabricAPI", fabric_id=114, infra_vlan_vid=3900
        )
        aci_pod = ACIPod.objects.create(
            name="ACIPodTestAPI", aci_fabric=aci_fabric, pod_id=1
        )

        # 10 Leaf Nodes: 3 pairs for the fixtures below, 2 pairs for
        # create_data. ACI Nodes derive a cached ACI Fabric on save(),
        # matching the ACINode API test fixture convention.
        aci_nodes: tuple = tuple(
            ACINode(
                name=f"ACIVPCProtectionGroupTestAPINode{i}",
                aci_pod=aci_pod,
                node_id=100 + i,
                role=NodeRoleChoices.ROLE_LEAF,
            )
            for i in range(1, 11)
        )
        for aci_node in aci_nodes:
            aci_node.full_clean()
            aci_node.save()

        vpc_groups: tuple = (
            ACIVPCProtectionGroup(
                name="ACIVPCProtectionGroupTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                aci_fabric=aci_fabric,
                logical_pair_id=1,
                aci_node_a=aci_nodes[0],
                aci_node_b=aci_nodes[1],
                nb_tenant=nb_tenant1,
                comments="# ACI Test 1",
            ),
            ACIVPCProtectionGroup(
                name="ACIVPCProtectionGroupTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                aci_fabric=aci_fabric,
                logical_pair_id=2,
                aci_node_a=aci_nodes[2],
                aci_node_b=aci_nodes[3],
                nb_tenant=nb_tenant2,
                comments="# ACI Test 2",
            ),
            ACIVPCProtectionGroup(
                name="ACIVPCProtectionGroupTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                aci_fabric=aci_fabric,
                logical_pair_id=3,
                aci_node_a=aci_nodes[4],
                aci_node_b=aci_nodes[5],
                nb_tenant=nb_tenant2,
                comments="# ACI Test 3",
            ),
        )
        ACIVPCProtectionGroup.objects.bulk_create(vpc_groups)

        cls.create_data: list[dict] = [
            {
                "name": "ACIVPCProtectionGroupTestAPI4",
                "name_alias": "Testing",
                "description": "Fourth ACI Test",
                "aci_fabric": aci_fabric.id,
                "logical_pair_id": 4,
                "aci_node_a": aci_nodes[6].id,
                "aci_node_b": aci_nodes[7].id,
                "nb_tenant": nb_tenant1.id,
                "comments": "# ACI Test 4",
            },
            {
                "name": "ACIVPCProtectionGroupTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "aci_fabric": aci_fabric.id,
                "logical_pair_id": 5,
                "aci_node_a": aci_nodes[8].id,
                "aci_node_b": aci_nodes[9].id,
                "nb_tenant": nb_tenant2.id,
                "comments": "# ACI Test 5",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }
