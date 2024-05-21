# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from ipam.models import VRF
from netbox.filtersets import NetBoxModelFilterSet
from tenancy.models import Tenant

from ..choices import (
    VRFPCEnforcementDirectionChoices,
    VRFPCEnforcementPreferenceChoices,
)
from ..models.tenant_networks import ACIVRF
from ..models.tenants import ACITenant


class ACIVRFFilterSet(NetBoxModelFilterSet):
    """Filter set for ACI VRF model."""

    aci_tenant = django_filters.ModelMultipleChoiceFilter(
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant (name)"),
    )
    aci_tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Tenant (ID)"),
    )
    nb_tenant = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        label=_("NetBox tenant (name)"),
    )
    nb_tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        to_field_name="id",
        label=_("NetBox tenant (ID)"),
    )
    nb_vrf = django_filters.ModelMultipleChoiceFilter(
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

    class Meta:
        model = ACIVRF
        fields: tuple = (
            "id",
            "name",
            "alias",
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
        """Return a QuerySet filtered by the models description."""
        if not value.strip():
            return queryset
        queryset_filter: Q = (
            Q(name__icontains=value)
            | Q(alias__icontains=value)
            | Q(description__icontains=value)
        )
        return queryset.filter(queryset_filter)
