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
