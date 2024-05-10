# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.views import generic
from utilities.views import register_model_view

from ..filtersets.tenants import ACITenantFilterSet
from ..forms.tenants import ACITenantFilterForm, ACITenantForm
from ..models.tenants import ACITenant
from ..tables.tenants import ACITenantTable


@register_model_view(ACITenant)
class ACITenantView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Tenant."""

    queryset = ACITenant.objects.prefetch_related(
        "nb_tenant",
        "tags",
    )


class ACITenantListView(generic.ObjectListView):
    """List view for listing all objects of ACI Tenant."""

    queryset = ACITenant.objects.prefetch_related(
        "nb_tenant",
        "tags",
    )
    filterset = ACITenantFilterSet
    filterset_form = ACITenantFilterForm
    table = ACITenantTable


@register_model_view(ACITenant, "edit")
class ACITenantEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Tenant."""

    queryset = ACITenant.objects.prefetch_related(
        "nb_tenant",
        "tags",
    )
    form = ACITenantForm


@register_model_view(ACITenant, "delete")
class ACITenantDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Tenant."""

    queryset = ACITenant.objects.prefetch_related(
        "nb_tenant",
        "tags",
    )
