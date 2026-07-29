# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the fabric ACI Node Interface model."""

from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....choices import NodeRoleChoices
from ....models.fabric.node_interfaces import ACINodeInterface
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ....views.fabric.node_interfaces import ACINodeInterfaceChildrenView
from ..base import ACIModelViewTestCase


class ACINodeInterfaceViewTestCase(
    ACIModelViewTestCase,
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    """Standard view tests for ACINodeInterface.

    ``BulkRenameObjectsViewTestCase`` is intentionally excluded - the
    model has no ``name`` field.
    """

    model = ACINodeInterface

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACINodeInterface view tests."""
        super().setUpTestData()

        cls.aci_pod = ACIPod.objects.create(
            name="ACIViewTestNodeInterfacePod", aci_fabric=cls.aci_fabric, pod_id=1
        )

        site = Site.objects.create(
            name="ACIViewTestNodeInterfaceSite", slug="acivt-leaf-iface"
        )
        manufacturer = Manufacturer.objects.create(
            name="ACIViewTestNodeInterfaceMfr", slug="acivt-leaf-iface-mfr"
        )
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model="ACIViewTestNodeInterfaceDeviceType",
            slug="acivt-leaf-iface-dt",
        )
        device_role = DeviceRole.objects.create(
            name="ACIViewTestNodeInterfaceRole", slug="acivt-leaf-iface-role"
        )
        cls.device = Device.objects.create(
            name="ACIViewTestNodeInterfaceDevice",
            device_type=device_type,
            role=device_role,
            site=site,
        )

        cls.aci_node = ACINode.objects.create(
            name="ACIViewTestNodeInterfaceNode",
            aci_pod=cls.aci_pod,
            node_id=101,
            node_object=cls.device,
            role="leaf",
            node_type="unknown",
        )
        cls.aci_node_spine = ACINode.objects.create(
            name="ACIViewTestNodeInterfaceNodeSpine",
            aci_pod=cls.aci_pod,
            node_id=201,
            role=NodeRoleChoices.ROLE_SPINE,
            node_type="unknown",
        )
        cls.aci_node_apic = ACINode.objects.create(
            name="ACIViewTestNodeInterfaceNodeApic",
            aci_pod=cls.aci_pod,
            node_id=1,
            role=NodeRoleChoices.ROLE_APIC,
            node_type="unknown",
        )

        interfaces = [
            Interface.objects.create(
                device=cls.device,
                name=f"eth1/{i}",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            )
            for i in range(1, 5)
        ]

        ACINodeInterface.objects.create(
            aci_node=cls.aci_node, module=1, port=1, nb_interface=interfaces[0]
        )
        ACINodeInterface.objects.create(
            aci_node=cls.aci_node, module=1, port=2, nb_interface=interfaces[1]
        )
        ACINodeInterface.objects.create(
            aci_node=cls.aci_node, module=1, port=3, nb_interface=interfaces[2]
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "aci_node": cls.aci_node.pk,
            "nb_interface": interfaces[3].pk,
            "module": 1,
            "port": 4,
            "sub_port": 0,
            "description": "Form-data Node Interface",
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        pod = cls.aci_pod.name
        node = cls.aci_node.name
        cls.csv_data = (
            "aci_fabric,aci_pod,aci_node,module,port,sub_port,description",
            f"{fabric},{pod},{node},1,10,0,CSV Node Interface 1",
            f"{fabric},{pod},{node},1,11,0,CSV Node Interface 2",
            f"{fabric},{pod},{node},1,12,0,CSV Node Interface 3",
        )

        node_interfaces = list(ACINodeInterface.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{node_interfaces[0].pk},Updated Node Interface 1",
            f"{node_interfaces[1].pk},Updated Node Interface 2",
            f"{node_interfaces[2].pk},Updated Node Interface 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Node Interface"}

    def test_acinode_nodeinterfaces_tab(self) -> None:
        """Node Interfaces tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acinode",
            "netbox_aci_plugin.view_acinodeinterface",
            "netbox_aci_plugin.add_acinodeinterface",
        )
        url = get_action_url(
            self.aci_node,
            action="nodeinterfaces",
            kwargs={"pk": self.aci_node.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACINodeInterface, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={self.aci_fabric.pk}&amp;'
            f"aci_pod={self.aci_pod.pk}&amp;"
            f"aci_node={self.aci_node.pk}",
        )

    def test_node_interfaces_tab_visible_for_leaf_node(self) -> None:
        """Node Interfaces tab renders for a Leaf node."""
        self.assertIsNotNone(ACINodeInterfaceChildrenView.tab.render(self.aci_node))

    def test_node_interfaces_tab_hidden_for_spine_node(self) -> None:
        """Node Interfaces tab is hidden for a Spine node."""
        self.assertIsNone(ACINodeInterfaceChildrenView.tab.render(self.aci_node_spine))

    def test_node_interfaces_tab_hidden_for_apic_node(self) -> None:
        """Node Interfaces tab is hidden for an APIC node."""
        self.assertIsNone(ACINodeInterfaceChildrenView.tab.render(self.aci_node_apic))
