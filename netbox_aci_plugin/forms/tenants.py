# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from tenancy.models import Tenant, TenantGroup
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from ..models.tenants import ACITenant


class ACITenantForm(NetBoxModelForm):
    """NetBox form for ACI Tenant model."""

    tenant_group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_("Tenant group"),
        initial_params={"tenants": "$tenant"},
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("Tenant"),
        query_params={"group_id": "$tenant_group"},
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet("name", "alias", "description", "tags", name=_("ACI Tenant")),
        FieldSet("tenant_group", "tenant", name=_("Tenancy")),
    )

    class Meta:
        model = ACITenant
        fields: tuple = (
            "name",
            "alias",
            "description",
            "tenant",
            "comments",
            "tags",
        )


class ACITenantFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for ACI Tenant model."""

    model = ACITenant
    fieldsets: tuple = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet("name", "alias", "description", name="Attributes"),
        FieldSet("tenant_group_id", "tenant_id", name="Tenancy"),
    )

    name = forms.CharField(required=False)
    alias = forms.CharField(required=False)
    description = forms.CharField(required=False)
    tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        null_option="None",
        label=_("Tenant group"),
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        null_option="None",
        query_params={"group_id": "$tenant_group_id"},
        label=_("Tenant"),
    )
    tag = TagFilterField(ACITenant)
