# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroupFilterSet,
    ACIEsgEndpointGroupSelectorFilterSet,
    ACIEsgEndpointSelectorFilterSet,
)
from ...forms.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroupBulkEditForm,
    ACIEndpointSecurityGroupEditForm,
    ACIEndpointSecurityGroupFilterForm,
    ACIEndpointSecurityGroupImportForm,
    ACIEsgEndpointGroupSelectorBulkEditForm,
    ACIEsgEndpointGroupSelectorEditForm,
    ACIEsgEndpointGroupSelectorFilterForm,
    ACIEsgEndpointGroupSelectorImportForm,
    ACIEsgEndpointSelectorBulkEditForm,
    ACIEsgEndpointSelectorEditForm,
    ACIEsgEndpointSelectorFilterForm,
    ACIEsgEndpointSelectorImportForm,
)
from ...models.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroup,
    ACIEsgEndpointGroupSelector,
    ACIEsgEndpointSelector,
)
from ...tables.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroupTable,
    ACIEsgEndpointGroupSelectorTable,
    ACIEsgEndpointSelectorTable,
)
from .contracts import ACIContractRelationChildrenView

#
# Base children views
#


class ACIEndpointSecurityGroupChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of Endpoint Security Group."""

    child_model = ACIEndpointSecurityGroup
    filterset = ACIEndpointSecurityGroupFilterSet
    tab = ViewTab(
        label=_("Endpoint Security Groups"),
        badge=lambda obj: obj.aci_endpoint_security_groups.count(),
        permission="netbox_aci_plugin.view_aciendpointsecuritygroup",
        weight=1000,
    )
    table = ACIEndpointSecurityGroupTable

    def get_children(self, request, parent):
        """Return all objects of ACIEndpointSecurityGroup."""
        return ACIEndpointSecurityGroup.objects.restrict(
            request.user, "view"
        ).prefetch_related(
            "aci_app_profile",
            "aci_vrf",
            "nb_tenant",
            "tags",
        )


class ACIEsgEndpointGroupSelectorChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI ESG EPG Selector."""

    child_model = ACIEsgEndpointGroupSelector
    filterset = ACIEsgEndpointGroupSelectorFilterSet
    tab = ViewTab(
        label=_("EPG Selectors"),
        badge=lambda obj: obj.aci_esg_endpoint_group_selectors.count(),
        permission="netbox_aci_plugin.view_aciesgendpointgroupselector",
        weight=1000,
    )
    table = ACIEsgEndpointGroupSelectorTable

    def get_children(self, request, parent):
        """Return all objects of ACIEsgEndpointGroupSelector."""
        return ACIEsgEndpointGroupSelector.objects.restrict(
            request.user, "view"
        ).prefetch_related(
            "aci_endpoint_security_group",
            "aci_epg_object",
            "nb_tenant",
            "tags",
        )


class ACIEsgEndpointSelectorChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI ESG Endpoint Selector."""

    child_model = ACIEsgEndpointSelector
    filterset = ACIEsgEndpointSelectorFilterSet
    tab = ViewTab(
        label=_("Endpoint Selectors"),
        badge=lambda obj: obj.aci_esg_endpoint_selectors.count(),
        permission="netbox_aci_plugin.view_aciesgendpointselector",
        weight=1000,
    )
    table = ACIEsgEndpointSelectorTable

    def get_children(self, request, parent):
        """Return all objects of ACIEsgEndpointSelector."""
        return ACIEsgEndpointSelector.objects.restrict(
            request.user, "view"
        ).prefetch_related(
            "aci_endpoint_security_group",
            "ep_object",
            "nb_tenant",
            "tags",
        )


#
# Endpoint Security Group views
#


@register_model_view(ACIEndpointSecurityGroup)
class ACIEndpointSecurityGroupView(generic.ObjectView):
    """Detail view for displaying a single object of ACI ESG."""

    queryset = ACIEndpointSecurityGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_vrf",
        "nb_tenant",
        "tags",
    )


@register_model_view(ACIEndpointSecurityGroup, "list", path="", detail=False)
class ACIEndpointSecurityGroupListView(generic.ObjectListView):
    """List view for listing all objects of ACI Endpoint Security Group."""

    queryset = ACIEndpointSecurityGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_vrf",
        "nb_tenant",
        "tags",
    )
    filterset = ACIEndpointSecurityGroupFilterSet
    filterset_form = ACIEndpointSecurityGroupFilterForm
    table = ACIEndpointSecurityGroupTable


@register_model_view(ACIEndpointSecurityGroup, "add", detail=False)
@register_model_view(ACIEndpointSecurityGroup, "edit")
class ACIEndpointSecurityGroupEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Endpoint Security Group."""

    queryset = ACIEndpointSecurityGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_vrf",
        "nb_tenant",
        "tags",
    )
    form = ACIEndpointSecurityGroupEditForm


