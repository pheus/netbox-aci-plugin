# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Breadcrumb target tests for the tenant domain's detail views.

Each crumb links to its own model's list view, filtered by an ancestor.
A wrong filter parameter still produces a well-formed URL, so the crumb
lands on an unfiltered list with nothing to signal it, and the layout
tests assert only how many crumbs a view declares.
"""

from __future__ import annotations

from types import SimpleNamespace

from django.test import SimpleTestCase
from django.urls import resolve, reverse

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

# view: [(list view name, filter parameter), ...] in breadcrumb order
EXPECTED_BREADCRUMBS = {
    ACIAppProfileView: [
        ("plugins:netbox_aci_plugin:aciappprofile_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:aciappprofile_list", "aci_tenant_id"),
    ],
    ACIBridgeDomainL3OutBindingView: [
        ("plugins:netbox_aci_plugin:acibridgedomainl3outbinding_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:acibridgedomainl3outbinding_list", "aci_tenant_id"),
        (
            "plugins:netbox_aci_plugin:acibridgedomainl3outbinding_list",
            "aci_bridge_domain_id",
        ),
    ],
    ACIBridgeDomainSubnetView: [
        ("plugins:netbox_aci_plugin:acibridgedomainsubnet_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:acibridgedomainsubnet_list", "aci_tenant_id"),
        ("plugins:netbox_aci_plugin:acibridgedomainsubnet_list", "aci_vrf_id"),
        (
            "plugins:netbox_aci_plugin:acibridgedomainsubnet_list",
            "aci_bridge_domain_id",
        ),
    ],
    ACIBridgeDomainView: [
        ("plugins:netbox_aci_plugin:acibridgedomain_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:acibridgedomain_list", "aci_tenant_id"),
        ("plugins:netbox_aci_plugin:acibridgedomain_list", "aci_vrf_id"),
    ],
    ACIContractFilterEntryView: [
        ("plugins:netbox_aci_plugin:acicontractfilterentry_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:acicontractfilterentry_list", "aci_tenant_id"),
        (
            "plugins:netbox_aci_plugin:acicontractfilterentry_list",
            "aci_contract_filter_id",
        ),
    ],
    ACIContractFilterView: [
        ("plugins:netbox_aci_plugin:acicontractfilter_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:acicontractfilter_list", "aci_tenant_id"),
    ],
    ACIContractRelationView: [
        ("plugins:netbox_aci_plugin:acicontractrelation_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:acicontractrelation_list", "aci_tenant_id"),
        ("plugins:netbox_aci_plugin:acicontractrelation_list", "aci_contract_id"),
    ],
    ACIContractSubjectFilterView: [
        ("plugins:netbox_aci_plugin:acicontractsubjectfilter_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:acicontractsubjectfilter_list", "aci_tenant_id"),
        ("plugins:netbox_aci_plugin:acicontractsubjectfilter_list", "aci_contract_id"),
        (
            "plugins:netbox_aci_plugin:acicontractsubjectfilter_list",
            "aci_contract_subject_id",
        ),
    ],
    ACIContractSubjectView: [
        ("plugins:netbox_aci_plugin:acicontractsubject_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:acicontractsubject_list", "aci_tenant_id"),
        ("plugins:netbox_aci_plugin:acicontractsubject_list", "aci_contract_id"),
    ],
    ACIContractView: [
        ("plugins:netbox_aci_plugin:acicontract_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:acicontract_list", "aci_tenant_id"),
    ],
    ACIEndpointGroupAAEPBindingView: [
        ("plugins:netbox_aci_plugin:aciendpointgroupaaepbinding_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:aciendpointgroupaaepbinding_list", "aci_aaep_id"),
    ],
    ACIEndpointGroupDomainBindingView: [
        (
            "plugins:netbox_aci_plugin:aciendpointgroupdomainbinding_list",
            "aci_fabric_id",
        ),
        (
            "plugins:netbox_aci_plugin:aciendpointgroupdomainbinding_list",
            "aci_epg_object_id",
        ),
    ],
    ACIEndpointGroupView: [
        ("plugins:netbox_aci_plugin:aciendpointgroup_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:aciendpointgroup_list", "aci_tenant_id"),
        ("plugins:netbox_aci_plugin:aciendpointgroup_list", "aci_app_profile_id"),
        ("plugins:netbox_aci_plugin:aciendpointgroup_list", "aci_bridge_domain_id"),
    ],
    ACIEndpointSecurityGroupView: [
        ("plugins:netbox_aci_plugin:aciendpointsecuritygroup_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:aciendpointsecuritygroup_list", "aci_tenant_id"),
        (
            "plugins:netbox_aci_plugin:aciendpointsecuritygroup_list",
            "aci_app_profile_id",
        ),
        ("plugins:netbox_aci_plugin:aciendpointsecuritygroup_list", "aci_vrf_id"),
    ],
    ACIEsgEndpointGroupSelectorView: [
        ("plugins:netbox_aci_plugin:aciesgendpointgroupselector_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:aciesgendpointgroupselector_list", "aci_tenant_id"),
        (
            "plugins:netbox_aci_plugin:aciesgendpointgroupselector_list",
            "aci_app_profile_id",
        ),
        (
            "plugins:netbox_aci_plugin:aciesgendpointgroupselector_list",
            "aci_endpoint_security_group_id",
        ),
    ],
    ACIEsgEndpointSelectorView: [
        ("plugins:netbox_aci_plugin:aciesgendpointselector_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:aciesgendpointselector_list", "aci_tenant_id"),
        ("plugins:netbox_aci_plugin:aciesgendpointselector_list", "aci_app_profile_id"),
        (
            "plugins:netbox_aci_plugin:aciesgendpointselector_list",
            "aci_endpoint_security_group_id",
        ),
    ],
    ACIExternalEndpointGroupView: [
        ("plugins:netbox_aci_plugin:aciexternalendpointgroup_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:aciexternalendpointgroup_list", "aci_tenant_id"),
        ("plugins:netbox_aci_plugin:aciexternalendpointgroup_list", "aci_l3out_id"),
    ],
    ACIExternalSubnetView: [
        ("plugins:netbox_aci_plugin:aciexternalsubnet_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:aciexternalsubnet_list", "aci_tenant_id"),
        ("plugins:netbox_aci_plugin:aciexternalsubnet_list", "aci_l3out_id"),
        (
            "plugins:netbox_aci_plugin:aciexternalsubnet_list",
            "aci_external_endpoint_group_id",
        ),
    ],
    ACIL3OutView: [
        ("plugins:netbox_aci_plugin:acil3out_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:acil3out_list", "aci_tenant_id"),
        ("plugins:netbox_aci_plugin:acil3out_list", "aci_vrf_id"),
    ],
    ACITenantView: [
        ("plugins:netbox_aci_plugin:acitenant_list", "aci_fabric_id"),
    ],
    ACIUSegEndpointGroupView: [
        ("plugins:netbox_aci_plugin:aciusegendpointgroup_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:aciusegendpointgroup_list", "aci_tenant_id"),
        ("plugins:netbox_aci_plugin:aciusegendpointgroup_list", "aci_app_profile_id"),
        ("plugins:netbox_aci_plugin:aciusegendpointgroup_list", "aci_bridge_domain_id"),
    ],
    ACIUSegNetworkAttributeView: [
        ("plugins:netbox_aci_plugin:aciusegnetworkattribute_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:aciusegnetworkattribute_list", "aci_tenant_id"),
        (
            "plugins:netbox_aci_plugin:aciusegnetworkattribute_list",
            "aci_app_profile_id",
        ),
        (
            "plugins:netbox_aci_plugin:aciusegnetworkattribute_list",
            "aci_useg_endpoint_group_id",
        ),
    ],
    ACIVRFView: [
        ("plugins:netbox_aci_plugin:acivrf_list", "aci_fabric_id"),
        ("plugins:netbox_aci_plugin:acivrf_list", "aci_tenant_id"),
    ],
}


class TenantBreadcrumbTargetTestCase(SimpleTestCase):
    """Pin where every tenant domain breadcrumb links."""

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
            for view_class in layout_views("netbox_aci_plugin.views.tenant")
            if view_class.layout.breadcrumbs
        }
        self.assertCountEqual(EXPECTED_BREADCRUMBS.keys(), declared)
