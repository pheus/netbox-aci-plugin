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
from utilities.forms import add_blank_choice
from utilities.forms.fields import (
    CommentField,
    CSVChoiceField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from ..choices import (
    ContractScopeChoices,
    QualityOfServiceClassChoices,
    QualityOfServiceDSCPChoices,
)
from ..models.tenant_contracts import ACIContract
from ..models.tenants import ACITenant

#
# Contract forms
#


class ACIContractEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Contract model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
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
    qos_class = forms.ChoiceField(
        choices=QualityOfServiceClassChoices,
        required=False,
        label=_("QoS class"),
        help_text=_(
            "Specifies the priority handling for traffic between Consumer and "
            "Provider within the fabric."
            "Default is 'unspecified'."
        ),
    )
    scope = forms.ChoiceField(
        choices=ContractScopeChoices,
        required=False,
        label=_("Scope"),
        help_text=_(
            "Scope defines the extent within which the contract is "
            "applicable. Default is 'vrf'."
        ),
    )
    target_dscp = forms.ChoiceField(
        choices=QualityOfServiceDSCPChoices,
        required=False,
        label=_("Target DSCP"),
        help_text=_(
            "Rewrites the DSCP value of the incoming traffic to the specified"
            "value. Default is 'unspecified'."
        ),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant",
            "description",
            "tags",
            name=_("ACI Contract"),
        ),
        FieldSet(
            "scope",
            name=_("Scope"),
        ),
        FieldSet(
            "qos_class",
            "target_dscp",
            name=_("Priority"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIContract
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "nb_tenant",
            "qos_class",
            "scope",
            "target_dscp",
            "comments",
            "tags",
        )


class ACIContractBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Contract model."""

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
    qos_class = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("QoS class"),
    )
    scope = forms.ChoiceField(
        choices=add_blank_choice(ContractScopeChoices),
        required=False,
        label=_("Scope"),
    )
    target_dscp = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP"),
    )
    comments = CommentField()

    model = ACIContract
    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant",
            "description",
            "tags",
            name=_("ACI Contract"),
        ),
        FieldSet(
            "scope",
            name=_("Scope"),
        ),
        FieldSet(
            "qos_class",
            "target_dscp",
            name=_("Priority"),
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


class ACIContractFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Contract model."""

    model = ACIContract
    fieldsets: tuple = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant_id",
            "description",
            name="Attributes",
        ),
        FieldSet(
            "scope",
            name=_("Scope"),
        ),
        FieldSet(
            "qos_class",
            "target_dscp",
            name=_("Priority"),
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
        null_option="None",
        required=False,
        label=_("NetBox tenant"),
    )
    qos_class = forms.MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("QoS class"),
    )
    scope = forms.MultipleChoiceField(
        choices=add_blank_choice(ContractScopeChoices),
        required=False,
        label=_("Scope"),
    )
    target_dscp = forms.MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP"),
    )
    tag = TagFilterField(ACIContract)


class ACIContractImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Contract model."""

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
    qos_class = CSVChoiceField(
        choices=QualityOfServiceDSCPChoices,
        required=False,
        label=_("QoS class"),
        help_text=_(
            "Specifies the priority handling for traffic between Consumer and "
            "Provider within the fabric."
            "Default is 'unspecified'."
        ),
    )
    scope = CSVChoiceField(
        choices=ContractScopeChoices,
        required=True,
        label=_("Scope"),
        help_text=_(
            "Scope defines the extent within which the contract is "
            "applicable. Default is 'vrf'."
        ),
    )
    target_dscp = CSVChoiceField(
        choices=QualityOfServiceDSCPChoices,
        required=False,
        label=_("Target DSCP"),
        help_text=_(
            "Rewrites the DSCP value of the incoming traffic to the specified"
            "value. Default is 'unspecified'."
        ),
    )

    class Meta:
        model = ACIContract
        fields: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "description",
            "nb_tenant",
            "qos_class",
            "scope",
            "target_dscp",
            "comments",
            "tags",
        )

    def _clean_field_default_unspecified(self, field_name) -> str:
        """Return default value for empty imported field."""
        field_value = self.cleaned_data.get(field_name, None)
        if not field_value:
            return "unspecified"
        return field_value

    def clean_qos_class(self) -> str:
        """Return a cleaned and validated value for qos_class."""
        return self._clean_field_default_unspecified("qos_class")

    def clean_target_dscp(self) -> str:
        """Return a cleaned and validated value for target_dscp."""
        return self._clean_field_default_unspecified("target_dscp")
