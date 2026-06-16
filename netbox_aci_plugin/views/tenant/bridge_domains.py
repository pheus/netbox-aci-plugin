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
from ...filtersets.tenant.bridge_domains import ACIBridgeDomainL3OutBindingFilterSet
from ...forms.tenant.bridge_domains import (
    ACIBridgeDomainBulkEditForm,
    ACIBridgeDomainEditForm,
    ACIBridgeDomainFilterForm,
    ACIBridgeDomainImportForm,
    ACIBridgeDomainL3OutBindingBulkEditForm,
    ACIBridgeDomainL3OutBindingEditForm,
    ACIBridgeDomainL3OutBindingFilterForm,
    ACIBridgeDomainL3OutBindingImportForm,
    ACIBridgeDomainSubnetBulkEditForm,
    ACIBridgeDomainSubnetEditForm,
    ACIBridgeDomainSubnetFilterForm,
    ACIBridgeDomainSubnetImportForm,
)
from ...models.tenant.bridge_domains import (
    ACIBridgeDomain,
    ACIBridgeDomainL3OutBinding,
    ACIBridgeDomainSubnet,
)
from ...object_actions import add_child_action
from ...tables.tenant.bridge_domains import (
    ACIBridgeDomainL3OutBindingTable,
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
        return (
            ACIBridgeDomain.objects.restrict(request.user, "view")
            .select_related(
                "aci_tenant",
                "aci_vrf",
                "nb_tenant",
                "owner",
            )
            .prefetch_related(
                "tags",
            )
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
        return (
            ACIBridgeDomainSubnet.objects.restrict(request.user, "view")
            .select_related(
                "aci_bridge_domain",
                "gateway_ip_address",
                "nb_tenant",
                "owner",
            )
            .prefetch_related(
                "tags",
            )
        )


class ACIBridgeDomainL3OutBindingChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching ACI BD L3Out bindings."""

    child_model = ACIBridgeDomainL3OutBinding
    filterset = ACIBridgeDomainL3OutBindingFilterSet
    tab = ViewTab(
        label=_("L3Outs"),
        badge=lambda obj: obj.aci_l3out_bindings.count(),
        permission="netbox_aci_plugin.view_acibridgedomainl3outbinding",
        weight=1000,
    )
    table = ACIBridgeDomainL3OutBindingTable

    def get_children(self, request, parent):
        """Return all objects of ACIBridgeDomainL3OutBinding."""
        return (
            ACIBridgeDomainL3OutBinding.objects.restrict(request.user, "view")
            .select_related("aci_bridge_domain", "aci_l3out")
            .prefetch_related("tags")
        )


#
# Bridge Domain views
#


@register_model_view(ACIBridgeDomain)
class ACIBridgeDomainView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.select_related(
        "aci_tenant",
        "aci_vrf",
        "nb_tenant",
        "owner",
    ).prefetch_related(
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

    queryset = ACIBridgeDomain.objects.select_related(
        "aci_tenant",
        "aci_vrf",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    filterset = ACIBridgeDomainFilterSet
    filterset_form = ACIBridgeDomainFilterForm
    table = ACIBridgeDomainTable


@register_model_view(ACIBridgeDomain, "add", detail=False)
@register_model_view(ACIBridgeDomain, "edit")
class ACIBridgeDomainEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.select_related(
        "aci_tenant",
        "aci_vrf",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    form = ACIBridgeDomainEditForm


@register_model_view(ACIBridgeDomain, "delete")
class ACIBridgeDomainDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.select_related(
        "aci_tenant",
        "aci_vrf",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )


@register_model_view(ACIBridgeDomain, "bridgedomainsubnets", path="subnets")
class ACIBridgeDomainBridgeDomainSubnetView(ACIBridgeDomainSubnetChildrenView):
    """Children view of ACI Bridge Domain Subnet of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACIBridgeDomainSubnet",
            _("Add a BD Subnet"),
            url_params={
                "aci_tenant": lambda ctx: ctx["object"].aci_tenant_id,
                "aci_vrf": lambda ctx: ctx["object"].aci_vrf_id,
                "aci_bridge_domain": lambda ctx: ctx["object"].pk,
                "nb_vrf": lambda ctx: ctx["object"].aci_vrf.nb_vrf_id,
                "nb_tenant": lambda ctx: ctx["object"].nb_tenant_id,
            },
        ),
    ) + ACIBridgeDomainSubnetChildrenView.actions

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
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACIEndpointGroup",
            _("Add an EPG"),
            url_params={
                "aci_tenant": lambda ctx: ctx["object"].aci_tenant_id,
                "aci_bridge_domain": lambda ctx: ctx["object"].pk,
                "nb_tenant": lambda ctx: ctx["object"].nb_tenant_id,
            },
        ),
    ) + ACIEndpointGroupChildrenView.actions

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

    queryset = ACIBridgeDomainSubnet.objects.select_related(
        "aci_bridge_domain",
        "gateway_ip_address",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )


