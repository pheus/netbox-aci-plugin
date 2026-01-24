# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import GetRelatedModelsMixin, ViewTab, register_model_view

from ...filtersets.fabric.fabrics import ACIFabricFilterSet
from ...forms.fabric.fabrics import (
    ACIFabricBulkEditForm,
    ACIFabricEditForm,
    ACIFabricFilterForm,
    ACIFabricImportForm,
)
from ...models.fabric.fabrics import ACIFabric
from ...models.fabric.nodes import ACINode
from ...tables.fabric.fabrics import ACIFabricTable
from ..fabric.nodes import ACINodeChildrenView
from ..fabric.pods import ACIPodChildrenView
from ..tenant.tenants import ACITenantChildrenView

if TYPE_CHECKING:
    from django.db.models import QuerySet


#
# Fabric views
#


@register_model_view(ACIFabric)
class ACIFabricView(GetRelatedModelsMixin, generic.ObjectView):
    """Detail view for displaying a single object of ACI Fabric."""

    queryset = ACIFabric.objects.select_related("nb_tenant", "owner").prefetch_related(
        "tags"
    )

    def get_extra_context(self, request, instance) -> dict:
        """Return related models as extra context."""
        # Get extra related models of directly referenced models
        extra_related_models: tuple[tuple[QuerySet, str], ...] = (
            (
                ACINode.objects.restrict(request.user, "view").filter(
                    aci_pod__aci_fabric=instance
                ),
                "aci_fabric_id",
            ),
        )

        return {
            "related_models": self.get_related_models(
                request, instance, extra=extra_related_models
            )
        }


@register_model_view(ACIFabric, "list", path="", detail=False)
class ACIFabricListView(generic.ObjectListView):
    """List view for listing all objects of ACI Fabric."""

    queryset = ACIFabric.objects.select_related("nb_tenant", "owner").prefetch_related(
        "tags"
    )
    filterset = ACIFabricFilterSet
    filterset_form = ACIFabricFilterForm
    table = ACIFabricTable


@register_model_view(ACIFabric, "add", detail=False)
@register_model_view(ACIFabric, "edit")
class ACIFabricEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Fabric."""

    queryset = ACIFabric.objects.select_related("nb_tenant", "owner").prefetch_related(
        "tags"
    )
    form = ACIFabricEditForm


@register_model_view(ACIFabric, "delete")
class ACIFabricDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Fabric."""

    queryset = ACIFabric.objects.select_related("nb_tenant", "owner").prefetch_related(
        "tags"
    )


@register_model_view(ACIFabric, "pods", path="pods")
class ACIFabricPodView(ACIPodChildrenView):
    """Children view of ACI Pod of ACI Fabric."""

    queryset = ACIFabric.objects.all()
    template_name = "netbox_aci_plugin/inc/acifabric/pods.html"

    def get_children(self, request, parent):
        """Return all ACIPod objects for the current ACIFabric."""
        return super().get_children(request, parent).filter(aci_fabric_id=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with ACIFabric colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACIFabric column
        table.columns.hide("aci_fabric")

        return table


@register_model_view(ACIFabric, "nodes", path="nodes")
class ACIFabricNodeView(ACINodeChildrenView):
    """Children view of ACI Node of ACI Fabric."""

    queryset = ACIFabric.objects.all()
    tab = ViewTab(
        label=_("Nodes"),
        badge=lambda obj: ACINodeChildrenView.child_model.objects.filter(
            aci_pod__aci_fabric=obj.pk
        ).count(),
        permission="netbox_aci_plugin.view_acinode",
        weight=1000,
    )
    template_name = "netbox_aci_plugin/inc/acifabric/nodes.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super().get_children(request, parent).filter(aci_pod__aci_fabric=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACIFabric colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACIFabric column
        table.columns.hide("aci_fabric")

        return table


@register_model_view(ACIFabric, "tenants", path="tenants")
class ACIFabricTenantView(ACITenantChildrenView):
    """Children view of ACI Tenant of ACI Fabric."""

    queryset = ACIFabric.objects.all()
    template_name = "netbox_aci_plugin/inc/acifabric/tenants.html"

    def get_children(self, request, parent):
        """Return all ACITenant objects for the current ACIFabric."""
        return super().get_children(request, parent).filter(aci_fabric_id=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with ACIFabric colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACIFabric column
        table.columns.hide("aci_fabric")

        return table


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
