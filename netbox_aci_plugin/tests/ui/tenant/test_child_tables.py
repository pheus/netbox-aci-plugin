# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Configuration tests for the tenant domain's embedded child tables.

ObjectsTablePanel loads its rows through a second htmx request that the
test client never follows, so nothing else in the suite constrains which
child model a card lists, which filter narrows it, or which parameters
its Add button prefills. A wrong filter key is the dangerous case: list
views ignore unknown GET parameters, so the card would silently list
every object of the child model instead of the parent's own.
"""

from __future__ import annotations

from django.test import SimpleTestCase

from netbox.ui.actions import AddObject
from netbox.ui.panels import ObjectsTablePanel

from ....filtersets.tenant.bridge_domains import ACIBridgeDomainSubnetFilterSet
from ....filtersets.tenant.contract_filters import ACIContractFilterEntryFilterSet
from ....filtersets.tenant.contracts import (
    ACIContractSubjectFilterFilterSet,
    ACIContractSubjectFilterSet,
)
from ....filtersets.tenant.l3outs import (
    ACIExternalEndpointGroupFilterSet,
    ACIExternalSubnetFilterSet,
)
from ....forms.tenant.bridge_domains import ACIBridgeDomainSubnetEditForm
from ....forms.tenant.contract_filters import ACIContractFilterEntryEditForm
from ....forms.tenant.contracts import (
    ACIContractSubjectEditForm,
    ACIContractSubjectFilterEditForm,
)
from ....forms.tenant.l3outs import (
    ACIExternalEndpointGroupEditForm,
    ACIExternalSubnetEditForm,
)
from ....views.tenant.bridge_domains import ACIBridgeDomainView
from ....views.tenant.contract_filters import ACIContractFilterView
from ....views.tenant.contracts import ACIContractSubjectView, ACIContractView
from ....views.tenant.l3outs import ACIExternalEndpointGroupView, ACIL3OutView
from ..base import layout_panels, layout_views

# view: (model label, title, filter keys, Add label, prefill keys,
#        child FilterSet, child EditForm)
EXPECTED_CHILD_TABLES = {
    ACIBridgeDomainView: (
        "netbox_aci_plugin.ACIBridgeDomainSubnet",
        "Subnets",
        ["aci_bridge_domain_id"],
        "Add a Subnet",
        ["aci_bridge_domain", "aci_vrf", "nb_tenant", "nb_vrf"],
        ACIBridgeDomainSubnetFilterSet,
        ACIBridgeDomainSubnetEditForm,
    ),
    ACIContractView: (
        "netbox_aci_plugin.ACIContractSubject",
        "Subjects",
        ["aci_contract_id"],
        "Add a Subject",
        ["aci_contract", "nb_tenant"],
        ACIContractSubjectFilterSet,
        ACIContractSubjectEditForm,
    ),
    ACIContractSubjectView: (
        "netbox_aci_plugin.ACIContractSubjectFilter",
        "Filters",
        ["aci_contract_subject_id"],
        "Assign a Filter",
        ["aci_contract_subject"],
        ACIContractSubjectFilterFilterSet,
        ACIContractSubjectFilterEditForm,
    ),
    ACIContractFilterView: (
        "netbox_aci_plugin.ACIContractFilterEntry",
        "Entries",
        ["aci_contract_filter_id"],
        "Add an Entry",
        ["aci_contract_filter"],
        ACIContractFilterEntryFilterSet,
        ACIContractFilterEntryEditForm,
    ),
    ACIL3OutView: (
        "netbox_aci_plugin.ACIExternalEndpointGroup",
        "External EPGs",
        ["aci_l3out_id"],
        "Add an External EPG",
        ["aci_l3out", "nb_tenant"],
        ACIExternalEndpointGroupFilterSet,
        ACIExternalEndpointGroupEditForm,
    ),
    ACIExternalEndpointGroupView: (
        "netbox_aci_plugin.ACIExternalSubnet",
        "External Subnets",
        ["aci_external_endpoint_group_id"],
        "Add a Subnet",
        ["aci_external_endpoint_group", "nb_tenant"],
        ACIExternalSubnetFilterSet,
        ACIExternalSubnetEditForm,
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


class TenantChildTablePanelTestCase(SimpleTestCase):
    """Pin the configuration of every embedded tenant child table."""

    def test_panels_list_the_expected_child_model(self) -> None:
        """Each card lists the child model its retired table listed."""
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
            filter_keys, filterset = expected[2], expected[5]
            with self.subTest(view=view_class.__name__):
                panel = child_table_panel(view_class)
                self.assertEqual(sorted(panel.filters), filter_keys)
                for key in panel.filters:
                    self.assertIn(key, filterset.base_filters)

    def test_add_action_prefills_real_child_form_fields(self) -> None:
        """Each Add button's prefill keys are fields on the child form.

        A renamed form field silently stops the button pre-filling, which
        no other test in the suite would notice.
        """
        for view_class, expected in EXPECTED_CHILD_TABLES.items():
            label, prefill_keys, form = expected[3], expected[4], expected[6]
            with self.subTest(view=view_class.__name__):
                panel = child_table_panel(view_class)
                add_actions = [a for a in panel.actions if isinstance(a, AddObject)]
                self.assertEqual(len(add_actions), 1)
                action = add_actions[0]
                self.assertEqual(str(action.label), label)
                self.assertEqual(sorted(action.url_params), prefill_keys)
                for key in action.url_params:
                    self.assertIn(key, form.base_fields)

    def test_every_card_is_pinned(self) -> None:
        """A ObjectsTablePanel added to a layout without a pin fails here."""
        declared = {
            view_class
            for view_class in layout_views("netbox_aci_plugin.views.tenant")
            if any(
                isinstance(panel, ObjectsTablePanel)
                for panel in layout_panels(view_class)
            )
        }
        self.assertCountEqual(EXPECTED_CHILD_TABLES.keys(), declared)
