# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the fabric ACI Pod model."""

from utilities.testing import ViewTestCases, create_tags

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
        ACIPod.objects.create(
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
