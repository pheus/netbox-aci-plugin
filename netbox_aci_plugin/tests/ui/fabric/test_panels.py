# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for the fabric domain's declarative UI panels.

Complements tests/views/fabric/, which pins the Override triad and the
vPC peer block through full HTTP round trips. These tests assert on
the declared structure (accessor, label, attr type) and on
get_value()'s resolved data, never on rendered markup: both the
always-shown Scope row (the accepted rendering delta) and the
sub_port zero sentinel are otherwise exercised only once, by whatever
fixture state the inherited detail-page test happens to carry.
"""

from __future__ import annotations

from dcim.models import Location, Region, Site
from netbox.ui import attrs

from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.node_interfaces import ACINodeInterface
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ....ui.panels.fabric.fabrics import ACIFabricPanel
from ....ui.panels.fabric.node_interfaces import ACINodeInterfacePanel
from ....ui.panels.fabric.nodes import ACINodeInfrastructurePanel
from ....ui.panels.fabric.pods import ACIPodPanel
from ..base import ACIBaseUITestCase


class FabricPanelScopeTestCase(ACIBaseUITestCase):
    """Unit tests for ACIFabricPanel's always-shown Scope row."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIFabricPanel tests."""
        cls.region = Region.objects.create(name="ACIUIFabricPanelRegion")
        cls.aci_fabric_scoped = ACIFabric.objects.create(
            name="ACIUIFabricPanelScopedFabric",
            fabric_id=1,
            infra_vlan_vid=100,
            scope=cls.region,
        )
        cls.aci_fabric_bare = ACIFabric.objects.create(
            name="ACIUIFabricPanelBareFabric", fabric_id=2, infra_vlan_vid=101
        )

    def test_scope_attr_is_a_linkified_gfk(self) -> None:
        """scope is a linkified GenericForeignKeyAttr on the scope field."""
        attr = ACIFabricPanel._attrs["scope"]
        self.assertIsInstance(attr, attrs.GenericForeignKeyAttr)
        self.assertEqual(attr.accessor, "scope")
        self.assertTrue(attr.linkify)

    def test_scope_get_value_is_none_when_unset(self) -> None:
        """The Scope row's value resolves to None when unset."""
        attr = ACIFabricPanel._attrs["scope"]
        self.assertIsNone(attr.get_value(self.aci_fabric_bare))

    def test_scope_get_value_resolves_the_scoped_object(self) -> None:
        """The Scope row's value resolves to the assigned scope object."""
        attr = ACIFabricPanel._attrs["scope"]
        self.assertEqual(attr.get_value(self.aci_fabric_scoped), self.region)


class PodPanelScopeTestCase(ACIBaseUITestCase):
    """Unit tests for ACIPodPanel's always-shown Scope row."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIPodPanel tests."""
        cls.aci_fabric = ACIFabric.objects.create(
            name="ACIUIPodPanelFabric", fabric_id=1, infra_vlan_vid=100
        )
        site = Site.objects.create(name="ACIUIPodPanelSite", slug="aci-ui-pod-site")
        cls.location = Location.objects.create(
            name="ACIUIPodPanelLocation", slug="aci-ui-pod-location", site=site
        )
        cls.aci_pod_scoped = ACIPod.objects.create(
            name="ACIUIPodPanelScopedPod",
            aci_fabric=cls.aci_fabric,
            pod_id=1,
            scope=cls.location,
        )
        cls.aci_pod_bare = ACIPod.objects.create(
            name="ACIUIPodPanelBarePod", aci_fabric=cls.aci_fabric, pod_id=2
        )

    def test_scope_attr_is_a_linkified_gfk(self) -> None:
        """scope is a linkified GenericForeignKeyAttr on the scope field."""
        attr = ACIPodPanel._attrs["scope"]
        self.assertIsInstance(attr, attrs.GenericForeignKeyAttr)
        self.assertEqual(attr.accessor, "scope")
        self.assertTrue(attr.linkify)

    def test_scope_get_value_is_none_when_unset(self) -> None:
        """The Scope row's value resolves to None when unset."""
        attr = ACIPodPanel._attrs["scope"]
        self.assertIsNone(attr.get_value(self.aci_pod_bare))

    def test_scope_get_value_resolves_the_scoped_object(self) -> None:
        """The Scope row's value resolves to the assigned scope object."""
        attr = ACIPodPanel._attrs["scope"]
        self.assertEqual(attr.get_value(self.aci_pod_scoped), self.location)


class NodeInfrastructurePanelVPCTestCase(ACIBaseUITestCase):
    """Unit tests for the vPC Protection Group compound attr row."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACINodeInfrastructurePanel tests."""
        aci_fabric = ACIFabric.objects.create(
            name="ACIUINodePanelFabric", fabric_id=1, infra_vlan_vid=100
        )
        aci_pod = ACIPod.objects.create(
            name="ACIUINodePanelPod", aci_fabric=aci_fabric, pod_id=1
        )
        cls.aci_node = ACINode.objects.create(
            name="ACIUINodePanelNode", aci_pod=aci_pod, node_id=101, role="leaf"
        )

    def test_vpc_protection_group_attr_is_templated(self) -> None:
        """vpc_protection_group is a TemplatedAttr on the property."""
        attr = ACINodeInfrastructurePanel._attrs["vpc_protection_group"]
        self.assertIsInstance(attr, attrs.TemplatedAttr)
        self.assertEqual(attr.accessor, "vpc_protection_group")

    def test_vpc_protection_group_get_value_is_none_when_unpaired(self) -> None:
        """An unpaired Node's vPC group row resolves to None."""
        attr = ACINodeInfrastructurePanel._attrs["vpc_protection_group"]
        self.assertIsNone(attr.get_value(self.aci_node))


class NodeInterfacePanelSubPortTestCase(ACIBaseUITestCase):
    """Unit tests for the Sub Port zero-sentinel attr."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACINodeInterfacePanel tests."""
        aci_fabric = ACIFabric.objects.create(
            name="ACIUINodeInterfacePanelFabric", fabric_id=1, infra_vlan_vid=100
        )
        aci_pod = ACIPod.objects.create(
            name="ACIUINodeInterfacePanelPod", aci_fabric=aci_fabric, pod_id=1
        )
        cls.aci_node = ACINode.objects.create(
            name="ACIUINodeInterfacePanelNode",
            aci_pod=aci_pod,
            node_id=101,
            role="leaf",
        )

    def test_sub_port_attr_reads_the_display_property(self) -> None:
        """sub_port is a NumericAttr on the sub_port_display property."""
        attr = ACINodeInterfacePanel._attrs["sub_port"]
        self.assertIsInstance(attr, attrs.NumericAttr)
        self.assertEqual(attr.accessor, "sub_port_display")

    def test_sub_port_get_value_is_none_for_zero_sentinel(self) -> None:
        """Sub Port resolves to None when unset (the 0 sentinel)."""
        iface = ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=1, port=1
        )
        attr = ACINodeInterfacePanel._attrs["sub_port"]
        self.assertIsNone(attr.get_value(iface))

    def test_sub_port_get_value_resolves_nonzero_value(self) -> None:
        """Sub Port resolves to a non-zero breakout sub port number."""
        iface = ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=1, port=1, sub_port=2
        )
        attr = ACINodeInterfacePanel._attrs["sub_port"]
        self.assertEqual(attr.get_value(iface), 2)
