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
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, add_blank_choice
from utilities.forms.fields import (
    CommentField,
    CSVChoiceField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet, TabbedGroups

from ..choices import (
    ContractScopeChoices,
    QualityOfServiceClassChoices,
    QualityOfServiceDSCPChoices,
)
from ..models.tenant_contracts import ACIContract, ACIContractSubject
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
            "Provider within the fabric. "
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
            "Rewrites the DSCP value of the incoming traffic to the specified "
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
            "Provider within the fabric. "
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
            "Rewrites the DSCP value of the incoming traffic to the specified "
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


#
# Contract Subject forms
#


class ACIContractSubjectEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Contract Subject model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        initial_params={"aci_contracts": "$aci_contract"},
        required=False,
        label=_("ACI Tenant"),
    )
    aci_contract = DynamicModelChoiceField(
        queryset=ACIContract.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        required=False,
        label=_("ACI Contract"),
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
    apply_both_directions_enabled = forms.BooleanField(
        required=False,
        label=_("Apply both directions enabled"),
        help_text=_(
            "Enables filters defined in the subject to be applied in both "
            "directions. Default is enabled."
        ),
    )
    qos_class = forms.ChoiceField(
        choices=QualityOfServiceClassChoices,
        required=False,
        label=_("QoS class"),
        help_text=_(
            "Specifies the priority handling for traffic between Consumer and "
            "Provider within the fabric. "
            "Default is 'unspecified'."
        ),
    )
    qos_class_cons_to_prov = forms.ChoiceField(
        choices=QualityOfServiceClassChoices,
        required=False,
        label=_("QoS class (consumer to provider)"),
        help_text=_(
            "Specifies the priority handling for traffic from Consumer to "
            "Provider within the fabric. "
            "Default is 'unspecified'."
        ),
    )
    qos_class_prov_to_cons = forms.ChoiceField(
        choices=QualityOfServiceClassChoices,
        required=False,
        label=_("QoS class (provider to consumer)"),
        help_text=_(
            "Specifies the priority handling for traffic from Provider to "
            "Consumer within the fabric. "
            "Default is 'unspecified'."
        ),
    )
    reverse_filter_ports_enabled = forms.BooleanField(
        required=False,
        label=_("Reverse filter ports enabled"),
        help_text=_(
            "Reverse source and destination ports to allow return traffic. "
            "Default is enabled."
        ),
    )
    target_dscp = forms.ChoiceField(
        choices=QualityOfServiceDSCPChoices,
        required=False,
        label=_("Target DSCP"),
        help_text=_(
            "Rewrites the DSCP value of the incoming traffic to the specified "
            "value. Default is 'unspecified'."
        ),
    )
    target_dscp_cons_to_prov = forms.ChoiceField(
        choices=QualityOfServiceDSCPChoices,
        required=False,
        label=_("Target DSCP (consumer to provider)"),
        help_text=_(
            "Rewrites the DSCP value of the incoming traffic to the specified "
            "value for traffic from Consumer to Provider. "
            "Default is 'unspecified'."
        ),
    )
    target_dscp_prov_to_cons = forms.ChoiceField(
        choices=QualityOfServiceDSCPChoices,
        required=False,
        label=_("Target DSCP (provider to consumer)"),
        help_text=_(
            "Rewrites the DSCP value of the incoming traffic to the specified "
            "value for traffic from Provider to Consumer. "
            "Default is 'unspecified'."
        ),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant",
            "aci_contract",
            "description",
            "tags",
            name=_("ACI Contract Subject"),
        ),
        FieldSet(
            "apply_both_directions_enabled",
            "reverse_filter_ports_enabled",
            name=_("Direction Settings"),
        ),
        FieldSet(
            TabbedGroups(
                FieldSet(
                    "service_graph_name",
                    name=_("Both directions"),
                ),
                FieldSet(
                    "service_graph_name_cons_to_prov",
                    "service_graph_name_prov_to_cons",
                    name=_("Separated directions"),
                ),
            ),
            name=_("Service Graph"),
        ),
        FieldSet(
            TabbedGroups(
                FieldSet(
                    "qos_class",
                    "target_dscp",
                    name=_("Both directions"),
                ),
                FieldSet(
                    "qos_class_cons_to_prov",
                    "qos_class_prov_to_cons",
                    "target_dscp_cons_to_prov",
                    "target_dscp_prov_to_cons",
                    name=_("Separated directions"),
                ),
            ),
            name=_("Priority"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIContractSubject
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_contract",
            "nb_tenant",
            "apply_both_directions_enabled",
            "qos_class",
            "qos_class_cons_to_prov",
            "qos_class_prov_to_cons",
            "reverse_filter_ports_enabled",
            "service_graph_name",
            "service_graph_name_cons_to_prov",
            "service_graph_name_prov_to_cons",
            "target_dscp",
            "target_dscp_cons_to_prov",
            "target_dscp_prov_to_cons",
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the ACI Contract Subject edit form."""

        # Initialize fields with initial values
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()
        if instance is not None:
            # Ensure correct tab selection of TabbedGroups
            if instance.apply_both_directions_enabled:
                # Ensure the tab "Both directions" is selected
                initial["qos_class_cons_to_prov"] = None
                initial["qos_class_prov_to_cons"] = None
                initial["target_dscp_cons_to_prov"] = None
                initial["target_dscp_prov_to_cons"] = None
            else:
                # Ensure the tab "Separated directions" is selected
                initial["qos_class"] = None
                initial["target_dscp"] = None
        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)


class ACIContractSubjectBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Contract Subject model."""

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
    aci_contract = DynamicModelChoiceField(
        queryset=ACIContract.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        required=False,
        label=_("ACI Contract"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
    )
    apply_both_direction_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Apply both direction enabled"),
    )
    qos_class = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("QoS class"),
    )
    qos_class_cons_to_prov = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("QoS class (consumer to provider)"),
    )
    qos_class_prov_to_cons = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("QoS class (provider to consumer)"),
    )
    reverse_filter_ports_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Reverse filter ports enabled"),
    )
    service_graph_name = forms.CharField(
        required=False,
        label=_("Service Graph Name"),
    )
    service_graph_name_cons_to_prov = forms.CharField(
        required=False,
        label=_("Service Graph Name (consumer to provider)"),
    )
    service_graph_name_prov_to_cons = forms.CharField(
        required=False,
        label=_("Service Graph Name (provider to consumer)"),
    )
    target_dscp = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP"),
    )
    target_dscp_cons_to_prov = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP (consumer to provider)"),
    )
    target_dscp_prov_to_cons = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP (provider to consumer)"),
    )
    comments = CommentField()

    model = ACIContractSubject
    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant",
            "aci_contract",
            "description",
            "tags",
            name=_("ACI Contract Subject"),
        ),
        FieldSet(
            "apply_both_directions_enabled",
            "reverse_filter_ports_enabled",
            name=_("Direction Settings"),
        ),
        FieldSet(
            "service_graph_name",
            "service_graph_name_cons_to_prov",
            "service_graph_name_prov_to_cons",
            name=_("Service Graph"),
        ),
        FieldSet(
            "qos_class",
            "qos_class_cons_to_prov",
            "qos_class_prov_to_cons",
            "target_dscp",
            "target_dscp_cons_to_prov",
            "target_dscp_prov_to_cons",
            name=_("Priority"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )
    nullable_fields = (
        "name_alias",
        "description",
        "nb_tenant",
        "service_graph_name",
        "service_graph_name_cons_to_prov",
        "service_graph_name_prov_to_cons",
        "comments",
    )


class ACIContractSubjectFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Contract Subject model."""

    model = ACIContractSubject
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
            "aci_contract_id",
            "description",
            name="Attributes",
        ),
        FieldSet(
            "apply_both_directions_enabled",
            "reverse_filter_ports_enabled",
            name=_("Direction Settings"),
        ),
        FieldSet(
            "service_graph_name",
            "service_graph_name_cons_to_prov",
            "service_graph_name_prov_to_cons",
            name=_("Service Graph"),
        ),
        FieldSet(
            "qos_class",
            "qos_class_cons_to_prov",
            "qos_class_prov_to_cons",
            "target_dscp",
            "target_dscp_cons_to_prov",
            "target_dscp_prov_to_cons",
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
    aci_contract_id = DynamicModelMultipleChoiceField(
        queryset=ACIContract.objects.all(),
        required=False,
        label=_("ACI Contract"),
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
    apply_both_directions_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Apply both directions enabled"),
    )
    qos_class = forms.MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("QoS class"),
    )
    qos_class_cons_to_prov = forms.MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("QoS class (consumer to provider)"),
    )
    qos_class_prov_to_cons = forms.MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("QoS class (provider to consumer)"),
    )
    reverse_filter_ports_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Reverse filter ports enabled"),
    )
    service_graph_name = forms.CharField(
        required=False,
        label=_("Service Graph name"),
    )
    service_graph_name_cons_to_prov = forms.CharField(
        required=False,
        label=_("Service Graph name (consumer to provider)"),
    )
    service_graph_name_prov_to_cons = forms.CharField(
        required=False,
        label=_("Service Graph name (provider to consumer)"),
    )
    target_dscp = forms.MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP"),
    )
    target_dscp_cons_to_prov = forms.MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP (consumer to provider)"),
    )
    target_dscp_prov_to_cons = forms.MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP (provider to consumer)"),
    )
    tag = TagFilterField(ACIContractSubject)


class ACIContractSubjectImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Contract Subject model."""

    aci_tenant = CSVModelChoiceField(
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Tenant"),
        help_text=_("Parent ACI Tenant of ACI Contract"),
    )
    aci_contract = CSVModelChoiceField(
        queryset=ACIContract.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Contract"),
        help_text=_("Assigned ACI Contract"),
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
            "Provider within the fabric. "
            "Default is 'unspecified'."
        ),
    )
    qos_class_cons_to_prov = CSVChoiceField(
        choices=QualityOfServiceDSCPChoices,
        required=False,
        label=_("QoS class (consumer to provider)"),
        help_text=_(
            "Specifies the priority handling for traffic between Consumer and "
            "Provider within the fabric. "
            "Default is 'unspecified'."
        ),
    )
    qos_class_prov_to_cons = CSVChoiceField(
        choices=QualityOfServiceDSCPChoices,
        required=False,
        label=_("QoS class (provider to consumer)"),
        help_text=_(
            "Specifies the priority handling for traffic from Consumer to "
            "Provider within the fabric. "
            "Default is 'unspecified'."
        ),
    )
    target_dscp = CSVChoiceField(
        choices=QualityOfServiceDSCPChoices,
        required=False,
        label=_("Target DSCP"),
        help_text=_(
            "Rewrites the DSCP value of the incoming traffic to the specified "
            "value. Default is 'unspecified'."
        ),
    )
    target_dscp_cons_to_prov = CSVChoiceField(
        choices=QualityOfServiceDSCPChoices,
        required=False,
        label=_("Target DSCP (consumer to provider)"),
        help_text=_(
            "Rewrites the DSCP value of the incoming traffic to the specified "
            "value for traffic from Consumer to Provider. "
            "Default is 'unspecified'."
        ),
    )
    target_dscp_prov_to_cons = CSVChoiceField(
        choices=QualityOfServiceDSCPChoices,
        required=False,
        label=_("Target DSCP (provider to consumer)"),
        help_text=_(
            "Rewrites the DSCP value of the incoming traffic to the specified "
            "value for traffic from Provider to Consumer. "
            "Default is 'unspecified'."
        ),
    )

    class Meta:
        model = ACIContractSubject
        fields: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "aci_contract",
            "description",
            "nb_tenant",
            "apply_both_directions_enabled",
            "qos_class",
            "qos_class_cons_to_prov",
            "qos_class_prov_to_cons",
            "reverse_filter_ports_enabled",
            "service_graph_name",
            "service_graph_name_cons_to_prov",
            "service_graph_name_prov_to_cons",
            "target_dscp",
            "target_dscp_cons_to_prov",
            "target_dscp_prov_to_cons",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)

        if not data:
            return

        # Limit queryset by parent ACI objects
        if data.get("aci_tenant"):
            # Limit ACIContract queryset by parent ACITenant
            self.fields["aci_contract"].queryset = ACIContract.objects.filter(
                aci_tenant__name=data["aci_tenant"]
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

    def clean_qos_class_cons_to_prov(self) -> str:
        """Return a cleaned and validated value for qos_class_cons_to_prov."""
        return self._clean_field_default_unspecified("qos_class_cons_to_prov")

    def clean_qos_class_prov_to_cons(self) -> str:
        """Return a cleaned and validated value for qos_class_prov_to_cons."""
        return self._clean_field_default_unspecified("qos_class_prov_to_cons")

    def clean_target_dscp(self) -> str:
        """Return a cleaned and validated value for target_dscp."""
        return self._clean_field_default_unspecified("target_dscp")

    def clean_target_dscp_cons_to_prov(self) -> str:
        """Return a cleaned value for target_dscp_cons_to_prov."""
        return self._clean_field_default_unspecified(
            "target_dscp_cons_to_prov"
        )

    def clean_target_dscp_prov_to_cons(self) -> str:
        """Return a cleaned value for target_dscp_prov_to_cons."""
        return self._clean_field_default_unspecified(
            "target_dscp_prov_to_cons"
        )
