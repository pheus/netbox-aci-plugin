# SPDX-FileCopyrightText: 2026 Martin Hauser
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
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, GenericObjectFormMixin
from utilities.forms.fields import (
    CommentField,
    CSVContentTypeField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    GenericObjectChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from ...constants import AAEP_DOMAIN_OBJECT_TYPES, ACI_DESC_MAX_LEN, ACI_NAME_MAX_LEN
from ...models.access_policies.aaep import (
    ACIAAEPDomainBinding,
    ACIAttachableAccessEntityProfile,
)
from ...models.access_policies.domains import ACIPhysicalDomain, ACIRoutedDomain
from ...models.fabric.fabrics import ACIFabric

#
# AAEP forms
#


class ACIAttachableAccessEntityProfileEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI AAEP model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        label=_("ACI Fabric"),
    )
    infra_vlan = forms.BooleanField(
        required=False,
        label=_("Infrastructure VLAN"),
        help_text=_(
            "Enable the infrastructure VLAN on ports associated with this AAEP."
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
            "infra_vlan",
            "description",
            "tags",
            name=_("ACI Attachable Access Entity Profile"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIAttachableAccessEntityProfile
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "infra_vlan",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACIAttachableAccessEntityProfileBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI AAEP model."""

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
    infra_vlan = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Infrastructure VLAN"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox tenant"),
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        query_params={"group_id": "$owner_group"},
        label=_("Owner"),
    )
    comments = CommentField()

    model = ACIAttachableAccessEntityProfile
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_fabric",
            "infra_vlan",
            "description",
            name=_("ACI Attachable Access Entity Profile"),
        ),
        FieldSet("nb_tenant", name=_("NetBox Tenancy")),
    )
    nullable_fields: tuple = (
        "comments",
        "description",
        "name_alias",
        "nb_tenant",
    )


class ACIAttachableAccessEntityProfileFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI AAEP model."""

    model = ACIAttachableAccessEntityProfile
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
            "infra_vlan",
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
    infra_vlan = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Infrastructure VLAN"),
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


class ACIAttachableAccessEntityProfileImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI AAEP model."""

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
        help_text=_("Name of the object's owner"),
    )

    class Meta:
        model = ACIAttachableAccessEntityProfile
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "infra_vlan",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


#
# AAEP Domain Binding forms
#


class ACIAAEPDomainBindingEditForm(GenericObjectFormMixin, NetBoxModelForm):
    """NetBox edit form for the ACI AAEP Domain Binding model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={"aci_aaeps": "$aci_aaep"},
        required=False,
        label=_("ACI Fabric"),
    )
    aci_aaep = DynamicModelChoiceField(
        queryset=ACIAttachableAccessEntityProfile.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        label=_("ACI AAEP"),
    )
    aci_domain_object = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(AAEP_DOMAIN_OBJECT_TYPES),
        query_params={"aci_fabric_id": "$aci_fabric"},
        selector=True,
        hx_target_id="aci_domain_object",
        label=_("ACI Domain Object"),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "aci_fabric",
            "aci_aaep",
            "tags",
            name=_("ACI AAEP Domain Binding"),
        ),
        FieldSet(
            "aci_domain_object",
            name=_("Domain Assignment"),
            html_id="aci_domain_object",
        ),
    )

    class Meta:
        model = ACIAAEPDomainBinding
        fields: tuple = (
            "aci_aaep",
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the ACI AAEP Domain Binding form."""
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()

        # Seed the helper aci_fabric dropdown from the bound domain, which
        # the generic object field knows nothing about.
        if instance is not None and instance.aci_domain_object:
            initial["aci_fabric"] = instance.aci_domain_object.aci_fabric

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)


class ACIAAEPDomainBindingBulkEditForm(GenericObjectFormMixin, NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI AAEP Domain Binding model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    aci_aaep = DynamicModelChoiceField(
        queryset=ACIAttachableAccessEntityProfile.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        required=False,
        label=_("ACI AAEP"),
    )
    aci_domain_object = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(AAEP_DOMAIN_OBJECT_TYPES),
        query_params={"aci_fabric_id": "$aci_fabric"},
        selector=True,
        required=False,
        hx_method="post",
        label=_("ACI Domain Object"),
    )
    comments = CommentField()

    model = ACIAAEPDomainBinding
    fieldsets: tuple = (
        FieldSet(
            "aci_fabric",
            "aci_aaep",
            "aci_domain_object",
            name=_("ACI AAEP Domain Binding"),
        ),
    )
    nullable_fields: tuple = ("comments",)


class ACIAAEPDomainBindingFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI AAEP Domain Binding model."""

    model = ACIAAEPDomainBinding
    fieldsets: tuple = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "aci_fabric_id",
            "aci_aaep_id",
            name=_("Attributes"),
        ),
        FieldSet(
            "aci_physical_domain_id",
            "aci_routed_domain_id",
            name=_("ACI Domain Assignment"),
        ),
    )

    aci_fabric_id = DynamicModelMultipleChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    aci_aaep_id = DynamicModelMultipleChoiceField(
        queryset=ACIAttachableAccessEntityProfile.objects.all(),
        required=False,
        label=_("ACI AAEP"),
    )
    aci_physical_domain_id = DynamicModelMultipleChoiceField(
        queryset=ACIPhysicalDomain.objects.all(),
        required=False,
        label=_("ACI Physical Domain"),
    )
    aci_routed_domain_id = DynamicModelMultipleChoiceField(
        queryset=ACIRoutedDomain.objects.all(),
        required=False,
        label=_("ACI Routed Domain"),
    )
    tag = TagFilterField(model)


class ACIAAEPDomainBindingImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI AAEP Domain Binding model."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
        help_text=_("Parent ACI Fabric of ACI AAEP."),
    )
    aci_aaep = CSVModelChoiceField(
        queryset=ACIAttachableAccessEntityProfile.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI AAEP"),
        help_text=_("Assigned ACI AAEP."),
    )
    aci_domain_object_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(AAEP_DOMAIN_OBJECT_TYPES),
        label=_("ACI domain object type (app & model)"),
    )
    aci_domain_object_id = forms.IntegerField(
        required=True,
        label=_("ACI domain object ID"),
    )

    class Meta:
        model = ACIAAEPDomainBinding
        fields: tuple = (
            "aci_fabric",
            "aci_aaep",
            "aci_domain_object_type",
            "aci_domain_object_id",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)

        if not data:
            return

        if data.get("aci_fabric") and data.get("aci_aaep"):
            # Limit ACIAttachableAccessEntityProfile by parent ACIFabric
            self.fields[
                "aci_aaep"
            ].queryset = ACIAttachableAccessEntityProfile.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
