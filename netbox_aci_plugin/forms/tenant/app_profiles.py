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
from ...models.tenant.app_profiles import ACIAppProfile
from ...models.tenant.tenants import ACITenant

#
# Application Profile forms
#


class ACIAppProfileEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Application Profile model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={"aci_tenants": "$aci_tenant"},
        required=False,
        label=_("ACI Fabric"),
    )
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        label=_("ACI Tenant"),
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
            "aci_tenant",
            "description",
            "tags",
            name=_("Application Profile"),
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
            "name_alias",
            "description",
            "aci_tenant",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACIAppProfileBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Application Profile model."""

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
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        required=False,
        label=_("ACI Tenant"),
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

    model = ACIAppProfile
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_tenant",
            "description",
            name=_("ACI Application Profile"),
        ),
        FieldSet(
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )
    nullable_fields: tuple = (
        "name_alias",
        "description",
        "nb_tenant",
        "comments",
    )


class ACIAppProfileFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Application Profile model."""

    model = ACIAppProfile
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
            "aci_tenant_id",
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
    aci_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        required=False,
        label=_("ACI Tenant"),
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


class ACIAppProfileImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Application Profile model."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
        help_text=_("Parent ACI Fabric of ACI Tenant"),
    )
    aci_tenant = CSVModelChoiceField(
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Tenant"),
        help_text=_("Assigned ACI Tenant"),
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
        model = ACIAppProfile
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_tenant",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)

        if not data:
            return

        if data.get("aci_fabric") and data.get("aci_tenant"):
            # Limit ACITenant queryset by parent ACIFabric
            self.fields["aci_tenant"].queryset = ACITenant.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
