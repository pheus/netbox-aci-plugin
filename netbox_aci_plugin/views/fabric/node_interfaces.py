# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...choices import NodeRoleChoices
from ...filtersets.fabric.node_interfaces import ACINodeInterfaceFilterSet
from ...forms.fabric.node_interfaces import (
    ACINodeInterfaceBulkEditForm,
    ACINodeInterfaceEditForm,
    ACINodeInterfaceFilterForm,
    ACINodeInterfaceImportForm,
)
from ...models.fabric.node_interfaces import ACINodeInterface
from ...tables.fabric.node_interfaces import ACINodeInterfaceTable

#
# Base children views
#


class ACINodeInterfaceChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Node Interface."""

    child_model = ACINodeInterface
    filterset = ACINodeInterfaceFilterSet
    tab = ViewTab(
        label=_("Node Interfaces"),
        badge=lambda obj: obj.aci_node_interfaces.count(),
        permission="netbox_aci_plugin.view_acinodeinterface",
        visible=lambda obj: obj.role == NodeRoleChoices.ROLE_LEAF,
        weight=1000,
    )
    table = ACINodeInterfaceTable

    def get_children(self, request, parent):
        """Return all objects of ACINodeInterface."""
        return (
            ACINodeInterface.objects.restrict(request.user, "view")
            .select_related(
                "aci_node",
                "aci_node__aci_pod",
                "aci_node__aci_pod__aci_fabric",
                "aci_node___aci_fabric",
                "nb_interface",
                "nb_tenant",
                "owner",
            )
            .prefetch_related(
                "tags",
            )
        )


#
# Node Interface views
#


@register_model_view(ACINodeInterface)
class ACINodeInterfaceView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Node Interface."""

    queryset = ACINodeInterface.objects.select_related(
        "aci_node",
        "aci_node__aci_pod",
        "aci_node__aci_pod__aci_fabric",
        "aci_node___aci_fabric",
        "nb_interface",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )


@register_model_view(ACINodeInterface, "list", path="", detail=False)
class ACINodeInterfaceListView(generic.ObjectListView):
    """List view for listing all objects of ACI Node Interface."""

    queryset = ACINodeInterface.objects.select_related(
        "aci_node",
        "aci_node__aci_pod",
        "aci_node__aci_pod__aci_fabric",
        "aci_node___aci_fabric",
        "nb_interface",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    filterset = ACINodeInterfaceFilterSet
    filterset_form = ACINodeInterfaceFilterForm
    table = ACINodeInterfaceTable


@register_model_view(ACINodeInterface, "add", detail=False)
@register_model_view(ACINodeInterface, "edit")
class ACINodeInterfaceEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Node Interface."""

    queryset = ACINodeInterface.objects.select_related(
        "aci_node",
        "aci_node__aci_pod",
        "aci_node__aci_pod__aci_fabric",
        "aci_node___aci_fabric",
        "nb_interface",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    form = ACINodeInterfaceEditForm


@register_model_view(ACINodeInterface, "delete")
class ACINodeInterfaceDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Node Interface."""

    queryset = ACINodeInterface.objects.select_related(
        "aci_node",
        "aci_node__aci_pod",
        "aci_node__aci_pod__aci_fabric",
        "aci_node___aci_fabric",
        "nb_interface",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )


@register_model_view(ACINodeInterface, "bulk_import", path="import", detail=False)
class ACINodeInterfaceBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple ACI Node Interface objects."""

    queryset = ACINodeInterface.objects.all()
    model_form = ACINodeInterfaceImportForm


@register_model_view(ACINodeInterface, "bulk_edit", path="edit", detail=False)
class ACINodeInterfaceBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI Node Interface."""

    queryset = ACINodeInterface.objects.all()
    filterset = ACINodeInterfaceFilterSet
    table = ACINodeInterfaceTable
    form = ACINodeInterfaceBulkEditForm


@register_model_view(ACINodeInterface, "bulk_delete", path="delete", detail=False)
class ACINodeInterfaceBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI Node Interface."""

    queryset = ACINodeInterface.objects.all()
    filterset = ACINodeInterfaceFilterSet
    table = ACINodeInterfaceTable
