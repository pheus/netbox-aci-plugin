# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ..filtersets.tenant_app_profiles import (
    ACIAppProfileFilterSet,
    ACIEndpointGroupFilterSet,
)
from ..forms.tenant_app_profiles import (
    ACIAppProfileFilterForm,
    ACIAppProfileForm,
    ACIEndpointGroupFilterForm,
    ACIEndpointGroupForm,
)
from ..models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup
from ..tables.tenant_app_profiles import (
    ACIAppProfileTable,
    ACIEndpointGroupTable,
)

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
        weight=1000,
    )
    table = ACIAppProfileTable

    def get_children(self, request, parent):
        """Return all objects of ACIAppProfile."""
        return ACIAppProfile.objects.all()


class ACIEndpointGroupChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Endpoint Group."""

    child_model = ACIEndpointGroup
    filterset = ACIEndpointGroupFilterSet
    tab = ViewTab(
        label=_("Endpoint Groups"),
        badge=lambda obj: obj.aci_endpoint_groups.count(),
        weight=1000,
    )
    table = ACIEndpointGroupTable

    def get_children(self, request, parent):
        """Return all objects of ACIEndpointGroup."""
        return ACIEndpointGroup.objects.all()


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


@register_model_view(ACIAppProfile, "edit")
class ACIAppProfileEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Application Profile."""

    queryset = ACIAppProfile.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )
    form = ACIAppProfileForm


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
        """Return all children objects for current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_app_profile=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return table with ACIAppProfile colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACIAppProfile column
        table.columns.hide("aci_app_profile")

        return table


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


@register_model_view(ACIEndpointGroup, "edit")
class ACIEndpointGroupEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Endpoint Group."""

    queryset = ACIEndpointGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
        "tags",
    )
    form = ACIEndpointGroupForm


@register_model_view(ACIEndpointGroup, "delete")
class ACIEndpointGroupDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Endpoint Group."""

    queryset = ACIEndpointGroup.objects.prefetch_related(
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
        "tags",
    )
