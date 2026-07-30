# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the fabric ACI VPC Protection Group model."""

from utilities.testing import ViewTestCases, create_tags

from ....choices import NodeRoleChoices
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ....models.fabric.vpc_protection_groups import ACIVPCProtectionGroup
from ..base import ACIModelViewTestCase


class ACIVPCProtectionGroupViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIVPCProtectionGroup."""

    model = ACIVPCProtectionGroup

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIVPCProtectionGroup view tests."""
        super().setUpTestData()

        cls.aci_pod = ACIPod.objects.create(
            name="ACIViewTestVPCPod", aci_fabric=cls.aci_fabric, pod_id=1
        )

        # 14 Leaf Nodes: 3 pairs for the fixtures below, 1 pair for
        # form_data, 3 pairs for csv_data.
        nodes = [
            ACINode.objects.create(
                name=f"ACIViewTestVPCNode{i}",
                aci_pod=cls.aci_pod,
                node_id=100 + i,
                role=NodeRoleChoices.ROLE_LEAF,
            )
            for i in range(1, 15)
        ]

        ACIVPCProtectionGroup.objects.create(
            name="ACIViewTestVPC1",
            aci_fabric=cls.aci_fabric,
            logical_pair_id=1,
            aci_node_a=nodes[0],
            aci_node_b=nodes[1],
        )
        ACIVPCProtectionGroup.objects.create(
            name="ACIViewTestVPC2",
            aci_fabric=cls.aci_fabric,
            logical_pair_id=2,
            aci_node_a=nodes[2],
            aci_node_b=nodes[3],
        )
        ACIVPCProtectionGroup.objects.create(
            name="ACIViewTestVPC3",
            aci_fabric=cls.aci_fabric,
            logical_pair_id=3,
            aci_node_a=nodes[4],
            aci_node_b=nodes[5],
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestVPCX",
            "name_alias": "VPCXAlias",
            "description": "Form-data VPC Protection Group",
            "aci_fabric": cls.aci_fabric.pk,
            "logical_pair_id": 100,
            "aci_node_a": nodes[6].pk,
            "aci_node_b": nodes[7].pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        cls.csv_data = (
            "name,aci_fabric,logical_pair_id,aci_node_a,aci_node_b,description",
            (
                f"ACIViewTestVPC4,{fabric},4,{nodes[8].node_id},{nodes[9].node_id},"
                "CSV VPC 4"
            ),
            (
                f"ACIViewTestVPC5,{fabric},5,{nodes[10].node_id},{nodes[11].node_id},"
                "CSV VPC 5"
            ),
            (
                f"ACIViewTestVPC6,{fabric},6,{nodes[12].node_id},{nodes[13].node_id},"
                "CSV VPC 6"
            ),
        )

        vpc_groups = list(ACIVPCProtectionGroup.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{vpc_groups[0].pk},Updated VPC Protection Group 1",
            f"{vpc_groups[1].pk},Updated VPC Protection Group 2",
            f"{vpc_groups[2].pk},Updated VPC Protection Group 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited VPC Protection Group"}
