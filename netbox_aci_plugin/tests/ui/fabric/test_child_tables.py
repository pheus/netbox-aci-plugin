# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Configuration tests for the fabric domain's embedded child tables.

ObjectsTablePanel loads its rows through a second htmx request that the
test client never follows, so nothing else in the suite constrains which
child model a card lists or which filter narrows it. A wrong filter key
is the dangerous case: list views ignore unknown GET parameters, so the
card would silently list every object of the child model.
"""

from __future__ import annotations

from django.test import SimpleTestCase

from netbox.ui.panels import ObjectsTablePanel

from ....filtersets.access_policies.leaf_switch_profiles import (
    ACILeafSwitchProfileFilterSet,
)
from ....views.fabric.nodes import ACINodeView
from ..base import layout_panels, layout_views

# view: (model label, title, filter keys, child FilterSet)
EXPECTED_CHILD_TABLES = {
    ACINodeView: (
        "netbox_aci_plugin.ACILeafSwitchProfile",
        "ACI Leaf Switch Profiles",
        ["covering_aci_node_id"],
        ACILeafSwitchProfileFilterSet,
    ),
}


def child_table_panel(view_class) -> ObjectsTablePanel:
    """Return the single ObjectsTablePanel declared by a view's layout."""
    found = [
        panel
        for row in view_class.layout
        for column in row
        for panel in column
        if isinstance(panel, ObjectsTablePanel)
    ]
    assert len(found) == 1, f"{view_class.__name__} declares {len(found)} panels"
    return found[0]


class FabricChildTablePanelTestCase(SimpleTestCase):
    """Pin the configuration of every embedded fabric child table."""

    def test_panels_list_the_expected_child_model(self) -> None:
        """Each card lists the child model its retired row listed."""
        for view_class, expected in EXPECTED_CHILD_TABLES.items():
            model_label, title = expected[0], expected[1]
            with self.subTest(view=view_class.__name__):
                panel = child_table_panel(view_class)
                self.assertEqual(panel.model_label, model_label)
                self.assertEqual(str(panel.title), title)

    def test_panel_filters_are_real_child_filterset_parameters(self) -> None:
        """Each filter key exists on the child FilterSet.

        A key the FilterSet does not define is ignored by the list view,
        so the card would list every object of the child model.
        """
        for view_class, expected in EXPECTED_CHILD_TABLES.items():
            filter_keys, filterset = expected[2], expected[3]
            with self.subTest(view=view_class.__name__):
                panel = child_table_panel(view_class)
                self.assertEqual(sorted(panel.filters), filter_keys)
                for key in panel.filters:
                    self.assertIn(key, filterset.base_filters)

    def test_panels_carry_no_add_action(self) -> None:
        """Coverage is resolved, so there is no child object to add."""
        for view_class in EXPECTED_CHILD_TABLES:
            with self.subTest(view=view_class.__name__):
                self.assertEqual(child_table_panel(view_class).actions, [])

    def test_every_card_is_pinned(self) -> None:
        """A ObjectsTablePanel added to a layout without a pin fails here."""
        declared = {
            view_class
            for view_class in layout_views("netbox_aci_plugin.views.fabric")
            if any(
                isinstance(panel, ObjectsTablePanel)
                for panel in layout_panels(view_class)
            )
        }
        self.assertCountEqual(EXPECTED_CHILD_TABLES.keys(), declared)
