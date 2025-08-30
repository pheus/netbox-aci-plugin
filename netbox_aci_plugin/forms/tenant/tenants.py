# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from tenancy.models import Tenant, TenantGroup
from utilities.forms.fields import (
    CommentField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from ...models.tenant.tenants import ACITenant


class ACITenantEditForm(NetBoxModelForm):
    """NetBox edit form for ACI Tenant model."""

    nb_tenant_group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        initial_params={"tenants": "$nb_tenant"},
        required=False,
        label=_("NetBox tenant group"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        query_params={"group_id": "$nb_tenant_group"},
        required=False,
        label=_("NetBox tenant"),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "description",
            "tags",
            name=_("ACI Tenant"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACITenant
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "nb_tenant",
            "comments",
            "tags",
        )


class ACITenantBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for ACI Tenant model."""

    name_alias = forms.CharField(
        max_length=64,
        required=False,
        label=_("Name Alias"),
    )
    description = forms.CharField(
        max_length=128,
        required=False,
        label=_("Description"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
    )
    comments = CommentField()

    model = ACITenant
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "description",
            name=_("ACI Tenant"),
        ),
        FieldSet(
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )
    nullable_fields = (
        "name_alias",
        "description",
        "nb_tenant",
        "comments",
    )


class ACITenantFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Tenant model."""

    model = ACITenant
    fieldsets: tuple = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "name_alias",
            "description",
            name="Attributes",
        ),
        FieldSet(
            "nb_tenant_group_id",
            "nb_tenant_id",
            name="NetBox Tenancy",
        ),
    )

    name = forms.CharField(
        required=False,
    )
    name_alias = forms.CharField(
        required=False,
    )
    description = forms.CharField(
        required=False,
    )
    nb_tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        null_option="None",
        required=False,
        label=_("Tenant group"),
    )
    nb_tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        query_params={"group_id": "$nb_tenant_group_id"},
        null_option="None",
        required=False,
        label=_("Tenant"),
    )
    tag = TagFilterField(model)


class ACITenantImportForm(NetBoxModelImportForm):
    """NetBox import form for ACITenant."""

    nb_tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox Tenant"),
        help_text=_("Assigned NetBox Tenant"),
    )

    class Meta:
        model = ACITenant
        fields = (
            "name",
            "name_alias",
            "description",
            "nb_tenant",
            "comments",
            "tags",
        )
