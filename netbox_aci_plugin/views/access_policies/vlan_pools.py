# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets.access_policies.vlan_pools import (
    ACIVLANPoolFilterSet,
    ACIVLANPoolRangeFilterSet,
)
from ...forms.access_policies.vlan_pools import (
    ACIVLANPoolBulkEditForm,
    ACIVLANPoolEditForm,
    ACIVLANPoolFilterForm,
    ACIVLANPoolImportForm,
    ACIVLANPoolRangeBulkEditForm,
    ACIVLANPoolRangeEditForm,
    ACIVLANPoolRangeFilterForm,
    ACIVLANPoolRangeImportForm,
)
from ...models.access_policies.vlan_pools import ACIVLANPool, ACIVLANPoolRange
from ...models.fabric.fabrics import ACIFabric
from ...object_actions import add_child_action
from ...tables.access_policies.vlan_pools import (
    ACIVLANPoolRangeTable,
    ACIVLANPoolTable,
)

#
# Base children views
#


class ACIVLANPoolChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI VLAN Pools."""

    child_model = ACIVLANPool
    filterset = ACIVLANPoolFilterSet
    tab = ViewTab(
        label=_("VLAN Pools"),
        badge=lambda obj: obj.aci_vlan_pools.count(),
        permission="netbox_aci_plugin.view_acivlanpool",
        weight=2100,
    )
    table = ACIVLANPoolTable

    def get_children(self, request, parent):
        """Return all ACIVLANPool objects."""
        return (
            ACIVLANPool.objects.restrict(request.user, "view")
            .select_related("aci_fabric", "nb_tenant", "nb_vlan_group", "owner")
            .prefetch_related("tags")
        )


class ACIVLANPoolRangeChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI VLAN Pool Ranges."""

    child_model = ACIVLANPoolRange
    filterset = ACIVLANPoolRangeFilterSet
    tab = ViewTab(
        label=_("Ranges"),
        badge=lambda obj: obj.aci_vlan_pool_ranges.count(),
        permission="netbox_aci_plugin.view_acivlanpoolrange",
        weight=1000,
    )
    table = ACIVLANPoolRangeTable

    def get_children(self, request, parent):
        """Return all ACIVLANPoolRange objects."""
        return (
            ACIVLANPoolRange.objects.restrict(request.user, "view")
            .select_related("aci_vlan_pool", "aci_vlan_pool__aci_fabric")
            .prefetch_related("tags")
        )


#
# VLAN Pool views
#


@register_model_view(ACIVLANPool)
class ACIVLANPoolView(generic.ObjectView):
    """Detail view for displaying a single object of ACI VLAN Pool."""

    queryset = ACIVLANPool.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "nb_vlan_group",
        "owner",
    ).prefetch_related("tags")


@register_model_view(ACIVLANPool, "list", path="", detail=False)
class ACIVLANPoolListView(generic.ObjectListView):
    """List view for listing all objects of ACI VLAN Pool."""

    queryset = ACIVLANPool.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "nb_vlan_group",
        "owner",
    ).prefetch_related("tags")
    filterset = ACIVLANPoolFilterSet
    filterset_form = ACIVLANPoolFilterForm
    table = ACIVLANPoolTable


@register_model_view(ACIVLANPool, "add", detail=False)
@register_model_view(ACIVLANPool, "edit")
class ACIVLANPoolEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI VLAN Pool."""

    queryset = ACIVLANPool.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "nb_vlan_group",
        "owner",
    ).prefetch_related("tags")
    form = ACIVLANPoolEditForm


@register_model_view(ACIVLANPool, "delete")
class ACIVLANPoolDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI VLAN Pool."""

    queryset = ACIVLANPool.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "nb_vlan_group",
        "owner",
    ).prefetch_related("tags")


