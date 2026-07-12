# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets.tenant.endpoint_group_bindings import (
    ACIEndpointGroupDomainBindingFilterSet,
)
from ...forms.tenant.endpoint_group_bindings import (
    ACIEndpointGroupDomainBindingBulkEditForm,
    ACIEndpointGroupDomainBindingEditForm,
    ACIEndpointGroupDomainBindingFilterForm,
    ACIEndpointGroupDomainBindingImportForm,
)
from ...models.access_policies.domains import ACIPhysicalDomain
from ...models.tenant.endpoint_group_bindings import ACIEndpointGroupDomainBinding
from ...models.tenant.endpoint_groups import ACIEndpointGroup, ACIUSegEndpointGroup
from ...object_actions import add_child_action
from ...tables.tenant.endpoint_group_bindings import (
    ACIEndpointGroupDomainBindingTable,
)

#
# Base children views
#


class ACIEndpointGroupDomainBindingChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI EPG Domain Bindings."""

    child_model = ACIEndpointGroupDomainBinding
    filterset = ACIEndpointGroupDomainBindingFilterSet
    tab = ViewTab(
        label=_("Domain Bindings"),
        badge=lambda obj: obj.aci_endpoint_group_domain_bindings.count(),
        permission="netbox_aci_plugin.view_aciendpointgroupdomainbinding",
        weight=1200,
    )
    table = ACIEndpointGroupDomainBindingTable

    def get_children(self, request, parent):
        """Return all ACIEndpointGroupDomainBinding objects."""
        return (
            ACIEndpointGroupDomainBinding.objects.restrict(request.user, "view")
            .select_related(
                "aci_epg_object_type",
                "aci_domain_object_type",
            )
            .prefetch_related(
                "aci_epg_object",
                "aci_domain_object",
                "tags",
            )
        )


#
# ACI Endpoint Group Domain Binding views
#


@register_model_view(ACIEndpointGroupDomainBinding)
class ACIEndpointGroupDomainBindingView(generic.ObjectView):
    """Detail view for displaying a single object of ACI EPG Domain Binding."""

    queryset = ACIEndpointGroupDomainBinding.objects.select_related(
        "aci_epg_object_type",
        "aci_domain_object_type",
    ).prefetch_related(
        "aci_epg_object",
        "aci_domain_object",
        "tags",
    )


@register_model_view(ACIEndpointGroupDomainBinding, "list", path="", detail=False)
class ACIEndpointGroupDomainBindingListView(generic.ObjectListView):
    """List view for listing all objects of ACIEndpointGroupDomainBinding."""

    queryset = ACIEndpointGroupDomainBinding.objects.select_related(
        "aci_epg_object_type",
        "aci_domain_object_type",
    ).prefetch_related(
        "aci_epg_object",
        "aci_domain_object",
        "tags",
    )
    filterset = ACIEndpointGroupDomainBindingFilterSet
    filterset_form = ACIEndpointGroupDomainBindingFilterForm
    table = ACIEndpointGroupDomainBindingTable


@register_model_view(ACIEndpointGroupDomainBinding, "add", detail=False)
@register_model_view(ACIEndpointGroupDomainBinding, "edit")
class ACIEndpointGroupDomainBindingEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACIEndpointGroupDomainBinding."""

    queryset = ACIEndpointGroupDomainBinding.objects.select_related(
        "aci_epg_object_type",
        "aci_domain_object_type",
    ).prefetch_related(
        "aci_epg_object",
        "aci_domain_object",
        "tags",
    )
    form = ACIEndpointGroupDomainBindingEditForm


