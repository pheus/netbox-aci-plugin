# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from extras.ui.panels import CustomFieldsPanel, TagsPanel
from netbox.ui import layout
from netbox.ui.breadcrumbs import Breadcrumb, filtered_list_url
from netbox.ui.panels import CommentsPanel
from netbox.views import generic
from utilities.views import register_model_view

from ...filtersets.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverrideFilterSet,
)
from ...forms.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverrideBulkEditForm,
    ACILeafInterfaceOverrideEditForm,
    ACILeafInterfaceOverrideFilterForm,
    ACILeafInterfaceOverrideImportForm,
)
from ...models.access_policies.leaf_interface_overrides import ACILeafInterfaceOverride
from ...tables.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverrideTable,
)
from ...ui.panels.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverridePanel,
)

#
# Leaf Interface Override views
#


@register_model_view(ACILeafInterfaceOverride)
class ACILeafInterfaceOverrideView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Leaf Override."""

    queryset = ACILeafInterfaceOverride.objects.select_related(
        "aci_node_interface",
        "aci_node_interface__aci_node",
        "aci_node_interface__aci_node__aci_pod",
        "aci_node_interface__aci_node__aci_pod__aci_fabric",
        "aci_node_interface__aci_node___aci_fabric",
        "aci_leaf_interface_policy_group",
    ).prefetch_related("tags")
    template_name = "generic/object.html"
    layout = layout.SimpleLayout(
        breadcrumbs=[
            Breadcrumb(
                "aci_fabric",
                url=filtered_list_url(
                    "plugins:netbox_aci_plugin:acileafinterfaceoverride_list",
                    "aci_fabric_id",
                ),
            ),
            Breadcrumb(
                lambda obj: obj.aci_node_interface.aci_node.aci_pod,
                url=filtered_list_url(
                    "plugins:netbox_aci_plugin:acileafinterfaceoverride_list",
                    "aci_pod_id",
                ),
            ),
            Breadcrumb(
                lambda obj: obj.aci_node_interface.aci_node,
                url=filtered_list_url(
                    "plugins:netbox_aci_plugin:acileafinterfaceoverride_list",
                    "aci_node_id",
                ),
            ),
            Breadcrumb(
                "aci_node_interface",
                url=filtered_list_url(
                    "plugins:netbox_aci_plugin:acileafinterfaceoverride_list",
                    "aci_node_interface_id",
                ),
            ),
        ],
        left_panels=[
            ACILeafInterfaceOverridePanel(),
            CustomFieldsPanel(),
        ],
        right_panels=[
            TagsPanel(),
            CommentsPanel(),
        ],
    )


@register_model_view(ACILeafInterfaceOverride, "list", path="", detail=False)
class ACILeafInterfaceOverrideListView(generic.ObjectListView):
    """List view for listing all objects of ACI Leaf Override."""

    queryset = ACILeafInterfaceOverride.objects.select_related(
        "aci_node_interface",
        "aci_node_interface__aci_node",
        "aci_node_interface__aci_node__aci_pod",
        "aci_node_interface__aci_node__aci_pod__aci_fabric",
        "aci_node_interface__aci_node___aci_fabric",
        "aci_leaf_interface_policy_group",
    ).prefetch_related("tags")
    filterset = ACILeafInterfaceOverrideFilterSet
    filterset_form = ACILeafInterfaceOverrideFilterForm
    table = ACILeafInterfaceOverrideTable


@register_model_view(ACILeafInterfaceOverride, "add", detail=False)
@register_model_view(ACILeafInterfaceOverride, "edit")
class ACILeafInterfaceOverrideEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Leaf Override."""

    queryset = ACILeafInterfaceOverride.objects.select_related(
        "aci_node_interface",
        "aci_node_interface__aci_node",
        "aci_node_interface__aci_node__aci_pod",
        "aci_node_interface__aci_node__aci_pod__aci_fabric",
        "aci_node_interface__aci_node___aci_fabric",
        "aci_leaf_interface_policy_group",
    ).prefetch_related("tags")
    form = ACILeafInterfaceOverrideEditForm


@register_model_view(ACILeafInterfaceOverride, "delete")
class ACILeafInterfaceOverrideDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Leaf Override."""

    queryset = ACILeafInterfaceOverride.objects.select_related(
        "aci_node_interface",
        "aci_node_interface__aci_node",
        "aci_node_interface__aci_node__aci_pod",
        "aci_node_interface__aci_node__aci_pod__aci_fabric",
        "aci_node_interface__aci_node___aci_fabric",
        "aci_leaf_interface_policy_group",
    ).prefetch_related("tags")


@register_model_view(
    ACILeafInterfaceOverride, "bulk_import", path="import", detail=False
)
class ACILeafInterfaceOverrideBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple ACI Leaf Override objects."""

    queryset = ACILeafInterfaceOverride.objects.all()
    model_form = ACILeafInterfaceOverrideImportForm


@register_model_view(ACILeafInterfaceOverride, "bulk_edit", path="edit", detail=False)
class ACILeafInterfaceOverrideBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI Leaf Override."""

    queryset = ACILeafInterfaceOverride.objects.all()
    filterset = ACILeafInterfaceOverrideFilterSet
    table = ACILeafInterfaceOverrideTable
    form = ACILeafInterfaceOverrideBulkEditForm


@register_model_view(
    ACILeafInterfaceOverride, "bulk_delete", path="delete", detail=False
)
class ACILeafInterfaceOverrideBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI Leaf Override."""

    queryset = ACILeafInterfaceOverride.objects.all()
    filterset = ACILeafInterfaceOverrideFilterSet
    table = ACILeafInterfaceOverrideTable
