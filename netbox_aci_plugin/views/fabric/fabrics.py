# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.views import generic
from utilities.views import GetRelatedModelsMixin, register_model_view

from ...filtersets.fabric.fabrics import ACIFabricFilterSet
from ...forms.fabric.fabrics import (
    ACIFabricBulkEditForm,
    ACIFabricEditForm,
    ACIFabricFilterForm,
    ACIFabricImportForm,
)
from ...models.fabric.fabrics import ACIFabric
from ...tables.fabric.fabrics import ACIFabricTable

#
# Fabric views
#


@register_model_view(ACIFabric)
class ACIFabricView(GetRelatedModelsMixin, generic.ObjectView):
    """Detail view for displaying a single object of ACI Fabric."""

    queryset = ACIFabric.objects.select_related("nb_tenant").prefetch_related("tags")


@register_model_view(ACIFabric, "list", path="", detail=False)
class ACIFabricListView(generic.ObjectListView):
    """List view for listing all objects of ACI Fabric."""

    queryset = ACIFabric.objects.select_related("nb_tenant").prefetch_related("tags")
    filterset = ACIFabricFilterSet
    filterset_form = ACIFabricFilterForm
    table = ACIFabricTable


@register_model_view(ACIFabric, "add", detail=False)
@register_model_view(ACIFabric, "edit")
class ACIFabricEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Fabric."""

    queryset = ACIFabric.objects.select_related("nb_tenant").prefetch_related("tags")
    form = ACIFabricEditForm


@register_model_view(ACIFabric, "delete")
class ACIFabricDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Fabric."""

    queryset = ACIFabric.objects.select_related("nb_tenant").prefetch_related("tags")


@register_model_view(ACIFabric, "bulk_import", path="import", detail=False)
class ACIFabricBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI Fabric."""

    queryset = ACIFabric.objects.all()
    model_form = ACIFabricImportForm


@register_model_view(ACIFabric, "bulk_edit", path="edit", detail=False)
class ACIFabricBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI Fabric."""

    queryset = ACIFabric.objects.all()
    filterset = ACIFabricFilterSet
    table = ACIFabricTable
    form = ACIFabricBulkEditForm


@register_model_view(ACIFabric, "bulk_delete", path="delete", detail=False)
class ACIFabricBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI Fabric."""

    queryset = ACIFabric.objects.all()
    filterset = ACIFabricFilterSet
    table = ACIFabricTable
