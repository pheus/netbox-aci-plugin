# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets.access_policies.aaep import (
    ACIAAEPDomainBindingFilterSet,
    ACIAttachableAccessEntityProfileFilterSet,
)
from ...forms.access_policies.aaep import (
    ACIAAEPDomainBindingBulkEditForm,
    ACIAAEPDomainBindingEditForm,
    ACIAAEPDomainBindingFilterForm,
    ACIAAEPDomainBindingImportForm,
    ACIAttachableAccessEntityProfileBulkEditForm,
    ACIAttachableAccessEntityProfileEditForm,
    ACIAttachableAccessEntityProfileFilterForm,
    ACIAttachableAccessEntityProfileImportForm,
)
from ...models.access_policies.aaep import (
    ACIAAEPDomainBinding,
    ACIAttachableAccessEntityProfile,
)
from ...models.fabric.fabrics import ACIFabric
from ...object_actions import add_child_action
from ...tables.access_policies.aaep import (
    ACIAAEPDomainBindingTable,
    ACIAttachableAccessEntityProfileTable,
)

#
# Base children views
#


class ACIAttachableAccessEntityProfileChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI AAEPs."""

    child_model = ACIAttachableAccessEntityProfile
    filterset = ACIAttachableAccessEntityProfileFilterSet
    tab = ViewTab(
        label=_("AAEPs"),
        badge=lambda obj: obj.aci_aaeps.count(),
        permission="netbox_aci_plugin.view_aciattachableaccessentityprofile",
        weight=2300,
    )
    table = ACIAttachableAccessEntityProfileTable

    def get_children(self, request, parent):
        """Return all ACIAttachableAccessEntityProfile objects."""
        return (
            ACIAttachableAccessEntityProfile.objects.restrict(request.user, "view")
            .select_related(
                "aci_fabric",
                "nb_tenant",
                "owner",
            )
            .prefetch_related("tags")
        )


class ACIAAEPDomainBindingChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI AAEP Domain Bindings."""

    child_model = ACIAAEPDomainBinding
    filterset = ACIAAEPDomainBindingFilterSet
    tab = ViewTab(
        label=_("Domain Bindings"),
        badge=lambda obj: obj.aci_aaep_domain_bindings.count(),
        permission="netbox_aci_plugin.view_aciaaepdomainbinding",
        weight=1000,
    )
    table = ACIAAEPDomainBindingTable

    def get_children(self, request, parent):
        """Return all ACIAAEPDomainBinding objects."""
        return (
            ACIAAEPDomainBinding.objects.restrict(request.user, "view")
            .select_related(
                "aci_aaep",
                "aci_domain_object_type",
            )
            .prefetch_related(
                "aci_domain_object",
                "tags",
            )
        )


#
# AAEP views
#


@register_model_view(ACIAttachableAccessEntityProfile)
class ACIAttachableAccessEntityProfileView(generic.ObjectView):
    """Detail view for displaying a single object of ACI AAEP."""

    queryset = ACIAttachableAccessEntityProfile.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )


@register_model_view(ACIAttachableAccessEntityProfile, "list", path="", detail=False)
class ACIAttachableAccessEntityProfileListView(generic.ObjectListView):
    """List view for listing all objects of ACI AAEP."""

    queryset = ACIAttachableAccessEntityProfile.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    filterset = ACIAttachableAccessEntityProfileFilterSet
    filterset_form = ACIAttachableAccessEntityProfileFilterForm
    table = ACIAttachableAccessEntityProfileTable


@register_model_view(ACIAttachableAccessEntityProfile, "add", detail=False)
@register_model_view(ACIAttachableAccessEntityProfile, "edit")
class ACIAttachableAccessEntityProfileEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI AAEP."""

    queryset = ACIAttachableAccessEntityProfile.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    form = ACIAttachableAccessEntityProfileEditForm


@register_model_view(ACIAttachableAccessEntityProfile, "delete")
class ACIAttachableAccessEntityProfileDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI AAEP."""

    queryset = ACIAttachableAccessEntityProfile.objects.select_related(
        "aci_fabric",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )


