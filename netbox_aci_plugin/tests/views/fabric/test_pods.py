# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the fabric ACI Pod model."""

from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ..base import ACIModelViewTestCase


class ACIPodViewTestCase(ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase):
    """Standard view tests for ACIPod."""

    model = ACIPod

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIPod view tests."""
        super().setUpTestData()

        # 3 ACIPod instances under the shared base fabric.
        cls.aci_pod = ACIPod.objects.create(
            name="ACIViewTestPod1", aci_fabric=cls.aci_fabric, pod_id=1
        )
        ACIPod.objects.create(
            name="ACIViewTestPod2", aci_fabric=cls.aci_fabric, pod_id=2
        )
        ACIPod.objects.create(
            name="ACIViewTestPod3", aci_fabric=cls.aci_fabric, pod_id=3
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestPodX",
            "name_alias": "PodXAlias",
            "description": "Form-data Pod",
            "aci_fabric": cls.aci_fabric.pk,
            "pod_id": 4,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        cls.csv_data = (
            "name,aci_fabric,pod_id,description",
            f"ACIViewTestPod4,{fabric},5,CSV Pod 4",
            f"ACIViewTestPod5,{fabric},6,CSV Pod 5",
            f"ACIViewTestPod6,{fabric},7,CSV Pod 6",
        )

        pods = list(ACIPod.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{pods[0].pk},Updated Pod 1",
            f"{pods[1].pk},Updated Pod 2",
            f"{pods[2].pk},Updated Pod 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Pod"}

    def test_acipod_nodes_tab_add_button(self) -> None:
        """Pod Nodes tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acipod",
            "netbox_aci_plugin.view_acinode",
            "netbox_aci_plugin.add_acinode",
        )
        url = get_action_url(
            self.aci_pod, action="nodes", kwargs={"pk": self.aci_pod.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACINode, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={self.aci_fabric.pk}&amp;'
            f"aci_pod={self.aci_pod.pk}",
        )
