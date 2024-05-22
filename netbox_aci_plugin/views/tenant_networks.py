# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ..filtersets.tenant_networks import (
    ACIBridgeDomainFilterSet,
    ACIVRFFilterSet,
)
from ..forms.tenant_networks import (
    ACIBridgeDomainFilterForm,
    ACIBridgeDomainForm,
    ACIVRFFilterForm,
    ACIVRFForm,
)
from ..models.tenant_networks import ACIVRF, ACIBridgeDomain
from ..tables.tenant_networks import ACIBridgeDomainTable, ACIVRFTable

#
# Base children views
#


class ACIVRFChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI VRF."""

    child_model = ACIVRF
    filterset = ACIVRFFilterSet
    tab = ViewTab(
        label=_("VRFs"),
        badge=lambda obj: obj.aci_vrfs.count(),
        weight=1000,
    )
    table = ACIVRFTable

    def get_children(self, request, parent):
        """Return all objects of ACIVRF."""
        return ACIVRF.objects.prefetch_related(
            "aci_tenant",
            "nb_tenant",
            "tags",
        )


class ACIBridgeDomainChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Bridge Domain."""

    child_model = ACIBridgeDomain
    filterset = ACIBridgeDomainFilterSet
    tab = ViewTab(
        label=_("Bridge Domains"),
        badge=lambda obj: obj.aci_bds.count(),
        weight=1000,
    )
    table = ACIBridgeDomainTable

    def get_children(self, request, parent):
        """Return all objects of ACIBridgeDomain."""
        return ACIBridgeDomain.objects.prefetch_related(
            "aci_vrf",
            "nb_tenant",
            "tags",
        )


#
# VRF views
#


@register_model_view(ACIVRF)
class ACIVRFView(generic.ObjectView):
    """Detail view for displaying a single object of ACI VRF."""

    queryset = ACIVRF.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )


class ACIVRFListView(generic.ObjectListView):
    """List view for listing all objects of ACI VRF."""

    queryset = ACIVRF.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )
    filterset = ACIVRFFilterSet
    filterset_form = ACIVRFFilterForm
    table = ACIVRFTable


@register_model_view(ACIVRF, "edit")
class ACIVRFEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI VRF."""

    queryset = ACIVRF.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )
    form = ACIVRFForm


@register_model_view(ACIVRF, "delete")
class ACIVRFDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI VRF."""

    queryset = ACIVRF.objects.prefetch_related(
        "aci_tenant",
        "nb_tenant",
        "tags",
    )


@register_model_view(ACIVRF, "bridgedomains", path="bridge-domains")
class ACIVRFBridgeDomainView(ACIBridgeDomainChildrenView):
    """Children view of ACI Bridge Domain of ACI VRF."""

    queryset = ACIVRF.objects.all()
    template_name = "netbox_aci_plugin/acivrf_bds.html"

    def get_children(self, request, parent):
        """Return all ACIVRF objects for current ACITenant."""
        return super().get_children(request, parent).filter(aci_vrf=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return table with ACITenant and ACIVRF colum hidden."""
        table = super().get_table(*args, **kwargs)

        # Hide ACITenant column
        table.columns.hide("aci_tenant")
        # Hide ACIVRF column
        table.columns.hide("aci_vrf")

        return table


#
# Bridge Domain views
#


@register_model_view(ACIBridgeDomain)
class ACIBridgeDomainView(generic.ObjectView):
    """Detail view for displaying a single object of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.prefetch_related(
        "aci_vrf",
        "nb_tenant",
        "tags",
    )


class ACIBridgeDomainListView(generic.ObjectListView):
    """List view for listing all objects of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.prefetch_related(
        "aci_vrf",
        "nb_tenant",
        "tags",
    )
    filterset = ACIBridgeDomainFilterSet
    filterset_form = ACIBridgeDomainFilterForm
    table = ACIBridgeDomainTable


@register_model_view(ACIBridgeDomain, "edit")
class ACIBridgeDomainEditView(generic.ObjectEditView):
    """Edit view for editing an object of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.prefetch_related(
        "aci_vrf",
        "nb_tenant",
        "tags",
    )
    form = ACIBridgeDomainForm


@register_model_view(ACIBridgeDomain, "delete")
class ACIBridgeDomainDeleteView(generic.ObjectDeleteView):
    """Delete view for deleting an object of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.prefetch_related(
        "aci_vrf",
        "nb_tenant",
        "tags",
    )
