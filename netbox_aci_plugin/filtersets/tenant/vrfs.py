# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from ipam.models import VRF
from netbox.filtersets import NetBoxModelFilterSet
from users.filterset_mixins import OwnerFilterMixin
from utilities.filtersets import register_filterset

from ...choices import (
    VRFPCEnforcementDirectionChoices,
    VRFPCEnforcementPreferenceChoices,
)
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF
from ..mixins import ACITenantFilterSetMixin, NBTenantFilterSetMixin


@register_filterset
class ACIVRFFilterSet(
    ACITenantFilterSetMixin,
    NBTenantFilterSetMixin,
    OwnerFilterMixin,
    NetBoxModelFilterSet,
):
    """Filter set for the ACI VRF model."""

    nb_vrf = django_filters.ModelMultipleChoiceFilter(
        field_name="nb_vrf__name",
        queryset=VRF.objects.all(),
        to_field_name="name",
        label=_("NetBox VRF (name)"),
    )
    nb_vrf_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VRF.objects.all(),
        to_field_name="id",
        label=_("NetBox VRF (ID)"),
    )
    pc_enforcement_direction = django_filters.MultipleChoiceFilter(
        choices=VRFPCEnforcementDirectionChoices,
        null_value=None,
    )
    pc_enforcement_preference = django_filters.MultipleChoiceFilter(
        choices=VRFPCEnforcementPreferenceChoices,
        null_value=None,
    )

    # Filters extended with a custom filter method
    present_in_aci_tenant_or_common_id = django_filters.ModelChoiceFilter(
        queryset=ACITenant.objects.all(),
        method="filter_present_in_aci_tenant_or_common_id",
        label=_("ACI Tenant (ID)"),
    )

    class Meta:
        model = ACIVRF
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "nb_tenant",
            "nb_vrf",
            "bd_enforcement_enabled",
            "dns_labels",
            "ip_data_plane_learning_enabled",
            "pc_enforcement_direction",
            "pc_enforcement_preference",
            "pim_ipv4_enabled",
            "pim_ipv6_enabled",
            "preferred_group_enabled",
        )
        filter_overrides = {
            ArrayField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            }
        }

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

    @extend_schema_field(OpenApiTypes.INT)
    def filter_present_in_aci_tenant_or_common_id(self, queryset, name, aci_tenant):
        """Return a QuerySet filtered by given ACI Tenant or 'common'."""
        if aci_tenant is None:
            return queryset.none()
        return queryset.filter(
            Q(aci_tenant=aci_tenant)
            | Q(
                aci_tenant__name="common",
                aci_tenant__aci_fabric_id=aci_tenant.aci_fabric_id,
            )
        )
