# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the fabric ACI Node model."""

from django.contrib.contenttypes.models import ContentType

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from utilities.testing import ViewTestCases, create_tags

from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ..base import ACIModelViewTestCase


class ACINodeViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACINode."""

    model = ACINode

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACINode view tests."""
        super().setUpTestData()

        cls.aci_pod = ACIPod.objects.create(
            name="ACIViewTestNodePod", aci_fabric=cls.aci_fabric, pod_id=1
        )

        # NetBox dcim chain - each ACI Node references a Device via its GFK.
        site = Site.objects.create(name="ACIViewTestNodeSite", slug="acivt-node")
        manufacturer = Manufacturer.objects.create(
            name="ACIViewTestNodeMfr", slug="acivt-node-mfr"
        )
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model="ACIViewTestNodeDeviceType",
            slug="acivt-node-dt",
        )
        device_role = DeviceRole.objects.create(
            name="ACIViewTestNodeRole", slug="acivt-node-role"
        )
        devices = [
            Device.objects.create(
                name=f"ACIViewTestNodeDevice{i}",
                device_type=device_type,
                role=device_role,
                site=site,
            )
            for i in range(1, 8)
        ]
        cls.device_ct = ContentType.objects.get_for_model(Device)

        ACINode.objects.create(
            name="ACIViewTestNode1",
            aci_pod=cls.aci_pod,
            node_id=101,
            node_object=devices[0],
            role="leaf",
            node_type="unknown",
        )
        ACINode.objects.create(
            name="ACIViewTestNode2",
            aci_pod=cls.aci_pod,
            node_id=102,
            node_object=devices[1],
            role="spine",
            node_type="unknown",
        )
        ACINode.objects.create(
            name="ACIViewTestNode3",
            aci_pod=cls.aci_pod,
            node_id=103,
            node_object=devices[2],
            role="leaf",
            node_type="unknown",
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestNodeX",
            "name_alias": "NodeXAlias",
            "description": "Form-data Node",
            "aci_pod": cls.aci_pod.pk,
            "node_id": 104,
            "node_object_type": cls.device_ct.pk,
            "node_object": devices[3].pk,
            "role": "leaf",
            "node_type": "unknown",
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        pod = cls.aci_pod.name
        cls.csv_data = (
            (
                "name,aci_fabric,aci_pod,node_id,node_object_type,"
                "node_object_id,role,node_type"
            ),
            (
                f"ACIViewTestNode4,{fabric},{pod},105,dcim.device,"
                f"{devices[4].pk},leaf,unknown"
            ),
            (
                f"ACIViewTestNode5,{fabric},{pod},106,dcim.device,"
                f"{devices[5].pk},spine,unknown"
            ),
            (
                f"ACIViewTestNode6,{fabric},{pod},107,dcim.device,"
                f"{devices[6].pk},leaf,unknown"
            ),
        )

        nodes = list(ACINode.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{nodes[0].pk},Updated Node 1",
            f"{nodes[1].pk},Updated Node 2",
            f"{nodes[2].pk},Updated Node 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Node"}
