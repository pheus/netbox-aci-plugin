# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for the ACI Node Interface model."""

from dcim.choices import InterfaceTypeChoices
from dcim.models import Interface
from utilities.testing import ChangeLoggedFilterSetTests

from ....choices import NodeRoleChoices
from ....filtersets.fabric.node_interfaces import ACINodeInterfaceFilterSet
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.node_interfaces import ACINodeInterface
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ...models.base import ACIBaseTestCase


class ACINodeInterfaceFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACINodeInterfaceFilterSet."""

    queryset = ACINodeInterface.objects.all()
    filterset = ACINodeInterfaceFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACINodeInterfaceFilterSet tests."""
        super().setUpTestData()
        cls.nb_interface_1 = Interface.objects.create(
            device=cls.aci_node_object1,
            name="eth1/1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        cls.aci_node_interface_1 = ACINodeInterface.objects.create(
            aci_node=cls.aci_node,
            nb_interface=cls.nb_interface_1,
            module=1,
            port=1,
            description="ACIFSTestNodeInterface1",
        )
        # A second interface on the same ACI Node, so test_id has more than
        # two objects to filter
        cls.aci_node_interface_2 = ACINodeInterface.objects.create(
            aci_node=cls.aci_node,
            module=1,
            port=2,
            description="ACIFSTestNodeInterface2",
        )

        # A second ACI Fabric, Pod, and Leaf Node so the fabric and pod
        # scoping filters have something to exclude
        cls.other_fabric = ACIFabric.objects.create(
            name="ACIFSNodeInterfaceOtherFabric",
            fabric_id=cls.aci_fabric_id + 1,
            infra_vlan_vid=cls.aci_fabric_infra_vlan_vid + 1,
        )
        cls.other_pod = ACIPod.objects.create(
            name="ACIFSNodeInterfaceOtherPod",
            aci_fabric=cls.other_fabric,
            pod_id=1,
        )
        cls.other_node = ACINode.objects.create(
            name="ACIFSNodeInterfaceOtherNode",
            aci_pod=cls.other_pod,
            node_id=101,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.aci_node_interface_3 = ACINodeInterface.objects.create(
            aci_node=cls.other_node,
            module=1,
            port=1,
            description="ACIFSTestNodeInterface3",
        )
        # A fourth interface with a distinct module and sub port, so the
        # module and sub_port filters have something to discriminate on
        cls.aci_node_interface_4 = ACINodeInterface.objects.create(
            aci_node=cls.aci_node,
            module=2,
            port=2,
            sub_port=1,
            description="ACIFSTestNodeInterface4",
        )

    def test_q(self) -> None:
        """Test q search matches the description field."""
        params = {"q": "ACIFSTestNodeInterface1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_node_interface_1, qs)
        self.assertNotIn(self.aci_node_interface_3, qs)

    def test_q_aci_node_name(self) -> None:
        """Test q search matches the related ACI Node name."""
        params = {"q": self.aci_node_name}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_node_interface_1, qs)
        self.assertIn(self.aci_node_interface_2, qs)
        self.assertNotIn(self.aci_node_interface_3, qs)

    def test_q_nb_interface_name(self) -> None:
        """Test q search matches the related NetBox interface name."""
        params = {"q": "eth1/1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_node_interface_1, qs)
        self.assertNotIn(self.aci_node_interface_3, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())

    def test_aci_fabric(self) -> None:
        """Test filtering by the ACI Node's cached ACI Fabric name."""
        params = {"aci_fabric": [self.aci_fabric_name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_node_interface_1, qs)
        self.assertIn(self.aci_node_interface_2, qs)
        self.assertNotIn(self.aci_node_interface_3, qs)

    def test_aci_fabric_id(self) -> None:
        """Test filtering by the ACI Node's cached ACI Fabric ID."""
        params = {"aci_fabric_id": [self.aci_fabric.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_node_interface_1, qs)
        self.assertIn(self.aci_node_interface_2, qs)
        self.assertNotIn(self.aci_node_interface_3, qs)

    def test_aci_pod_id(self) -> None:
        """Test filtering by the ACI Node's ACI Pod ID."""
        params = {"aci_pod_id": [self.aci_pod.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_node_interface_1, qs)
        self.assertIn(self.aci_node_interface_2, qs)
        self.assertNotIn(self.aci_node_interface_3, qs)

    def test_aci_node_id(self) -> None:
        """Test filtering by the ACI Node ID."""
        params = {"aci_node_id": [self.aci_node.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_node_interface_1, qs)
        self.assertIn(self.aci_node_interface_2, qs)
        self.assertNotIn(self.aci_node_interface_3, qs)

    def test_nb_interface_id(self) -> None:
        """Test filtering by the NetBox interface ID."""
        params = {"nb_interface_id": [self.nb_interface_1.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_node_interface_1, qs)
        self.assertNotIn(self.aci_node_interface_2, qs)
        self.assertNotIn(self.aci_node_interface_3, qs)

    def test_module(self) -> None:
        """Test filtering by the module number."""
        params = {"module": [2]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_node_interface_4, qs)
        self.assertNotIn(self.aci_node_interface_1, qs)
        self.assertNotIn(self.aci_node_interface_2, qs)
        self.assertNotIn(self.aci_node_interface_3, qs)

    def test_port(self) -> None:
        """Test filtering by the port number."""
        params = {"port": [1]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_node_interface_1, qs)
        self.assertIn(self.aci_node_interface_3, qs)
        self.assertNotIn(self.aci_node_interface_2, qs)
        self.assertNotIn(self.aci_node_interface_4, qs)

    def test_sub_port(self) -> None:
        """Test filtering by the sub port number."""
        params = {"sub_port": [1]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_node_interface_4, qs)
        self.assertNotIn(self.aci_node_interface_1, qs)
        self.assertNotIn(self.aci_node_interface_2, qs)
        self.assertNotIn(self.aci_node_interface_3, qs)
