# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Row-order tests for the fabric domain's declarative UI panels.

Each panel renders its attributes in declaration order, so these pin
the order the retired detail templates authored. Panels declare every
attribute inline rather than inheriting a shared tail, because
ObjectAttributesPanelMeta always places inherited attributes before
locally declared ones and offers no way to reorder them.
"""

from __future__ import annotations

from django.test import SimpleTestCase

from netbox.ui.panels import ObjectAttributesPanel

from ....ui.panels.fabric.fabrics import ACIFabricPanel
from ....ui.panels.fabric.node_interfaces import (
    ACINodeInterfaceOverridePanel,
    ACINodeInterfacePanel,
)
from ....ui.panels.fabric.nodes import ACINodeInfrastructurePanel, ACINodePanel
from ....ui.panels.fabric.pods import ACIPodPanel
from ....ui.panels.fabric.vpc_protection_groups import ACIVPCProtectionGroupPanel
from ..base import layout_panels, layout_views

# Attribute name and accessor, in the order the retired detail template
# rendered each row. The accessor is pinned because a copy-paste slip can
# point a row at a neighbouring field without changing the row order.
EXPECTED_ORDER = {
    ACIFabricPanel: [
        ("description", "description"),
        ("fabric_id", "fabric_id"),
        ("infra_vlan_vid", "infra_vlan_vid"),
        ("infra_vlan", "infra_vlan"),
        ("gipo_pool", "gipo_pool"),
        ("nb_tenant", "nb_tenant"),
        ("scope", "scope"),
    ],
    ACIPodPanel: [
        ("aci_fabric", "aci_fabric"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("pod_id", "pod_id"),
        ("tep_pool", "tep_pool"),
        ("nb_tenant", "nb_tenant"),
        ("scope", "scope"),
    ],
    ACINodePanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_pod", "aci_pod"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("node_id", "node_id"),
        ("node_object", "node_object"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACINodeInfrastructurePanel: [
        ("role", "role"),
        ("node_type", "node_type"),
        ("tep_ip_address", "tep_ip_address"),
        ("vpc_protection_group", "vpc_protection_group"),
    ],
    ACINodeInterfacePanel: [
        ("aci_node", "aci_node"),
        ("description", "description"),
        ("nb_interface", "nb_interface"),
        ("module", "module"),
        ("port", "port"),
        ("sub_port", "sub_port_display"),
        ("interface_token", "interface_token"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACINodeInterfaceOverridePanel: [
        ("aci_leaf_interface_override", "leaf_interface_override"),
        (
            "aci_leaf_interface_policy_group",
            "leaf_interface_override.aci_leaf_interface_policy_group",
        ),
    ],
    ACIVPCProtectionGroupPanel: [
        ("aci_fabric", "aci_fabric"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("logical_pair_id", "logical_pair_id"),
        ("aci_node_a", "aci_node_a"),
        ("aci_node_b", "aci_node_b"),
        ("aci_pod", "aci_pod"),
        ("nb_tenant", "nb_tenant"),
    ],
}


class FabricPanelAttributeOrderTestCase(SimpleTestCase):
    """Pin the attribute order of every fabric domain panel."""

    def test_panels_declare_attributes_in_the_authored_order(self) -> None:
        """Each panel keeps the row order of the template it replaced."""
        for panel_class, expected in EXPECTED_ORDER.items():
            with self.subTest(panel=panel_class.__name__):
                pairs = [
                    (name, attr.accessor) for name, attr in panel_class._attrs.items()
                ]
                self.assertEqual(pairs, expected)

    def test_every_declared_panel_is_pinned(self) -> None:
        """A panel added to a layout without a pin fails here."""
        declared = {
            type(panel)
            for view_class in layout_views("netbox_aci_plugin.views.fabric")
            for panel in layout_panels(view_class)
            if isinstance(panel, ObjectAttributesPanel)
        }
        self.assertCountEqual(EXPECTED_ORDER.keys(), declared)
