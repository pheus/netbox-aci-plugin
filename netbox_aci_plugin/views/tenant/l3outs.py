# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Views for tenant L3Out models."""

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets.tenant.l3outs import (
    ACIExternalEndpointGroupFilterSet,
    ACIExternalSubnetFilterSet,
    ACIL3OutFilterSet,
)
from ...forms.tenant.l3outs import (
    ACIExternalEndpointGroupBulkEditForm,
    ACIExternalEndpointGroupEditForm,
    ACIExternalEndpointGroupFilterForm,
    ACIExternalEndpointGroupImportForm,
    ACIExternalSubnetBulkEditForm,
    ACIExternalSubnetEditForm,
    ACIExternalSubnetFilterForm,
    ACIExternalSubnetImportForm,
    ACIL3OutBulkEditForm,
    ACIL3OutEditForm,
    ACIL3OutFilterForm,
    ACIL3OutImportForm,
)
from ...models.access_policies.domains import ACIRoutedDomain
from ...models.tenant.l3outs import (
    ACIExternalEndpointGroup,
    ACIExternalSubnet,
    ACIL3Out,
)
from ...tables.tenant.l3outs import (
    ACIExternalEndpointGroupReducedTable,
    ACIExternalEndpointGroupTable,
    ACIExternalSubnetReducedTable,
    ACIExternalSubnetTable,
    ACIL3OutTable,
)
from .contracts import ACIContractRelationChildrenView


#
# Base children views
#
class ACIL3OutChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI L3Outs."""

    child_model = ACIL3Out
    filterset = ACIL3OutFilterSet
    tab = ViewTab(
        label=_("L3Outs"),
        badge=lambda obj: obj.aci_l3outs.count(),
        permission="netbox_aci_plugin.view_acil3out",
        weight=1000,
    )
    table = ACIL3OutTable

    def get_children(self, request, parent):
        """Return all objects of ACIL3Out."""
        return (
            ACIL3Out.objects.restrict(request.user, "view")
            .select_related(
                "aci_tenant",
                "aci_vrf",
                "aci_routed_domain",
                "nb_tenant",
                "owner",
            )
            .prefetch_related("tags")
        )


class ACIExternalEndpointGroupChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching ACI External EPGs."""

    child_model = ACIExternalEndpointGroup
    filterset = ACIExternalEndpointGroupFilterSet
    tab = ViewTab(
        label=_("External EPGs"),
        badge=lambda obj: obj.aci_external_endpoint_groups.count(),
        permission="netbox_aci_plugin.view_aciexternalendpointgroup",
        weight=1000,
    )
    table = ACIExternalEndpointGroupTable

    def get_children(self, request, parent):
        """Return all objects of ACIExternalEndpointGroup."""
        return (
            ACIExternalEndpointGroup.objects.restrict(request.user, "view")
            .select_related(
                "aci_l3out",
                "aci_l3out__aci_tenant",
                "aci_l3out__aci_vrf",
                "nb_tenant",
                "owner",
            )
            .prefetch_related("tags")
        )


class ACIExternalSubnetChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching ACI External Subnets."""

    child_model = ACIExternalSubnet
    filterset = ACIExternalSubnetFilterSet
    tab = ViewTab(
        label=_("External Subnets"),
        badge=lambda obj: obj.aci_external_subnets.count(),
        permission="netbox_aci_plugin.view_aciexternalsubnet",
        weight=1000,
    )
    table = ACIExternalSubnetTable

    def get_children(self, request, parent):
        """Return all objects of ACIExternalSubnet."""
        return (
            ACIExternalSubnet.objects.restrict(request.user, "view")
            .select_related(
                "aci_external_endpoint_group",
                "aci_external_endpoint_group__aci_l3out",
                "nb_prefix",
                "nb_tenant",
                "owner",
            )
            .prefetch_related("tags")
        )


#
# L3Out views
#
@register_model_view(ACIL3Out)
class ACIL3OutView(generic.ObjectView):
    """Detail view for displaying a single object of ACI L3Out."""

    queryset = ACIL3Out.objects.select_related(
        "aci_tenant",
        "aci_vrf",
        "aci_routed_domain",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")

    def get_extra_context(self, request, instance) -> dict:
        """Return related External EPGs as extra context."""
        external_endpoint_groups_table = ACIExternalEndpointGroupReducedTable(
            instance.aci_external_endpoint_groups.all()
        )
        external_endpoint_groups_table.configure(request=request)
        return {
            "external_endpoint_groups_table": external_endpoint_groups_table,
        }


@register_model_view(ACIL3Out, "list", path="", detail=False)
class ACIL3OutListView(generic.ObjectListView):
    """List view for listing all objects of ACI L3Out."""

    queryset = ACIL3Out.objects.select_related(
        "aci_tenant",
        "aci_vrf",
        "aci_routed_domain",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    table = ACIL3OutTable
    filterset = ACIL3OutFilterSet
    filterset_form = ACIL3OutFilterForm


@register_model_view(ACIL3Out, "add", detail=False)
@register_model_view(ACIL3Out, "edit")
class ACIL3OutEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI L3Out."""

    queryset = ACIL3Out.objects.select_related(
        "aci_tenant",
        "aci_vrf",
        "aci_routed_domain",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    form = ACIL3OutEditForm


@register_model_view(ACIL3Out, "delete")
class ACIL3OutDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI L3Out."""

    queryset = ACIL3Out.objects.select_related(
        "aci_tenant",
        "aci_vrf",
        "aci_routed_domain",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")


@register_model_view(
    ACIL3Out, "externalendpointgroups", path="external-endpoint-groups"
)
class ACIL3OutExternalEndpointGroupsView(ACIExternalEndpointGroupChildrenView):
    """Children view of ACI External EPGs of ACI L3Out."""

    queryset = ACIL3Out.objects.all()
    template_name = "netbox_aci_plugin/inc/acil3out/externalendpointgroups.html"

    def get_children(self, request, parent):
        """Return all children objects of the current parent object."""
        return super().get_children(request, parent).filter(aci_l3out=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return table with ACI L3Out column hidden."""
        table = super().get_table(*args, **kwargs)
        table.columns.hide("aci_l3out")
        return table


@register_model_view(ACIL3Out, "bulk_import", path="import", detail=False)
class ACIL3OutBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI L3Out."""

    queryset = ACIL3Out.objects.all()
    model_form = ACIL3OutImportForm


@register_model_view(ACIL3Out, "bulk_edit", path="edit", detail=False)
class ACIL3OutBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI L3Out."""

    queryset = ACIL3Out.objects.all()
    filterset = ACIL3OutFilterSet
    table = ACIL3OutTable
    form = ACIL3OutBulkEditForm


@register_model_view(ACIL3Out, "bulk_delete", path="delete", detail=False)
class ACIL3OutBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI L3Out."""

    queryset = ACIL3Out.objects.all()
    filterset = ACIL3OutFilterSet
    table = ACIL3OutTable


@register_model_view(ACIRoutedDomain, "l3outs")
class ACIRoutedDomainL3OutsView(ACIL3OutChildrenView):
    """Children view of ACI L3Outs of ACI Routed Domain."""

    queryset = ACIRoutedDomain.objects.all()
    template_name = "netbox_aci_plugin/inc/acirouteddomain/l3outs.html"

    def get_children(self, request, parent):
        """Return all children objects of the current parent object."""
        return super().get_children(request, parent).filter(aci_routed_domain=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return table with ACI Routed Domain column hidden."""
        table = super().get_table(*args, **kwargs)
        table.columns.hide("aci_routed_domain")
        return table


#
# External Endpoint Group views
#
@register_model_view(ACIExternalEndpointGroup)
class ACIExternalEndpointGroupView(generic.ObjectView):
    """Detail view for displaying a single object of ACI External EPG."""

    queryset = ACIExternalEndpointGroup.objects.select_related(
        "aci_l3out", "aci_l3out__aci_tenant", "aci_l3out__aci_vrf", "nb_tenant", "owner"
    ).prefetch_related("tags")

    def get_extra_context(self, request, instance) -> dict:
        """Return related subnets as extra context."""
        subnets_table = ACIExternalSubnetReducedTable(
            instance.aci_external_subnets.all()
        )
        subnets_table.configure(request=request)
        return {
            "subnets_table": subnets_table,
        }


@register_model_view(ACIExternalEndpointGroup, "list", path="", detail=False)
class ACIExternalEndpointGroupListView(generic.ObjectListView):
    """List view for listing all objects of ACI External EPG."""

    queryset = ACIExternalEndpointGroup.objects.select_related(
        "aci_l3out", "aci_l3out__aci_tenant", "aci_l3out__aci_vrf", "nb_tenant", "owner"
    ).prefetch_related("tags")
    table = ACIExternalEndpointGroupTable
    filterset = ACIExternalEndpointGroupFilterSet
    filterset_form = ACIExternalEndpointGroupFilterForm


@register_model_view(ACIExternalEndpointGroup, "add", detail=False)
@register_model_view(ACIExternalEndpointGroup, "edit")
class ACIExternalEndpointGroupEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI External EPG."""

    queryset = ACIExternalEndpointGroup.objects.select_related(
        "aci_l3out", "aci_l3out__aci_tenant", "aci_l3out__aci_vrf", "nb_tenant", "owner"
    ).prefetch_related("tags")
    form = ACIExternalEndpointGroupEditForm


@register_model_view(ACIExternalEndpointGroup, "delete")
class ACIExternalEndpointGroupDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI External EPG."""

    queryset = ACIExternalEndpointGroup.objects.select_related(
        "aci_l3out", "aci_l3out__aci_tenant", "aci_l3out__aci_vrf", "nb_tenant", "owner"
    ).prefetch_related("tags")


@register_model_view(ACIExternalEndpointGroup, "subnets")
class ACIExternalEndpointGroupExternalSubnetView(ACIExternalSubnetChildrenView):
    """Children view of ACI External Subnets of ACI External EPG."""

    queryset = ACIExternalEndpointGroup.objects.all()
    template_name = "netbox_aci_plugin/inc/aciexternalendpointgroup/subnets.html"

    def get_children(self, request, parent):
        """Return all children objects of the current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_external_endpoint_group=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return table with External EPG column hidden."""
        table = super().get_table(*args, **kwargs)
        table.columns.hide("aci_external_endpoint_group")
        return table


@register_model_view(
    ACIExternalEndpointGroup, "contractrelations", path="contract-relations"
)
class ACIExternalEndpointGroupContractRelationView(ACIContractRelationChildrenView):
    """Children view of ACI Contract Relation of ACI External EPG."""

    queryset = ACIExternalEndpointGroup.objects.all()
    template_name = (
        "netbox_aci_plugin/inc/aciexternalendpointgroup/contractrelations.html"
    )

    def get_children(self, request, parent):
        """Return all children objects of the current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(_aci_external_endpoint_group=parent.pk)
        )

    def get_extra_context(self, request, instance) -> dict:
        """Return ContentType as extra context."""
        content_type = ContentType.objects.get_for_model(ACIExternalEndpointGroup)
        return {"content_type_id": content_type.id}

    def get_table(self, *args, **kwargs):
        """Return the table with ACI object columns hidden."""
        table = super().get_table(*args, **kwargs)
        table.columns.hide("aci_contract_tenant")
        table.columns.hide("aci_object_type")
        table.columns.hide("aci_object")
        return table


@register_model_view(
    ACIExternalEndpointGroup, "bulk_import", path="import", detail=False
)
class ACIExternalEndpointGroupBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI External EPG."""

    queryset = ACIExternalEndpointGroup.objects.all()
    model_form = ACIExternalEndpointGroupImportForm


@register_model_view(ACIExternalEndpointGroup, "bulk_edit", path="edit", detail=False)
class ACIExternalEndpointGroupBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI External EPG."""

    queryset = ACIExternalEndpointGroup.objects.all()
    filterset = ACIExternalEndpointGroupFilterSet
    table = ACIExternalEndpointGroupTable
    form = ACIExternalEndpointGroupBulkEditForm


@register_model_view(
    ACIExternalEndpointGroup, "bulk_delete", path="delete", detail=False
)
class ACIExternalEndpointGroupBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI External EPG."""

    queryset = ACIExternalEndpointGroup.objects.all()
    filterset = ACIExternalEndpointGroupFilterSet
    table = ACIExternalEndpointGroupTable


#
# External Subnet views
#
@register_model_view(ACIExternalSubnet)
class ACIExternalSubnetView(generic.ObjectView):
    """Detail view for displaying a single object of ACI External Subnet."""

    queryset = ACIExternalSubnet.objects.select_related(
        "aci_external_endpoint_group",
        "aci_external_endpoint_group__aci_l3out",
        "nb_prefix",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")


@register_model_view(ACIExternalSubnet, "list", path="", detail=False)
class ACIExternalSubnetListView(generic.ObjectListView):
    """List view for listing all objects of ACI External Subnet."""

    queryset = ACIExternalSubnet.objects.select_related(
        "aci_external_endpoint_group",
        "aci_external_endpoint_group__aci_l3out",
        "nb_prefix",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    table = ACIExternalSubnetTable
    filterset = ACIExternalSubnetFilterSet
    filterset_form = ACIExternalSubnetFilterForm


@register_model_view(ACIExternalSubnet, "add", detail=False)
@register_model_view(ACIExternalSubnet, "edit")
class ACIExternalSubnetEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI External Subnet."""

    queryset = ACIExternalSubnet.objects.select_related(
        "aci_external_endpoint_group",
        "aci_external_endpoint_group__aci_l3out",
        "nb_prefix",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")
    form = ACIExternalSubnetEditForm


@register_model_view(ACIExternalSubnet, "delete")
class ACIExternalSubnetDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI External Subnet."""

    queryset = ACIExternalSubnet.objects.select_related(
        "aci_external_endpoint_group",
        "aci_external_endpoint_group__aci_l3out",
        "nb_prefix",
        "nb_tenant",
        "owner",
    ).prefetch_related("tags")


@register_model_view(ACIExternalSubnet, "bulk_import", path="import", detail=False)
class ACIExternalSubnetBulkImportView(generic.BulkImportView):
    """Bulk import view for ACI External Subnet objects."""

    queryset = ACIExternalSubnet.objects.all()
    model_form = ACIExternalSubnetImportForm


@register_model_view(ACIExternalSubnet, "bulk_edit", path="edit", detail=False)
class ACIExternalSubnetBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI External Subnet."""

    queryset = ACIExternalSubnet.objects.all()
    filterset = ACIExternalSubnetFilterSet
    table = ACIExternalSubnetTable
    form = ACIExternalSubnetBulkEditForm


@register_model_view(ACIExternalSubnet, "bulk_delete", path="delete", detail=False)
class ACIExternalSubnetBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for ACI External Subnet objects."""

    queryset = ACIExternalSubnet.objects.all()
    filterset = ACIExternalSubnetFilterSet
    table = ACIExternalSubnetTable
