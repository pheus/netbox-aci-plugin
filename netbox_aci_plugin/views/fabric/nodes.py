# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets.fabric.nodes import ACINodeFilterSet
from ...forms.fabric.nodes import (
    ACINodeBulkEditForm,
    ACINodeEditForm,
    ACINodeFilterForm,
    ACINodeImportForm,
)
from ...models.fabric.nodes import ACINode
from ...tables.fabric.nodes import ACINodeTable

#
# Base children views
#


class ACINodeChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Node."""

    child_model = ACINode
    filterset = ACINodeFilterSet
    tab = ViewTab(
        label=_("Nodes"),
        badge=lambda obj: obj.aci_nodes.count(),
        permission="netbox_aci_plugin.view_acinode",
        weight=1000,
    )
    table = ACINodeTable

    def get_children(self, request, parent):
        """Return all objects of ACINode."""
        return (
            ACINode.objects.restrict(request.user, "view")
            .select_related(
                "aci_pod",
                "node_object_type",
                "tep_ip_address",
                "nb_tenant",
                "owner",
            )
            .prefetch_related(
                "node_object",
                "tags",
            )
        )


#
# Node views
#


@register_model_view(ACINode)
class ACINodeView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Node."""

    queryset = ACINode.objects.select_related(
        "aci_pod", "node_object_type", "tep_ip_address", "nb_tenant", "owner"
    ).prefetch_related("node_object", "tags")


@register_model_view(ACINode, "list", path="", detail=False)
class ACINodeListView(generic.ObjectListView):
    """List view for listing all objects of ACI Node."""

    queryset = ACINode.objects.select_related(
        "aci_pod", "node_object_type", "tep_ip_address", "nb_tenant", "owner"
    ).prefetch_related("node_object", "tags")
    filterset = ACINodeFilterSet
    filterset_form = ACINodeFilterForm
    table = ACINodeTable


@register_model_view(ACINode, "add", detail=False)
@register_model_view(ACINode, "edit")
class ACINodeEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Node."""

    queryset = ACINode.objects.select_related(
        "aci_pod", "node_object_type", "tep_ip_address", "nb_tenant", "owner"
    ).prefetch_related("node_object", "tags")
    form = ACINodeEditForm


@register_model_view(ACINode, "delete")
class ACINodeDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Node."""

    queryset = ACINode.objects.select_related(
        "aci_pod", "node_object_type", "tep_ip_address", "nb_tenant", "owner"
    ).prefetch_related("node_object", "tags")


@register_model_view(ACINode, "bulk_import", path="import", detail=False)
class ACINodeBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI Node."""

    queryset = ACINode.objects.all()
    model_form = ACINodeImportForm


@register_model_view(ACINode, "bulk_edit", path="edit", detail=False)
class ACINodeBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI Node."""

    queryset = ACINode.objects.all()
    filterset = ACINodeFilterSet
    table = ACINodeTable
    form = ACINodeBulkEditForm


@register_model_view(ACINode, "bulk_delete", path="delete", detail=False)
class ACINodeBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI Node."""

    queryset = ACINode.objects.all()
    filterset = ACINodeFilterSet
    table = ACINodeTable
