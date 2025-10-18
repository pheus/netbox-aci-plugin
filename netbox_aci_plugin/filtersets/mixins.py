# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_filters
from django.utils.translation import gettext as _
from tenancy.models import Tenant, TenantGroup
from utilities.filters import TreeNodeMultipleChoiceFilter

from ..models.fabric.fabrics import ACIFabric
from ..models.tenant.tenants import ACITenant


class ACIFabricFilterSetMixin(django_filters.FilterSet):
    """Filter set mixin for the ACI Fabric model."""

    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )


class ACITenantFilterSetMixin(django_filters.FilterSet):
    """Filter set mixin for the ACI Tenant model."""

    aci_fabric = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_tenant__aci_fabric__name",
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        label=_("ACI Fabric (name)"),
    )
    aci_fabric_id = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_tenant__aci_fabric",
        queryset=ACIFabric.objects.all(),
        to_field_name="id",
        label=_("ACI Fabric (ID)"),
    )
    aci_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="aci_tenant__name",
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        label=_("ACI Tenant (name)"),
    )
    aci_tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ACITenant.objects.all(),
        to_field_name="id",
        label=_("ACI Tenant (ID)"),
    )


class NBTenantFilterSetMixin(django_filters.FilterSet):
    """Filter set mixin for the NetBox Tenant model."""

    nb_tenant_group = TreeNodeMultipleChoiceFilter(
        field_name="nb_tenant__group",
        queryset=TenantGroup.objects.all(),
        to_field_name="slug",
        lookup_expr="in",
        label=_("NetBox tenant group (slug)"),
    )
    nb_tenant_group_id = TreeNodeMultipleChoiceFilter(
        field_name="nb_tenant__group",
        queryset=TenantGroup.objects.all(),
        lookup_expr="in",
        label=_("NetBox tenant group (ID)"),
    )
    nb_tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="nb_tenant__slug",
        queryset=Tenant.objects.all(),
        to_field_name="slug",
        label=_("NetBox tenant (slug)"),
    )
    nb_tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label=_("NetBox tenant (ID)"),
    )