@register_model_view(ACIFabric, "vlan_pools", path="vlan-pools")
class ACIFabricVLANPoolView(ACIVLANPoolChildrenView):
    """Children view of ACI VLAN Pools of an ACI Fabric."""

    queryset = ACIFabric.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACIVLANPool",
            _("Add a VLAN Pool"),
            url_params={
                "aci_fabric": lambda ctx: ctx["object"].pk,
                "nb_tenant": lambda ctx: ctx["object"].nb_tenant_id,
            },
        ),
    ) + ACIVLANPoolChildrenView.actions

    def get_children(self, request, parent):
        """Return all ACIVLANPool objects for the current ACIFabric."""
        return super().get_children(request, parent).filter(aci_fabric_id=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with ACIFabric column hidden."""
        table = super().get_table(*args, **kwargs)
        table.columns.hide("aci_fabric")
        return table


@register_model_view(ACIVLANPool, "bulk_import", path="import", detail=False)
class ACIVLANPoolBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI VLAN Pool."""

    queryset = ACIVLANPool.objects.all()
    model_form = ACIVLANPoolImportForm


@register_model_view(ACIVLANPool, "bulk_edit", path="edit", detail=False)
class ACIVLANPoolBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI VLAN Pool."""

    queryset = ACIVLANPool.objects.all()
    filterset = ACIVLANPoolFilterSet
    table = ACIVLANPoolTable
    form = ACIVLANPoolBulkEditForm


@register_model_view(ACIVLANPool, "bulk_delete", path="delete", detail=False)
class ACIVLANPoolBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI VLAN Pool."""

    queryset = ACIVLANPool.objects.all()
    filterset = ACIVLANPoolFilterSet
    table = ACIVLANPoolTable


#
# VLAN Pool Range views
#


@register_model_view(ACIVLANPoolRange)
class ACIVLANPoolRangeView(generic.ObjectView):
    """Detail view for displaying a single object of ACI VLAN Pool Range."""

    queryset = ACIVLANPoolRange.objects.select_related(
        "aci_vlan_pool",
        "aci_vlan_pool__aci_fabric",
    ).prefetch_related("tags")


@register_model_view(ACIVLANPoolRange, "list", path="", detail=False)
class ACIVLANPoolRangeListView(generic.ObjectListView):
    """List view for listing all objects of ACI VLAN Pool Range."""

    queryset = ACIVLANPoolRange.objects.select_related(
        "aci_vlan_pool",
        "aci_vlan_pool__aci_fabric",
    ).prefetch_related("tags")
    filterset = ACIVLANPoolRangeFilterSet
    filterset_form = ACIVLANPoolRangeFilterForm
    table = ACIVLANPoolRangeTable


@register_model_view(ACIVLANPoolRange, "add", detail=False)
@register_model_view(ACIVLANPoolRange, "edit")
class ACIVLANPoolRangeEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI VLAN Pool Range."""

    queryset = ACIVLANPoolRange.objects.select_related(
        "aci_vlan_pool",
        "aci_vlan_pool__aci_fabric",
    ).prefetch_related("tags")
    form = ACIVLANPoolRangeEditForm


@register_model_view(ACIVLANPoolRange, "delete")
class ACIVLANPoolRangeDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI VLAN Pool Range."""

    queryset = ACIVLANPoolRange.objects.select_related(
        "aci_vlan_pool",
        "aci_vlan_pool__aci_fabric",
    ).prefetch_related("tags")


@register_model_view(ACIVLANPool, "vlanpoolranges", path="ranges")
class ACIVLANPoolVLANPoolRangeView(ACIVLANPoolRangeChildrenView):
    """Children view of ACI VLAN Pool Ranges of an ACI VLAN Pool."""

    queryset = ACIVLANPool.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACIVLANPoolRange",
            _("Add a VLAN Range"),
            url_params={
                "aci_fabric": lambda ctx: ctx["object"].aci_fabric_id,
                "aci_vlan_pool": lambda ctx: ctx["object"].pk,
            },
        ),
    ) + ACIVLANPoolRangeChildrenView.actions

    def get_children(self, request, parent):
        """Return all ACIVLANPoolRange objects for the current ACIVLANPool."""
        return super().get_children(request, parent).filter(aci_vlan_pool_id=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with ACIVLANPool column hidden."""
        table = super().get_table(*args, **kwargs)
        table.columns.hide("aci_vlan_pool")
        return table


@register_model_view(ACIVLANPoolRange, "bulk_import", path="import", detail=False)
class ACIVLANPoolRangeBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple ACI VLAN Pool Ranges."""

    queryset = ACIVLANPoolRange.objects.all()
    model_form = ACIVLANPoolRangeImportForm


@register_model_view(ACIVLANPoolRange, "bulk_edit", path="edit", detail=False)
class ACIVLANPoolRangeBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple ACI VLAN Pool Ranges."""

    queryset = ACIVLANPoolRange.objects.all()
    filterset = ACIVLANPoolRangeFilterSet
    table = ACIVLANPoolRangeTable
    form = ACIVLANPoolRangeBulkEditForm


@register_model_view(ACIVLANPoolRange, "bulk_delete", path="delete", detail=False)
class ACIVLANPoolRangeBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple ACI VLAN Pool Ranges."""

    queryset = ACIVLANPoolRange.objects.all()
    filterset = ACIVLANPoolRangeFilterSet
    table = ACIVLANPoolRangeTable
