# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""API tests for fabric Node Interface models."""

from rest_framework import status

from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from tenancy.models import Tenant
from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.node_interfaces import ACINodeInterface
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod


class ACINodeInterfaceAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Node Interface."""

    model = ACINodeInterface
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_node",
        "display",
        "id",
        "interface_token",
        "module",
        "nb_tenant",
        "port",
        "sub_port",
        "url",
    ]
    user_permissions = (
        "dcim.view_device",
        "dcim.view_interface",
        "netbox_aci_plugin.view_acifabric",
        "netbox_aci_plugin.view_acinode",
        "netbox_aci_plugin.view_acipod",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Node Interface for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        site = Site.objects.create(
            name="ACINodeInterfaceTestAPISite", slug="acinodeinterfacetestapisite"
        )
        manufacturer = Manufacturer.objects.create(
            name="ACINodeInterfaceTestAPIManufacturer",
            slug="acinodeinterfacetestapimanufacturer",
        )
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model="ACINodeInterfaceTestAPIDeviceType",
            slug="acinodeinterfacetestapidevicetype",
        )
        device_role = DeviceRole.objects.create(
            name="ACINodeInterfaceTestAPIDeviceRole",
            slug="acinodeinterfacetestapidevicerole",
        )
        device = Device.objects.create(
            name="ACINodeInterfaceTestAPIDevice",
            device_type=device_type,
            role=device_role,
            site=site,
        )
        interface1 = Interface.objects.create(
            device=device, name="eth1/1", type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        interface2 = Interface.objects.create(
            device=device, name="eth1/2", type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )

        aci_fabric = ACIFabric.objects.create(
            name="ACITestFabricAPI", fabric_id=113, infra_vlan_vid=3900
        )
        aci_pod = ACIPod.objects.create(
            name="ACIPodTestAPI", aci_fabric=aci_fabric, pod_id=1
        )
        aci_node = ACINode(
            name="ACINodeTestAPI",
            aci_pod=aci_pod,
            node_id=101,
            node_object=device,
            role="leaf",
            node_type="unknown",
        )
        # ACI Nodes derive a cached ACI Fabric on save(), matching the
        # ACINode API test fixture convention (no bulk_create())
        aci_node.full_clean()
        aci_node.save()
        cls.aci_node = aci_node

        node_interfaces: tuple = (
            ACINodeInterface(
                aci_node=aci_node,
                module=1,
                port=1,
                nb_interface=interface1,
                description="First ACI Test",
                nb_tenant=nb_tenant1,
                comments="# ACI Test 1",
            ),
            ACINodeInterface(
                aci_node=aci_node,
                module=1,
                port=2,
                description="Second ACI Test",
                nb_tenant=nb_tenant2,
                comments="# ACI Test 2",
            ),
            ACINodeInterface(
                aci_node=aci_node,
                module=1,
                port=3,
                sub_port=1,
                description="Third ACI Test",
                nb_tenant=nb_tenant2,
                comments="# ACI Test 3",
            ),
        )
        ACINodeInterface.objects.bulk_create(node_interfaces)

        cls.create_data: list[dict] = [
            {
                "aci_node": aci_node.id,
                "module": 1,
                "port": 4,
                "nb_interface": interface2.id,
                "description": "Fourth ACI Test",
                "nb_tenant": nb_tenant1.id,
                "comments": "# ACI Test 4",
            },
            {
                "aci_node": aci_node.id,
                "module": 2,
                "port": 1,
                "sub_port": 2,
                "description": "Fifth ACI Test",
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

    def test_interface_token_ignores_create_input(self) -> None:
        """POST cannot set interface_token, it derives from coordinates."""
        self.add_permissions("netbox_aci_plugin.add_acinodeinterface")
        data = {
            "aci_node": self.aci_node.id,
            "module": 1,
            "port": 17,
            "interface_token": "eth9/99",
        }
        response = self.client.post(
            self._get_list_url(), data, format="json", **self.header
        )
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data["interface_token"], "eth1/17")

    def test_interface_token_ignores_update_input(self) -> None:
        """PATCH cannot override interface_token, it stays derived."""
        self.add_permissions("netbox_aci_plugin.change_acinodeinterface")
        instance = ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=1, port=17
        )
        url = self._get_detail_url(instance)
        response = self.client.patch(
            url, {"interface_token": "eth9/99"}, format="json", **self.header
        )
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data["interface_token"], "eth1/17")
        instance.refresh_from_db()
        self.assertEqual(instance.interface_token, "eth1/17")
