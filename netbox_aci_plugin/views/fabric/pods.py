# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import GetRelatedModelsMixin, ViewTab, register_model_view

from ...filtersets.fabric.pods import ACIPodFilterSet
from ...forms.fabric.pods import (
    ACIPodBulkEditForm,
    ACIPodEditForm,
    ACIPodFilterForm,
    ACIPodImportForm,
)
from ...models.fabric.pods import ACIPod
from ...tables.fabric.pods import ACIPodTable
from ..fabric.nodes import ACINodeChildrenView

#
# Base children views
#


class ACIPodChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Pod."""

    child_model = ACIPod
    filterset = ACIPodFilterSet
    tab = ViewTab(
        label=_("Pods"),
        badge=lambda obj: obj.aci_pods.count(),
        permission="netbox_aci_plugin.view_acipod",
        weight=1000,
    )
    table = ACIPodTable

    def get_children(self, request, parent):
        """Return all objects of ACIPod."""
        return (
            ACIPod.objects.restrict(request.user, "view")
            .select_related(
                "aci_fabric",
                "tep_pool",
                "nb_tenant",
                "owner",
            )
            .prefetch_related(
                "tags",
            )
        )


#
# Pod views
#


@register_model_view(ACIPod)
class ACIPodView(GetRelatedModelsMixin, generic.ObjectView):
    """Detail view for displaying a single object of ACI Pod."""

    queryset = ACIPod.objects.select_related(
        "aci_fabric", "tep_pool", "nb_tenant", "owner"
    ).prefetch_related("tags")

    def get_extra_context(self, request, instance) -> dict:
        """Return related models as extra context."""
        return {"related_models": self.get_related_models(request, instance)}


@register_model_view(ACIPod, "list", path="", detail=False)
class ACIPodListView(generic.ObjectListView):
    """List view for listing all objects of ACI Pod."""

    queryset = ACIPod.objects.select_related(
        "aci_fabric", "tep_pool", "nb_tenant", "owner"
    ).prefetch_related("tags")
    filterset = ACIPodFilterSet
    filterset_form = ACIPodFilterForm
    table = ACIPodTable


@register_model_view(ACIPod, "add", detail=False)
@register_model_view(ACIPod, "edit")
class ACIPodEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Pod."""

    queryset = ACIPod.objects.select_related(
        "aci_fabric", "tep_pool", "nb_tenant", "owner"
    ).prefetch_related("tags")
    form = ACIPodEditForm


@register_model_view(ACIPod, "delete")
class ACIPodDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Pod."""

    queryset = ACIPod.objects.select_related(
        "aci_fabric", "tep_pool", "nb_tenant", "owner"
    ).prefetch_related("tags")


@register_model_view(ACIPod, "nodes", path="nodes")
class ACIPodNodeView(ACINodeChildrenView):
    """Children view of ACI Pod of ACI Pod."""

    queryset = ACIPod.objects.all()
    template_name = "netbox_aci_plugin/inc/acipod/nodes.html"

    def get_children(self, request, parent):
        """Return all ACINode objects for the current ACIPod."""
        return super().get_children(request, parent).filter(aci_pod_id=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with ACIPod colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACIPod column
        table.columns.hide("aci_pod")

        return table


@register_model_view(ACIPod, "bulk_import", path="import", detail=False)
class ACIPodBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI Pod."""

    queryset = ACIPod.objects.all()
    model_form = ACIPodImportForm


@register_model_view(ACIPod, "bulk_edit", path="edit", detail=False)
class ACIPodBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI Pod."""

    queryset = ACIPod.objects.all()
    filterset = ACIPodFilterSet
    table = ACIPodTable
    form = ACIPodBulkEditForm


@register_model_view(ACIPod, "bulk_delete", path="delete", detail=False)
class ACIPodBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI Pod."""

    queryset = ACIPod.objects.all()
    filterset = ACIPodFilterSet
    table = ACIPodTable