@register_model_view(ACIFabric, "aaeps", path="aaeps")
class ACIFabricAAEPView(ACIAttachableAccessEntityProfileChildrenView):
    """Children view of ACI AAEPs of an ACI Fabric."""

    queryset = ACIFabric.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACIAttachableAccessEntityProfile",
            _("Add an AAEP"),
            url_params={
                "aci_fabric": lambda ctx: ctx["object"].pk,
                "nb_tenant": lambda ctx: ctx["object"].nb_tenant_id,
            },
        ),
    ) + ACIAttachableAccessEntityProfileChildrenView.actions

    def get_children(self, request, parent):
        """Return all ACI AAEP objects for the current ACIFabric."""
        return super().get_children(request, parent).filter(aci_fabric_id=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with ACIFabric column hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACIFabric column
        table.columns.hide("aci_fabric")

        return table


@register_model_view(
    ACIAttachableAccessEntityProfile, "domainbindings", path="domain-bindings"
)
class ACIAttachableAccessEntityProfileDomainBindingView(
    ACIAAEPDomainBindingChildrenView
):
    """Children view of ACI AAEP Domain Bindings of an ACI AAEP."""

    queryset = ACIAttachableAccessEntityProfile.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACIAAEPDomainBinding",
            _("Bind a Domain"),
            url_params={
                "aci_aaep": lambda ctx: ctx["object"].pk,
            },
        ),
    ) + ACIAAEPDomainBindingChildrenView.actions

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(aci_aaep=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with ACI AAEP column hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACI AAEP column
        table.columns.hide("aci_aaep")

        return table


@register_model_view(
    ACIAttachableAccessEntityProfile, "bulk_import", path="import", detail=False
)
class ACIAttachableAccessEntityProfileBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI AAEP."""

    queryset = ACIAttachableAccessEntityProfile.objects.all()
    model_form = ACIAttachableAccessEntityProfileImportForm


@register_model_view(
    ACIAttachableAccessEntityProfile, "bulk_edit", path="edit", detail=False
)
class ACIAttachableAccessEntityProfileBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI AAEP."""

    queryset = ACIAttachableAccessEntityProfile.objects.all()
    filterset = ACIAttachableAccessEntityProfileFilterSet
    table = ACIAttachableAccessEntityProfileTable
    form = ACIAttachableAccessEntityProfileBulkEditForm


@register_model_view(
    ACIAttachableAccessEntityProfile, "bulk_delete", path="delete", detail=False
)
class ACIAttachableAccessEntityProfileBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI AAEP."""

    queryset = ACIAttachableAccessEntityProfile.objects.all()
    filterset = ACIAttachableAccessEntityProfileFilterSet
    table = ACIAttachableAccessEntityProfileTable


#
# AAEP Domain Binding views
#


@register_model_view(ACIAAEPDomainBinding)
class ACIAAEPDomainBindingView(generic.ObjectView):
    """Detail view for displaying a single object of ACIAAEPDomainBinding."""

    queryset = ACIAAEPDomainBinding.objects.select_related(
        "aci_aaep",
        "aci_domain_object_type",
    ).prefetch_related(
        "aci_domain_object",
        "tags",
    )


@register_model_view(ACIAAEPDomainBinding, "list", path="", detail=False)
class ACIAAEPDomainBindingListView(generic.ObjectListView):
    """List view for listing all objects of ACIAAEPDomainBinding."""

    queryset = ACIAAEPDomainBinding.objects.select_related(
        "aci_aaep",
        "aci_domain_object_type",
    ).prefetch_related(
        "aci_domain_object",
        "tags",
    )
    filterset = ACIAAEPDomainBindingFilterSet
    filterset_form = ACIAAEPDomainBindingFilterForm
    table = ACIAAEPDomainBindingTable


@register_model_view(ACIAAEPDomainBinding, "add", detail=False)
@register_model_view(ACIAAEPDomainBinding, "edit")
class ACIAAEPDomainBindingEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACIAAEPDomainBinding."""

    queryset = ACIAAEPDomainBinding.objects.select_related(
        "aci_aaep",
        "aci_domain_object_type",
    ).prefetch_related(
        "aci_domain_object",
        "tags",
    )
    form = ACIAAEPDomainBindingEditForm


@register_model_view(ACIAAEPDomainBinding, "delete")
class ACIAAEPDomainBindingDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACIAAEPDomainBinding."""

    queryset = ACIAAEPDomainBinding.objects.select_related(
        "aci_aaep",
        "aci_domain_object_type",
    ).prefetch_related(
        "aci_domain_object",
        "tags",
    )


@register_model_view(ACIAAEPDomainBinding, "bulk_import", path="import", detail=False)
class ACIAAEPDomainBindingBulkImportView(generic.BulkImportView):
    """Bulk import view for importing AAEP Domain Binding objects."""

    queryset = ACIAAEPDomainBinding.objects.all()
    model_form = ACIAAEPDomainBindingImportForm


@register_model_view(ACIAAEPDomainBinding, "bulk_edit", path="edit", detail=False)
class ACIAAEPDomainBindingBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing AAEP Domain Binding objects."""

    queryset = ACIAAEPDomainBinding.objects.all()
    filterset = ACIAAEPDomainBindingFilterSet
    table = ACIAAEPDomainBindingTable
    form = ACIAAEPDomainBindingBulkEditForm


@register_model_view(ACIAAEPDomainBinding, "bulk_delete", path="delete", detail=False)
class ACIAAEPDomainBindingBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting AAEP Domain Binding objects."""

    queryset = ACIAAEPDomainBinding.objects.all()
    filterset = ACIAAEPDomainBindingFilterSet
    table = ACIAAEPDomainBindingTable
