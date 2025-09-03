# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets.tenant.endpoint_groups import (
    ACIEndpointGroupFilterSet,
    ACIUSegEndpointGroupFilterSet,
    ACIUSegNetworkAttributeFilterSet,
)
from ...forms.tenant.endpoint_groups import (
    ACIEndpointGroupBulkEditForm,
    ACIEndpointGroupEditForm,
    ACIEndpointGroupFilterForm,
    ACIEndpointGroupImportForm,
    ACIUSegEndpointGroupBulkEditForm,
    ACIUSegEndpointGroupEditForm,
    ACIUSegEndpointGroupFilterForm,
    ACIUSegEndpointGroupImportForm,
    ACIUSegNetworkAttributeBulkEditForm,
    ACIUSegNetworkAttributeEditForm,
    ACIUSegNetworkAttributeFilterForm,
    ACIUSegNetworkAttributeImportForm,
)
from ...models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
    ACIUSegNetworkAttribute,
)
from ...tables.tenant.endpoint_groups import (
    ACIEndpointGroupTable,
    ACIUSegEndpointGroupTable,
    ACIUSegNetworkAttributeTable,
)
from .contracts import ACIContractRelationChildrenView

#
# Base children views
#


class ACIEndpointGroupChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Endpoint Group."""

    child_model = ACIEndpointGroup
    filterset = ACIEndpointGroupFilterSet
    tab = ViewTab(
        label=_("Endpoint Groups"),
        badge=lambda obj: obj.aci_endpoint_groups.count(),
        permission="netbox_aci_plugin.view_aciendpointgroup",
        weight=1000,
    )
    table = ACIEndpointGroupTable

    def get_children(self, request, parent):
        """Return all objects of ACIEndpointGroup."""
        return ACIEndpointGroup.objects.restrict(request.user, "view").prefetch_related(
            "aci_app_profile",
            "aci_bridge_domain",
            "nb_tenant",
            "tags",
        )


class ACIUSegEndpointGroupChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI uSeg Endpoint Group."""

    child_model = ACIUSegEndpointGroup
    filterset = ACIUSegEndpointGroupFilterSet
    tab = ViewTab(
        label=_("uSeg Endpoint Groups"),
        badge=lambda obj: obj.aci_useg_endpoint_groups.count(),
        permission="netbox_aci_plugin.view_aciusegendpointgroup",
        weight=1000,
    )
    table = ACIUSegEndpointGroupTable

    def get_children(self, request, parent):
        """Return all objects of ACIUSegEndpointGroup."""
        return ACIUSegEndpointGroup.objects.restrict(
            request.user, "view"
        ).prefetch_related(
            "aci_app_profile",
            "aci_bridge_domain",
            "nb_tenant",
            "tags",
        )


class ACIUSegNetworkAttributeChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI uSeg Network Attribute."""

    child_model = ACIUSegNetworkAttribute
    filterset = ACIUSegNetworkAttributeFilterSet
    tab = ViewTab(
        label=_("Network Attributes"),
        badge=lambda obj: obj.aci_useg_network_attributes.count(),
        permission="netbox_aci_plugin.view_aciusegnetworkattribute",
        weight=1000,
    )
    table = ACIUSegNetworkAttributeTable

    def get_children(self, request, parent):
        """Return all objects of ACIUSegNetworkAttribute."""
        return ACIUSegNetworkAttribute.objects.restrict(
            request.user, "view"
        ).prefetch_related(
            "aci_useg_endpoint_group",
            "attr_object_type",
            "attr_object",
            "nb_tenant",
            "tags",
        )


#
# Endpoint Group views
#


@register_model_view(ACIEndpointGroup)
class ACIEndpointGroupView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Endpoint Group."""

    queryset = ACIEndpointGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
        "tags",
    )


@register_model_view(ACIEndpointGroup, "list", path="", detail=False)
class ACIEndpointGroupListView(generic.ObjectListView):
    """List view for listing all objects of ACI Endpoint Group."""

    queryset = ACIEndpointGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
        "tags",
    )
    filterset = ACIEndpointGroupFilterSet
    filterset_form = ACIEndpointGroupFilterForm
    table = ACIEndpointGroupTable


