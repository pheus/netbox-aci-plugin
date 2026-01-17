# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from dcim.models import Device
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from ipam.models import IPAddress
from netbox.filtersets import NetBoxModelFilterSet
from users.filterset_mixins import OwnerFilterMixin
from utilities.filters import ContentTypeFilter
from utilities.filtersets import register_filterset
from virtualization.models import VirtualMachine

from ...models.fabric.fabrics import ACIFabric
from ...models.fabric.nodes import ACINode
from ...models.fabric.pods import ACIPod
from ..mixins import ACIFabricFilterSetMixin, NBTenantFilterSetMixin


@register_filterset
class ACINodeFilterSet(
    ACIFabricFilterSetMixin,
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    NetBoxModelFilterSet,
):
    """Filter set for the ACI Node model."""

    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_pod__aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_pod__aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    aci_pod = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_pod__name",
        queryset=ACIPod.objects.all(),
        to_field_name="name",
        label=_("ACI Pod (name)"),
    )
    aci_pod_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_pod",
        queryset=ACIPod.objects.all(),
        to_field_name="id",
        label=_("ACI Pod (ID)"),
    )
    node_object_type = ContentTypeFilter(
        label=_("Node Object Type"),
    )
    tep_ip_address = django_filters.ModelMultipleChoiceFilter(
        field_name="tep_ip_address__address",
        queryset=IPAddress.objects.all(),
        to_field_name="address",
        label=_("TEP IP Address (address)"),
    )
    tep_ip_address_id = django_filters.ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        to_field_name="id",
        label=_("TEP IP Address (ID)"),
    )

    # Cached related objects filters
    device = django_filters.ModelMultipleChoiceFilter(
        field_name="_device__name",
        queryset=Device.objects.all(),
        to_field_name="name",
        label=_("Device (name)"),
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_device",
        queryset=Device.objects.all(),
        to_field_name="id",
        label=_("Device (ID)"),
    )
    virtual_machine = django_filters.ModelMultipleChoiceFilter(
        field_name="_virtual_machine__name",
        queryset=VirtualMachine.objects.all(),
        to_field_name="name",
        label=_("Virtual Machine (name)"),
    )
    virtual_machine_id = django_filters.ModelMultipleChoiceFilter(
        field_name="_virtual_machine",
        queryset=VirtualMachine.objects.all(),
        to_field_name="id",
        label=_("Virtual Machine (ID)"),
    )

    class Meta:
        model = ACINode
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "node_id",
            "node_object_type",
            "node_object_id",
            "role",
            "node_type",
            "tep_ip_address",
            "nb_tenant",
        )

    def search(self, queryset, name, value):
        """Return a QuerySet filtered by the model's description."""
        if not value.strip():
            return queryset
        queryset_filter: Q = (
            Q(name__icontains=value)
            | Q(name_alias__icontains=value)
            | Q(description__icontains=value)
        )
        return queryset.filter(queryset_filter)
