# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ...filtersets.tenant.app_profiles import ACIAppProfileFilterSet
from ...forms.tenant.app_profiles import (
    ACIAppProfileBulkEditForm,
    ACIAppProfileEditForm,
    ACIAppProfileFilterForm,
    ACIAppProfileImportForm,
)
from ...models.tenant.app_profiles import ACIAppProfile
from ...tables.tenant.app_profiles import ACIAppProfileTable
from .endpoint_groups import (
    ACIEndpointGroupChildrenView,
    ACIUSegEndpointGroupChildrenView,
)
from .endpoint_security_groups import ACIEndpointSecurityGroupChildrenView

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
        return ACIAppProfile.objects.restrict(request.user, "view").prefetch_related(
            "aci_tenant",
            "nb_tenant",
            "tags",
        )


#
# Application Profile views
#


@register_model_view(ACIAppProfile)
class ACIAppProfileView(generic.ObjectView):
    """Detail view for displaying a single object of ACI App Profile."""

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
    template_name = "netbox_aci_plugin/inc/aciappprofile/endpointgroups.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(aci_app_profile=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with ACIAppProfile colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACIAppProfile column
        table.columns.hide("aci_app_profile")

        return table


@register_model_view(ACIAppProfile, "usegendpointgroups", path="useg-endpoint-groups")
class ACIAppProfileUSegEndpointGroupView(ACIUSegEndpointGroupChildrenView):
    """Children view of ACI uSeg Endpoint Group of ACI Application Profile."""

    queryset = ACIAppProfile.objects.all()
    template_name = "netbox_aci_plugin/inc/aciappprofile/usegendpointgroups.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(aci_app_profile=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with ACIAppProfile colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACIAppProfile column
        table.columns.hide("aci_app_profile")

        return table


@register_model_view(
    ACIAppProfile, "endpointsecuritygroups", path="endpoint-security-groups"
)
class ACIAppProfileEndpointSecurityGroupView(ACIEndpointSecurityGroupChildrenView):
    """Children view of ACI Endpoint Security Group of ACI App Profile."""

    queryset = ACIAppProfile.objects.all()
    template_name = "netbox_aci_plugin/inc/aciappprofile/endpointsecuritygroups.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(aci_app_profile=parent.pk)

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
