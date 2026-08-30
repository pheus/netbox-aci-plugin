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

from ...filtersets.fabric.vpc_protection_groups import ACIVPCProtectionGroupFilterSet
from ...forms.fabric.vpc_protection_groups import (
    ACIVPCProtectionGroupBulkEditForm,
    ACIVPCProtectionGroupEditForm,
    ACIVPCProtectionGroupFilterForm,
    ACIVPCProtectionGroupImportForm,
)
from ...models.fabric.vpc_protection_groups import ACIVPCProtectionGroup
from ...tables.fabric.vpc_protection_groups import ACIVPCProtectionGroupTable
from ...ui.panels.fabric.vpc_protection_groups import ACIVPCProtectionGroupPanel

#
# VPC Protection Group views
#


@register_model_view(ACIVPCProtectionGroup)
class ACIVPCProtectionGroupView(generic.ObjectView):
    """Detail view for displaying a single object of VPC Protection Group."""

    # Shallower than the API queryset, which nests two Node serializers
    # that each render the Pod and Fabric.
    queryset = ACIVPCProtectionGroup.objects.select_related(
        "aci_fabric",
        "aci_node_a",
        "aci_node_a__aci_pod",
        "aci_node_b",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    template_name = "generic/object.html"
    layout = layout.SimpleLayout(
        breadcrumbs=[
            Breadcrumb(
                "aci_fabric",
                url=filtered_list_url(
                    "plugins:netbox_aci_plugin:acivpcprotectiongroup_list",
                    "aci_fabric_id",
                ),
            ),
        ],
        left_panels=[
            ACIVPCProtectionGroupPanel(),
            CustomFieldsPanel(),
        ],
        right_panels=[
            TagsPanel(),
            CommentsPanel(),
        ],
    )


@register_model_view(ACIVPCProtectionGroup, "list", path="", detail=False)
class ACIVPCProtectionGroupListView(generic.ObjectListView):
    """List view for listing all objects of ACI VPC Protection Group."""

    queryset = ACIVPCProtectionGroup.objects.select_related(
        "aci_fabric",
        "aci_node_a",
        "aci_node_a__aci_pod",
        "aci_node_b",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    filterset = ACIVPCProtectionGroupFilterSet
    filterset_form = ACIVPCProtectionGroupFilterForm
    table = ACIVPCProtectionGroupTable


@register_model_view(ACIVPCProtectionGroup, "add", detail=False)
@register_model_view(ACIVPCProtectionGroup, "edit")
class ACIVPCProtectionGroupEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI VPC Protection Group."""

    queryset = ACIVPCProtectionGroup.objects.select_related(
        "aci_fabric",
        "aci_node_a",
        "aci_node_a__aci_pod",
        "aci_node_b",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    form = ACIVPCProtectionGroupEditForm


@register_model_view(ACIVPCProtectionGroup, "delete")
class ACIVPCProtectionGroupDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI VPC Protection Group."""

    queryset = ACIVPCProtectionGroup.objects.select_related(
        "aci_fabric",
        "aci_node_a",
        "aci_node_a__aci_pod",
        "aci_node_b",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )


@register_model_view(ACIVPCProtectionGroup, "bulk_import", path="import", detail=False)
class ACIVPCProtectionGroupBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple VPC Protection Group objects."""

    queryset = ACIVPCProtectionGroup.objects.all()
    model_form = ACIVPCProtectionGroupImportForm


@register_model_view(ACIVPCProtectionGroup, "bulk_edit", path="edit", detail=False)
class ACIVPCProtectionGroupBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple ACI VPC Protection Group objects."""

    queryset = ACIVPCProtectionGroup.objects.all()
    filterset = ACIVPCProtectionGroupFilterSet
    table = ACIVPCProtectionGroupTable
    form = ACIVPCProtectionGroupBulkEditForm


@register_model_view(ACIVPCProtectionGroup, "bulk_delete", path="delete", detail=False)
class ACIVPCProtectionGroupBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple VPC Protection Group objects."""

    queryset = ACIVPCProtectionGroup.objects.all()
    filterset = ACIVPCProtectionGroupFilterSet
    table = ACIVPCProtectionGroupTable
