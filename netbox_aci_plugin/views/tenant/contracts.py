# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets.tenant.contracts import (
    ACIContractFilterSet,
    ACIContractRelationFilterSet,
    ACIContractSubjectFilterFilterSet,
    ACIContractSubjectFilterSet,
)
from ...forms.tenant.contracts import (
    ACIContractBulkEditForm,
    ACIContractEditForm,
    ACIContractFilterForm,
    ACIContractImportForm,
    ACIContractRelationBulkEditForm,
    ACIContractRelationEditForm,
    ACIContractRelationFilterForm,
    ACIContractRelationImportForm,
    ACIContractSubjectBulkEditForm,
    ACIContractSubjectEditForm,
    ACIContractSubjectFilterBulkEditForm,
    ACIContractSubjectFilterEditForm,
    ACIContractSubjectFilterFilterForm,
    ACIContractSubjectFilterForm,
    ACIContractSubjectFilterImportForm,
    ACIContractSubjectImportForm,
)
from ...models.tenant.contracts import (
    ACIContract,
    ACIContractRelation,
    ACIContractSubject,
    ACIContractSubjectFilter,
)
from ...tables.tenant.contracts import (
    ACIContractRelationTable,
    ACIContractSubjectFilterReducedTable,
    ACIContractSubjectFilterTable,
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
        return ACIContract.objects.restrict(request.user, "view").prefetch_related(
            "aci_tenant",
            "nb_tenant",
            "tags",
        )


class ACIContractRelationChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Contract Relation."""

    child_model = ACIContractRelation
    filterset = ACIContractRelationFilterSet
    tab = ViewTab(
        label=_("Contracts"),
        badge=lambda obj: obj.aci_contract_relations.count(),
        permission="netbox_aci_plugin.view_acicontractrelation",
        weight=1100,
    )
    table = ACIContractRelationTable

    def get_children(self, request, parent):
        """Return all objects of ACIContractRelation."""
        return ACIContractRelation.objects.restrict(
            request.user, "view"
        ).prefetch_related(
            "aci_contract",
            "aci_object_type",
            "aci_object",
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


class ACIContractSubjectFilterChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of Contract Subject Filter."""

    child_model = ACIContractSubjectFilter
    filterset = ACIContractSubjectFilterFilterSet
    tab = ViewTab(
        label=_("Subject Filters"),
        badge=lambda obj: obj.aci_contract_subject_filters.count(),
        permission="netbox_aci_plugin.view_acicontractsubjectfilter",
        weight=1000,
    )
    table = ACIContractSubjectFilterTable

    def get_children(self, request, parent):
        """Return all objects of ACIContractSubjectFilter."""
        return ACIContractSubjectFilter.objects.restrict(
            request.user, "view"
        ).prefetch_related(
            "aci_contract_filter",
            "aci_contract_subject",
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


@register_model_view(ACIContract, "list", path="", detail=False)
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


@register_model_view(ACIContract, "add", detail=False)
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


@register_model_view(ACIContract, "contractrelations", path="relations")
class ACIContractContractRelationView(ACIContractRelationChildrenView):
    """Children view of ACI Contract Relation of ACI Contract."""

    queryset = ACIContract.objects.all()
    template_name = "netbox_aci_plugin/inc/acicontract/relations.html"
    tab = ViewTab(
        label=_("Relations"),
        badge=lambda obj: obj.aci_contract_relations.count(),
        permission="netbox_aci_plugin.view_acicontractrelation",
        weight=1100,
    )

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(aci_contract=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with ACIContract colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACITenant column of ACIContract
        table.columns.hide("aci_contract_tenant")
        # Hide ACIContract column
        table.columns.hide("aci_contract")

        return table


@register_model_view(ACIContract, "contractsubjects", path="subjects")
class ACIContractContractSubjectView(ACIContractSubjectChildrenView):
    """Children view of ACI Contract Subject of ACI Contract."""

    queryset = ACIContract.objects.all()
    template_name = "netbox_aci_plugin/inc/acicontract/subjects.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(aci_contract=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with ACIContract colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACITenant column of ACIContractSubject
        table.columns.hide("aci_tenant")
        # Hide ACIContract column
        table.columns.hide("aci_contract")

        return table


@register_model_view(ACIContract, "bulk_import", path="import", detail=False)
class ACIContractBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACIContract."""

    queryset = ACIContract.objects.all()
    model_form = ACIContractImportForm


@register_model_view(ACIContract, "bulk_edit", path="edit", detail=False)
class ACIContractBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACIContract."""

    queryset = ACIContract.objects.all()
    filterset = ACIContractFilterSet
    table = ACIContractTable
    form = ACIContractBulkEditForm


@register_model_view(ACIContract, "bulk_delete", path="delete", detail=False)
class ACIContractBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACIContract."""

    queryset = ACIContract.objects.all()
    filterset = ACIContractFilterSet
    table = ACIContractTable


#
# Contract Relation views
#


@register_model_view(ACIContractRelation)
class ACIContractRelationView(generic.ObjectView):
    """Detail view for displaying a single object of ACIContractRelation."""

    queryset = ACIContractRelation.objects.prefetch_related(
        "aci_contract",
        "aci_object",
        "tags",
    )


@register_model_view(ACIContractRelation, "list", path="", detail=False)
class ACIContractRelationListView(generic.ObjectListView):
    """List view for listing all objects of ACIContractRelation."""

    queryset = ACIContractRelation.objects.prefetch_related(
        "aci_contract",
        "aci_object",
        "tags",
    )
    filterset = ACIContractRelationFilterSet
    filterset_form = ACIContractRelationFilterForm
    table = ACIContractRelationTable


@register_model_view(ACIContractRelation, "add", detail=False)
@register_model_view(ACIContractRelation, "edit")
class ACIContractRelationEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACIContractRelation."""

    queryset = ACIContractRelation.objects.prefetch_related(
        "aci_contract",
        "aci_object",
        "tags",
    )
    form = ACIContractRelationEditForm


@register_model_view(ACIContractRelation, "delete")
class ACIContractRelationDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACIContractRelation."""

    queryset = ACIContractRelation.objects.prefetch_related(
        "aci_contract",
        "aci_object",
        "tags",
    )


@register_model_view(ACIContractRelation, "bulk_import", path="import", detail=False)
class ACIContractRelationBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of Contract Relation."""

    queryset = ACIContractRelation.objects.all()
    model_form = ACIContractRelationImportForm


@register_model_view(ACIContractRelation, "bulk_edit", path="edit", detail=False)
class ACIContractRelationBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of Contract Relation."""

    queryset = ACIContractRelation.objects.all()
    filterset = ACIContractRelationFilterSet
    table = ACIContractRelationTable
    form = ACIContractRelationBulkEditForm


@register_model_view(ACIContractRelation, "bulk_delete", path="delete", detail=False)
class ACIContractRelationBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of Contract Subject."""

    queryset = ACIContractRelation.objects.all()
    filterset = ACIContractRelationFilterSet
    table = ACIContractRelationTable


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

    def get_extra_context(self, request, instance) -> dict:
        """Return related Contract Subject Filters as extra context."""
        contract_subject_filters_table = ACIContractSubjectFilterReducedTable(
            instance.aci_contract_subject_filters.all()
        )
        contract_subject_filters_table.configure(request=request)

        return {
            "contract_subject_filters_table": contract_subject_filters_table,
        }


@register_model_view(ACIContractSubject, "list", path="", detail=False)
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


@register_model_view(ACIContractSubject, "add", detail=False)
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


@register_model_view(ACIContractSubject, "contractsubjectfilters", path="filters")
class ACIContractContractSubjectFilterView(ACIContractSubjectFilterChildrenView):
    """Children view of ACI Contract Subject Filter of ACI Contract Subject."""

    queryset = ACIContractSubject.objects.all()
    template_name = "netbox_aci_plugin/inc/acicontractsubject/subjectfilters.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super().get_children(request, parent).filter(aci_contract_subject=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACIContractSubject colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACITenant column of ACIContractSubject
        table.columns.hide("aci_contract_subject_tenant")
        # Hide ACIContractSubject column
        table.columns.hide("aci_contract_subject")

        return table


@register_model_view(ACIContractSubject, "bulk_import", path="import", detail=False)
class ACIContractSubjectBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of Contract Subject."""

    queryset = ACIContractSubject.objects.all()
    model_form = ACIContractSubjectImportForm


@register_model_view(ACIContractSubject, "bulk_edit", path="edit", detail=False)
class ACIContractSubjectBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of Contract Subject."""

    queryset = ACIContractSubject.objects.all()
    filterset = ACIContractSubjectFilterSet
    table = ACIContractSubjectTable
    form = ACIContractSubjectBulkEditForm


@register_model_view(ACIContractSubject, "bulk_delete", path="delete", detail=False)
class ACIContractSubjectBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of Contract Subject."""

    queryset = ACIContractSubject.objects.all()
    filterset = ACIContractSubjectFilterSet
    table = ACIContractSubjectTable


#
# Contract Subject Filter views
#


@register_model_view(ACIContractSubjectFilter)
class ACIContractSubjectFilterView(generic.ObjectView):
    """Detail view for displaying a single object of Subject Filter."""

    queryset = ACIContractSubjectFilter.objects.prefetch_related(
        "aci_contract_filter",
        "aci_contract_subject",
        "tags",
    )


@register_model_view(ACIContractSubjectFilter, "list", path="", detail=False)
class ACIContractSubjectFilterListView(generic.ObjectListView):
    """List view for listing all objects of Subject Filter."""

    queryset = ACIContractSubjectFilter.objects.prefetch_related(
        "aci_contract_filter",
        "aci_contract_subject",
        "tags",
    )
    filterset = ACIContractSubjectFilterFilterSet
    filterset_form = ACIContractSubjectFilterFilterForm
    table = ACIContractSubjectFilterTable


@register_model_view(ACIContractSubjectFilter, "add", detail=False)
@register_model_view(ACIContractSubjectFilter, "edit")
class ACIContractSubjectFilterEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACIContractSubjectFilter."""

    queryset = ACIContractSubjectFilter.objects.prefetch_related(
        "aci_contract_filter",
        "aci_contract_subject",
        "tags",
    )
    form = ACIContractSubjectFilterEditForm


@register_model_view(ACIContractSubjectFilter, "delete")
class ACIContractSubjectFilterDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACIContractSubjectFilter."""

    queryset = ACIContractSubjectFilter.objects.prefetch_related(
        "aci_contract_filter",
        "aci_contract_subject",
        "tags",
    )


@register_model_view(
    ACIContractSubjectFilter, "bulk_import", path="import", detail=False
)
class ACIContractSubjectFilterBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of Subject Filter."""

    queryset = ACIContractSubjectFilter.objects.all()
    model_form = ACIContractSubjectFilterImportForm


@register_model_view(ACIContractSubjectFilter, "bulk_edit", path="edit", detail=False)
class ACIContractSubjectFilterBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of Subject Filter."""

    queryset = ACIContractSubjectFilter.objects.all()
    filterset = ACIContractSubjectFilterFilterSet
    table = ACIContractSubjectFilterTable
    form = ACIContractSubjectFilterBulkEditForm


@register_model_view(
    ACIContractSubjectFilter, "bulk_delete", path="delete", detail=False
)
class ACIContractSubjectFilterBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of Subject Filter."""

    queryset = ACIContractSubjectFilter.objects.all()
    filterset = ACIContractSubjectFilterFilterSet
    table = ACIContractSubjectFilterTable
