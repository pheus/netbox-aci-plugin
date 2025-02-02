# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ..filtersets.tenant_app_profiles import (
    ACIAppProfileFilterSet,
    ACIEndpointGroupFilterSet,
)
from ..forms.tenant_app_profiles import (
    ACIAppProfileBulkEditForm,
    ACIAppProfileEditForm,
    ACIAppProfileFilterForm,
    ACIAppProfileImportForm,
    ACIEndpointGroupBulkEditForm,
    ACIEndpointGroupEditForm,
    ACIEndpointGroupFilterForm,
    ACIEndpointGroupImportForm,
)
from ..models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup
from ..tables.tenant_app_profiles import (
    ACIAppProfileTable,
    ACIEndpointGroupTable,
)
from .tenant_contracts import ACIContractRelationChildrenView

#
# Base children views
#


class ACIAppProfileChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Application Profile."""

    child_model = ACIAppProfile
    filterset = ACIAppProfileFilterSet
    tab = ViewTab(
        label=_("Application Profiles"),
        badge=lambda obj: obj.aci_app_profiles.count(),
        permission="netbox_aci_plugin.view_aciappprofile",
        weight=1000,
    )
    table = ACIAppProfileTable

    def get_children(self, request, parent):
        """Return all objects of ACIAppProfile."""
        return ACIAppProfile.objects.restrict(
            request.user, "view"
        ).prefetch_related(
            "aci_tenant",
            "nb_tenant",
            "tags",
        )


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
        return ACIEndpointGroup.objects.restrict(
            request.user, "view"
        ).prefetch_related(
            "aci_app_profile",
            "aci_bridge_domain",
            "nb_tenant",
            "tags",
        )


#
# Application Profile views
#


@register_model_view(ACIAppProfile)
class ACIAppProfileView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Application Profile."""

    queryset = ACIAppProfile.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )


@register_model_view(ACIAppProfile, "list", path="", detail=False)
class ACIAppProfileListView(generic.ObjectListView):
    """List view for listing all objects of ACI Application Profile."""

    queryset = ACIAppProfile.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )
    filterset = ACIAppProfileFilterSet
    filterset_form = ACIAppProfileFilterForm
    table = ACIAppProfileTable


@register_model_view(ACIAppProfile, "add", detail=False)
@register_model_view(ACIAppProfile, "edit")
class ACIAppProfileEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Application Profile."""

    queryset = ACIAppProfile.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )
    form = ACIAppProfileEditForm


@register_model_view(ACIAppProfile, "delete")
class ACIAppProfileDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Application Profile."""

    queryset = ACIAppProfile.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )


@register_model_view(ACIAppProfile, "endpointgroups", path="endpoint-groups")
class ACIAppProfileEndpointGroupView(ACIEndpointGroupChildrenView):
    """Children view of ACI Endpoint Group of ACI Application Profile."""

    queryset = ACIAppProfile.objects.all()
    template_name = "netbox_aci_plugin/aciappprofile_endpointgroups.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_app_profile=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACIAppProfile colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACIAppProfile column
        table.columns.hide("aci_app_profile")

        return table


@register_model_view(ACIAppProfile, "bulk_import", path="import", detail=False)
class ACIAppProfileBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI App Profile."""

    queryset = ACIAppProfile.objects.all()
    model_form = ACIAppProfileImportForm


@register_model_view(ACIAppProfile, "bulk_edit", path="edit", detail=False)
class ACIAppProfileBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI App Profile."""

    queryset = ACIAppProfile.objects.all()
    filterset = ACIAppProfileFilterForm
    table = ACIAppProfileTable
    form = ACIAppProfileBulkEditForm


@register_model_view(ACIAppProfile, "bulk_delete", path="delete", detail=False)
class ACIAppProfileBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI App Profile."""

    queryset = ACIAppProfile.objects.all()
    filterset = ACIAppProfileFilterSet
    table = ACIAppProfileTable


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


@register_model_view(
    ACIEndpointGroup, "contractrelations", path="contract-relations"
)
class ACIVRFContractRelationView(ACIContractRelationChildrenView):
    """Children view of ACI Contract Relation of ACI Endpoint Group."""

    queryset = ACIEndpointGroup.objects.all()
    template_name = "netbox_aci_plugin/aciendpointgroup_contractrelations.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_endpoint_group=parent.pk)
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


@register_model_view(
    ACIEndpointGroup, "bulk_import", path="import", detail=False
)
class ACIEndpointGroupBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI Endpoint Group."""

    queryset = ACIEndpointGroup.objects.all()
    model_form = ACIEndpointGroupImportForm


@register_model_view(ACIEndpointGroup, "bulk_edit", path="edit", detail=False)
class ACIEndpointGroupBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI Endpoint Group."""

    queryset = ACIEndpointGroup.objects.all()
    filterset = ACIAppProfileFilterSet
    table = ACIEndpointGroupTable
    form = ACIEndpointGroupBulkEditForm


@register_model_view(
    ACIEndpointGroup, "bulk_delete", path="delete", detail=False
)
class ACIEndpointGroupBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI Endpoint Group."""

    queryset = ACIEndpointGroup.objects.all()
    filterset = ACIEndpointGroupFilterSet
    table = ACIEndpointGroupTable
