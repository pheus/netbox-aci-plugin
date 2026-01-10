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
from users.models import Owner, OwnerGroup
from utilities.forms.fields import (
    CommentField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from ...constants import ACI_DESC_MAX_LEN, ACI_NAME_MAX_LEN
from ...models.fabric.fabrics import ACIFabric
from ...models.tenant.tenants import ACITenant


class ACITenantEditForm(NetBoxModelForm):
    """NetBox edit form for ACI Tenant model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        label=_("ACI Fabric"),
    )
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
    owner_group = DynamicModelChoiceField(
        label=_("Owner group"),
        queryset=OwnerGroup.objects.all(),
        required=False,
        null_option="None",
        initial_params={"members": "$owner"},
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        query_params={"group_id": "$owner_group"},
        label=_("Owner"),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_fabric",
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
            "aci_fabric",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACITenantBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for ACI Tenant model."""

    name_alias = forms.CharField(
        max_length=ACI_NAME_MAX_LEN,
        required=False,
        label=_("Name Alias"),
    )
    description = forms.CharField(
        max_length=ACI_DESC_MAX_LEN,
        required=False,
        label=_("Description"),
    )
    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        query_params={"group_id": "$owner_group"},
        label=_("Owner"),
    )
    comments = CommentField()

    model = ACITenant
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_fabric",
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
            "aci_fabric_id",
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "nb_tenant_group_id",
            "nb_tenant_id",
            name=_("NetBox Tenancy"),
        ),
        FieldSet(
            "owner_group_id",
            "owner_id",
            name=_("Ownership"),
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
    aci_fabric_id = DynamicModelMultipleChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    nb_tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        null_option="None",
        required=False,
        label=_("NetBox tenant group"),
    )
    nb_tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        query_params={"group_id": "$nb_tenant_group_id"},
        null_option="None",
        required=False,
        label=_("NetBox tenant"),
    )
    owner_group_id = DynamicModelMultipleChoiceField(
        queryset=OwnerGroup.objects.all(),
        required=False,
        null_option="None",
        label=_("Owner Group"),
    )
    owner_id = DynamicModelMultipleChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        null_option="None",
        query_params={"group_id": "$owner_group_id"},
        label=_("Owner"),
    )
    tag = TagFilterField(model)


class ACITenantImportForm(NetBoxModelImportForm):
    """NetBox import form for ACITenant."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
        help_text=_("Assigned ACI Fabric"),
    )
    nb_tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox Tenant"),
        help_text=_("Assigned NetBox Tenant"),
    )
    owner = CSVModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        to_field_name="name",
        help_text=_("Name of the object's owner"),
    )

    class Meta:
        model = ACITenant
        fields = (
            "name",
            "name_alias",
            "aci_fabric",
            "description",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )
