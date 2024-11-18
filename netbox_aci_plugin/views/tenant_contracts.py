# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ..filtersets.tenant_contracts import ACIContractFilterSet
from ..forms.tenant_contracts import (
    ACIContractBulkEditForm,
    ACIContractEditForm,
    ACIContractFilterForm,
    ACIContractImportForm,
)
from ..models.tenant_contracts import ACIContract
from ..tables.tenant_contracts import ACIContractTable

#
# Base children views
#


class ACIContractChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Contract."""

    child_model = ACIContract
    filterset = ACIContractFilterSet
    tab = ViewTab(
        label=_("Contracts"),
        badge=lambda obj: obj.aci_contracts.count(),
        permission="netbox_aci_plugin.view_acicontract",
        weight=1000,
    )
    table = ACIContractTable

    def get_children(self, request, parent):
        """Return all objects of ACIContract."""
        return ACIContract.objects.restrict(
            request.user, "view"
        ).prefetch_related(
            "aci_tenant",
            "nb_tenant",
            "tags",
        )


#
# Contract views
#


@register_model_view(ACIContract)
class ACIContractView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Contract."""

    queryset = ACIContract.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )


class ACIContractListView(generic.ObjectListView):
    """List view for listing all objects of ACI Contract."""

    queryset = ACIContract.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )
    filterset = ACIContractFilterSet
    filterset_form = ACIContractFilterForm
    table = ACIContractTable


@register_model_view(ACIContract, "edit")
class ACIContractEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Contract."""

    queryset = ACIContract.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )
    form = ACIContractEditForm


@register_model_view(ACIContract, "delete")
class ACIContractDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Contract."""

    queryset = ACIContract.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )


class ACIContractBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACIContract."""

    queryset = ACIContract.objects.all()
    model_form = ACIContractImportForm


class ACIContractBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACIContract."""

    queryset = ACIContract.objects.all()
    filterset = ACIContractFilterSet
    table = ACIContractTable
    form = ACIContractBulkEditForm


class ACIContractBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACIContract."""

    queryset = ACIContract.objects.all()
    filterset = ACIContractFilterSet
    table = ACIContractTable
