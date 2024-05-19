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

from ..models.tenant_app_profiles import ACIAppProfile
from ..models.tenants import ACITenant


class ACIAppProfileForm(NetBoxModelForm):
    """NetBox form for ACI Application Profile model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        label=_("ACI Tenant"),
        query_params={"nb_tenant_id": "$nb_tenant"},
    )
    nb_tenant_group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_("NetBox Tenant group"),
        initial_params={"tenants": "$nb_tenant"},
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
        query_params={"group_id": "$nb_tenant_group"},
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "alias",
            "aci_tenant",
            "description",
            "tags",
            name=_("ACI Application Profile"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIAppProfile
        fields: tuple = (
            "name",
            "alias",
            "description",
            "aci_tenant",
            "nb_tenant",
            "comments",
            "tags",
        )


class ACIAppProfileFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for ACI Application Profile model."""

    model = ACIAppProfile
    fieldsets: tuple = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "alias",
            "aci_tenant_id",
            "description",
            name="Attributes",
        ),
        FieldSet(
            "nb_tenant_group_id",
            "nb_tenant_id",
            name="NetBox Tenancy",
        ),
    )

    name = forms.CharField(required=False)
    alias = forms.CharField(required=False)
    description = forms.CharField(required=False)
    aci_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        required=False,
        null_option="None",
        query_params={"tenant_id": "$nb_tenant_id"},
        label=_("ACI Tenant"),
    )
    nb_tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        null_option="None",
        label=_("NetBox Tenant group"),
    )
    nb_tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        null_option="None",
        query_params={"group_id": "$nb_tenant_group_id"},
        label=_("NetBox Tenant"),
    )
    tag = TagFilterField(ACITenant)