@register_model_view(ACIEndpointGroupDomainBinding, "delete")
class ACIEndpointGroupDomainBindingDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACIEndpointGroupDomainBinding."""

    queryset = ACIEndpointGroupDomainBinding.objects.select_related(
        "aci_epg_object_type",
        "aci_domain_object_type",
    ).prefetch_related(
        "aci_epg_object",
        "aci_domain_object",
        "tags",
    )


@register_model_view(ACIEndpointGroup, "domainbindings", path="domain-bindings")
class ACIEndpointGroupDomainBindingsView(ACIEndpointGroupDomainBindingChildrenView):
    """Children view of ACI EPG Domain Bindings of an ACI Endpoint Group."""

    queryset = ACIEndpointGroup.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACIEndpointGroupDomainBinding",
            _("Bind a Domain"),
            url_params={
                "aci_fabric": lambda ctx: ctx["object"].aci_tenant.aci_fabric_id,
                "aci_epg_object": lambda ctx: ctx["object"].pk,
                "aci_epg_object_type": lambda ctx: (
                    ContentType.objects.get_for_model(ctx["object"]).pk
                ),
            },
        ),
    ) + ACIEndpointGroupDomainBindingChildrenView.actions

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super().get_children(request, parent).filter(aci_endpoint_group=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACI EPG object columns hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACI EPG object type column
        table.columns.hide("aci_epg_object_type")
        # Hide ACI EPG object column
        table.columns.hide("aci_epg_object")

        return table


@register_model_view(ACIUSegEndpointGroup, "domainbindings", path="domain-bindings")
class ACIUSegEndpointGroupDomainBindingView(ACIEndpointGroupDomainBindingChildrenView):
    """Children view of ACI EPG Domain Bindings of an ACI uSeg EPG."""

    queryset = ACIUSegEndpointGroup.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACIEndpointGroupDomainBinding",
            _("Bind a Domain"),
            url_params={
                "aci_fabric": lambda ctx: ctx["object"].aci_tenant.aci_fabric_id,
                "aci_epg_object": lambda ctx: ctx["object"].pk,
                "aci_epg_object_type": lambda ctx: (
                    ContentType.objects.get_for_model(ctx["object"]).pk
                ),
            },
        ),
    ) + ACIEndpointGroupDomainBindingChildrenView.actions

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_useg_endpoint_group=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACI EPG object columns hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACI EPG object type column
        table.columns.hide("aci_epg_object_type")
        # Hide ACI EPG object column
        table.columns.hide("aci_epg_object")

        return table


@register_model_view(ACIPhysicalDomain, "endpointgroupbindings", path="endpoint-groups")
class ACIPhysicalDomainEndpointGroupBindingsView(
    ACIEndpointGroupDomainBindingChildrenView
):
    """Children view of ACI EPG Domain Bindings of an ACI Physical Domain."""

    queryset = ACIPhysicalDomain.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACIEndpointGroupDomainBinding",
            _("Bind an Endpoint Group"),
            url_params={
                "aci_fabric": lambda ctx: ctx["object"].aci_fabric_id,
                "aci_domain_object": lambda ctx: ctx["object"].pk,
                "aci_domain_object_type": lambda ctx: (
                    ContentType.objects.get_for_model(ctx["object"]).pk
                ),
            },
        ),
    ) + ACIEndpointGroupDomainBindingChildrenView.actions
    tab = ViewTab(
        label=_("Endpoint Groups"),
        badge=lambda obj: obj.aci_endpoint_group_domain_bindings.count(),
        permission="netbox_aci_plugin.view_aciendpointgroupdomainbinding",
        weight=1200,
    )

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super().get_children(request, parent).filter(aci_physical_domain=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACI domain object columns hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACI domain object type column
        table.columns.hide("aci_domain_object_type")
        # Hide ACI domain object column
        table.columns.hide("aci_domain_object")

        return table


@register_model_view(
    ACIEndpointGroupDomainBinding, "bulk_import", path="import", detail=False
)
class ACIEndpointGroupDomainBindingBulkImportView(generic.BulkImportView):
    """Bulk import view for importing Endpoint Group Domain Binding objects."""

    queryset = ACIEndpointGroupDomainBinding.objects.all()
    model_form = ACIEndpointGroupDomainBindingImportForm


@register_model_view(
    ACIEndpointGroupDomainBinding, "bulk_edit", path="edit", detail=False
)
class ACIEndpointGroupDomainBindingBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing Endpoint Group Domain Binding objects."""

    queryset = ACIEndpointGroupDomainBinding.objects.all()
    filterset = ACIEndpointGroupDomainBindingFilterSet
    table = ACIEndpointGroupDomainBindingTable
    form = ACIEndpointGroupDomainBindingBulkEditForm


@register_model_view(
    ACIEndpointGroupDomainBinding, "bulk_delete", path="delete", detail=False
)
class ACIEndpointGroupDomainBindingBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting Endpoint Group Domain Binding objects."""

    queryset = ACIEndpointGroupDomainBinding.objects.all()
    filterset = ACIEndpointGroupDomainBindingFilterSet
    table = ACIEndpointGroupDomainBindingTable
