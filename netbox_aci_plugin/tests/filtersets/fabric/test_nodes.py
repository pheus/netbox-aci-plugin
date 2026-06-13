# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for the ACI Node model."""

from dcim.models import Device
from ipam.models import IPAddress
from utilities.testing import ChangeLoggedFilterSetTests

from ....choices import NodeRoleChoices
from ....filtersets.fabric.nodes import ACINodeFilterSet
from ....models.fabric.nodes import ACINode
from ...models.base import ACIBaseTestCase


class ACINodeFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACINodeFilterSet."""

    queryset = ACINode.objects.all()
    filterset = ACINodeFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACINodeFilterSet tests."""
        super().setUpTestData()
        cls.node_device_2 = Device.objects.create(
            name="ACIFSNodeDevice2",
            device_type=cls.device_type1,
            role=cls.device_role1,
            site=cls.site,
        )
        cls.node_device_3 = Device.objects.create(
            name="ACIFSNodeDevice3",
            device_type=cls.device_type1,
            role=cls.device_role1,
            site=cls.site,
        )
        cls.node_tep_ip_2 = IPAddress.objects.create(address="10.0.0.2/19")
        cls.node_tep_ip_3 = IPAddress.objects.create(address="10.0.0.3/19")
        cls.aci_node_2 = ACINode.objects.create(
            name="ACIFSTestNode2",
            aci_pod=cls.aci_pod,
            node_id=102,
            node_object=cls.node_device_2,
            role=NodeRoleChoices.ROLE_LEAF,
            tep_ip_address=cls.node_tep_ip_2,
        )
        cls.aci_node_3 = ACINode.objects.create(
            name="ACIFSTestNode3",
            aci_pod=cls.aci_pod,
            node_id=103,
            node_object=cls.node_device_3,
            role=NodeRoleChoices.ROLE_LEAF,
            tep_ip_address=cls.node_tep_ip_3,
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestNode2"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_node_2, qs)
        self.assertNotIn(self.aci_node_3, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())
