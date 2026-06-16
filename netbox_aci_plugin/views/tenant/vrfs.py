# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets.tenant.vrfs import ACIVRFFilterSet
from ...forms.tenant.vrfs import (
    ACIVRFBulkEditForm,
    ACIVRFEditForm,
    ACIVRFFilterForm,
    ACIVRFImportForm,
)
from ...models.tenant.vrfs import ACIVRF
from ...object_actions import add_child_action
from ...tables.tenant.vrfs import ACIVRFTable
from .bridge_domains import ACIBridgeDomainChildrenView
from .contracts import ACIContractRelationChildrenView

#
# Base children views
#


class ACIVRFChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI VRF."""

    child_model = ACIVRF
    filterset = ACIVRFFilterSet
    tab = ViewTab(
        label=_("VRFs"),
        badge=lambda obj: obj.aci_vrfs.count(),
        permission="netbox_aci_plugin.view_acivrf",
        weight=1000,
    )
    table = ACIVRFTable

    def get_children(self, request, parent):
        """Return all objects of ACIVRF."""
        return (
            ACIVRF.objects.restrict(request.user, "view")
            .select_related(
                "aci_tenant",
                "nb_tenant",
                "owner",
            )
            .prefetch_related(
                "tags",
            )
        )


#
# VRF views
#


@register_model_view(ACIVRF)
class ACIVRFView(generic.ObjectView):
    """Detail view for displaying a single object of ACI VRF."""

    queryset = ACIVRF.objects.select_related(
        "aci_tenant",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )


@register_model_view(ACIVRF, "list", path="", detail=False)
class ACIVRFListView(generic.ObjectListView):
    """List view for listing all objects of ACI VRF."""

    queryset = ACIVRF.objects.select_related(
        "aci_tenant",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    filterset = ACIVRFFilterSet
    filterset_form = ACIVRFFilterForm
    table = ACIVRFTable


@register_model_view(ACIVRF, "add", detail=False)
@register_model_view(ACIVRF, "edit")
class ACIVRFEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI VRF."""

    queryset = ACIVRF.objects.select_related(
        "aci_tenant",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    form = ACIVRFEditForm


@register_model_view(ACIVRF, "delete")
class ACIVRFDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI VRF."""

    queryset = ACIVRF.objects.select_related(
        "aci_tenant",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )


@register_model_view(ACIVRF, "bridgedomains", path="bridge-domains")
class ACIVRFBridgeDomainView(ACIBridgeDomainChildrenView):
    """Children view of ACI Bridge Domain of ACI VRF."""

    queryset = ACIVRF.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACIBridgeDomain",
            _("Add a Bridge Domain"),
            url_params={
                "aci_tenant": lambda ctx: ctx["object"].aci_tenant_id,
                "aci_vrf": lambda ctx: ctx["object"].pk,
            },
        ),
    ) + ACIBridgeDomainChildrenView.actions

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(aci_vrf=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return table with ACITenant and ACIVRF colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACITenant column
        table.columns.hide("aci_tenant")
        # Hide ACIVRF column
        table.columns.hide("aci_vrf")

        return table


@register_model_view(ACIVRF, "contractrelations", path="contract-relations")
class ACIVRFContractRelationView(ACIContractRelationChildrenView):
    """Children view of ACI Contract Relation of ACI VRF."""

    queryset = ACIVRF.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACIContractRelation",
            _("Add a Relation"),
            url_params={
                "aci_tenant": lambda ctx: ctx["object"].aci_tenant_id,
                "aci_object": lambda ctx: ctx["object"].pk,
                "aci_object_type": lambda ctx: (
                    ContentType.objects.get_for_model(ctx["object"]).pk
                ),
            },
        ),
    ) + ACIContractRelationChildrenView.actions

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(aci_vrf=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with ACI object colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACITenant column of ACIContract
        table.columns.hide("aci_contract_tenant")
        # Hide ACI object type column
        table.columns.hide("aci_object_type")
        # Hide ACI object column
        table.columns.hide("aci_object")

        return table


@register_model_view(ACIVRF, "bulk_import", path="import", detail=False)
class ACIVRFBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI VRF."""

    queryset = ACIVRF.objects.all()
    model_form = ACIVRFImportForm


@register_model_view(ACIVRF, "bulk_edit", path="edit", detail=False)
class ACIVRFBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI VRF."""

    queryset = ACIVRF.objects.all()
    filterset = ACIVRFFilterSet
    table = ACIVRFTable
    form = ACIVRFBulkEditForm


@register_model_view(ACIVRF, "bulk_delete", path="delete", detail=False)
class ACIVRFBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI VRF."""

    queryset = ACIVRF.objects.all()
    filterset = ACIVRFFilterSet
    table = ACIVRFTable
