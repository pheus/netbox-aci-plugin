# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from tenancy.models import Tenant, TenantGroup
from users.models import Owner, OwnerGroup
from utilities.forms import (
    BOOLEAN_WITH_BLANK_CHOICES,
    GenericObjectFormMixin,
    add_blank_choice,
)
from utilities.forms.fields import (
    ChoiceField,
    CommentField,
    CSVChoiceField,
    CSVContentTypeField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    GenericObjectChoiceField,
    MultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet, TabbedGroups

from ...choices import (
    ContractRelationRoleChoices,
    ContractScopeChoices,
    ContractSubjectFilterActionChoices,
    ContractSubjectFilterApplyDirectionChoices,
    ContractSubjectFilterPriorityChoices,
    QualityOfServiceClassChoices,
    QualityOfServiceDSCPChoices,
)
from ...constants import (
    ACI_DESC_MAX_LEN,
    ACI_NAME_MAX_LEN,
    CONTRACT_RELATION_OBJECT_TYPES,
)
from ...models.fabric.fabrics import ACIFabric
from ...models.tenant.contract_filters import ACIContractFilter
from ...models.tenant.contracts import (
    ACIContract,
    ACIContractRelation,
    ACIContractSubject,
    ACIContractSubjectFilter,
)
from ...models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
)
from ...models.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroup,
)
from ...models.tenant.l3outs import ACIExternalEndpointGroup
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF

#
# Contract forms
#


class ACIContractEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Contract model."""

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
    qos_class = ChoiceField(
        choices=QualityOfServiceClassChoices,
        label=_("QoS class"),
        help_text=_(
            "Specifies the priority handling for traffic between Consumer and "
            "Provider within the fabric. "
            "Default is 'unspecified'."
        ),
    )
    scope = ChoiceField(
        choices=ContractScopeChoices,
        label=_("Scope"),
        help_text=_(
            "Scope defines the extent within which the contract is "
            "applicable. Default is 'context'."
        ),
    )
    target_dscp = ChoiceField(
        choices=QualityOfServiceDSCPChoices,
        label=_("Target DSCP"),
        help_text=_(
            "Rewrites the DSCP value of the incoming traffic to the specified "
            "value. Default is 'unspecified'."
        ),
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
        initial_params={"members": "$owner"},
        null_option="None",
        required=False,
        label=_("Owner group"),
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        query_params={"group_id": "$owner_group"},
        required=False,
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
            "qos_class",
            "scope",
            "target_dscp",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACIContractBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Contract model."""

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
    qos_class = ChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("QoS class"),
    )
    scope = ChoiceField(
        choices=add_blank_choice(ContractScopeChoices),
        required=False,
        label=_("Scope"),
    )
    target_dscp = ChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        label=_("Owner"),
    )
    comments = CommentField()

    model = ACIContract
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_tenant",
            "description",
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
            "description",
            "aci_fabric_id",
            "aci_tenant_id",
            name=_("Attributes"),
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
    qos_class = MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("QoS class"),
    )
    scope = MultipleChoiceField(
        choices=add_blank_choice(ContractScopeChoices),
        required=False,
        label=_("Scope"),
    )
    target_dscp = MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP"),
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
    owner_group_id = DynamicModelMultipleChoiceField(
        queryset=OwnerGroup.objects.all(),
        null_option="None",
        required=False,
        label=_("Owner Group"),
    )
    owner_id = DynamicModelMultipleChoiceField(
        queryset=Owner.objects.all(),
        query_params={"group_id": "$owner_group_id"},
        null_option="None",
        required=False,
        label=_("Owner"),
    )
    tag = TagFilterField(model)


class ACIContractImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Contract model."""

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
        model = ACIContract
        fields: tuple = (
            "name",
            "name_alias",
            "aci_fabric",
            "aci_tenant",
            "description",
            "qos_class",
            "scope",
            "target_dscp",
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


class ACIContractRelationEditForm(GenericObjectFormMixin, NetBoxModelForm):
    """NetBox edit form for the ACI Contract Relation model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={"aci_tenants": "$aci_tenant"},
        required=False,
        label=_("ACI Fabric"),
    )
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        required=False,
        label=_("ACI Tenant"),
    )
    aci_contract = DynamicModelChoiceField(
        queryset=ACIContract.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "present_in_aci_tenant_or_common_id": "$aci_tenant",
        },
        label=_("ACI Contract"),
    )
    aci_object = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(
            CONTRACT_RELATION_OBJECT_TYPES
        ),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "aci_tenant_id": "$aci_tenant",
        },
        selector=True,
        hx_target_id="aci_object",
        label=_("ACI Object"),
    )
    role = ChoiceField(
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
            "aci_fabric",
            "aci_tenant",
            "aci_contract",
            "tags",
            name=_("ACI Contract Relation"),
        ),
        FieldSet(
            "aci_object",
            name=_("ACI Object Assignment"),
            html_id="aci_object",
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
            "role",
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the ACI Contract Relation form."""
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()

        # Seed the helper dropdowns from the OBJECT tenant, not the contract
        # tenant. A contract held in "common" must still filter the object
        # dropdown by its own tenant, and the contract dropdown must offer
        # both the object's tenant and common.
        if instance is not None and instance.aci_object:
            initial["aci_tenant"] = instance.aci_object_tenant
            initial["aci_fabric"] = instance.aci_object_tenant.aci_fabric

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)


class ACIContractRelationBulkEditForm(GenericObjectFormMixin, NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Contract Relation model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        required=False,
        label=_("ACI Tenant"),
    )
    aci_contract = DynamicModelChoiceField(
        queryset=ACIContract.objects.all(),
        query_params={"present_in_aci_tenant_or_common_id": "$aci_tenant"},
        required=False,
        label=_("ACI Contract"),
    )
    aci_object = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(
            CONTRACT_RELATION_OBJECT_TYPES
        ),
        query_params={"aci_tenant_id": "$aci_tenant"},
        selector=True,
        required=False,
        hx_method="post",
        label=_("ACI Object"),
    )
    role = ChoiceField(
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
            "aci_object",
            name=_("ACI Contract Relation"),
        ),
        FieldSet(
            "role",
            name=_("Role"),
        ),
    )
    nullable_fields: tuple = ("comments",)


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
            "aci_fabric_id",
            "aci_tenant_id",
            "aci_contract_id",
            name=_("Attributes"),
        ),
        FieldSet(
            "aci_endpoint_group_tenant_id",
            "aci_endpoint_group_id",
            "aci_endpoint_security_group_tenant_id",
            "aci_endpoint_security_group_id",
            "aci_useg_endpoint_group_tenant_id",
            "aci_useg_endpoint_group_id",
            "aci_external_endpoint_group_tenant_id",
            "aci_external_endpoint_group_id",
            "aci_vrf_tenant_id",
            "aci_vrf_id",
            name=_("ACI Object Assignment"),
        ),
        FieldSet(
            "role",
            name=_("Role"),
        ),
    )
    aci_fabric_id = DynamicModelMultipleChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
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
    aci_endpoint_security_group_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        required=False,
        label=_("ACI Tenant of Endpoint Security Group"),
    )
    aci_endpoint_security_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        required=False,
        label=_("ACI Endpoint Security Group"),
    )
    aci_useg_endpoint_group_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        required=False,
        label=_("ACI Tenant of uSeg Endpoint Group"),
    )
    aci_useg_endpoint_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIUSegEndpointGroup.objects.all(),
        required=False,
        label=_("ACI uSeg Endpoint Group"),
    )
    aci_external_endpoint_group_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        required=False,
        label=_("ACI Tenant of External Endpoint Group"),
    )
    aci_external_endpoint_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIExternalEndpointGroup.objects.all(),
        required=False,
        label=_("ACI External Endpoint Group"),
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
    role = MultipleChoiceField(
        choices=add_blank_choice(ContractRelationRoleChoices),
        required=False,
        label=_("Role"),
    )
    tag = TagFilterField(model)


class ACIContractRelationImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Contract Relation model."""

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
    is_aci_contract_in_common = forms.BooleanField(
        required=False,
        label=_("Is ACI Contract in 'common'"),
        help_text=_("Assigned ACI Contract is in ACI Tenant 'common'"),
    )

    class Meta:
        model = ACIContractRelation
        fields: tuple = (
            "aci_fabric",
            "aci_tenant",
            "aci_contract",
            "aci_object_type",
            "aci_object_id",
            "role",
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

            if data.get("is_aci_contract_in_common") == "true":
                # Limit ACIContract queryset by "common" tenant
                self.fields["aci_contract"].queryset = ACIContract.objects.filter(
                    aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_tenant__name="common",
                )
            else:
                # Limit ACIContract queryset by selected ACITenant
                self.fields["aci_contract"].queryset = ACIContract.objects.filter(
                    aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_tenant__name=data["aci_tenant"],
                )


#
# Contract Subject forms
#


class ACIContractSubjectEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Contract Subject model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={"aci_tenants__aci_contracts": "$aci_contract"},
        required=False,
        label=_("ACI Fabric"),
    )
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        initial_params={"aci_contracts": "$aci_contract"},
        required=False,
        label=_("ACI Tenant"),
    )
    aci_contract = DynamicModelChoiceField(
        queryset=ACIContract.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "present_in_aci_tenant_or_common_id": "$aci_tenant",
        },
        label=_("ACI Contract"),
    )
    apply_both_directions_enabled = forms.BooleanField(
        required=False,
        label=_("Apply both directions enabled"),
        help_text=_(
            "Enables filters defined in the subject to be applied in both "
            "directions. Default is enabled."
        ),
    )
    qos_class = ChoiceField(
        choices=QualityOfServiceClassChoices,
        label=_("QoS class"),
        help_text=_(
            "Specifies the priority handling for traffic between Consumer and "
            "Provider within the fabric. "
            "Default is 'unspecified'."
        ),
    )
    qos_class_cons_to_prov = ChoiceField(
        choices=QualityOfServiceClassChoices,
        label=_("QoS class (consumer to provider)"),
        help_text=_(
            "Specifies the priority handling for traffic from Consumer to "
            "Provider within the fabric. "
            "Default is 'unspecified'."
        ),
    )
    qos_class_prov_to_cons = ChoiceField(
        choices=QualityOfServiceClassChoices,
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
    target_dscp = ChoiceField(
        choices=QualityOfServiceDSCPChoices,
        label=_("Target DSCP"),
        help_text=_(
            "Rewrites the DSCP value of the incoming traffic to the specified "
            "value. Default is 'unspecified'."
        ),
    )
    target_dscp_cons_to_prov = ChoiceField(
        choices=QualityOfServiceDSCPChoices,
        label=_("Target DSCP (consumer to provider)"),
        help_text=_(
            "Rewrites the DSCP value of the incoming traffic to the specified "
            "value for traffic from Consumer to Provider. "
            "Default is 'unspecified'."
        ),
    )
    target_dscp_prov_to_cons = ChoiceField(
        choices=QualityOfServiceDSCPChoices,
        label=_("Target DSCP (provider to consumer)"),
        help_text=_(
            "Rewrites the DSCP value of the incoming traffic to the specified "
            "value for traffic from Provider to Consumer. "
            "Default is 'unspecified'."
        ),
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
        initial_params={"members": "$owner"},
        null_option="None",
        required=False,
        label=_("Owner group"),
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        query_params={"group_id": "$owner_group"},
        required=False,
        label=_("Owner"),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_fabric",
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
            "nb_tenant",
            "owner",
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
    aci_contract = DynamicModelChoiceField(
        queryset=ACIContract.objects.all(),
        query_params={"present_in_aci_tenant_or_common_id": "$aci_tenant"},
        required=False,
        label=_("ACI Contract"),
    )
    apply_both_directions_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Apply both direction enabled"),
    )
    qos_class = ChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("QoS class"),
    )
    qos_class_cons_to_prov = ChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("QoS class (consumer to provider)"),
    )
    qos_class_prov_to_cons = ChoiceField(
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
    target_dscp = ChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP"),
    )
    target_dscp_cons_to_prov = ChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP (consumer to provider)"),
    )
    target_dscp_prov_to_cons = ChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP (provider to consumer)"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        label=_("Owner"),
    )
    comments = CommentField()

    model = ACIContractSubject
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_tenant",
            "aci_contract",
            "description",
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
            "description",
            "aci_fabric_id",
            "aci_tenant_id",
            "aci_contract_id",
            name=_("Attributes"),
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
    aci_contract_id = DynamicModelMultipleChoiceField(
        queryset=ACIContract.objects.all(),
        required=False,
        label=_("ACI Contract"),
    )
    apply_both_directions_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Apply both directions enabled"),
    )
    qos_class = MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("QoS class"),
    )
    qos_class_cons_to_prov = MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("QoS class (consumer to provider)"),
    )
    qos_class_prov_to_cons = MultipleChoiceField(
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
    target_dscp = MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP"),
    )
    target_dscp_cons_to_prov = MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP (consumer to provider)"),
    )
    target_dscp_prov_to_cons = MultipleChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Target DSCP (provider to consumer)"),
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
    owner_group_id = DynamicModelMultipleChoiceField(
        queryset=OwnerGroup.objects.all(),
        null_option="None",
        required=False,
        label=_("Owner Group"),
    )
    owner_id = DynamicModelMultipleChoiceField(
        queryset=Owner.objects.all(),
        query_params={"group_id": "$owner_group_id"},
        null_option="None",
        required=False,
        label=_("Owner"),
    )
    tag = TagFilterField(model)


class ACIContractSubjectImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Contract Subject model."""

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
        help_text=_("Parent ACI Tenant of ACI Contract"),
    )
    aci_contract = CSVModelChoiceField(
        queryset=ACIContract.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Contract"),
        help_text=_("Assigned ACI Contract"),
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
        model = ACIContractSubject
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_tenant",
            "aci_contract",
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
            # Limit ACIContract queryset by parent ACITenant
            self.fields["aci_contract"].queryset = ACIContract.objects.filter(
                aci_tenant__aci_fabric__name=data["aci_fabric"],
                aci_tenant__name=data["aci_tenant"],
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

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={
            "aci_tenants__aci_contracts__aci_contract_subjects": "$aci_contract_subject"
        },
        required=False,
        label=_("ACI Fabric"),
    )
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        initial_params={
            "aci_contracts__aci_contract_subjects": "$aci_contract_subject"
        },
        required=False,
        label=_("ACI Tenant"),
    )
    aci_contract = DynamicModelChoiceField(
        queryset=ACIContract.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "present_in_aci_tenant_or_common_id": "$aci_tenant",
        },
        initial_params={"aci_contract_subjects": "$aci_contract_subject"},
        required=False,
        label=_("ACI Contract"),
    )
    aci_contract_filter = DynamicModelChoiceField(
        queryset=ACIContractFilter.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "present_in_aci_tenant_or_common_id": "$aci_tenant",
        },
        label=_("ACI Contract Filter"),
    )
    aci_contract_subject = DynamicModelChoiceField(
        queryset=ACIContractSubject.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "present_in_aci_tenant_or_common_id": "$aci_tenant",
            "aci_contract_id": "$aci_contract",
        },
        label=_("ACI Contract Subject"),
    )
    action = ChoiceField(
        choices=ContractSubjectFilterActionChoices,
        label=_("Action"),
        help_text=_(
            "Defines the action to be taken on the traffic matched by the "
            "filter. Choose 'permit' to allow the traffic, or 'deny' to block "
            "it. Default is 'permit'."
        ),
    )
    apply_direction = ChoiceField(
        choices=ContractSubjectFilterApplyDirectionChoices,
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
    priority = ChoiceField(
        choices=ContractSubjectFilterPriorityChoices,
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
            "aci_fabric",
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
        query_params={"present_in_aci_tenant_or_common_id": "$aci_tenant"},
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
    action = ChoiceField(
        choices=add_blank_choice(ContractSubjectFilterActionChoices),
        required=False,
        label=_("Action"),
    )
    apply_direction = ChoiceField(
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
    priority = ChoiceField(
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
            "aci_fabric_id",
            "aci_tenant_id",
            "aci_contract_id",
            "aci_contract_subject_id",
            "aci_contract_filter_id",
            "action",
            name=_("Attributes"),
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
    action = MultipleChoiceField(
        choices=add_blank_choice(ContractSubjectFilterActionChoices),
        required=False,
        label=_("Action"),
    )
    apply_direction = MultipleChoiceField(
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
    priority = MultipleChoiceField(
        choices=add_blank_choice(ContractSubjectFilterPriorityChoices),
        required=False,
        label=_("(Deny) Priority"),
    )
    tag = TagFilterField(model)


class ACIContractSubjectFilterImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Contract Subject Filter model."""

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

        if (
            data.get("aci_fabric")
            and data.get("aci_tenant")
            and data.get("aci_contract")
        ):
            # Limit ACITenant queryset by parent ACIFabric
            self.fields["aci_tenant"].queryset = ACITenant.objects.filter(
                aci_fabric__name=data["aci_fabric"],
            )
            # Limit ACIContract queryset by parent ACITenant
            self.fields["aci_contract"].queryset = ACIContract.objects.filter(
                aci_tenant__aci_fabric__name=data["aci_fabric"],
                aci_tenant__name=data["aci_tenant"],
            )
            # Limit ACIContractSubject queryset by parent ACIContract
            aci_subject_queryset = ACIContractSubject.objects.filter(
                aci_contract__aci_tenant__aci_fabric__name=data["aci_fabric"],
                aci_contract__aci_tenant__name=data["aci_tenant"],
                aci_contract__name=data["aci_contract"],
            )
            self.fields["aci_contract_subject"].queryset = aci_subject_queryset

            if data.get("is_aci_contract_filter_in_common") == "true":
                # Limit ACIContractFilter queryset by "common" ACITenant
                aci_filter_queryset = ACIContractFilter.objects.filter(
                    aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_tenant__name="common",
                )
                self.fields["aci_contract_filter"].queryset = aci_filter_queryset
            else:
                # Limit ACIContractFilter queryset by ACITenant of ACIContract
                aci_filter_queryset = ACIContractFilter.objects.filter(
                    aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_tenant__name=data["aci_tenant"],
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
