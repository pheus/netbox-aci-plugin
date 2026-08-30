# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Layout composition tests for the tenant domain's detail views.

Pins which panels each view renders, in which order, and in which
column, plus the depth of its breadcrumb trail. Without this a panel
can be dropped from a layout and vanish from the page while every
other test stays green, because the panel tests instantiate their
subject directly and the inherited detail-page test asserts only the
response status. Tenant has zero pre-existing detail-page content
assertions, so this file is the only thing standing between a silent
regression and a green suite.

The trailing PluginContentPanel in every column is part of the pin: it
is appended only by SimpleLayout, so its presence is what keeps other
plugins' template extensions rendering on these pages.
"""

from __future__ import annotations

from django.test import SimpleTestCase

from ....views.tenant.app_profiles import ACIAppProfileView
from ....views.tenant.bridge_domains import (
    ACIBridgeDomainL3OutBindingView,
    ACIBridgeDomainSubnetView,
    ACIBridgeDomainView,
)
from ....views.tenant.contract_filters import (
    ACIContractFilterEntryView,
    ACIContractFilterView,
)
from ....views.tenant.contracts import (
    ACIContractRelationView,
    ACIContractSubjectFilterView,
    ACIContractSubjectView,
    ACIContractView,
)
from ....views.tenant.endpoint_group_bindings import (
    ACIEndpointGroupAAEPBindingView,
    ACIEndpointGroupDomainBindingView,
)
from ....views.tenant.endpoint_groups import (
    ACIEndpointGroupView,
    ACIUSegEndpointGroupView,
    ACIUSegNetworkAttributeView,
)
from ....views.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroupView,
    ACIEsgEndpointGroupSelectorView,
    ACIEsgEndpointSelectorView,
)
from ....views.tenant.l3outs import (
    ACIExternalEndpointGroupView,
    ACIExternalSubnetView,
    ACIL3OutView,
)
from ....views.tenant.tenants import ACITenantView
from ....views.tenant.vrfs import ACIVRFView
from ..base import layout_views

# view: (left column, right column, bottom row, breadcrumb count)
EXPECTED_LAYOUTS = {
    ACITenantView: (
        [
            "ACITenantPanel",
            "CustomFieldsPanel",
            "TagsPanel",
            "CommentsPanel",
            "PluginContentPanel",
        ],
        ["RelatedObjectsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        1,
    ),
    ACIVRFView: (
        [
            "ACIVRFPanel",
            "ACIVRFPolicyControlPanel",
            "ACIVRFEndpointLearningPanel",
            "ACIVRFMulticastPanel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        [
            "ACIVRFAdditionalSettingsPanel",
            "TagsPanel",
            "CommentsPanel",
            "PluginContentPanel",
        ],
        ["PluginContentPanel"],
        2,
    ),
    ACIAppProfileView: (
        ["ACIAppProfilePanel", "CustomFieldsPanel", "PluginContentPanel"],
        ["TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        2,
    ),
    ACIBridgeDomainView: (
        [
            "ACIBridgeDomainPanel",
            "ACIBridgeDomainRoutingPanel",
            "ACIBridgeDomainForwardingMethodPanel",
            "ACIBridgeDomainEndpointLearningPanel",
            "ACIBridgeDomainMulticastPanel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        [
            "ObjectsTablePanel",
            "ACIBridgeDomainAdditionalSettingsPanel",
            "TagsPanel",
            "CommentsPanel",
            "PluginContentPanel",
        ],
        ["PluginContentPanel"],
        3,
    ),
    ACIBridgeDomainSubnetView: (
        [
            "ACIBridgeDomainSubnetPanel",
            "ACIBridgeDomainSubnetScopePanel",
            "ACIBridgeDomainSubnetControlPanel",
            "ACIBridgeDomainSubnetEndpointLearningPanel",
            "ACIBridgeDomainSubnetIPv6Panel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        ["TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        4,
    ),
    ACIBridgeDomainL3OutBindingView: (
        ["ACIBridgeDomainL3OutBindingPanel", "CustomFieldsPanel", "PluginContentPanel"],
        ["TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        3,
    ),
    ACIContractView: (
        [
            "ACIContractPanel",
            "ACIContractScopePanel",
            "ACIContractPriorityPanel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        ["ObjectsTablePanel", "TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        2,
    ),
    ACIContractRelationView: (
        ["ACIContractRelationPanel", "CustomFieldsPanel", "PluginContentPanel"],
        ["TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        3,
    ),
    ACIContractSubjectView: (
        [
            "ACIContractSubjectPanel",
            "ACIContractSubjectDirectionPanel",
            "ACIContractSubjectServiceGraphPanel",
            "ACIContractSubjectPriorityPanel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        ["ObjectsTablePanel", "TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        3,
    ),
    ACIContractSubjectFilterView: (
        [
            "ACIContractSubjectFilterPanel",
            "ACIContractSubjectFilterDirectionPanel",
            "ACIContractSubjectFilterDirectivesPanel",
            "ACIContractSubjectFilterPriorityPanel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        ["TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        4,
    ),
    ACIContractFilterView: (
        ["ACIContractFilterPanel", "CustomFieldsPanel", "PluginContentPanel"],
        ["TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["ObjectsTablePanel", "PluginContentPanel"],
        2,
    ),
    ACIContractFilterEntryView: (
        [
            "ACIContractFilterEntryPanel",
            "ACIContractFilterEntryEthernetPanel",
            "ACIContractFilterEntryARPPanel",
            "ACIContractFilterEntryIPProtocolPanel",
            "ACIContractFilterEntryICMPPanel",
            "ACIContractFilterEntryPortRangePanel",
            "ACIContractFilterEntryTCPPanel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        ["TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        3,
    ),
    ACIEndpointGroupView: (
        [
            "ACIEndpointGroupPanel",
            "ACIEndpointGroupPolicyEnforcementPanel",
            "ACIEndpointGroupForwardingPanel",
            "ACIEndpointGroupQoSPanel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        ["TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        4,
    ),
    ACIUSegEndpointGroupView: (
        [
            "ACIUSegEndpointGroupPanel",
            "ACIUSegEndpointGroupPolicyEnforcementPanel",
            "ACIUSegEndpointGroupForwardingPanel",
            "ACIUSegEndpointGroupQoSPanel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        ["TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        4,
    ),
    ACIUSegNetworkAttributeView: (
        [
            "ACIUSegNetworkAttributePanel",
            "ACIUSegNetworkAttributeEPGSubnetPanel",
            "ACIUSegNetworkAttributeAssignmentPanel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        ["TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        4,
    ),
    ACIEndpointGroupDomainBindingView: (
        [
            "ACIEndpointGroupDomainBindingPanel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        ["TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        2,
    ),
    ACIEndpointGroupAAEPBindingView: (
        ["ACIEndpointGroupAAEPBindingPanel", "CustomFieldsPanel", "PluginContentPanel"],
        ["TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        2,
    ),
    ACIEndpointSecurityGroupView: (
        [
            "ACIEndpointSecurityGroupPanel",
            "ACIEndpointSecurityGroupPolicyEnforcementPanel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        ["TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        4,
    ),
    ACIEsgEndpointGroupSelectorView: (
        [
            "ACIEsgEndpointGroupSelectorPanel",
            "ACIEsgEndpointGroupSelectorAssignmentPanel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        ["TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        4,
    ),
    ACIEsgEndpointSelectorView: (
        [
            "ACIEsgEndpointSelectorPanel",
            "ACIEsgEndpointSelectorAssignmentPanel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        ["TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        4,
    ),
    ACIL3OutView: (
        [
            "ACIL3OutPanel",
            "ACIL3OutPolicyPanel",
            "ACIL3OutProtocolsPanel",
            "ACIL3OutPolicyReferencesPanel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        ["ObjectsTablePanel", "TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        3,
    ),
    ACIExternalEndpointGroupView: (
        [
            "ACIExternalEndpointGroupPanel",
            "ACIExternalEndpointGroupPolicyPanel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        ["ObjectsTablePanel", "TagsPanel", "CommentsPanel", "PluginContentPanel"],
        ["PluginContentPanel"],
        3,
    ),
    ACIExternalSubnetView: (
        [
            "ACIExternalSubnetPanel",
            "ACIExternalSubnetScopePanel",
            "CustomFieldsPanel",
            "PluginContentPanel",
        ],
        [
            "ACIExternalSubnetRouteSummarizationPanel",
            "TagsPanel",
            "CommentsPanel",
            "PluginContentPanel",
        ],
        ["PluginContentPanel"],
        4,
    ),
}


def panel_names(column) -> list[str]:
    """Return the class names of the panels in a layout column."""
    return [type(panel).__name__ for panel in column]


class TenantLayoutCompositionTestCase(SimpleTestCase):
    """Pin the panel composition of every tenant domain detail view."""

    def test_layouts_render_the_expected_panels_per_column(self) -> None:
        """Each view keeps its panels, their order, and their column."""
        for view_class, expected in EXPECTED_LAYOUTS.items():
            left, right, bottom, breadcrumbs = expected
            with self.subTest(view=view_class.__name__):
                rows = list(view_class.layout)
                self.assertEqual(len(rows), 2)
                top_columns = list(rows[0])
                self.assertEqual(len(top_columns), 2)
                self.assertEqual(panel_names(top_columns[0]), left)
                self.assertEqual(panel_names(top_columns[1]), right)
                bottom_columns = list(rows[1])
                self.assertEqual(len(bottom_columns), 1)
                self.assertEqual(panel_names(bottom_columns[0]), bottom)
                self.assertEqual(len(view_class.layout.breadcrumbs), breadcrumbs)

    def test_every_layout_view_is_pinned(self) -> None:
        """A view gaining a layout without a pin fails here.

        The test above iterates EXPECTED_LAYOUTS, so its completeness is
        a property of the text unless something asserts it.
        """
        self.assertCountEqual(
            EXPECTED_LAYOUTS.keys(), layout_views("netbox_aci_plugin.views.tenant")
        )
