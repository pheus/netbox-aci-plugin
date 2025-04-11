# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from netbox.filtersets import NetBoxModelFilterSet
from tenancy.models import Tenant

from ...models.tenant.app_profiles import ACIAppProfile
from ...models.tenant.endpoint_security_groups import ACIEndpointSecurityGroup
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF


class ACIEndpointSecurityGroupFilterSet(NetBoxModelFilterSet):
    """Filter set for the ACI Endpoint Security Group model."""

    aci_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_app_profile__aci_tenant",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant (name)"),
    )
    aci_tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_app_profile__aci_tenant",
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Tenant (ID)"),
    )
    aci_app_profile = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIAppProfile.objects.all(),
        to_field_name="name",
        label=_("ACI Application Profile (name)"),
    )
    aci_app_profile_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIAppProfile.objects.all(),
        to_field_name="id",
        label=_("ACI Application Profile (ID)"),
    )
    aci_vrf = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIVRF.objects.all(),
        to_field_name="name",
        label=_("ACI VRF (name)"),
    )
    aci_vrf_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACIVRF.objects.all(),
        to_field_name="id",
        label=_("ACI VRF (ID)"),
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

    class Meta:
        model = ACIEndpointSecurityGroup
        fields: tuple = (
            "id",
            "name",
            "name_alias",
            "description",
            "aci_app_profile",
            "aci_vrf",
            "nb_tenant",
            "admin_shutdown",
            "intra_esg_isolation_enabled",
            "preferred_group_member_enabled",
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
