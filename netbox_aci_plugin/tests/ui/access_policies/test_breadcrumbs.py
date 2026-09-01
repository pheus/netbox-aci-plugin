# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Breadcrumb target tests for the access-policies domain's detail views.

Each crumb links to its own model's list view, filtered by an ancestor.
A wrong filter parameter still produces a well-formed URL, so the crumb
lands on an unfiltered list with nothing to signal it, and the layout
tests assert only how many crumbs a view declares.
"""

from __future__ import annotations

from types import SimpleNamespace

from django.test import SimpleTestCase
from django.urls import resolve, reverse

from ....views.access_policies.aaep import (
    ACIAAEPDomainBindingView,
    ACIAttachableAccessEntityProfileView,
)
from ....views.access_policies.domains import (
    ACIPhysicalDomainView,
    ACIRoutedDomainView,
)
from ....views.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroupView,
)
from ....views.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverrideView,
)
from ....views.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfileView,
    ACILeafInterfaceSelectorView,
    ACILeafPortBlockView,
)
from ....views.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlockView,
    ACILeafSelectorView,
    ACILeafSwitchProfileInterfaceBindingView,
    ACILeafSwitchProfileView,
)
from ....views.access_policies.vlan_pools import (
    ACIVLANPoolRangeView,
    ACIVLANPoolView,
)
from ..base import layout_views

# view: [(list view name, filter parameter), ...] in breadcrumb order
EXPECTED_BREADCRUMBS = {
    ACIAAEPDomainBindingView: [
        ("plugins:netbox_aci_plugin:aciaaepdomainbinding_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:aciaaepdomainbinding_list", "aci_aaep_id"),
    ],
    ACIAttachableAccessEntityProfileView: [
        (
            "plugins:netbox_aci_plugin:aciattachableaccessentityprofile_list",
            "aci_fabric_id",
        ),
    ],
    ACILeafInterfaceOverrideView: [
        ("plugins:netbox_aci_plugin:acileafinterfaceoverride_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:acileafinterfaceoverride_list", "aci_pod_id"),
        ("plugins:netbox_aci_plugin:acileafinterfaceoverride_list", "aci_node_id"),
        (
            "plugins:netbox_aci_plugin:acileafinterfaceoverride_list",
            "aci_node_interface_id",
        ),
    ],
    ACILeafInterfacePolicyGroupView: [
        ("plugins:netbox_aci_plugin:acileafinterfacepolicygroup_list", "aci_fabric_id"),
    ],
    ACILeafInterfaceProfileView: [
        ("plugins:netbox_aci_plugin:acileafinterfaceprofile_list", "aci_fabric_id"),
    ],
    ACILeafInterfaceSelectorView: [
        ("plugins:netbox_aci_plugin:acileafinterfaceselector_list", "aci_fabric_id"),
        (
            "plugins:netbox_aci_plugin:acileafinterfaceselector_list",
            "aci_leaf_interface_profile_id",
        ),
    ],
    ACILeafNodeBlockView: [
        ("plugins:netbox_aci_plugin:acileafnodeblock_list", "aci_fabric_id"),
        (
            "plugins:netbox_aci_plugin:acileafnodeblock_list",
            "aci_leaf_switch_profile_id",
        ),
        ("plugins:netbox_aci_plugin:acileafnodeblock_list", "aci_leaf_selector_id"),
    ],
    ACILeafPortBlockView: [
        ("plugins:netbox_aci_plugin:acileafportblock_list", "aci_fabric_id"),
        (
            "plugins:netbox_aci_plugin:acileafportblock_list",
            "aci_leaf_interface_profile_id",
        ),
        (
            "plugins:netbox_aci_plugin:acileafportblock_list",
            "aci_leaf_interface_selector_id",
        ),
    ],
    ACILeafSelectorView: [
        ("plugins:netbox_aci_plugin:acileafselector_list", "aci_fabric_id"),
        (
            "plugins:netbox_aci_plugin:acileafselector_list",
            "aci_leaf_switch_profile_id",
        ),
    ],
    ACILeafSwitchProfileInterfaceBindingView: [
        (
            "plugins:netbox_aci_plugin:acileafswitchprofileinterfacebinding_list",
            "aci_fabric_id",
        ),
    ],
    ACILeafSwitchProfileView: [
        ("plugins:netbox_aci_plugin:acileafswitchprofile_list", "aci_fabric_id"),
    ],
    ACIPhysicalDomainView: [
        ("plugins:netbox_aci_plugin:aciphysicaldomain_list", "aci_fabric_id"),
    ],
    ACIRoutedDomainView: [
        ("plugins:netbox_aci_plugin:acirouteddomain_list", "aci_fabric_id"),
    ],
    ACIVLANPoolRangeView: [
        ("plugins:netbox_aci_plugin:acivlanpoolrange_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:acivlanpoolrange_list", "aci_vlan_pool_id"),
    ],
    ACIVLANPoolView: [
        ("plugins:netbox_aci_plugin:acivlanpool_list", "aci_fabric_id"),
    ],
}


class AccessPoliciesBreadcrumbTargetTestCase(SimpleTestCase):
    """Pin where every access-policies domain breadcrumb links."""

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
            for view_class in layout_views("netbox_aci_plugin.views.access_policies")
            if view_class.layout.breadcrumbs
        }
        self.assertCountEqual(EXPECTED_BREADCRUMBS.keys(), declared)
