# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets.access_policies.domains import (
    ACIPhysicalDomainFilterSet,
    ACIRoutedDomainFilterSet,
)
from ...forms.access_policies.domains import (
    ACIPhysicalDomainBulkEditForm,
    ACIPhysicalDomainEditForm,
    ACIPhysicalDomainFilterForm,
    ACIPhysicalDomainImportForm,
    ACIRoutedDomainBulkEditForm,
    ACIRoutedDomainEditForm,
    ACIRoutedDomainFilterForm,
    ACIRoutedDomainImportForm,
)
from ...models.access_policies.domains import ACIPhysicalDomain, ACIRoutedDomain
from ...models.fabric.fabrics import ACIFabric
from ...object_actions import add_child_action
from ...tables.access_policies.domains import (
    ACIPhysicalDomainTable,
    ACIRoutedDomainTable,
)

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
                "aci_vlan_pool",
            )
            .prefetch_related("tags")
        )


class ACIPhysicalDomainChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Physical Domains."""

    child_model = ACIPhysicalDomain
    filterset = ACIPhysicalDomainFilterSet
    tab = ViewTab(
        label=_("Physical Domains"),
        badge=lambda obj: obj.aci_physical_domains.count(),
        permission="netbox_aci_plugin.view_aciphysicaldomain",
        weight=2200,
    )
    table = ACIPhysicalDomainTable

    def get_children(self, request, parent):
        """Return all ACIPhysicalDomain objects."""
        return (
            ACIPhysicalDomain.objects.restrict(request.user, "view")
            .select_related(
                "aci_fabric",
                "nb_tenant",
                "owner",
                "aci_vlan_pool",
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
        "aci_vlan_pool",
    ).prefetch_related("tags")


@register_model_view(ACIRoutedDomain, "list", path="", detail=False)
class ACIRoutedDomainListView(generic.ObjectListView):
    """List view for listing all objects of ACI Routed Domain."""

    queryset = ACIRoutedDomain.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
        "aci_vlan_pool",
    ).prefetch_related("tags")
    filterset = ACIRoutedDomainFilterSet
    filterset_form = ACIRoutedDomainFilterForm
    table = ACIRoutedDomainTable


@register_model_view(ACIRoutedDomain, "add", detail=False)
@register_model_view(ACIRoutedDomain, "edit")
class ACIRoutedDomainEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Routed Domain."""

    queryset = ACIRoutedDomain.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
        "aci_vlan_pool",
    ).prefetch_related("tags")
    form = ACIRoutedDomainEditForm


@register_model_view(ACIRoutedDomain, "delete")
class ACIRoutedDomainDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Routed Domain."""

    queryset = ACIRoutedDomain.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
        "aci_vlan_pool",
    ).prefetch_related("tags")


@register_model_view(ACIFabric, "routed_domains", path="routed-domains")
class ACIFabricRoutedDomainView(ACIRoutedDomainChildrenView):
    """Children view of ACI Routed Domains of an ACI Fabric."""

    queryset = ACIFabric.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACIRoutedDomain",
            _("Add a Domain"),
            url_params={
                "aci_fabric": lambda ctx: ctx["object"].pk,
                "nb_tenant": lambda ctx: ctx["object"].nb_tenant_id,
            },
        ),
    ) + ACIRoutedDomainChildrenView.actions

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


#
# Physical Domain views
#


@register_model_view(ACIPhysicalDomain)
class ACIPhysicalDomainView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Physical Domain."""

    queryset = ACIPhysicalDomain.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
        "aci_vlan_pool",
    ).prefetch_related("tags")


@register_model_view(ACIPhysicalDomain, "list", path="", detail=False)
class ACIPhysicalDomainListView(generic.ObjectListView):
    """List view for listing all objects of ACI Physical Domain."""

    queryset = ACIPhysicalDomain.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
        "aci_vlan_pool",
    ).prefetch_related("tags")
    filterset = ACIPhysicalDomainFilterSet
    filterset_form = ACIPhysicalDomainFilterForm
    table = ACIPhysicalDomainTable


@register_model_view(ACIPhysicalDomain, "add", detail=False)
@register_model_view(ACIPhysicalDomain, "edit")
class ACIPhysicalDomainEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Physical Domain."""

    queryset = ACIPhysicalDomain.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
        "aci_vlan_pool",
    ).prefetch_related("tags")
    form = ACIPhysicalDomainEditForm


@register_model_view(ACIPhysicalDomain, "delete")
class ACIPhysicalDomainDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Physical Domain."""

    queryset = ACIPhysicalDomain.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
        "aci_vlan_pool",
    ).prefetch_related("tags")


@register_model_view(ACIFabric, "physical_domains", path="physical-domains")
class ACIFabricPhysicalDomainView(ACIPhysicalDomainChildrenView):
    """Children view of ACI Physical Domains of an ACI Fabric."""

    queryset = ACIFabric.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACIPhysicalDomain",
            _("Add a Domain"),
            url_params={
                "aci_fabric": lambda ctx: ctx["object"].pk,
                "nb_tenant": lambda ctx: ctx["object"].nb_tenant_id,
            },
        ),
    ) + ACIPhysicalDomainChildrenView.actions

    def get_children(self, request, parent):
        """Return all ACIPhysicalDomain objects for the current ACIFabric."""
        return super().get_children(request, parent).filter(aci_fabric_id=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with ACIFabric column hidden."""
        table = super().get_table(*args, **kwargs)
        table.columns.hide("aci_fabric")
        return table


@register_model_view(ACIPhysicalDomain, "bulk_import", path="import", detail=False)
class ACIPhysicalDomainBulkImportView(generic.BulkImportView):
    """Bulk import view for importing ACI Physical Domain objects."""

    queryset = ACIPhysicalDomain.objects.all()
    model_form = ACIPhysicalDomainImportForm


@register_model_view(ACIPhysicalDomain, "bulk_edit", path="edit", detail=False)
class ACIPhysicalDomainBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI Physical Domain."""

    queryset = ACIPhysicalDomain.objects.all()
    filterset = ACIPhysicalDomainFilterSet
    table = ACIPhysicalDomainTable
    form = ACIPhysicalDomainBulkEditForm


@register_model_view(ACIPhysicalDomain, "bulk_delete", path="delete", detail=False)
class ACIPhysicalDomainBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting ACI Physical Domain objects."""

    queryset = ACIPhysicalDomain.objects.all()
    filterset = ACIPhysicalDomainFilterSet
    table = ACIPhysicalDomainTable
