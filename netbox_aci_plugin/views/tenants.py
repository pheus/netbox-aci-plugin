# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.relations import get_related_models
from utilities.views import ViewTab, register_model_view

from ..filtersets.tenants import ACITenantFilterSet
from ..forms.tenants import (
    ACITenantBulkEditForm,
    ACITenantEditForm,
    ACITenantFilterForm,
    ACITenantImportForm,
)
from ..models.tenant_app_profiles import ACIEndpointGroup
from ..models.tenants import ACITenant
from ..tables.tenants import ACITenantTable
from .tenant_app_profiles import (
    ACIAppProfileChildrenView,
    ACIEndpointGroupChildrenView,
)
from .tenant_contracts import ACIContractChildrenView
from .tenant_networks import ACIBridgeDomainChildrenView, ACIVRFChildrenView

#
# Tenant views
#


@register_model_view(ACITenant)
class ACITenantView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Tenant."""

    queryset = ACITenant.objects.prefetch_related(
        "nb_tenant",
        "tags",
    )

    def get_extra_context(self, request, instance) -> dict:
        """Return related models as extra context."""

        # Get related models from ForeignKey fields
        related_models: list[tuple] = [
            (
                model.objects.restrict(request.user, "view").filter(
                    aci_tenant=instance
                ),
                f"{field}_id",
            )
            for model, field in get_related_models(ACITenant, ordered=False)
        ]

        # Get related models of directly referenced models
        related_sub_models: list[tuple] = [
            (
                ACIEndpointGroup.objects.restrict(request.user, "view").filter(
                    aci_app_profile__aci_tenant=instance
                ),
                "aci_tenant_id",
            ),
        ]

        # Combine the lists and sort the combined list by the model's name
        sorted_related_models = sorted(
            related_models + related_sub_models,
            key=lambda x: x[0].model._meta.verbose_name.lower(),
        )

        return {
            "related_models": sorted_related_models,
        }


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
    form = ACITenantEditForm


@register_model_view(ACITenant, "delete")
class ACITenantDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Tenant."""

    queryset = ACITenant.objects.prefetch_related(
        "nb_tenant",
        "tags",
    )


@register_model_view(ACITenant, "appprofiles", path="app-profiles")
class ACITenantAppProfileView(ACIAppProfileChildrenView):
    """Children view of ACI Application Profile of ACI Tenant."""

    queryset = ACITenant.objects.all()
    template_name = "netbox_aci_plugin/acitenant_appprofiles.html"

    def get_children(self, request, parent):
        """Return all ACIAppProfile objects for the current ACITenant."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_tenant_id=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACITenant colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACITenant column
        table.columns.hide("aci_tenant")

        return table


@register_model_view(ACITenant, "vrfs", path="vrfs")
class ACITenantVRFView(ACIVRFChildrenView):
    """Children view of ACI VRF of ACI Tenant."""

    queryset = ACITenant.objects.all()
    template_name = "netbox_aci_plugin/acitenant_vrfs.html"

    def get_children(self, request, parent):
        """Return all ACIVRF objects for current ACITenant."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_tenant_id=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACITenant colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACITenant column
        table.columns.hide("aci_tenant")

        return table


@register_model_view(ACITenant, "bridgedomains", path="bridge-domains")
class ACITenantBridgeDomainView(ACIBridgeDomainChildrenView):
    """Children view of ACI Bridge Domain of ACI Tenant."""

    queryset = ACITenant.objects.all()
    template_name = "netbox_aci_plugin/acitenant_bridgedomains.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_tenant_id=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACITenant colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACITenant column
        table.columns.hide("aci_tenant")

        return table


@register_model_view(ACITenant, "endpointgroups", path="endpoint-groups")
class ACITenantEndpointGroupView(ACIEndpointGroupChildrenView):
    """Children view of ACI Endpoint Group of ACI Tenant."""

    queryset = ACITenant.objects.all()
    tab = ViewTab(
        label=_("Endpoint Groups"),
        badge=lambda obj: ACIEndpointGroupChildrenView.child_model.objects.filter(
            aci_app_profile__aci_tenant=obj.pk
        ).count(),
        permission="netbox_aci_plugin.view_aciendpointgroup",
        weight=1000,
    )
    template_name = "netbox_aci_plugin/acitenant_endpointgroups.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_app_profile__aci_tenant=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACITenant colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACITenant column
        table.columns.hide("aci_tenant")

        return table


@register_model_view(ACITenant, "contracts", path="contracts")
class ACITenantContractView(ACIContractChildrenView):
    """Children view of ACI Application Profile of ACI Tenant."""

    queryset = ACITenant.objects.all()
    template_name = "netbox_aci_plugin/acitenant_contracts.html"

    def get_children(self, request, parent):
        """Return all ACIContract objects for the current ACITenant."""
        return (
            super()
            .get_children(request, parent)
            .filter(aci_tenant_id=parent.pk)
        )

    def get_table(self, *args, **kwargs):
        """Return the table with ACITenant colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACITenant column
        table.columns.hide("aci_tenant")

        return table


class ACITenantBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI Tenant."""

    queryset = ACITenant.objects.all()
    model_form = ACITenantImportForm


class ACITenantBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI Tenant."""

    queryset = ACITenant.objects.all()
    filterset = ACITenantFilterSet
    table = ACITenantTable
    form = ACITenantBulkEditForm


class ACITenantBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI Tenant."""

    queryset = ACITenant.objects.all()
    filterset = ACITenantFilterSet
    table = ACITenantTable
