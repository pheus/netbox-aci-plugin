# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Configuration tests for the access-policies domain's context tables.

Three sibling views render a node table built by their own
get_extra_context(). test_layouts.py reduces each to the class name
ContextTablePanel, which makes all three indistinguishable, so nothing
pins which heading belongs to which page. The distinction is real in
the ACI model: a Profile or Selector resolves down to nodes, whereas a
Node Block covers them.
"""

from __future__ import annotations

from django.test import SimpleTestCase

from netbox.ui.panels import ContextTablePanel

from ....views.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlockView,
    ACILeafSelectorView,
    ACILeafSwitchProfileView,
)
from ..base import layout_panels, layout_views

# view: (context key, title)
EXPECTED_CONTEXT_TABLES = {
    ACILeafSwitchProfileView: ("aci_nodes_table", "Resolved ACI Nodes"),
    ACILeafSelectorView: ("aci_nodes_table", "Resolved ACI Nodes"),
    ACILeafNodeBlockView: ("aci_nodes_table", "Covered ACI Nodes"),
}


def context_table_panel(view_class) -> ContextTablePanel:
    """Return the single ContextTablePanel declared by a view's layout."""
    found = [
        panel
        for row in view_class.layout
        for column in row
        for panel in column
        if isinstance(panel, ContextTablePanel)
    ]
    assert len(found) == 1, f"{view_class.__name__} declares {len(found)} panels"
    return found[0]


class AccessPoliciesContextTablePanelTestCase(SimpleTestCase):
    """Pin the configuration of every access-policies context table."""

    def test_panels_read_the_expected_context_key(self) -> None:
        """Each card reads the key its view's get_extra_context() sets.

        A key the view does not set makes should_render() return False
        and the card vanish from the page.
        """
        for view_class, expected in EXPECTED_CONTEXT_TABLES.items():
            with self.subTest(view=view_class.__name__):
                self.assertEqual(context_table_panel(view_class).table, expected[0])

    def test_panels_carry_the_expected_heading(self) -> None:
        """Each card keeps the heading its retired template rendered."""
        for view_class, expected in EXPECTED_CONTEXT_TABLES.items():
            with self.subTest(view=view_class.__name__):
                self.assertEqual(
                    str(context_table_panel(view_class).title), expected[1]
                )

    def test_every_card_is_pinned(self) -> None:
        """A ContextTablePanel added to a layout without a pin fails here."""
        declared = {
            view_class
            for view_class in layout_views("netbox_aci_plugin.views.access_policies")
            if any(
                isinstance(panel, ContextTablePanel)
                for panel in layout_panels(view_class)
            )
        }
        self.assertCountEqual(EXPECTED_CONTEXT_TABLES.keys(), declared)
