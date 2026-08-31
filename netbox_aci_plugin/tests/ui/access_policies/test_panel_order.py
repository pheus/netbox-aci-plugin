# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Row-order tests for the access-policies domain's declarative UI panels.

Each panel renders its attributes in declaration order, so these pin
the order the retired detail templates authored. Panels declare every
attribute inline rather than inheriting a shared tail, because
ObjectAttributesPanelMeta always places inherited attributes before
locally declared ones and offers no way to reorder them.
"""

from __future__ import annotations

from django.test import SimpleTestCase

from netbox.ui.panels import ObjectAttributesPanel

from ....ui.panels.access_policies.aaep import (
    ACIAAEPDomainBindingPanel,
    ACIAttachableAccessEntityProfilePanel,
)
from ....ui.panels.access_policies.domains import (
    ACIPhysicalDomainPanel,
    ACIRoutedDomainPanel,
)
from ....ui.panels.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroupPanel,
)
from ....ui.panels.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverridePanel,
)
from ....ui.panels.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfilePanel,
    ACILeafInterfaceSelectorPanel,
    ACILeafPortBlockPanel,
    ACILeafPortBlockRangePanel,
)
from ....ui.panels.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlockPanel,
    ACILeafNodeBlockRangePanel,
    ACILeafSelectorPanel,
    ACILeafSwitchProfileInterfaceBindingPanel,
    ACILeafSwitchProfilePanel,
)
from ....ui.panels.access_policies.vlan_pools import (
    ACIVLANPoolPanel,
    ACIVLANPoolRangePanel,
)
from ..base import layout_panels, layout_views

# Attribute name and accessor, in the order the retired detail template
# rendered each row. The accessor is pinned because a copy-paste slip can
# point a row at a neighbouring field without changing the row order.
EXPECTED_ORDER = {
    ACIAttachableAccessEntityProfilePanel: [
        ("aci_fabric", "aci_fabric"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("infra_vlan", "infra_vlan"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIAAEPDomainBindingPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_aaep", "aci_aaep"),
        ("aci_domain_object", "aci_domain_object"),
    ],
    ACIPhysicalDomainPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_vlan_pool", "aci_vlan_pool"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("security_domains", "security_domains"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIRoutedDomainPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_vlan_pool", "aci_vlan_pool"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("security_domains", "security_domains"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACILeafInterfacePolicyGroupPanel: [
        ("aci_fabric", "aci_fabric"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("group_type", "group_type"),
        ("aci_aaep", "aci_aaep"),
        ("lag_type", "lag_type"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACILeafInterfaceOverridePanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_node_interface", "aci_node_interface"),
        ("aci_leaf_interface_policy_group", "aci_leaf_interface_policy_group"),
        ("description", "description"),
    ],
    ACILeafInterfaceProfilePanel: [
        ("aci_fabric", "aci_fabric"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
        ("selector_count", "selector_count"),
    ],
    ACILeafInterfaceSelectorPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_leaf_interface_profile", "aci_leaf_interface_profile"),
        ("aci_leaf_interface_policy_group", "aci_leaf_interface_policy_group"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
        ("port_block_count", "port_block_count"),
    ],
    ACILeafPortBlockPanel: [
        ("aci_fabric", "aci_fabric"),
        (
            "aci_leaf_interface_profile",
            "aci_leaf_interface_selector.aci_leaf_interface_profile",
        ),
        ("aci_leaf_interface_selector", "aci_leaf_interface_selector"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACILeafPortBlockRangePanel: [
        ("module_from", "module_from"),
        ("module_to", "module_to"),
        ("port_from", "port_from"),
        ("port_to", "port_to"),
    ],
    ACILeafSwitchProfilePanel: [
        ("aci_fabric", "aci_fabric"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
        ("selector_count", "selector_count"),
    ],
    ACILeafSelectorPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_leaf_switch_profile", "aci_leaf_switch_profile"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
        ("node_block_count", "node_block_count"),
    ],
    ACILeafNodeBlockPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_leaf_switch_profile", "aci_leaf_selector.aci_leaf_switch_profile"),
        ("aci_leaf_selector", "aci_leaf_selector"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACILeafNodeBlockRangePanel: [
        ("node_id_from", "node_id_from"),
        ("node_id_to", "node_id_to"),
    ],
    ACILeafSwitchProfileInterfaceBindingPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_leaf_switch_profile", "aci_leaf_switch_profile"),
        ("aci_leaf_interface_profile", "aci_leaf_interface_profile"),
    ],
    ACIVLANPoolPanel: [
        ("aci_fabric", "aci_fabric"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("allocation_mode", "allocation_mode"),
        ("nb_vlan_group", "nb_vlan_group"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIVLANPoolRangePanel: [
        ("aci_vlan_pool", "aci_vlan_pool"),
        ("vlan_id_from", "vlan_id_from"),
        ("vlan_id_to", "vlan_id_to"),
        ("allocation_mode", "allocation_mode"),
        ("role", "role"),
    ],
}


class AccessPoliciesPanelAttributeOrderTestCase(SimpleTestCase):
    """Pin the attribute order of every access-policies domain panel."""

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
            for view_class in layout_views("netbox_aci_plugin.views.access_policies")
            for panel in layout_panels(view_class)
            if isinstance(panel, ObjectAttributesPanel)
        }
        self.assertCountEqual(EXPECTED_ORDER.keys(), declared)
