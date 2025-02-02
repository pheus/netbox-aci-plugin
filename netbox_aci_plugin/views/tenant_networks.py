# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ..filtersets.tenant_networks import (
    ACIBridgeDomainFilterSet,
    ACIBridgeDomainSubnetFilterSet,
    ACIVRFFilterSet,
)
from ..forms.tenant_networks import (
    ACIBridgeDomainBulkEditForm,
    ACIBridgeDomainEditForm,
    ACIBridgeDomainFilterForm,
    ACIBridgeDomainImportForm,
    ACIBridgeDomainSubnetBulkEditForm,
    ACIBridgeDomainSubnetEditForm,
    ACIBridgeDomainSubnetFilterForm,
    ACIBridgeDomainSubnetImportForm,
    ACIVRFBulkEditForm,
    ACIVRFEditForm,
    ACIVRFFilterForm,
    ACIVRFImportForm,
)
from ..models.tenant_networks import (
    ACIVRF,
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)
from ..tables.tenant_networks import (
    ACIBridgeDomainSubnetReducedTable,
    ACIBridgeDomainSubnetTable,
    ACIBridgeDomainTable,
    ACIVRFTable,
)
from .tenant_app_profiles import ACIEndpointGroupChildrenView
from .tenant_contracts import ACIContractRelationChildrenView

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


class ACIBridgeDomainChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Bridge Domain."""

    child_model = ACIBridgeDomain
    filterset = ACIBridgeDomainFilterSet
    tab = ViewTab(
        label=_("Bridge Domains"),
        badge=lambda obj: obj.aci_bridge_domains.count(),
        permission="netbox_aci_plugin.view_acibridgedomain",
        weight=1000,
    )
    table = ACIBridgeDomainTable

    def get_children(self, request, parent):
        """Return all objects of ACIBridgeDomain."""
        return ACIBridgeDomain.objects.restrict(
            request.user, "view"
        ).prefetch_related(
            "aci_tenant",
            "aci_vrf",
            "nb_tenant",
            "tags",
        )


class ACIBridgeDomainSubnetChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Bridge Domain Subnet."""

    child_model = ACIBridgeDomainSubnet
    filterset = ACIBridgeDomainSubnetFilterSet
    tab = ViewTab(
        label=_("BD Subnets"),
        badge=lambda obj: obj.aci_bridge_domain_subnets.count(),
        permission="netbox_aci_plugin.view_acibridgedomainsubnet",
        weight=1000,
    )
    table = ACIBridgeDomainSubnetTable

    def get_children(self, request, parent):
        """Return all objects of ACIBridgeDomainSubnet."""
        return ACIBridgeDomainSubnet.objects.restrict(
            request.user, "view"
        ).prefetch_related(
            "aci_bridge_domain",
            "gateway_ip_address",
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
    template_name = "netbox_aci_plugin/acivrf_bridgedomains.html"

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
    template_name = "netbox_aci_plugin/acivrf_contractrelations.html"

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


#
# Bridge Domain views
#


@register_model_view(ACIBridgeDomain)
class ACIBridgeDomainView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.prefetch_related(
        "aci_bridge_domain_subnets",
        "aci_tenant",
        "aci_vrf",
        "nb_tenant",
        "tags",
    )

    def get_extra_context(self, request, instance) -> dict:
        """Return related Bridge Domain Subnets as extra context."""
        subnets_table = ACIBridgeDomainSubnetReducedTable(
            instance.aci_bridge_domain_subnets.all()
        )
        subnets_table.configure(request=request)

        return {
            "subnets_table": subnets_table,
        }


@register_model_view(ACIBridgeDomain, "list", path="", detail=False)
class ACIBridgeDomainListView(generic.ObjectListView):
    """List view for listing all objects of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.prefetch_related(
        "aci_tenant",
        "aci_vrf",
        "nb_tenant",
        "tags",
    )
    filterset = ACIBridgeDomainFilterSet
    filterset_form = ACIBridgeDomainFilterForm
    table = ACIBridgeDomainTable


@register_model_view(ACIBridgeDomain, "add", detail=False)
@register_model_view(ACIBridgeDomain, "edit")
class ACIBridgeDomainEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.prefetch_related(
        "aci_tenant",
        "aci_vrf",
        "nb_tenant",
        "tags",
    )
    form = ACIBridgeDomainEditForm


@register_model_view(ACIBridgeDomain, "delete")
class ACIBridgeDomainDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.prefetch_related(
        "aci_tenant",
        "aci_vrf",
        "nb_tenant",
        "tags",
    )


@register_model_view(ACIBridgeDomain, "bridgedomainsubnets", path="subnets")
class ACIBridgeDomainBridgeDomainSubnetView(ACIBridgeDomainSubnetChildrenView):
    """Children view of ACI Bridge Domain Subnet of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.all()
    template_name = "netbox_aci_plugin/acibridgedomain_subnets.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_bridge_domain=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return table with ACIBridgeDomain colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACIBridgeDomain column
        table.columns.hide("aci_bridge_domain")

        return table


@register_model_view(ACIBridgeDomain, "endpointgroups", path="endpoint-groups")
class ACIBridgeDomainEndpointGroupView(ACIEndpointGroupChildrenView):
    """Children view of ACI Endpoint Group of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.all()
    template_name = "netbox_aci_plugin/acibridgedomain_endpointgroups.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_bridge_domain=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return table with ACIBridgeDomain colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACIBridgeDomain column
        table.columns.hide("aci_bridge_domain")

        return table


@register_model_view(
    ACIBridgeDomain, "bulk_import", path="import", detail=False
)
class ACIBridgeDomainBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.all()
    model_form = ACIBridgeDomainImportForm


@register_model_view(ACIBridgeDomain, "bulk_edit", path="edit", detail=False)
class ACIBridgeDomainBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.all()
    filterset = ACIBridgeDomainFilterSet
    table = ACIBridgeDomainTable
    form = ACIBridgeDomainBulkEditForm


@register_model_view(
    ACIBridgeDomain, "bulk_delete", path="delete", detail=False
)
class ACIBridgeDomainBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.all()
    filterset = ACIBridgeDomainFilterSet
    table = ACIBridgeDomainTable


#
# Bridge Domain Subnet views
#


@register_model_view(ACIBridgeDomainSubnet)
class ACIBridgeDomainSubnetView(generic.ObjectView):
    """Detail view for displaying a single object of ACI BD Subnet."""

    queryset = ACIBridgeDomainSubnet.objects.prefetch_related(
        "aci_bridge_domain",
        "gateway_ip_address",
        "nb_tenant",
        "tags",
    )


@register_model_view(ACIBridgeDomainSubnet, "list", path="", detail=False)
class ACIBridgeDomainSubnetListView(generic.ObjectListView):
    """List view for listing all objects of ACI BD Subnet."""

    queryset = ACIBridgeDomainSubnet.objects.prefetch_related(
        "aci_bridge_domain",
        "gateway_ip_address",
        "nb_tenant",
        "tags",
    )
    filterset = ACIBridgeDomainSubnetFilterSet
    filterset_form = ACIBridgeDomainSubnetFilterForm
    table = ACIBridgeDomainSubnetTable


@register_model_view(ACIBridgeDomainSubnet, "add", detail=False)
@register_model_view(ACIBridgeDomainSubnet, "edit")
class ACIBridgeDomainSubnetEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI BD Subnet."""

    queryset = ACIBridgeDomainSubnet.objects.prefetch_related(
        "aci_bridge_domain",
        "gateway_ip_address",
        "nb_tenant",
        "tags",
    )
    form = ACIBridgeDomainSubnetEditForm


@register_model_view(ACIBridgeDomainSubnet, "delete")
class ACIBridgeDomainSubnetDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI BD Subnet."""

    queryset = ACIBridgeDomainSubnet.objects.prefetch_related(
        "aci_bridge_domain",
        "gateway_ip_address",
        "nb_tenant",
        "tags",
    )


@register_model_view(
    ACIBridgeDomainSubnet, "bulk_import", path="import", detail=False
)
class ACIBridgeDomainSubnetBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI BD Subnet."""

    queryset = ACIBridgeDomainSubnet.objects.all()
    model_form = ACIBridgeDomainSubnetImportForm


@register_model_view(
    ACIBridgeDomainSubnet, "bulk_edit", path="edit", detail=False
)
class ACIBridgeDomainSubnetBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI BD Subnet."""

    queryset = ACIBridgeDomainSubnet.objects.all()
    filterset = ACIBridgeDomainSubnetFilterSet
    table = ACIBridgeDomainSubnetTable
    form = ACIBridgeDomainSubnetBulkEditForm


@register_model_view(
    ACIBridgeDomainSubnet, "bulk_delete", path="delete", detail=False
)
class ACIBridgeDomainSubnetBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI BD Subnet."""

    queryset = ACIBridgeDomainSubnet.objects.all()
    filterset = ACIBridgeDomainSubnetFilterSet
    table = ACIBridgeDomainSubnetTable
