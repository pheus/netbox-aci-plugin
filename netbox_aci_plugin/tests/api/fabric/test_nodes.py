# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""API tests for fabric Node models."""

from rest_framework import status

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from ipam.models import IPAddress, Prefix
from tenancy.models import Tenant
from utilities.testing import APIViewTestCases, GraphQLQueryTest

from ....api.urls import app_name
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ....models.fabric.vpc_protection_groups import ACIVPCProtectionGroup


class ACINodeAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Node."""

    model = ACINode
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_pod",
        "description",
        "display",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "node_id",
        "url",
    ]
    user_permissions = (
        "ipam.view_prefix",
        "ipam.view_vlan",
        "netbox_aci_plugin.view_acifabric",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Node for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        cls.site1 = Site.objects.create(
            name="ACINodeTestAPISite1", slug="acinodetestapisite1"
        )
        cls.site2 = Site.objects.create(
            name="ACINodeTestAPISite2", slug="acinodetestapisite2"
        )
        cls.manufacturer = Manufacturer.objects.create(
            name="ACINodeTestAPIManufacturer", slug="acinodetestapimanufacturer"
        )
        cls.device_type1 = DeviceType.objects.create(
            manufacturer=cls.manufacturer,
            model="ACINodeTestAPIDeviceType1",
            slug="acinodetestapidevicetype1",
        )
        cls.device_role1 = DeviceRole.objects.create(
            name="ACINodeTestAPIDeviceRole1", slug="acinodetestapidevicerole1"
        )

        # Related ACI Pod objects
        tep_pool_pod1 = Prefix(prefix="10.1.0.0/19")
        tep_pool_pod1.full_clean()
        tep_pool_pod1.save()
        tep_pool_pod2 = Prefix(prefix="10.2.0.0/19")
        tep_pool_pod2.full_clean()
        tep_pool_pod2.save()

        # Related ACI Node objects
        tep_ip_pod1_node1 = IPAddress(address="10.1.0.1/19")
        tep_ip_pod1_node1.full_clean()
        tep_ip_pod1_node1.save()
        tep_ip_pod1_node2 = IPAddress(address="10.1.0.2/19")
        tep_ip_pod1_node2.full_clean()
        tep_ip_pod1_node2.save()
        tep_ip_pod1_node3 = IPAddress(address="10.1.0.3/19")
        tep_ip_pod1_node3.full_clean()
        tep_ip_pod1_node3.save()

        tep_ip_pod2_node1 = IPAddress(address="10.2.0.1/19")
        tep_ip_pod2_node1.full_clean()
        tep_ip_pod2_node1.save()
        tep_ip_pod2_node2 = IPAddress(address="10.2.0.2/19")
        tep_ip_pod2_node2.full_clean()
        tep_ip_pod2_node2.save()

        pod1_node1 = Device.objects.create(
            name="ACINodeTestAPIPod1Node1",
            device_type=cls.device_type1,
            role=cls.device_role1,
            site=cls.site1,
        )
        pod1_node2 = Device.objects.create(
            name="ACINodeTestAPIPod1Node2",
            device_type=cls.device_type1,
            role=cls.device_role1,
            site=cls.site1,
        )
        pod1_node3 = Device.objects.create(
            name="ACINodeTestAPIPod1Node3",
            device_type=cls.device_type1,
            role=cls.device_role1,
            site=cls.site1,
        )
        pod2_node1 = Device.objects.create(
            name="ACINodeTestAPIPod2Node1",
            device_type=cls.device_type1,
            role=cls.device_role1,
            site=cls.site2,
        )
        pod2_node2 = Device.objects.create(
            name="ACINodeTestAPIPod2Node2",
            device_type=cls.device_type1,
            role=cls.device_role1,
            site=cls.site2,
        )

        aci_fabric = ACIFabric.objects.create(
            name="ACITestFabricAPI1",
            fabric_id=111,
            infra_vlan_vid=3900,
        )

        aci_pod1 = ACIPod.objects.create(
            name="ACIPodTestAPI1",
            aci_fabric=aci_fabric,
            pod_id="1",
            tep_pool=tep_pool_pod1,
            scope=cls.site1,
        )
        aci_pod2 = ACIPod.objects.create(
            name="ACIPodTestAPI2",
            aci_fabric=aci_fabric,
            pod_id="2",
            tep_pool=tep_pool_pod2,
            scope=cls.site2,
        )

        aci_nodes: tuple = (
            ACINode(
                name="ACINodeTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                aci_pod=aci_pod1,
                node_id="101",
                node_object=pod1_node1,
                role="leaf",
                node_type="unknown",
                tep_ip_address=tep_ip_pod1_node1,
                nb_tenant=nb_tenant1,
                comments="# ACI Test 1",
            ),
            ACINode(
                name="ACINodeTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                aci_pod=aci_pod1,
                node_id="102",
                node_object=pod1_node2,
                node_type="unknown",
                tep_ip_address=tep_ip_pod1_node2,
                nb_tenant=nb_tenant2,
                comments="# ACI Test 2",
            ),
            ACINode(
                name="ACINodeTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                aci_pod=aci_pod2,
                node_id="201",
                node_object=pod2_node1,
                role="leaf",
                tep_ip_address=tep_ip_pod2_node1,
                nb_tenant=nb_tenant2,
                comments="# ACI Test 3",
            ),
        )
        # ACI nodes derive a cached ACI Fabric during validation
        # (ACINode.clean()/save()), so this fixture cannot use
        # bulk_create() like its sibling API test classes.
        for aci_node in aci_nodes:
            aci_node.full_clean()
            aci_node.save()

        # A union, which the generated query cannot express
        cls.graphql_query_tests = (
            GraphQLQueryTest(
                name="node_object_union",
                query=(
                    "{ aci_node_list { node_object { ... on DeviceType { name } } } }"
                ),
                assert_result=cls.assert_node_object_resolves,
            ),
        )

        cls.create_data: list[dict] = [
            {
                "name": "ACINodeTestAPI4",
                "name_alias": "Testing",
                "description": "Forth ACI Test",
                "aci_pod": aci_pod1.id,
                "node_id": 103,
                "node_object_type": "dcim.device",
                "node_object_id": pod1_node3.id,
                "role": "spine",
                "node_type": "unknown",
                "tep_ip_address": tep_ip_pod1_node3.id,
                "nb_tenant": nb_tenant1.id,
                "comments": "# ACI Test 4",
            },
            {
                "name": "ACINodeTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "aci_pod": aci_pod2.id,
                "node_id": 202,
                "node_object_type": "dcim.device",
                "node_object_id": pod2_node2.id,
                "role": "leaf",
                "node_type": "unknown",
                "tep_ip_address": tep_ip_pod2_node2.id,
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

    def test_create_duplicate_node_id_returns_400(self) -> None:
        """POSTing a Node ID already used in the ACI Fabric returns 400.

        Node IDs are unique per ACI Fabric, not per ACI Pod, so a
        duplicate in a different Pod of the same Fabric must still be
        rejected.
        """
        self.add_permissions("netbox_aci_plugin.add_acinode")
        aci_pod2 = ACIPod.objects.get(name="ACIPodTestAPI2")
        data = {
            "name": "ACINodeTestAPI6",
            "aci_pod": aci_pod2.id,
            "node_id": 101,
            "role": "leaf",
            "node_type": "unknown",
        }
        response = self.client.post(
            self._get_list_url(), data, format="json", **self.header
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("node_id", response.data)

    def test_update_vpc_paired_node_pod_returns_400(self) -> None:
        """PATCHing a VPC-paired Node's ACI Pod returns 400.

        A Node that belongs to a VPC Protection Group must keep its
        ACI Pod. Removing the Protection Group is required first.
        """
        self.add_permissions("netbox_aci_plugin.change_acinode")
        aci_pod1 = ACIPod.objects.get(name="ACIPodTestAPI1")
        aci_pod2 = ACIPod.objects.get(name="ACIPodTestAPI2")
        node_a = ACINode(
            name="ACINodeTestAPIVPCNodeA", aci_pod=aci_pod1, node_id=110, role="leaf"
        )
        node_a.full_clean()
        node_a.save()
        node_b = ACINode(
            name="ACINodeTestAPIVPCNodeB", aci_pod=aci_pod1, node_id=111, role="leaf"
        )
        node_b.full_clean()
        node_b.save()
        ACIVPCProtectionGroup.objects.create(
            name="ACINodeTestAPIVPCGroup",
            aci_fabric=aci_pod1.aci_fabric,
            logical_pair_id=999,
            aci_node_a=node_a,
            aci_node_b=node_b,
        )

        url = self._get_detail_url(node_a)
        response = self.client.patch(
            url, {"aci_pod": aci_pod2.id}, format="json", **self.header
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("aci_pod", response.data)

    def assert_node_object_resolves(self, data) -> None:
        """The node object union resolves to the linked NetBox devices."""
        resolved = {
            row["node_object"]["name"]
            for row in data["aci_node_list"]
            if row["node_object"]
        }
        expected = {
            node.node_object.name
            for node in ACINode.objects.all()
            if node.node_object is not None
        }
        self.assertTrue(expected)
        self.assertEqual(resolved, expected)
