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
        return ACIVRF.objects.restrict(request.user, "view").prefetch_related(
            "aci_tenant",
            "nb_tenant",
            "tags",
        )


#
# VRF views
#


@register_model_view(ACIVRF)
class ACIVRFView(generic.ObjectView):
    """Detail view for displaying a single object of ACI VRF."""

    queryset = ACIVRF.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )


@register_model_view(ACIVRF, "list", path="", detail=False)
class ACIVRFListView(generic.ObjectListView):
    """List view for listing all objects of ACI VRF."""

    queryset = ACIVRF.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )
    filterset = ACIVRFFilterSet
    filterset_form = ACIVRFFilterForm
    table = ACIVRFTable


@register_model_view(ACIVRF, "add", detail=False)
@register_model_view(ACIVRF, "edit")
class ACIVRFEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI VRF."""

    queryset = ACIVRF.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )
    form = ACIVRFEditForm


@register_model_view(ACIVRF, "delete")
class ACIVRFDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI VRF."""

    queryset = ACIVRF.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )


@register_model_view(ACIVRF, "bridgedomains", path="bridge-domains")
class ACIVRFBridgeDomainView(ACIBridgeDomainChildrenView):
    """Children view of ACI Bridge Domain of ACI VRF."""

    queryset = ACIVRF.objects.all()
    template_name = "netbox_aci_plugin/inc/acivrf/bridgedomains.html"

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
    template_name = "netbox_aci_plugin/inc/acivrf/contractrelations.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(aci_vrf=parent.pk)

    def get_extra_context(self, request, instance) -> dict:
        """Return ContentType as extra context."""
        aci_vrf_content_type = ContentType.objects.get_for_model(ACIVRF)

        return {
            "content_type_id": aci_vrf_content_type.id,
        }

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
