# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from tenancy.models import Tenant, TenantGroup
from utilities.forms import (
    BOOLEAN_WITH_BLANK_CHOICES,
    add_blank_choice,
    get_field_value,
)
from utilities.forms.fields import (
    CommentField,
    ContentTypeChoiceField,
    CSVChoiceField,
    CSVContentTypeField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet, TabbedGroups
from utilities.forms.widgets import HTMXSelect
from utilities.templatetags.builtins.filters import bettertitle

from ...choices import (
    ContractRelationRoleChoices,
    ContractScopeChoices,
    ContractSubjectFilterActionChoices,
    ContractSubjectFilterApplyDirectionChoices,
    ContractSubjectFilterPriorityChoices,
    QualityOfServiceClassChoices,
    QualityOfServiceDSCPChoices,
)
from ...constants import CONTRACT_RELATION_OBJECT_TYPES
from ...models.tenant.contract_filters import ACIContractFilter
from ...models.tenant.contracts import (
    ACIContract,
    ACIContractRelation,
    ACIContractSubject,
    ACIContractSubjectFilter,
)
from ...models.tenant.endpoint_groups import ACIEndpointGroup
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF

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
            "applicable. Default is 'context'."
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
    tag = TagFilterField(model)


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
        choices=QualityOfServiceClassChoices,
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
            "applicable. Default is 'context'."
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
# Contract Relation forms
#


class ACIContractRelationEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Contract Relation model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        initial_params={"aci_contracts": "$aci_contract"},
        required=False,
        label=_("ACI Tenant"),
    )
    aci_contract = DynamicModelChoiceField(
        queryset=ACIContract.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        label=_("ACI Contract"),
    )
    aci_object_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(CONTRACT_RELATION_OBJECT_TYPES),
        widget=HTMXSelect(),
        label=_("ACI Object Type"),
    )
    aci_object = DynamicModelChoiceField(
        queryset=ACIEndpointGroup.objects.none(),  # Initial queryset
        query_params={"aci_tenant_id": "$aci_tenant"},
        selector=True,
        label=_("ACI Object"),
        disabled=True,
    )
    role = forms.ChoiceField(
        choices=ContractRelationRoleChoices,
        required=True,
        label=_("Role"),
        help_text=_(
            "Specifies the role of the ACI Contract for the given "
            "ACI object as either a provider or a consumer. "
            "Default is 'provider'."
        ),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "aci_tenant",
            "aci_contract",
            "aci_object_type",
            "aci_object",
            "tags",
            name=_("ACI Contract Relation"),
        ),
        FieldSet(
            "role",
            name=_("Role"),
        ),
    )

    class Meta:
        model = ACIContractRelation
        fields: tuple = (
            "aci_contract",
            "aci_object_type",
            "role",
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the ACI Contract Relation form."""
        # Initialize fields with initial values
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()

        if instance is not None and instance.aci_object:
            # Initialize ACI object field
            initial["aci_object"] = instance.aci_object

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

        if aci_object_type_id := get_field_value(self, "aci_object_type"):
            try:
                # Retrieve the ContentType model class based on the ACI object
                # type
                aci_object_type = ContentType.objects.get(pk=aci_object_type_id)
                aci_model = aci_object_type.model_class()

                # Configure the queryset and label for the aci_object field
                self.fields["aci_object"].queryset = aci_model.objects.all()
                self.fields["aci_object"].widget.attrs["selector"] = (
                    aci_model._meta.label_lower
                )
                self.fields["aci_object"].disabled = False
                self.fields["aci_object"].label = _(
                    bettertitle(aci_model._meta.verbose_name)
                )
            except ObjectDoesNotExist:
                pass

            # Clears the aci_object field if the selected type changes
            if (
                self.instance
                and self.instance.pk
                and aci_object_type_id != self.instance.aci_object_type_id
            ):
                self.initial["aci_object"] = None

    def clean(self) -> None:
        """Validate form fields for the ACI Contract Relation form."""
        super().clean()

        # Ensure the selected ACI object gets assigned
        self.instance.aci_object = self.cleaned_data.get("aci_object")


class ACIContractRelationBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Contract Relation model."""

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
    aci_object_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(CONTRACT_RELATION_OBJECT_TYPES),
        required=False,
        widget=HTMXSelect(method="post", attrs={"hx-select": "#form_fields"}),
        label=_("ACI Object Type"),
    )
    aci_object = DynamicModelChoiceField(
        queryset=ACIEndpointGroup.objects.none(),  # Initial queryset
        query_params={"aci_tenant_id": "$aci_tenant"},
        selector=True,
        required=False,
        label=_("ACI Object"),
        disabled=True,
    )
    role = forms.ChoiceField(
        choices=add_blank_choice(ContractRelationRoleChoices),
        required=False,
        label=_("Role"),
    )
    comments = CommentField()

    model = ACIContractRelation
    fieldsets: tuple = (
        FieldSet(
            "aci_tenant",
            "aci_contract",
            "aci_object_type",
            "aci_object",
            "tags",
            name=_("ACI Contract Relation"),
        ),
        FieldSet(
            "role",
            name=_("Role"),
        ),
    )
    nullable_fields: tuple = ("comments",)

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the ACI Contract Relation bulk edit form."""
        super().__init__(*args, **kwargs)

        if aci_object_type_id := get_field_value(self, "aci_object_type"):
            try:
                # Retrieve the ContentType model class based on the ACI object
                # type
                aci_object_type = ContentType.objects.get(pk=aci_object_type_id)
                aci_model = aci_object_type.model_class()

                # Configure the queryset and label for the aci_object field
                self.fields["aci_object"].queryset = aci_model.objects.all()
                self.fields["aci_object"].widget.attrs["selector"] = (
                    aci_model._meta.label_lower
                )
                self.fields["aci_object"].disabled = False
                self.fields["aci_object"].label = _(
                    bettertitle(aci_model._meta.verbose_name)
                )
            except ObjectDoesNotExist:
                pass


class ACIContractRelationFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Contract Relation model."""

    model = ACIContractRelation
    fieldsets: tuple = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "aci_tenant_id",
            "aci_contract_id",
            name="Attributes",
        ),
        FieldSet(
            "aci_endpoint_group_tenant_id",
            "aci_endpoint_group_id",
            "aci_vrf_tenant_id",
            "aci_vrf_id",
            name=_("ACI Object Assignment"),
        ),
        FieldSet(
            "role",
            name=_("Role"),
        ),
    )
    aci_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        required=False,
        label=_("ACI Tenant of Contract"),
    )
    aci_contract_id = DynamicModelMultipleChoiceField(
        queryset=ACIContract.objects.all(),
        required=False,
        label=_("ACI Contract"),
    )
    aci_endpoint_group_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        required=False,
        label=_("ACI Tenant of Endpoint Group"),
    )
    aci_endpoint_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIEndpointGroup.objects.all(),
        required=False,
        label=_("ACI Endpoint Group"),
    )
    aci_vrf_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        required=False,
        label=_("ACI Tenant of VRF"),
    )
    aci_vrf_id = DynamicModelMultipleChoiceField(
        queryset=ACIVRF.objects.all(),
        required=False,
        label=_("ACI VRF"),
    )
    role = forms.ChoiceField(
        choices=add_blank_choice(ContractRelationRoleChoices),
        required=False,
        label=_("Role"),
    )
    tag = TagFilterField(model)


class ACIContractRelationImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Contract Relation model."""

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
    aci_object_id = forms.IntegerField(
        required=True,
        label=_("ACI Object ID"),
    )
    aci_object_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(CONTRACT_RELATION_OBJECT_TYPES),
        label=_("ACI Object Type (app & model)"),
    )
    role = CSVChoiceField(
        choices=ContractRelationRoleChoices,
        required=False,
        label=_("Role"),
        help_text=_(
            "Specifies the role of the ACI Contract for the given "
            "ACI object as either a provider or a consumer. "
            "Default is 'prov' (Provider)."
        ),
    )

    class Meta:
        model = ACIContractRelation
        fields: tuple = (
            "aci_tenant",
            "aci_contract",
            "aci_object_type",
            "aci_object_id",
            "role",
            "comments",
            "tags",
        )
        labels: dict = {
            "aci_object_id": "ACI Object ID",
        }

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)

        if not data:
            return

        # Limit ACIContract queryset
        if data.get("aci_tenant"):
            # Limit ACIContract queryset by parent ACITenant
            self.fields["aci_contract"].queryset = ACIContract.objects.filter(
                aci_tenant__name=data["aci_tenant"]
            )


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
    tag = TagFilterField(model)


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
        choices=QualityOfServiceClassChoices,
        required=False,
        label=_("QoS class"),
        help_text=_(
            "Specifies the priority handling for traffic between Consumer and "
            "Provider within the fabric. "
            "Default is 'unspecified'."
        ),
    )
    qos_class_cons_to_prov = CSVChoiceField(
        choices=QualityOfServiceClassChoices,
        required=False,
        label=_("QoS class (consumer to provider)"),
        help_text=_(
            "Specifies the priority handling for traffic between Consumer and "
            "Provider within the fabric. "
            "Default is 'unspecified'."
        ),
    )
    qos_class_prov_to_cons = CSVChoiceField(
        choices=QualityOfServiceClassChoices,
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
        return self._clean_field_default_unspecified("target_dscp_cons_to_prov")

    def clean_target_dscp_prov_to_cons(self) -> str:
        """Return a cleaned value for target_dscp_prov_to_cons."""
        return self._clean_field_default_unspecified("target_dscp_prov_to_cons")


#
# Contract Subject Filter forms
#


class ACIContractSubjectFilterEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Contract Subject Filter model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        initial_params={
            "aci_contracts__aci_contract_subjects": "$aci_contract_subject"
        },
        required=False,
        label=_("ACI Tenant"),
    )
    aci_contract = DynamicModelChoiceField(
        queryset=ACIContract.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        initial_params={"aci_contract_subjects": "aci_contract_subject"},
        required=False,
        label=_("ACI Contract"),
    )
    aci_contract_filter = DynamicModelChoiceField(
        queryset=ACIContractFilter.objects.all(),
        query_params={"present_in_aci_tenant_or_common_id": "$aci_tenant"},
        label=_("ACI Contract Filter"),
    )
    aci_contract_subject = DynamicModelChoiceField(
        queryset=ACIContractSubject.objects.all(),
        query_params={"aci_contract_id": "$aci_contract"},
        label=_("ACI Contract Subject"),
    )
    action = forms.ChoiceField(
        choices=ContractSubjectFilterActionChoices,
        label=_("Action"),
        help_text=_(
            "Defines the action to be taken on the traffic matched by the "
            "filter. Choose 'permit' to allow the traffic, or 'deny' to block "
            "it. Default is 'permit'."
        ),
    )
    apply_direction = forms.ChoiceField(
        choices=ContractSubjectFilterApplyDirectionChoices,
        required=False,
        label=_("Apply direction"),
        help_text=_(
            "Specifies the direction to apply the filter: 'both' directions, "
            "'ctp' (consumer to provider), or 'ptc' (provider to consumer). "
            "Default is 'both'."
        ),
    )
    log_enabled = forms.BooleanField(
        required=False,
        label=_("Logging enabled"),
        help_text=_("Enables logging for the matched traffic. Default is disabled."),
    )
    policy_compression_enabled = forms.BooleanField(
        required=False,
        label=_("Policy compression enabled"),
        help_text=_(
            "Enable policy-based compression for filtering traffic. "
            "This reduces the number of rules in the TCAM. "
            "Default is disabled."
        ),
    )
    priority = forms.ChoiceField(
        choices=ContractSubjectFilterPriorityChoices,
        required=False,
        label=_("(Deny) Priority"),
        help_text=_(
            "Specifies the priority of the deny action for matched traffic. "
            "Only relevant when 'deny' is selected as the action. "
            "Default is 'default'."
        ),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "aci_tenant",
            "aci_contract",
            "aci_contract_subject",
            "aci_contract_filter",
            "action",
            "tags",
            name=_("ACI Contract Subject Filter"),
        ),
        FieldSet(
            "apply_direction",
            name=_("Directions Settings"),
        ),
        FieldSet(
            "log_enabled",
            "policy_compression_enabled",
            name=_("Directives Settings"),
        ),
        FieldSet(
            "priority",
            name=_("Priority Settings"),
        ),
    )

    class Meta:
        model = ACIContractSubjectFilter
        fields: tuple = (
            "aci_contract_filter",
            "aci_contract_subject",
            "action",
            "apply_direction",
            "log_enabled",
            "policy_compression_enabled",
            "priority",
            "comments",
            "tags",
        )


class ACIContractSubjectFilterBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Contract Subject Filter model."""

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
    aci_contract_filter = DynamicModelChoiceField(
        queryset=ACIContractFilter.objects.all(),
        query_params={"present_in_aci_tenant_or_common_id": "$aci_tenant"},
        required=False,
        label=_("ACI Contract Filter"),
    )
    aci_contract_subject = DynamicModelChoiceField(
        queryset=ACIContractSubject.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        required=False,
        label=_("ACI Contract Subject"),
    )
    action = forms.ChoiceField(
        choices=add_blank_choice(ContractSubjectFilterActionChoices),
        required=False,
        label=_("Action"),
    )
    apply_direction = forms.ChoiceField(
        choices=add_blank_choice(ContractSubjectFilterApplyDirectionChoices),
        required=False,
        label=_("Apply direction"),
    )
    log_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Logging enabled"),
    )
    policy_compression_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Policy compression enabled"),
    )
    priority = forms.ChoiceField(
        choices=add_blank_choice(ContractSubjectFilterPriorityChoices),
        required=False,
        label=_("(Deny) Priority"),
    )
    comments = CommentField()

    model = ACIContractSubjectFilter
    fieldsets: tuple = (
        FieldSet(
            "aci_tenant",
            "aci_contract",
            "aci_contract_subject",
            "aci_contract_filter",
            "action",
            "tags",
            name=_("ACI Contract Subject Filter"),
        ),
        FieldSet(
            "apply_direction",
            name=_("Directions Settings"),
        ),
        FieldSet(
            "log_enabled",
            "policy_compression_enabled",
            name=_("Directives Settings"),
        ),
        FieldSet(
            "priority",
            name=_("Priority Settings"),
        ),
    )
    nullable_fields = ("comments",)


class ACIContractSubjectFilterFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Contract Subject Filter model."""

    model = ACIContractSubjectFilter
    fieldsets: tuple = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "aci_tenant_id",
            "aci_contract_id",
            "aci_contract_subject_id",
            "aci_contract_filter_id",
            "action",
            "name",
            name="Attributes",
        ),
        FieldSet(
            "apply_direction",
            name=_("Directions Settings"),
        ),
        FieldSet(
            "log_enabled",
            "policy_compression_enabled",
            name=_("Directives Settings"),
        ),
        FieldSet(
            "priority",
            name=_("Priority Settings"),
        ),
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
    aci_contract_filter_id = DynamicModelMultipleChoiceField(
        queryset=ACIContractFilter.objects.all(),
        required=False,
        label=_("ACI Contract Filter"),
    )
    aci_contract_subject_id = DynamicModelMultipleChoiceField(
        queryset=ACIContractSubject.objects.all(),
        required=False,
        label=_("ACI Contract Subject"),
    )
    action = forms.MultipleChoiceField(
        choices=add_blank_choice(ContractSubjectFilterActionChoices),
        required=False,
        label=_("Action"),
    )
    apply_direction = forms.MultipleChoiceField(
        choices=add_blank_choice(ContractSubjectFilterApplyDirectionChoices),
        required=False,
        label=_("Apply direction"),
    )
    log_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Logging enabled"),
    )
    policy_compression_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Policy compression enabled"),
    )
    priority = forms.MultipleChoiceField(
        choices=add_blank_choice(ContractSubjectFilterPriorityChoices),
        required=False,
        label=_("(Deny) Priority"),
    )
    tag = TagFilterField(model)


class ACIContractSubjectFilterImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Contract Subject Filter model."""

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
        help_text=_("Parent ACI Contract of ACI Contract Subject"),
    )
    aci_contract_filter = CSVModelChoiceField(
        queryset=ACIContractFilter.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Contract Filter"),
        help_text=_("Assigned ACI Contract Filter"),
    )
    aci_contract_subject = CSVModelChoiceField(
        queryset=ACIContractSubject.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Contract Subject"),
        help_text=_("Assigned ACI Contract Subject"),
    )
    action = CSVChoiceField(
        choices=ContractSubjectFilterActionChoices,
        required=True,
        label=_("Action"),
        help_text=_(
            "Defines the action to be taken on the traffic matched by the "
            "filter. Choose 'permit' to allow the traffic, or 'deny' to block "
            "it. Default is 'permit'."
        ),
    )
    apply_direction = CSVChoiceField(
        choices=ContractSubjectFilterApplyDirectionChoices,
        required=False,
        label=_("Apply direction"),
        help_text=_(
            "Specifies the direction to apply the filter: 'both' directions, "
            "'ctp' (consumer to provider), or 'ptc' (provider to consumer). "
            "Default is 'both'."
        ),
    )
    priority = CSVChoiceField(
        choices=ContractSubjectFilterPriorityChoices,
        required=False,
        label=_("(Deny) Priority"),
        help_text=_(
            "Specifies the priority of the deny action for matched traffic. "
            "Only relevant when 'deny' is selected as the action. "
            "Default is 'default'."
        ),
    )
    is_aci_contract_filter_in_common = forms.BooleanField(
        required=False,
        label=_("Is ACI Contract Filter in 'common'"),
        help_text=_("Assigned ACI Contract Filter is in ACI Tenant 'common'"),
    )

    class Meta:
        model = ACIContractSubjectFilter
        fields: tuple = (
            "aci_contract_filter",
            "aci_contract_subject",
            "action",
            "apply_direction",
            "log_enabled",
            "policy_compression_enabled",
            "priority",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)

        if not data:
            return

        # Limit ACIContractSubject queryset by parent ACI objects
        if data.get("aci_tenant") and data.get("aci_contract"):
            # Limit ACIContract queryset by parent ACITenant
            self.fields["aci_contract"].queryset = ACIContract.objects.filter(
                aci_tenant__name=data["aci_tenant"]
            )
            # Limit ACIContractSubject queryset by parent ACIContract
            aci_subject_queryset = ACIContractSubject.objects.filter(
                aci_contract__name=data["aci_contract"]
            )
            self.fields["aci_contract_subject"].queryset = aci_subject_queryset

        # Limit ACIContractFilter queryset by "common" ACITenant
        if data.get("is_aci_contract_filter_in_common") == "true":
            aci_filter_queryset = ACIContractFilter.objects.filter(
                aci_tenant__name="common"
            )
            self.fields["aci_contract_filter"].queryset = aci_filter_queryset
        # Limit ACIContractFilter queryset by parent ACITenant
        elif data.get("aci_tenant"):
            # Limit ACIContractFilter queryset by ACITenant of ACIContract
            aci_filter_queryset = ACIContractFilter.objects.filter(
                aci_tenant__name=data["aci_tenant"]
            )
            self.fields["aci_contract_filter"].queryset = aci_filter_queryset

    def clean_apply_direction(self) -> str | None:
        """Return a cleaned and validated value for apply_direction."""
        field_value = self.cleaned_data.get("apply_direction", None)
        if not field_value:
            return ContractSubjectFilterApplyDirectionChoices.DIR_BOTH
        return field_value

    def clean_priority(self) -> str | None:
        """Return a cleaned and validated value for priority."""
        field_value = self.cleaned_data.get("priority", None)
        if not field_value:
            return ContractSubjectFilterPriorityChoices.CLASS_DEFAULT
        return field_value
