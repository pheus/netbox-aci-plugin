# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Breadcrumb target tests for the fabric domain's detail views.

Each crumb links to its own model's list view, filtered by an ancestor.
A wrong filter parameter still produces a well-formed URL, so the crumb
lands on an unfiltered list with nothing to signal it, and the layout
tests assert only how many crumbs a view declares.
"""

from __future__ import annotations

from types import SimpleNamespace

from django.test import SimpleTestCase
from django.urls import resolve, reverse

from ....views.fabric.node_interfaces import ACINodeInterfaceView
from ....views.fabric.nodes import ACINodeView
from ....views.fabric.pods import ACIPodView
from ....views.fabric.vpc_protection_groups import ACIVPCProtectionGroupView
from ..base import layout_views

# view: [(list view name, filter parameter), ...] in breadcrumb order
EXPECTED_BREADCRUMBS = {
    ACINodeInterfaceView: [
        ("plugins:netbox_aci_plugin:acinodeinterface_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:acinodeinterface_list", "aci_pod_id"),
        ("plugins:netbox_aci_plugin:acinodeinterface_list", "aci_node_id"),
    ],
    ACINodeView: [
        ("plugins:netbox_aci_plugin:acinode_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:acinode_list", "aci_pod_id"),
    ],
    ACIPodView: [
        ("plugins:netbox_aci_plugin:acipod_list", "aci_fabric_id"),
    ],
    ACIVPCProtectionGroupView: [
        ("plugins:netbox_aci_plugin:acivpcprotectiongroup_list", "aci_fabric_id"),
    ],
}


class FabricBreadcrumbTargetTestCase(SimpleTestCase):
    """Pin where every fabric domain breadcrumb links."""

    def test_breadcrumbs_link_to_the_expected_filtered_list(self) -> None:
        """Each crumb builds its pinned list URL and filter parameter."""
        for view_class, expected in EXPECTED_BREADCRUMBS.items():
            with self.subTest(view=view_class.__name__):
                built = [
                    crumb.url(SimpleNamespace(pk=1))
                    for crumb in view_class.layout.breadcrumbs
                ]
                self.assertEqual(built, [f"{reverse(v)}?{p}=1" for v, p in expected])

    def test_breadcrumb_parameters_are_real_filterset_fields(self) -> None:
        """Each filter parameter exists on the target list FilterSet."""
        for view_class, expected in EXPECTED_BREADCRUMBS.items():
            with self.subTest(view=view_class.__name__):
                for viewname, param in expected:
                    list_view = resolve(reverse(viewname)).func.view_class
                    self.assertIn(param, list_view.filterset.base_filters)

    def test_every_breadcrumb_view_is_pinned(self) -> None:
        """A view gaining a breadcrumb without a pin fails here."""
        declared = {
            view_class
            for view_class in layout_views("netbox_aci_plugin.views.fabric")
            if view_class.layout.breadcrumbs
        }
        self.assertCountEqual(EXPECTED_BREADCRUMBS.keys(), declared)
