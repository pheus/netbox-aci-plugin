# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.postgres.forms import SimpleArrayField
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
from ...models.access_policies.domains import ACIRoutedDomain
from ...models.fabric.fabrics import ACIFabric
from ...validators import (
    ACIPolicyDescriptionValidator,
    ACIPolicyNameRequiredValidator,
)


class ACIRoutedDomainEditForm(NetBoxModelForm):
    """NetBox edit form for ACI Routed Domain model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        label=_("ACI Fabric"),
    )
    security_domains = SimpleArrayField(
        base_field=forms.CharField(
            max_length=ACI_NAME_MAX_LEN,
            validators=[ACIPolicyNameRequiredValidator],
        ),
        delimiter=",",
        label=_("Security Domains"),
        required=False,
        help_text=_("Optional comma-separated list of ACI security domain names."),
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
        queryset=OwnerGroup.objects.all(),
        required=False,
        null_option="None",
        initial_params={"members": "$owner"},
        label=_("Owner group"),
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
            "aci_fabric",
            "name",
            "name_alias",
            "description",
            "security_domains",
            "tags",
            name=_("ACI Routed Domain"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIRoutedDomain
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "security_domains",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )

    def clean_security_domains(self) -> list[str]:
        """Return security domain names without empty entries."""
        security_domains = self.cleaned_data.get("security_domains") or []
        return [domain.strip() for domain in security_domains if domain.strip()]


class ACIRoutedDomainBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for ACI Routed Domain model."""

    name_alias = forms.CharField(
        max_length=ACI_NAME_MAX_LEN,
        required=False,
        label=_("Name Alias"),
        validators=[ACIPolicyNameRequiredValidator],
    )
    description = forms.CharField(
        max_length=ACI_DESC_MAX_LEN,
        required=False,
        label=_("Description"),
        validators=[ACIPolicyDescriptionValidator],
    )
    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    security_domains = SimpleArrayField(
        base_field=forms.CharField(
            max_length=ACI_NAME_MAX_LEN,
            validators=[ACIPolicyNameRequiredValidator],
        ),
        delimiter=",",
        label=_("Security Domains"),
        required=False,
        help_text=_("Optional comma-separated list of ACI security domain names."),
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

    model = ACIRoutedDomain
    fieldsets: tuple = (
        FieldSet(
            "aci_fabric",
            "name_alias",
            "description",
            "security_domains",
            name=_("ACI Routed Domain"),
        ),
        FieldSet("nb_tenant", name=_("NetBox Tenancy")),
    )
    nullable_fields: tuple = (
        "comments",
        "description",
        "name_alias",
        "nb_tenant",
        "owner",
        "security_domains",
    )


class ACIRoutedDomainFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for ACI Routed Domain model."""

    model = ACIRoutedDomain
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
            "aci_fabric_id",
            "security_domain",
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
    security_domain = forms.CharField(
        required=False,
        label=_("Security Domain"),
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


class ACIRoutedDomainImportForm(NetBoxModelImportForm):
    """NetBox import form for ACI Routed Domain model."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
        help_text=_("Assigned ACI Fabric."),
    )
    nb_tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox Tenant"),
        help_text=_("Assigned NetBox Tenant."),
    )
    owner = CSVModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        to_field_name="name",
        help_text=_("Name of the object's owner."),
    )
    security_domains = SimpleArrayField(
        base_field=forms.CharField(
            max_length=ACI_NAME_MAX_LEN,
            validators=[ACIPolicyNameRequiredValidator],
        ),
        delimiter=",",
        label=_("Security Domains"),
        required=False,
        help_text=_("Optional comma-separated list of ACI security domain names."),
    )

    class Meta:
        model = ACIRoutedDomain
        fields: tuple = (
            "aci_fabric",
            "name",
            "name_alias",
            "description",
            "security_domains",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )

    def clean_security_domains(self) -> list[str]:
        """Return security domain names without empty entries."""
        security_domains = self.cleaned_data.get("security_domains") or []
        return [domain.strip() for domain in security_domains if domain.strip()]
