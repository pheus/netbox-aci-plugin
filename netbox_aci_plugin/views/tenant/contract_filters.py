# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets.tenant.contract_filters import (
    ACIContractFilterEntryFilterSet,
    ACIContractFilterFilterSet,
)
from ...forms.tenant.contract_filters import (
    ACIContractFilterBulkEditForm,
    ACIContractFilterEditForm,
    ACIContractFilterEntryBulkEditForm,
    ACIContractFilterEntryEditForm,
    ACIContractFilterEntryFilterForm,
    ACIContractFilterEntryImportForm,
    ACIContractFilterFilterForm,
    ACIContractFilterImportForm,
)
from ...models.tenant.contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from ...tables.tenant.contract_filters import (
    ACIContractFilterEntryReducedTable,
    ACIContractFilterEntryTable,
    ACIContractFilterTable,
)

#
# Base children views
#


class ACIContractFilterEntryChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Contract Filter Entry."""

    child_model = ACIContractFilterEntry
    filterset = ACIContractFilterEntryFilterSet
    tab = ViewTab(
        label=_("Filter Entries"),
        badge=lambda obj: obj.aci_contract_filter_entries.count(),
        permission="netbox_aci_plugin.view_acicontractfilterentry",
        weight=1000,
    )
    table = ACIContractFilterEntryTable

    def get_children(self, request, parent):
        """Return all objects of ACIContractFilterEntry."""
        return ACIContractFilterEntry.objects.restrict(
            request.user, "view"
        ).prefetch_related(
            "aci_contract_filter",
            "tags",
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


@register_model_view(ACIContractFilter, "list", path="", detail=False)
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


@register_model_view(ACIContractFilter, "add", detail=False)
@register_model_view(ACIContractFilter, "edit")
class ACIContractFilterEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Contract Filter."""

    queryset = ACIContractFilter.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )
    form = ACIContractFilterEditForm


@register_model_view(ACIContractFilter, "delete")
class ACIContractFilterDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Contract Filter."""

    queryset = ACIContractFilter.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )


@register_model_view(ACIContractFilter, "contractfilterentries", path="entries")
class ACIContractFilterContractFilterEntryView(ACIContractFilterEntryChildrenView):
    """Children view of ACI Contract Filter Entry of ACI Contract Filter."""

    queryset = ACIContractFilter.objects.all()
    template_name = "netbox_aci_plugin/inc/acicontractfilter/entries.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super().get_children(request, parent).filter(aci_contract_filter=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACIContractFilter colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACIContractFilter column
        table.columns.hide("aci_contract_filter")

        return table


@register_model_view(ACIContractFilter, "bulk_import", path="import", detail=False)
class ACIContractFilterBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACIContractFilter."""

    queryset = ACIContractFilter.objects.all()
    model_form = ACIContractFilterImportForm


@register_model_view(ACIContractFilter, "bulk_edit", path="edit", detail=False)
class ACIContractFilterBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACIContractFilter."""

    queryset = ACIContractFilter.objects.all()
    filterset = ACIContractFilterFilterSet
    table = ACIContractFilterTable
    form = ACIContractFilterBulkEditForm


@register_model_view(ACIContractFilter, "bulk_delete", path="delete", detail=False)
class ACIContractFilterBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACIContractFilter."""

    queryset = ACIContractFilter.objects.all()
    filterset = ACIContractFilterFilterSet
    table = ACIContractFilterTable


#
# Contract Filter Entry views
#


@register_model_view(ACIContractFilterEntry)
class ACIContractFilterEntryView(generic.ObjectView):
    """Detail view for displaying a single object of ACIContractFilterEntry."""

    queryset = ACIContractFilterEntry.objects.prefetch_related(
        "aci_contract_filter",
        "tags",
    )


@register_model_view(ACIContractFilterEntry, "list", path="", detail=False)
class ACIContractFilterEntryListView(generic.ObjectListView):
    """List view for listing all objects of ACIContractFilterEntry."""

    queryset = ACIContractFilterEntry.objects.prefetch_related(
        "aci_contract_filter",
        "tags",
    )
    filterset = ACIContractFilterEntryFilterSet
    filterset_form = ACIContractFilterEntryFilterForm
    table = ACIContractFilterEntryTable


@register_model_view(ACIContractFilterEntry, "add", detail=False)
@register_model_view(ACIContractFilterEntry, "edit")
class ACIContractFilterEntryEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACIContractFilterEntry."""

    queryset = ACIContractFilterEntry.objects.prefetch_related(
        "aci_contract_filter",
        "tags",
    )
    form = ACIContractFilterEntryEditForm


@register_model_view(ACIContractFilterEntry, "delete")
class ACIContractFilterEntryDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACIContractFilterEntry."""

    queryset = ACIContractFilterEntry.objects.prefetch_related(
        "aci_contract_filter",
        "tags",
    )


@register_model_view(ACIContractFilterEntry, "bulk_import", path="import", detail=False)
class ACIContractFilterEntryBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of Filter Entry."""

    queryset = ACIContractFilterEntry.objects.all()
    model_form = ACIContractFilterEntryImportForm


@register_model_view(ACIContractFilterEntry, "bulk_edit", path="edit", detail=False)
class ACIContractFilterEntryBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of Filter Entry."""

    queryset = ACIContractFilterEntry.objects.all()
    filterset = ACIContractFilterEntryFilterSet
    table = ACIContractFilterEntryTable
    form = ACIContractFilterEntryBulkEditForm


@register_model_view(ACIContractFilterEntry, "bulk_delete", path="delete", detail=False)
class ACIContractFilterEntryBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of Filter Entry."""

    queryset = ACIContractFilterEntry.objects.all()
    filterset = ACIContractFilterEntryFilterSet
    table = ACIContractFilterEntryTable
