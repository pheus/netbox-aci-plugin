# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets.access_policies.domains import ACIRoutedDomainFilterSet
from ...forms.access_policies.domains import (
    ACIRoutedDomainBulkEditForm,
    ACIRoutedDomainEditForm,
    ACIRoutedDomainFilterForm,
    ACIRoutedDomainImportForm,
)
from ...models.access_policies.domains import ACIRoutedDomain
from ...models.fabric.fabrics import ACIFabric
from ...tables.access_policies.domains import ACIRoutedDomainTable

#
# Base children views
#


class ACIRoutedDomainChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Routed Domains."""

    child_model = ACIRoutedDomain
    filterset = ACIRoutedDomainFilterSet
    tab = ViewTab(
        label=_("Routed Domains"),
        badge=lambda obj: obj.aci_routed_domains.count(),
        permission="netbox_aci_plugin.view_acirouteddomain",
        weight=2000,
    )
    table = ACIRoutedDomainTable

    def get_children(self, request, parent):
        """Return all ACIRoutedDomain objects."""
        return (
            ACIRoutedDomain.objects.restrict(request.user, "view")
            .select_related(
                "aci_fabric",
                "nb_tenant",
                "owner",
            )
            .prefetch_related("tags")
        )


#
# Routed Domain views
#


@register_model_view(ACIRoutedDomain)
class ACIRoutedDomainView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Routed Domain."""

    queryset = ACIRoutedDomain.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")


@register_model_view(ACIRoutedDomain, "list", path="", detail=False)
class ACIRoutedDomainListView(generic.ObjectListView):
    """List view for listing all objects of ACI Routed Domain."""

    queryset = ACIRoutedDomain.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    table = ACIRoutedDomainTable
    filterset = ACIRoutedDomainFilterSet
    filterset_form = ACIRoutedDomainFilterForm


@register_model_view(ACIRoutedDomain, "add", detail=False)
@register_model_view(ACIRoutedDomain, "edit")
class ACIRoutedDomainEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Routed Domain."""

    queryset = ACIRoutedDomain.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    form = ACIRoutedDomainEditForm


@register_model_view(ACIRoutedDomain, "delete")
class ACIRoutedDomainDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Routed Domain."""

    queryset = ACIRoutedDomain.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")


@register_model_view(ACIFabric, "routed_domains", path="routed-domains")
class ACIFabricRoutedDomainView(ACIRoutedDomainChildrenView):
    """Children view of ACI Routed Domains of an ACI Fabric."""

    queryset = ACIFabric.objects.all()
    template_name = "netbox_aci_plugin/inc/acifabric/routed_domains.html"

    def get_children(self, request, parent):
        """Return all ACIRoutedDomain objects for the current ACIFabric."""
        return super().get_children(request, parent).filter(aci_fabric_id=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with ACIFabric column hidden."""
        table = super().get_table(*args, **kwargs)
        table.columns.hide("aci_fabric")
        return table


@register_model_view(ACIRoutedDomain, "bulk_import", path="import", detail=False)
class ACIRoutedDomainBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI Routed Domain."""

    queryset = ACIRoutedDomain.objects.all()
    model_form = ACIRoutedDomainImportForm


@register_model_view(ACIRoutedDomain, "bulk_edit", path="edit", detail=False)
class ACIRoutedDomainBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI Routed Domain."""

    queryset = ACIRoutedDomain.objects.all()
    filterset = ACIRoutedDomainFilterSet
    table = ACIRoutedDomainTable
    form = ACIRoutedDomainBulkEditForm


@register_model_view(ACIRoutedDomain, "bulk_delete", path="delete", detail=False)
class ACIRoutedDomainBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI Routed Domain."""

    queryset = ACIRoutedDomain.objects.all()
    filterset = ACIRoutedDomainFilterSet
    table = ACIRoutedDomainTable