@register_model_view(ACIEndpointGroup, "add", detail=False)
@register_model_view(ACIEndpointGroup, "edit")
class ACIEndpointGroupEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Endpoint Group."""

    queryset = ACIEndpointGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
        "tags",
    )
    form = ACIEndpointGroupEditForm


@register_model_view(ACIEndpointGroup, "delete")
class ACIEndpointGroupDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Endpoint Group."""

    queryset = ACIEndpointGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
        "tags",
    )


@register_model_view(ACIEndpointGroup, "contractrelations", path="contract-relations")
class ACIEndpointGroupContractRelationView(ACIContractRelationChildrenView):
    """Children view of ACI Contract Relation of ACI Endpoint Group."""

    queryset = ACIEndpointGroup.objects.all()
    template_name = "netbox_aci_plugin/inc/aciendpointgroup/contractrelations.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super().get_children(request, parent).filter(aci_endpoint_group=parent.pk)
        )

    def get_extra_context(self, request, instance) -> dict:
        """Return ContentType as extra context."""
        aci_endpoint_group_content_type = ContentType.objects.get_for_model(
            ACIEndpointGroup
        )

        return {
            "content_type_id": aci_endpoint_group_content_type.id,
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


@register_model_view(ACIEndpointGroup, "bulk_import", path="import", detail=False)
class ACIEndpointGroupBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACIEndpointGroup."""

    queryset = ACIEndpointGroup.objects.all()
    model_form = ACIEndpointGroupImportForm


@register_model_view(ACIEndpointGroup, "bulk_edit", path="edit", detail=False)
class ACIEndpointGroupBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI Endpoint Group."""

    queryset = ACIEndpointGroup.objects.all()
    filterset = ACIEndpointGroupFilterSet
    table = ACIEndpointGroupTable
    form = ACIEndpointGroupBulkEditForm


@register_model_view(ACIEndpointGroup, "bulk_delete", path="delete", detail=False)
class ACIEndpointGroupBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI Endpoint Group."""

    queryset = ACIEndpointGroup.objects.all()
    filterset = ACIEndpointGroupFilterSet
    table = ACIEndpointGroupTable


#
# uSeg Endpoint Group views
#


@register_model_view(ACIUSegEndpointGroup)
class ACIUSegEndpointGroupView(generic.ObjectView):
    """Detail view for displaying a single object of ACI uSeg EPG."""

    queryset = ACIUSegEndpointGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
        "tags",
    )


@register_model_view(ACIUSegEndpointGroup, "list", path="", detail=False)
class ACIUSegEndpointGroupListView(generic.ObjectListView):
    """List view for listing all objects of ACI uSeg Endpoint Group."""

    queryset = ACIUSegEndpointGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
        "tags",
    )
    filterset = ACIUSegEndpointGroupFilterSet
    filterset_form = ACIUSegEndpointGroupFilterForm
    table = ACIUSegEndpointGroupTable


@register_model_view(ACIUSegEndpointGroup, "add", detail=False)
@register_model_view(ACIUSegEndpointGroup, "edit")
class ACIUSegEndpointGroupEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI uSeg Endpoint Group."""

    queryset = ACIUSegEndpointGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
        "tags",
    )
    form = ACIUSegEndpointGroupEditForm


@register_model_view(ACIUSegEndpointGroup, "delete")
class ACIUSegEndpointGroupDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI uSeg Endpoint Group."""

    queryset = ACIUSegEndpointGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
        "tags",
    )


@register_model_view(
    ACIUSegEndpointGroup, "contractrelations", path="contract-relations"
)
class ACIUSegEndpointGroupContractRelationView(ACIContractRelationChildrenView):
    """Children view of ACI Contract Relation of ACI uSeg Endpoint Group."""

    queryset = ACIUSegEndpointGroup.objects.all()
    template_name = "netbox_aci_plugin/inc/aciusegendpointgroup/contractrelations.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_useg_endpoint_group=parent.pk)
        )

    def get_extra_context(self, request, instance) -> dict:
        """Return ContentType as extra context."""
        aci_useg_endpoint_group_content_type = ContentType.objects.get_for_model(
            ACIUSegEndpointGroup
        )

        return {
            "content_type_id": aci_useg_endpoint_group_content_type.id,
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


@register_model_view(
    ACIUSegEndpointGroup, "usegnetworkattributes", path="network-attributes"
)
class ACIUSegEndpointGroupUSegNetworkAttributeView(ACIUSegNetworkAttributeChildrenView):
    """Children view of ACI uSeg Network Attribute of uSeg Endpoint Group."""

    queryset = ACIUSegEndpointGroup.objects.all()
    template_name = "netbox_aci_plugin/inc/aciusegendpointgroup/networkattributes.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_useg_endpoint_group=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACIUSegEndpointGroup colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACITenant column of ACIContract
        table.columns.hide("aci_tenant")
        # Hide ACIUSegEndpointGroup column
        table.columns.hide("aci_useg_endpoint_group")

        return table


@register_model_view(ACIUSegEndpointGroup, "bulk_import", path="import", detail=False)
class ACIUSegEndpointGroupBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of uSegEndpointGroup."""

    queryset = ACIUSegEndpointGroup.objects.all()
    model_form = ACIUSegEndpointGroupImportForm


