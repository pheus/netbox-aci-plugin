# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import GetRelatedModelsMixin, ViewTab, register_model_view

from ...filtersets.tenant.tenants import ACITenantFilterSet
from ...forms.tenant.tenants import (
    ACITenantBulkEditForm,
    ACITenantEditForm,
    ACITenantFilterForm,
    ACITenantImportForm,
)
from ...models.tenant.endpoint_groups import ACIEndpointGroup
from ...models.tenant.endpoint_security_groups import ACIEndpointSecurityGroup
from ...models.tenant.tenants import ACITenant
from ...tables.tenant.tenants import ACITenantTable
from .app_profiles import ACIAppProfileChildrenView
from .bridge_domains import ACIBridgeDomainChildrenView
from .contracts import ACIContractChildrenView
from .endpoint_groups import ACIEndpointGroupChildrenView
from .endpoint_security_groups import ACIEndpointSecurityGroupChildrenView
from .vrfs import ACIVRFChildrenView

#
# Tenant views
#


@register_model_view(ACITenant)
class ACITenantView(GetRelatedModelsMixin, generic.ObjectView):
    """Detail view for displaying a single object of ACI Tenant."""

    queryset = ACITenant.objects.prefetch_related(
        "nb_tenant",
        "tags",
    )

    def get_extra_context(self, request, instance) -> dict:
        """Return related models as extra context."""
        # Get extra related models of directly referenced models
        extra_related_models: tuple[tuple[QuerySet, str], ...] = (
            (
                ACIEndpointGroup.objects.restrict(request.user, "view").filter(
                    aci_app_profile__aci_tenant=instance
                ),
                "aci_tenant_id",
            ),
            (
                ACIEndpointSecurityGroup.objects.restrict(request.user, "view").filter(
                    aci_app_profile__aci_tenant=instance
                ),
                "aci_tenant_id",
            ),
        )

        return {
            "related_models": self.get_related_models(
                request, instance, extra=extra_related_models
            )
        }


@register_model_view(ACITenant, "list", path="", detail=False)
class ACITenantListView(generic.ObjectListView):
    """List view for listing all objects of ACI Tenant."""

    queryset = ACITenant.objects.prefetch_related(
        "nb_tenant",
        "tags",
    )
    filterset = ACITenantFilterSet
    filterset_form = ACITenantFilterForm
    table = ACITenantTable


@register_model_view(ACITenant, "add", detail=False)
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
    template_name = "netbox_aci_plugin/inc/acitenant/appprofiles.html"

    def get_children(self, request, parent):
        """Return all ACIAppProfile objects for the current ACITenant."""
        return super().get_children(request, parent).filter(aci_tenant_id=parent.pk)

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
    template_name = "netbox_aci_plugin/inc/acitenant/endpointgroups.html"

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


@register_model_view(
    ACITenant, "endpointsecuritygroups", path="endpoint-security-groups"
)
class ACITenantEndpointSecurityGroupView(ACIEndpointSecurityGroupChildrenView):
    """Children view of ACI Endpoint Security Group of ACI Tenant."""

    queryset = ACITenant.objects.all()
    tab = ViewTab(
        label=_("Endpoint Security Groups"),
        badge=(
            lambda obj: (
                ACIEndpointSecurityGroupChildrenView.child_model.objects.filter(
                    aci_app_profile__aci_tenant=obj.pk
                ).count()
            )
        ),
        permission="netbox_aci_plugin.view_aciendpointsecuritygroup",
        weight=1000,
    )
    template_name = "netbox_aci_plugin/inc/acitenant/endpointsecuritygroups.html"

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


@register_model_view(ACITenant, "bridgedomains", path="bridge-domains")
class ACITenantBridgeDomainView(ACIBridgeDomainChildrenView):
    """Children view of ACI Bridge Domain of ACI Tenant."""

    queryset = ACITenant.objects.all()
    template_name = "netbox_aci_plugin/inc/acitenant/bridgedomains.html"

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(aci_tenant_id=parent.pk)

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
    template_name = "netbox_aci_plugin/inc/acitenant/vrfs.html"

    def get_children(self, request, parent):
        """Return all ACIVRF objects for current ACITenant."""
        return super().get_children(request, parent).filter(aci_tenant_id=parent.pk)

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
    template_name = "netbox_aci_plugin/inc/acitenant/contracts.html"

    def get_children(self, request, parent):
        """Return all ACIContract objects for the current ACITenant."""
        return super().get_children(request, parent).filter(aci_tenant_id=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return the table with ACITenant colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACITenant column
        table.columns.hide("aci_tenant")

        return table


@register_model_view(ACITenant, "bulk_import", path="import", detail=False)
class ACITenantBulkImportView(generic.BulkImportView):
    """Bulk import view for importing multiple objects of ACI Tenant."""

    queryset = ACITenant.objects.all()
    model_form = ACITenantImportForm


@register_model_view(ACITenant, "bulk_edit", path="edit", detail=False)
class ACITenantBulkEditView(generic.BulkEditView):
    """Bulk edit view for editing multiple objects of ACI Tenant."""

    queryset = ACITenant.objects.all()
    filterset = ACITenantFilterSet
    table = ACITenantTable
    form = ACITenantBulkEditForm


@register_model_view(ACITenant, "bulk_delete", path="delete", detail=False)
class ACITenantBulkDeleteView(generic.BulkDeleteView):
    """Bulk delete view for deleting multiple objects of ACI Tenant."""

    queryset = ACITenant.objects.all()
    filterset = ACITenantFilterSet
    table = ACITenantTable
