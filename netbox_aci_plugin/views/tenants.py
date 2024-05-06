# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.views import generic

from ..filtersets.tenants import ACITenantFilterSet
from ..forms.tenants import ACITenantForm
from ..models.tenants import ACITenant
from ..tables.tenants import ACITenantTable


class ACITenantView(generic.ObjectView):
    """View for a single instance of ACI Tenant."""

    queryset = ACITenant.objects.all()


class ACITenantListView(generic.ObjectListView):
    """View for listing all instances of ACI Tenant."""

    queryset = ACITenant.objects.all()
    filterset = ACITenantFilterSet
    table = ACITenantTable


class ACITenantEditView(generic.ObjectEditView):
    """View for editing an instance of ACI Tenant."""

    queryset = ACITenant.objects.all()
    form = ACITenantForm


class ACITenantDeleteView(generic.ObjectDeleteView):
    """View for deleting an instance of ACI Tenant."""

    queryset = ACITenant.objects.all()
