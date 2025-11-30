# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from ipam.models import IPAddress, Prefix
from tenancy.models import Tenant
from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod


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
        ACINode.objects.bulk_create(aci_nodes)

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
