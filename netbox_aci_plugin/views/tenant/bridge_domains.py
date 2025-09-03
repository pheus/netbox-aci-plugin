# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets import (
    ACIBridgeDomainFilterSet,
    ACIBridgeDomainSubnetFilterSet,
)
from ...forms.tenant.bridge_domains import (
    ACIBridgeDomainBulkEditForm,
    ACIBridgeDomainEditForm,
    ACIBridgeDomainFilterForm,
    ACIBridgeDomainImportForm,
    ACIBridgeDomainSubnetBulkEditForm,
    ACIBridgeDomainSubnetEditForm,
    ACIBridgeDomainSubnetFilterForm,
    ACIBridgeDomainSubnetImportForm,
)
from ...models.tenant.bridge_domains import (
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)
from ...tables.tenant.bridge_domains import (
    ACIBridgeDomainSubnetReducedTable,
    ACIBridgeDomainSubnetTable,
    ACIBridgeDomainTable,
)
from .endpoint_groups import ACIEndpointGroupChildrenView

#
# Base children views
#


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
        return ACIBridgeDomain.objects.restrict(request.user, "view").prefetch_related(
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
    template_name = "netbox_aci_plugin/inc/acibridgedomain/subnets.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(aci_bridge_domain=parent.pk)

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
    template_name = "netbox_aci_plugin/inc/acibridgedomain/endpointgroups.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(aci_bridge_domain=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return table with ACIBridgeDomain colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACIBridgeDomain column
        table.columns.hide("aci_bridge_domain")

        return table


@register_model_view(ACIBridgeDomain, "bulk_import", path="import", detail=False)
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


@register_model_view(ACIBridgeDomain, "bulk_delete", path="delete", detail=False)
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


@register_model_view(ACIBridgeDomainSubnet, "bulk_import", path="import", detail=False)
class ACIBridgeDomainSubnetBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI BD Subnet."""

    queryset = ACIBridgeDomainSubnet.objects.all()
    model_form = ACIBridgeDomainSubnetImportForm


@register_model_view(ACIBridgeDomainSubnet, "bulk_edit", path="edit", detail=False)
class ACIBridgeDomainSubnetBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI BD Subnet."""

    queryset = ACIBridgeDomainSubnet.objects.all()
    filterset = ACIBridgeDomainSubnetFilterSet
    table = ACIBridgeDomainSubnetTable
    form = ACIBridgeDomainSubnetBulkEditForm


@register_model_view(ACIBridgeDomainSubnet, "bulk_delete", path="delete", detail=False)
class ACIBridgeDomainSubnetBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI BD Subnet."""

    queryset = ACIBridgeDomainSubnet.objects.all()
    filterset = ACIBridgeDomainSubnetFilterSet
    table = ACIBridgeDomainSubnetTable