@register_model_view(ACIUSegEndpointGroup, "bulk_edit", path="edit", detail=False)
class ACIUSegEndpointGroupBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of uSegEndpointGroup."""

    queryset = ACIUSegEndpointGroup.objects.all()
    filterset = ACIUSegEndpointGroupFilterSet
    table = ACIUSegEndpointGroupTable
    form = ACIUSegEndpointGroupBulkEditForm


@register_model_view(ACIUSegEndpointGroup, "bulk_delete", path="delete", detail=False)
class ACIUSegEndpointGroupBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of uSegEndpointGroup."""

    queryset = ACIUSegEndpointGroup.objects.all()
    filterset = ACIUSegEndpointGroupFilterSet
    table = ACIUSegEndpointGroupTable


#
# uSeg Network Attribute views
#


@register_model_view(ACIUSegNetworkAttribute)
class ACIUSegNetworkAttributeView(generic.ObjectView):
    """Detail view for displaying a single object of uSeg Network Attribute."""

    queryset = ACIUSegNetworkAttribute.objects.prefetch_related(
        "aci_useg_endpoint_group",
        "attr_object",
        "nb_tenant",
        "tags",
    )


@register_model_view(ACIUSegNetworkAttribute, "list", path="", detail=False)
class ACIUSegNetworkAttributeListView(generic.ObjectListView):
    """List view for listing all objects of ACI uSeg Network Attribute."""

    queryset = ACIUSegNetworkAttribute.objects.prefetch_related(
        "aci_useg_endpoint_group",
        "attr_object",
        "nb_tenant",
        "tags",
    )
    filterset = ACIUSegNetworkAttributeFilterSet
    filterset_form = ACIUSegNetworkAttributeFilterForm
    table = ACIUSegNetworkAttributeTable


@register_model_view(ACIUSegNetworkAttribute, "add", detail=False)
@register_model_view(ACIUSegNetworkAttribute, "edit")
class ACIUSegNetworkAttributeEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI uSeg Network Attribute."""

    queryset = ACIUSegNetworkAttribute.objects.prefetch_related(
        "aci_useg_endpoint_group",
        "attr_object",
        "nb_tenant",
        "tags",
    )
    form = ACIUSegNetworkAttributeEditForm


@register_model_view(ACIUSegNetworkAttribute, "delete")
class ACIUSegNetworkAttributeDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI uSeg Network Attribute."""

    queryset = ACIUSegNetworkAttribute.objects.prefetch_related(
        "aci_useg_endpoint_group",
        "attr_object",
        "nb_tenant",
        "tags",
    )


@register_model_view(
    ACIUSegNetworkAttribute, "bulk_import", path="import", detail=False
)
class ACIUSegNetworkAttributeBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of Network Attribute."""

    queryset = ACIUSegNetworkAttribute.objects.all()
    model_form = ACIUSegNetworkAttributeImportForm


@register_model_view(ACIUSegNetworkAttribute, "bulk_edit", path="edit", detail=False)
class ACIUSegNetworkAttributeBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of Network Attribute."""

    queryset = ACIUSegNetworkAttribute.objects.all()
    filterset = ACIUSegNetworkAttributeFilterSet
    table = ACIUSegNetworkAttributeTable
    form = ACIUSegNetworkAttributeBulkEditForm


@register_model_view(
    ACIUSegNetworkAttribute, "bulk_delete", path="delete", detail=False
)
class ACIUSegNetworkAttributeBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of Network Attribute."""

    queryset = ACIUSegNetworkAttribute.objects.all()
    filterset = ACIUSegNetworkAttributeFilterSet
    table = ACIUSegNetworkAttributeTable