@register_model_view(ACIBridgeDomainSubnet, "list", path="", detail=False)
class ACIBridgeDomainSubnetListView(generic.ObjectListView):
    """List view for listing all objects of ACI BD Subnet."""

    queryset = ACIBridgeDomainSubnet.objects.select_related(
        "aci_bridge_domain",
        "gateway_ip_address",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    filterset = ACIBridgeDomainSubnetFilterSet
    filterset_form = ACIBridgeDomainSubnetFilterForm
    table = ACIBridgeDomainSubnetTable


@register_model_view(ACIBridgeDomainSubnet, "add", detail=False)
@register_model_view(ACIBridgeDomainSubnet, "edit")
class ACIBridgeDomainSubnetEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI BD Subnet."""

    queryset = ACIBridgeDomainSubnet.objects.select_related(
        "aci_bridge_domain",
        "gateway_ip_address",
        "nb_tenant",
        "owner",
    ).prefetch_related(
        "tags",
    )
    form = ACIBridgeDomainSubnetEditForm


@register_model_view(ACIBridgeDomainSubnet, "delete")
class ACIBridgeDomainSubnetDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI BD Subnet."""

    queryset = ACIBridgeDomainSubnet.objects.select_related(
        "aci_bridge_domain",
        "gateway_ip_address",
        "nb_tenant",
        "owner",
    ).prefetch_related(
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


#
# Bridge Domain L3Out Binding views
#
@register_model_view(ACIBridgeDomainL3OutBinding)
class ACIBridgeDomainL3OutBindingView(generic.ObjectView):
    """Detail view for displaying a single object of ACI BD L3Out Binding."""

    queryset = ACIBridgeDomainL3OutBinding.objects.select_related(
        "aci_bridge_domain", "aci_l3out"
    ).prefetch_related("tags")


@register_model_view(ACIBridgeDomainL3OutBinding, "list", path="", detail=False)
class ACIBridgeDomainL3OutBindingListView(generic.ObjectListView):
    """List view for listing all objects of ACI BD L3Out Binding."""

    queryset = ACIBridgeDomainL3OutBinding.objects.select_related(
        "aci_bridge_domain", "aci_l3out"
    ).prefetch_related("tags")
    table = ACIBridgeDomainL3OutBindingTable
    filterset = ACIBridgeDomainL3OutBindingFilterSet
    filterset_form = ACIBridgeDomainL3OutBindingFilterForm


@register_model_view(ACIBridgeDomainL3OutBinding, "add", detail=False)
@register_model_view(ACIBridgeDomainL3OutBinding, "edit")
class ACIBridgeDomainL3OutBindingEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI BD L3Out Binding."""

    queryset = ACIBridgeDomainL3OutBinding.objects.select_related(
        "aci_bridge_domain", "aci_l3out"
    ).prefetch_related("tags")
    form = ACIBridgeDomainL3OutBindingEditForm


@register_model_view(ACIBridgeDomainL3OutBinding, "delete")
class ACIBridgeDomainL3OutBindingDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI BD L3Out Binding."""

    queryset = ACIBridgeDomainL3OutBinding.objects.select_related(
        "aci_bridge_domain", "aci_l3out"
    ).prefetch_related("tags")


@register_model_view(
    ACIBridgeDomainL3OutBinding, "bulk_import", path="import", detail=False
)
class ACIBridgeDomainL3OutBindingBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple ACI BD L3Out Bindings."""

    queryset = ACIBridgeDomainL3OutBinding.objects.all()
    model_form = ACIBridgeDomainL3OutBindingImportForm


@register_model_view(
    ACIBridgeDomainL3OutBinding, "bulk_edit", path="edit", detail=False
)
class ACIBridgeDomainL3OutBindingBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple ACI BD L3Out Bindings."""

    queryset = ACIBridgeDomainL3OutBinding.objects.all()
    filterset = ACIBridgeDomainL3OutBindingFilterSet
    table = ACIBridgeDomainL3OutBindingTable
    form = ACIBridgeDomainL3OutBindingBulkEditForm


@register_model_view(
    ACIBridgeDomainL3OutBinding, "bulk_delete", path="delete", detail=False
)
class ACIBridgeDomainL3OutBindingBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple ACI BD L3Out Bindings."""

    queryset = ACIBridgeDomainL3OutBinding.objects.all()
    filterset = ACIBridgeDomainL3OutBindingFilterSet
    table = ACIBridgeDomainL3OutBindingTable


@register_model_view(ACIBridgeDomain, "l3outbindings", path="l3outs")
class ACIBridgeDomainL3OutBindingsView(ACIBridgeDomainL3OutBindingChildrenView):
    """Children view of ACI BD L3Out bindings of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACIBridgeDomainL3OutBinding",
            _("Attach an L3Out"),
            url_params={
                "aci_fabric": lambda ctx: ctx["object"].aci_fabric.pk,
                "aci_tenant": lambda ctx: ctx["object"].aci_tenant_id,
                "aci_vrf": lambda ctx: ctx["object"].aci_vrf_id,
                "aci_bridge_domain": lambda ctx: ctx["object"].pk,
            },
        ),
    ) + ACIBridgeDomainL3OutBindingChildrenView.actions

    def get_children(self, request, parent):
        """Return all children objects of the current parent object."""
        return super().get_children(request, parent).filter(aci_bridge_domain=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return table with ACI Bridge Domain column hidden."""
        table = super().get_table(*args, **kwargs)
        table.columns.hide("aci_bridge_domain")
        return table
