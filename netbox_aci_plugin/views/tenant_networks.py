# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.views import generic
from utilities.views import register_model_view

from ..filtersets.tenant_networks import ACIVRFFilterSet
from ..forms.tenant_networks import ACIVRFFilterForm, ACIVRFForm
from ..models.tenant_networks import ACIVRF
from ..tables.tenant_networks import ACIVRFTable


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