@register_model_view(ACIEndpointSecurityGroup, "delete")
class ACIEndpointSecurityGroupDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Endpoint Security Group."""

    queryset = ACIEndpointSecurityGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_vrf",
        "nb_tenant",
        "tags",
    )


@register_model_view(
    ACIEndpointSecurityGroup, "contractrelations", path="contract-relations"
)
class ACIEndpointSecurityGroupContractRelationView(ACIContractRelationChildrenView):
    """Children view of ACI Contract Relation of ACI ESG."""

    queryset = ACIEndpointSecurityGroup.objects.all()
    template_name = (
        "netbox_aci_plugin/inc/aciendpointsecuritygroup/contractrelations.html"
    )

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_endpoint_security_group=parent.pk)
        )

    def get_extra_context(self, request, instance) -> dict:
        """Return ContentType as extra context."""
        aci_endpoint_security_group_content_type = ContentType.objects.get_for_model(
            ACIEndpointSecurityGroup
        )

        return {
            "content_type_id": aci_endpoint_security_group_content_type.id,
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


@register_model_view(ACIEndpointSecurityGroup, "epgselectors", path="epg-selectors")
class ACIEndpointSecurityGroupEsgEndpointGroupSelectorView(
    ACIEsgEndpointGroupSelectorChildrenView
):
    """Children view of ACI ESG Endpoint Group Selector of ACI ESG."""

    queryset = ACIEndpointSecurityGroup.objects.all()
    template_name = "netbox_aci_plugin/inc/aciendpointsecuritygroup/epgselectors.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_endpoint_security_group=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACI EndpointSecurityGroup colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACITenant column of ACIEndpointSecurityGroup
        table.columns.hide("aci_tenant")
        # Hide ACI AppProfile column
        table.columns.hide("aci_app_profile")
        # Hide ACI EndpointSecurityGroup column
        table.columns.hide("aci_endpoint_security_group")

        return table


@register_model_view(ACIEndpointSecurityGroup, "epselectors", path="ep-selectors")
class ACIEndpointSecurityGroupEsgEndpointSelectorView(
    ACIEsgEndpointSelectorChildrenView
):
    """Children view of ACI ESG Endpoint Selector of ACI ESG."""

    queryset = ACIEndpointSecurityGroup.objects.all()
    template_name = "netbox_aci_plugin/inc/aciendpointsecuritygroup/epselectors.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_endpoint_security_group=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACI EndpointSecurityGroup colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACITenant column of ACIEndpointSecurityGroup
        table.columns.hide("aci_tenant")
        # Hide ACI AppProfile column
        table.columns.hide("aci_app_profile")
        # Hide ACI EndpointSecurityGroup column
        table.columns.hide("aci_endpoint_security_group")

        return table


@register_model_view(
    ACIEndpointSecurityGroup, "bulk_import", path="import", detail=False
)
class ACIEndpointSecurityGroupBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI ESG."""

    queryset = ACIEndpointSecurityGroup.objects.all()
    model_form = ACIEndpointSecurityGroupImportForm


@register_model_view(ACIEndpointSecurityGroup, "bulk_edit", path="edit", detail=False)
class ACIEndpointSecurityGroupBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI ESG."""

    queryset = ACIEndpointSecurityGroup.objects.all()
    filterset = ACIEndpointSecurityGroupFilterSet
    table = ACIEndpointSecurityGroupTable
    form = ACIEndpointSecurityGroupBulkEditForm


@register_model_view(
    ACIEndpointSecurityGroup, "bulk_delete", path="delete", detail=False
)
class ACIEndpointSecurityGroupBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI ESG."""

    queryset = ACIEndpointSecurityGroup.objects.all()
    filterset = ACIEndpointSecurityGroupFilterSet
    table = ACIEndpointSecurityGroupTable


#
# ESG Endpoint Group (EPG) Selector views
#


@register_model_view(ACIEsgEndpointGroupSelector)
class ACIEsgEndpointGroupSelectorView(generic.ObjectView):
    """Detail view for displaying a single object of ACI ESG EPG Selector."""

    queryset = ACIEsgEndpointGroupSelector.objects.prefetch_related(
        "aci_endpoint_security_group",
        "aci_epg_object",
        "nb_tenant",
        "tags",
    )


@register_model_view(ACIEsgEndpointGroupSelector, "list", path="", detail=False)
class ACIEsgEndpointGroupSelectorListView(generic.ObjectListView):
    """List view for listing all objects of ACI ESG EPG Selector."""

    queryset = ACIEsgEndpointGroupSelector.objects.prefetch_related(
        "aci_endpoint_security_group",
        "aci_epg_object",
        "nb_tenant",
        "tags",
    )
    filterset = ACIEsgEndpointGroupSelectorFilterSet
    filterset_form = ACIEsgEndpointGroupSelectorFilterForm
    table = ACIEsgEndpointGroupSelectorTable


