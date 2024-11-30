# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ..filtersets.tenant_contracts import (
    ACIContractFilterSet,
    ACIContractSubjectFilterSet,
)
from ..forms.tenant_contracts import (
    ACIContractBulkEditForm,
    ACIContractEditForm,
    ACIContractFilterForm,
    ACIContractImportForm,
    ACIContractSubjectBulkEditForm,
    ACIContractSubjectEditForm,
    ACIContractSubjectFilterForm,
    ACIContractSubjectImportForm,
)
from ..models.tenant_contracts import ACIContract, ACIContractSubject
from ..tables.tenant_contracts import (
    ACIContractSubjectReducedTable,
    ACIContractSubjectTable,
    ACIContractTable,
)

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


class ACIContractSubjectChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Contract Subject."""

    child_model = ACIContractSubject
    filterset = ACIContractSubjectFilterSet
    tab = ViewTab(
        label=_("Subjects"),
        badge=lambda obj: obj.aci_contract_subjects.count(),
        permission="netbox_aci_plugin.view_acicontractsubject",
        weight=1000,
    )
    table = ACIContractSubjectTable

    def get_children(self, request, parent):
        """Return all objects of ACIContractSubject."""
        return ACIContractSubject.objects.restrict(
            request.user, "view"
        ).prefetch_related(
            "aci_contract",
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

    def get_extra_context(self, request, instance) -> dict:
        """Return related Contract Subjects as extra context."""
        contract_subjects_table = ACIContractSubjectReducedTable(
            instance.aci_contract_subjects.all()
        )
        contract_subjects_table.configure(request=request)

        return {
            "contract_subjects_table": contract_subjects_table,
        }


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


@register_model_view(ACIContract, "contractsubjects", path="subjects")
class ACIContractContractSubjectView(ACIContractSubjectChildrenView):
    """Children view of ACI Contract Subject of ACI Contract."""

    queryset = ACIContract.objects.all()
    template_name = "netbox_aci_plugin/acicontract_subjects.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_contract=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACIContract colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACITenant column of ACIContractSubject
        table.columns.hide("aci_tenant")
        # Hide ACIContract column
        table.columns.hide("aci_contract")

        return table


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


#
# Contract Subject views
#


@register_model_view(ACIContractSubject)
class ACIContractSubjectView(generic.ObjectView):
    """Detail view for displaying a single object of ACIContractSubject."""

    queryset = ACIContractSubject.objects.prefetch_related(
        "aci_contract",
        "nb_tenant",
        "tags",
    )


class ACIContractSubjectListView(generic.ObjectListView):
    """List view for listing all objects of ACIContractSubject."""

    queryset = ACIContractSubject.objects.prefetch_related(
        "aci_contract",
        "nb_tenant",
        "tags",
    )
    filterset = ACIContractSubjectFilterSet
    filterset_form = ACIContractSubjectFilterForm
    table = ACIContractSubjectTable


@register_model_view(ACIContractSubject, "edit")
class ACIContractSubjectEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACIContractSubject."""

    queryset = ACIContractSubject.objects.prefetch_related(
        "aci_contract",
        "nb_tenant",
        "tags",
    )
    form = ACIContractSubjectEditForm


@register_model_view(ACIContractSubject, "delete")
class ACIContractSubjectDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACIContractSubject."""

    queryset = ACIContractSubject.objects.prefetch_related(
        "aci_contract",
        "nb_tenant",
        "tags",
    )


class ACIContractSubjectBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of Contract Subject."""

    queryset = ACIContractSubject.objects.all()
    model_form = ACIContractSubjectImportForm


class ACIContractSubjectBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of Contract Subject."""

    queryset = ACIContractSubject.objects.all()
    filterset = ACIContractSubjectFilterSet
    table = ACIContractSubjectTable
    form = ACIContractSubjectBulkEditForm


class ACIContractSubjectBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of Contract Subject."""

    queryset = ACIContractSubject.objects.all()
    filterset = ACIContractSubjectFilterSet
    table = ACIContractSubjectTable
