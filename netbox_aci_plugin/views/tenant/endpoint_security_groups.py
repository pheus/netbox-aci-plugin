# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets.tenant.app_profiles import ACIAppProfileFilterSet
from ...filtersets.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroupFilterSet,
)
from ...forms.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroupBulkEditForm,
    ACIEndpointSecurityGroupEditForm,
    ACIEndpointSecurityGroupFilterForm,
    ACIEndpointSecurityGroupImportForm,
)
from ...models.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroup,
)
from ...tables.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroupTable,
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


#
# Endpoint Security Group views
#


@register_model_view(ACIEndpointSecurityGroup)
class ACIEndpointSecurityGroupView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Endpoint Security Group."""

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
class ACIEndpointSecurityGroupContractRelationView(
    ACIContractRelationChildrenView
):
    """Children view of ACI Contract Relation of ACI Endpoint Security Group."""

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
        aci_endpoint_security_group_content_type = (
            ContentType.objects.get_for_model(ACIEndpointSecurityGroup)
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


@register_model_view(
    ACIEndpointSecurityGroup, "bulk_import", path="import", detail=False
)
class ACIEndpointSecurityGroupBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACIEndpointSecurityGroup."""

    queryset = ACIEndpointSecurityGroup.objects.all()
    model_form = ACIEndpointSecurityGroupImportForm


@register_model_view(
    ACIEndpointSecurityGroup, "bulk_edit", path="edit", detail=False
)
class ACIEndpointSecurityGroupBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI Endpoint Security Group."""

    queryset = ACIEndpointSecurityGroup.objects.all()
    filterset = ACIAppProfileFilterSet
    table = ACIEndpointSecurityGroupTable
    form = ACIEndpointSecurityGroupBulkEditForm


@register_model_view(
    ACIEndpointSecurityGroup, "bulk_delete", path="delete", detail=False
)
class ACIEndpointSecurityGroupBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI Endpoint Security Group."""

    queryset = ACIEndpointSecurityGroup.objects.all()
    filterset = ACIEndpointSecurityGroupFilterSet
    table = ACIEndpointSecurityGroupTable