@register_model_view(ACIEsgEndpointGroupSelector, "add", detail=False)
@register_model_view(ACIEsgEndpointGroupSelector, "edit")
class ACIEsgEndpointGroupSelectorEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI ESG EPG Selector."""

    queryset = ACIEsgEndpointGroupSelector.objects.prefetch_related(
        "aci_endpoint_security_group",
        "aci_epg_object",
        "nb_tenant",
        "tags",
    )
    form = ACIEsgEndpointGroupSelectorEditForm


@register_model_view(ACIEsgEndpointGroupSelector, "delete")
class ACIEsgEndpointGroupSelectorDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI ESG EPG Selector."""

    queryset = ACIEsgEndpointGroupSelector.objects.prefetch_related(
        "aci_endpoint_security_group",
        "aci_epg_object",
        "nb_tenant",
        "tags",
    )


@register_model_view(
    ACIEsgEndpointGroupSelector, "bulk_import", path="import", detail=False
)
class ACIEsgEndpointGroupSelectorBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ESG EPG Selector."""

    queryset = ACIEsgEndpointGroupSelector.objects.all()
    model_form = ACIEsgEndpointGroupSelectorImportForm


@register_model_view(
    ACIEsgEndpointGroupSelector, "bulk_edit", path="edit", detail=False
)
class ACIEsgEndpointGroupSelectorBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI ESG EPG Selector."""

    queryset = ACIEsgEndpointGroupSelector.objects.all()
    filterset = ACIEsgEndpointGroupSelectorFilterSet
    table = ACIEsgEndpointGroupSelectorTable
    form = ACIEsgEndpointGroupSelectorBulkEditForm


@register_model_view(
    ACIEsgEndpointGroupSelector, "bulk_delete", path="delete", detail=False
)
class ACIEsgEndpointGroupSelectorBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ESG EPG Selector."""

    queryset = ACIEsgEndpointGroupSelector.objects.all()
    filterset = ACIEsgEndpointGroupSelectorFilterSet
    table = ACIEsgEndpointGroupSelectorTable


#
# ESG Endpoint Selector views
#


@register_model_view(ACIEsgEndpointSelector)
class ACIEsgEndpointSelectorView(generic.ObjectView):
    """Detail view for displaying a single object of ACI ESG EP Selector."""

    queryset = ACIEsgEndpointSelector.objects.prefetch_related(
        "aci_endpoint_security_group",
        "ep_object",
        "nb_tenant",
        "tags",
    )


@register_model_view(ACIEsgEndpointSelector, "list", path="", detail=False)
class ACIEsgEndpointSelectorListView(generic.ObjectListView):
    """List view for listing all objects of ACI ESG Endpoint Selector."""

    queryset = ACIEsgEndpointSelector.objects.prefetch_related(
        "aci_endpoint_security_group",
        "ep_object",
        "nb_tenant",
        "tags",
    )
    filterset = ACIEsgEndpointSelectorFilterSet
    filterset_form = ACIEsgEndpointSelectorFilterForm
    table = ACIEsgEndpointSelectorTable


@register_model_view(ACIEsgEndpointSelector, "add", detail=False)
@register_model_view(ACIEsgEndpointSelector, "edit")
class ACIEsgEndpointSelectorEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI ESG Endpoint Selector."""

    queryset = ACIEsgEndpointSelector.objects.prefetch_related(
        "aci_endpoint_security_group",
        "ep_object",
        "nb_tenant",
        "tags",
    )
    form = ACIEsgEndpointSelectorEditForm


@register_model_view(ACIEsgEndpointSelector, "delete")
class ACIEsgEndpointSelectorDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI ESG Endpoint Selector."""

    queryset = ACIEsgEndpointSelector.objects.prefetch_related(
        "aci_endpoint_security_group",
        "ep_object",
        "nb_tenant",
        "tags",
    )


@register_model_view(ACIEsgEndpointSelector, "bulk_import", path="import", detail=False)
class ACIEsgEndpointSelectorBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ESG EP Selector."""

    queryset = ACIEsgEndpointSelector.objects.all()
    model_form = ACIEsgEndpointSelectorImportForm


@register_model_view(ACIEsgEndpointSelector, "bulk_edit", path="edit", detail=False)
class ACIEsgEndpointSelectorBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI ESG EP Selector."""

    queryset = ACIEsgEndpointSelector.objects.all()
    filterset = ACIEsgEndpointSelectorFilterSet
    table = ACIEsgEndpointSelectorTable
    form = ACIEsgEndpointSelectorBulkEditForm


@register_model_view(ACIEsgEndpointSelector, "bulk_delete", path="delete", detail=False)
class ACIEsgEndpointSelectorBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ESG EP Selector."""

    queryset = ACIEsgEndpointSelector.objects.all()
    filterset = ACIEsgEndpointSelectorFilterSet
    table = ACIEsgEndpointSelectorTable
