# SPDX-FileCopyrightText: 2026 Martin Hauser
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

from ...choices import LeafInterfacePolicyGroupTypeChoices
from ...constants import ACI_DESC_MAX_LEN, ACI_NAME_MAX_LEN
from ...models.access_policies.aaep import ACIAttachableAccessEntityProfile
from ...models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ...models.fabric.fabrics import ACIFabric

#
# Leaf Interface Policy Group forms
#


class ACILeafInterfacePolicyGroupEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Leaf Interface Policy Group model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        label=_("ACI Fabric"),
    )
    group_type = forms.ChoiceField(
        choices=LeafInterfacePolicyGroupTypeChoices,
        label=_("Type"),
        help_text=_(
            "Type of the Interface Policy Group. The type cannot be "
            "changed after creation."
        ),
    )
    aci_aaep = DynamicModelChoiceField(
        queryset=ACIAttachableAccessEntityProfile.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        required=False,
        label=_("ACI AAEP"),
        help_text=_(
            "Attachable Access Entity Profile associated with the Policy "
            "Group. Required for a deployable access path."
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
            "group_type",
            "aci_aaep",
            "description",
            "tags",
            name=_("ACI Leaf Interface Policy Group"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACILeafInterfacePolicyGroup
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "group_type",
            "aci_aaep",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the ACI Leaf Interface Policy Group form."""
        super().__init__(*args, **kwargs)

        # The type is immutable after creation, so lock it once an
        # instance already exists. A disabled field's value is read
        # from initial (already populated from the instance here), not
        # from POST, so a submitted change is silently ignored.
        if self.instance and self.instance.pk:
            self.fields["group_type"].disabled = True


class ACILeafInterfacePolicyGroupBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Leaf Interface Policy Group model."""

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
    aci_aaep = DynamicModelChoiceField(
        queryset=ACIAttachableAccessEntityProfile.objects.all(),
        required=False,
        label=_("ACI AAEP"),
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

    model = ACILeafInterfacePolicyGroup
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_fabric",
            "aci_aaep",
            "description",
            name=_("ACI Leaf Interface Policy Group"),
        ),
        FieldSet("nb_tenant", name=_("NetBox Tenancy")),
    )
    nullable_fields: tuple = (
        "aci_aaep",
        "comments",
        "description",
        "name_alias",
        "nb_tenant",
    )


class ACILeafInterfacePolicyGroupFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Leaf Interface Policy Group model."""

    model = ACILeafInterfacePolicyGroup
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
            "group_type",
            "aci_aaep_id",
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
    group_type = forms.MultipleChoiceField(
        choices=add_blank_choice(LeafInterfacePolicyGroupTypeChoices),
        required=False,
        label=_("Type"),
    )
    aci_aaep_id = DynamicModelMultipleChoiceField(
        queryset=ACIAttachableAccessEntityProfile.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric_id"},
        required=False,
        label=_("ACI AAEP"),
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


class ACILeafInterfacePolicyGroupImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Leaf Interface Policy Group model."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
        help_text=_("Assigned ACI Fabric."),
    )
    group_type = CSVChoiceField(
        choices=LeafInterfacePolicyGroupTypeChoices,
        label=_("Type"),
        help_text=_(
            "Type of the Interface Policy Group. The type cannot be "
            "changed after creation."
        ),
    )
    aci_aaep = CSVModelChoiceField(
        queryset=ACIAttachableAccessEntityProfile.objects.all(),
        to_field_name="name",
        required=False,
        label=_("ACI AAEP"),
        help_text=_("Assigned ACI AAEP."),
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
        model = ACILeafInterfacePolicyGroup
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "group_type",
            "aci_aaep",
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

        # Limit ACIAttachableAccessEntityProfile by parent ACIFabric
        aaep_queryset = None
        if data.get("aci_fabric") and data.get("aci_aaep"):
            aaep_queryset = ACIAttachableAccessEntityProfile.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
        elif data.get("aci_aaep") and self.instance.pk:
            # A sparse update row may omit aci_fabric entirely
            aaep_queryset = ACIAttachableAccessEntityProfile.objects.filter(
                aci_fabric_id=self.instance.aci_fabric_id
            )

        if aaep_queryset is not None:
            self.fields["aci_aaep"].queryset = aaep_queryset
