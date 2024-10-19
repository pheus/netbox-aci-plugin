# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.views import generic
from utilities.views import register_model_view

from ..filtersets.tenant_contract_filters import ACIContractFilterFilterSet
from ..forms.tenant_contract_filters import (
    ACIContractFilterBulkEditForm,
    ACIContractFilterFilterForm,
    ACIContractFilterForm,
    ACIContractFilterImportForm,
)
from ..models.tenant_contract_filters import ACIContractFilter
from ..tables.tenant_contract_filters import (
    ACIContractFilterEntryReducedTable,
    ACIContractFilterTable,
)

#
# Contract Filter views
#


@register_model_view(ACIContractFilter)
class ACIContractFilterView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Contract Filter."""

    queryset = ACIContractFilter.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )

    def get_extra_context(self, request, instance) -> dict:
        """Return related Contract Filter Entries as extra context."""
        contract_filter_entries_table = ACIContractFilterEntryReducedTable(
            instance.aci_contract_filter_entries.all()
        )
        contract_filter_entries_table.configure(request=request)

        return {
            "contract_filter_entries_table": contract_filter_entries_table,
        }


class ACIContractFilterListView(generic.ObjectListView):
    """List view for listing all objects of ACI Contract Filter."""

    queryset = ACIContractFilter.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )
    filterset = ACIContractFilterFilterSet
    filterset_form = ACIContractFilterFilterForm
    table = ACIContractFilterTable


@register_model_view(ACIContractFilter, "edit")
class ACIContractFilterEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Contract Filter."""

    queryset = ACIContractFilter.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )
    form = ACIContractFilterForm


@register_model_view(ACIContractFilter, "delete")
class ACIContractFilterDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Contract Filter."""

    queryset = ACIContractFilter.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )


class ACIContractFilterBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACIContractFilter."""

    queryset = ACIContractFilter.objects.all()
    model_form = ACIContractFilterImportForm


class ACIContractFilterBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACIContractFilter."""

    queryset = ACIContractFilter.objects.all()
    filterset = ACIContractFilterFilterSet
    table = ACIContractFilterTable
    form = ACIContractFilterBulkEditForm


class ACIContractFilterBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACIContractFilter."""

    queryset = ACIContractFilter.objects.all()
    filterset = ACIContractFilterFilterSet
    table = ACIContractFilterTable
