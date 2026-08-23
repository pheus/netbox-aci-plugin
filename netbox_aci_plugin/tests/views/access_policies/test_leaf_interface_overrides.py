# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the access policies ACI Leaf Interface Override model."""

from utilities.testing import ViewTestCases, create_tags

from ....choices import LeafInterfacePolicyGroupTypeChoices, NodeRoleChoices
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ....models.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverride,
)
from ....models.fabric.node_interfaces import ACINodeInterface
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ..base import ACIModelViewTestCase


class ACILeafInterfaceOverrideViewTestCase(
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
    """Standard view tests for ACILeafInterfaceOverride.

    ``BulkRenameObjectsViewTestCase`` is intentionally excluded - the
    model has no ``name`` field.
    """

    model = ACILeafInterfaceOverride

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafInterfaceOverride view tests."""
        super().setUpTestData()

        cls.aci_pod = ACIPod.objects.create(
            name="ACIViewTestOverridePod", aci_fabric=cls.aci_fabric, pod_id=1
        )
        cls.aci_node = ACINode.objects.create(
            name="ACIViewTestOverrideNode",
            aci_pod=cls.aci_pod,
            node_id=101,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.aci_leaf_interface_policy_group = (
            ACILeafInterfacePolicyGroup.objects.create(
                name="ACIViewTestOverridePolicyGroup",
                aci_fabric=cls.aci_fabric,
                group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            )
        )

        # 6 Node Interfaces: 3 already overridden, 3 free for create/CSV.
        cls.node_interfaces = [
            ACINodeInterface.objects.create(aci_node=cls.aci_node, module=1, port=i)
            for i in range(1, 7)
        ]

        # 3 existing Override instances for GET / edit / delete / list / bulk
        ACILeafInterfaceOverride.objects.create(
            aci_node_interface=cls.node_interfaces[0],
            aci_leaf_interface_policy_group=cls.aci_leaf_interface_policy_group,
        )
        ACILeafInterfaceOverride.objects.create(
            aci_node_interface=cls.node_interfaces[1],
            aci_leaf_interface_policy_group=cls.aci_leaf_interface_policy_group,
        )
        ACILeafInterfaceOverride.objects.create(
            aci_node_interface=cls.node_interfaces[2],
            aci_leaf_interface_policy_group=cls.aci_leaf_interface_policy_group,
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        # Node Interface 4 has no Override, so create and edit stay unique
        cls.form_data = {
            "aci_node_interface": cls.node_interfaces[3].pk,
            "aci_leaf_interface_policy_group": cls.aci_leaf_interface_policy_group.pk,
            "description": "Form-data Override",
            "tags": [t.pk for t in tags],
        }

        # Rows key on the APIC coordinates, the import form's natural key
        fabric = cls.aci_fabric.name
        pod = cls.aci_pod.name
        node = cls.aci_node.name
        policy_group = cls.aci_leaf_interface_policy_group.name
        cls.csv_data = (
            "aci_fabric,aci_pod,aci_node,module,port,aci_leaf_interface_policy_group",
            f"{fabric},{pod},{node},1,4,{policy_group}",
            f"{fabric},{pod},{node},1,5,{policy_group}",
            f"{fabric},{pod},{node},1,6,{policy_group}",
        )

        overrides = list(ACILeafInterfaceOverride.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{overrides[0].pk},Updated Override 1",
            f"{overrides[1].pk},Updated Override 2",
            f"{overrides[2].pk},Updated Override 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Override"}
