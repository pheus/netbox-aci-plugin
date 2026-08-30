# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.utils.text import format_lazy
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
    CSVChoiceField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet, InlineFields

from ...choices import LeafInterfacePolicyGroupTypeChoices
from ...constants import (
    ACI_DESC_MAX_LEN,
    ACI_NAME_MAX_LEN,
    LEAF_PORT_BLOCK_MODULE_MAX,
    LEAF_PORT_BLOCK_MODULE_MIN,
    NODE_INTERFACE_PORT_MAX,
    NODE_INTERFACE_PORT_MIN,
)
from ...models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ...models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
    ACILeafInterfaceSelector,
    ACILeafPortBlock,
)
from ...models.fabric.fabrics import ACIFabric

#
# Leaf Interface Profile forms
#


class ACILeafInterfaceProfileEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Leaf Interface Profile model."""

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
            "description",
            "tags",
            name=_("ACI Leaf Interface Profile"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACILeafInterfaceProfile
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


class ACILeafInterfaceProfileBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Leaf Interface Profile model."""

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
        label=_("Owner"),
    )
    comments = CommentField()

    model = ACILeafInterfaceProfile
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_fabric",
            "description",
            name=_("ACI Leaf Interface Profile"),
        ),
        FieldSet("nb_tenant", name=_("NetBox Tenancy")),
    )
    nullable_fields: tuple = (
        "comments",
        "description",
        "name_alias",
        "nb_tenant",
    )


class ACILeafInterfaceProfileFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Leaf Interface Profile model."""

    model = ACILeafInterfaceProfile
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


class ACILeafInterfaceProfileImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Leaf Interface Profile model."""

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

    class Meta:
        model = ACILeafInterfaceProfile
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


#
# Leaf Interface Selector forms
#


class ACILeafInterfaceSelectorEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Leaf Interface Selector model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={"aci_leaf_interface_profiles": "$aci_leaf_interface_profile"},
        required=False,
        label=_("ACI Fabric"),
    )
    aci_leaf_interface_profile = DynamicModelChoiceField(
        queryset=ACILeafInterfaceProfile.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        label=_("ACI Leaf Interface Profile"),
    )
    aci_leaf_interface_policy_group = DynamicModelChoiceField(
        queryset=ACILeafInterfacePolicyGroup.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        required=False,
        label=_("ACI Leaf Interface Policy Group"),
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
            "aci_leaf_interface_profile",
            "aci_leaf_interface_policy_group",
            "description",
            "tags",
            name=_("ACI Leaf Interface Selector"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACILeafInterfaceSelector
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_leaf_interface_profile",
            "aci_leaf_interface_policy_group",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACILeafInterfaceSelectorBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Leaf Interface Selector model."""

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
    aci_leaf_interface_profile = DynamicModelChoiceField(
        queryset=ACILeafInterfaceProfile.objects.all(),
        required=False,
        label=_("ACI Leaf Interface Profile"),
    )
    aci_leaf_interface_policy_group = DynamicModelChoiceField(
        queryset=ACILeafInterfacePolicyGroup.objects.all(),
        required=False,
        label=_("ACI Leaf Interface Policy Group"),
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

    model = ACILeafInterfaceSelector
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_leaf_interface_profile",
            "aci_leaf_interface_policy_group",
            "description",
            name=_("ACI Leaf Interface Selector"),
        ),
        FieldSet("nb_tenant", name=_("NetBox Tenancy")),
    )
    nullable_fields: tuple = (
        "aci_leaf_interface_policy_group",
        "comments",
        "description",
        "name_alias",
        "nb_tenant",
    )


class ACILeafInterfaceSelectorFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Leaf Interface Selector model."""

    model = ACILeafInterfaceSelector
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
            "aci_leaf_interface_profile_id",
            "aci_leaf_interface_policy_group_id",
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
    # Top-level Fabric and Profile do not cascade into each other
    aci_fabric_id = DynamicModelMultipleChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    aci_leaf_interface_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACILeafInterfaceProfile.objects.all(),
        required=False,
        label=_("ACI Leaf Interface Profile"),
    )
    aci_leaf_interface_policy_group_id = DynamicModelMultipleChoiceField(
        queryset=ACILeafInterfacePolicyGroup.objects.all(),
        required=False,
        label=_("ACI Leaf Interface Policy Group"),
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


class ACILeafInterfaceSelectorImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Leaf Interface Selector model."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
        help_text=_("Parent ACI Fabric of ACI Leaf Interface Profile."),
    )
    aci_leaf_interface_profile = CSVModelChoiceField(
        queryset=ACILeafInterfaceProfile.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Leaf Interface Profile"),
        help_text=_("Assigned ACI Leaf Interface Profile."),
    )
    aci_leaf_interface_policy_group = CSVModelChoiceField(
        queryset=ACILeafInterfacePolicyGroup.objects.all(),
        to_field_name="name",
        required=False,
        label=_("ACI Leaf Interface Policy Group"),
        help_text=_("Assigned ACI Leaf Interface Policy Group."),
    )
    aci_leaf_interface_policy_group_type = CSVChoiceField(
        choices=LeafInterfacePolicyGroupTypeChoices,
        required=False,
        label=_("ACI Leaf Interface Policy Group Type"),
        help_text=_(
            "Type of the assigned ACI Leaf Interface Policy Group. Needed "
            "only when an access and a bundle group share a name."
        ),
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

    class Meta:
        model = ACILeafInterfaceSelector
        fields: tuple = (
            "name",
            "name_alias",
            "aci_fabric",
            "aci_leaf_interface_profile",
            "description",
            "aci_leaf_interface_policy_group",
            "aci_leaf_interface_policy_group_type",
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

        # Limit ACILeafInterfaceProfile by parent ACIFabric
        profile_queryset = None
        if data.get("aci_fabric") and data.get("aci_leaf_interface_profile"):
            profile_queryset = ACILeafInterfaceProfile.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
        elif data.get("aci_leaf_interface_profile") and self.instance.pk:
            # A sparse update row may omit aci_fabric entirely
            profile_queryset = ACILeafInterfaceProfile.objects.filter(
                aci_fabric_id=self.instance.aci_leaf_interface_profile.aci_fabric_id
            )
        if profile_queryset is not None:
            self.fields["aci_leaf_interface_profile"].queryset = profile_queryset

        # Policy Group names are unique per Fabric and type class, so an
        # access and a bundle group may share one name in one Fabric
        policy_group_queryset = None
        if data.get("aci_fabric") and data.get("aci_leaf_interface_policy_group"):
            policy_group_queryset = ACILeafInterfacePolicyGroup.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
        elif data.get("aci_leaf_interface_policy_group") and self.instance.pk:
            # A sparse update row may omit aci_fabric entirely
            policy_group_queryset = ACILeafInterfacePolicyGroup.objects.filter(
                aci_fabric_id=self.instance.aci_leaf_interface_profile.aci_fabric_id
            )
        if policy_group_queryset is not None:
            if data.get("aci_leaf_interface_policy_group_type"):
                policy_group_queryset = policy_group_queryset.filter(
                    group_type=data["aci_leaf_interface_policy_group_type"]
                )
            self.fields[
                "aci_leaf_interface_policy_group"
            ].queryset = policy_group_queryset


#
# Leaf Port Block forms
#


class ACILeafPortBlockEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Leaf Port Block model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={
            "aci_leaf_interface_profiles__aci_leaf_interface_selectors": (
                "$aci_leaf_interface_selector"
            )
        },
        required=False,
        label=_("ACI Fabric"),
    )
    aci_leaf_interface_profile = DynamicModelChoiceField(
        queryset=ACILeafInterfaceProfile.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        initial_params={"aci_leaf_interface_selectors": "$aci_leaf_interface_selector"},
        required=False,
        label=_("ACI Leaf Interface Profile"),
    )
    aci_leaf_interface_selector = DynamicModelChoiceField(
        queryset=ACILeafInterfaceSelector.objects.all(),
        query_params={"aci_leaf_interface_profile_id": "$aci_leaf_interface_profile"},
        label=_("ACI Leaf Interface Selector"),
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
            "aci_leaf_interface_profile",
            "aci_leaf_interface_selector",
            "description",
            "tags",
            name=_("ACI Leaf Port Block"),
        ),
        FieldSet(
            InlineFields(
                "module_from",
                "module_to",
                label=_("Modules"),
                help_text=format_lazy(
                    _("First and last module of the block, from {min} to {max}."),
                    min=LEAF_PORT_BLOCK_MODULE_MIN,
                    max=LEAF_PORT_BLOCK_MODULE_MAX,
                ),
            ),
            InlineFields(
                "port_from",
                "port_to",
                label=_("Ports"),
                help_text=format_lazy(
                    _("First and last port of the block, from {min} to {max}."),
                    min=NODE_INTERFACE_PORT_MIN,
                    max=NODE_INTERFACE_PORT_MAX,
                ),
            ),
            name=_("Module and Port Ranges"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACILeafPortBlock
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_leaf_interface_selector",
            "module_from",
            "module_to",
            "port_from",
            "port_to",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACILeafPortBlockBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Leaf Port Block model."""

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
    aci_leaf_interface_selector = DynamicModelChoiceField(
        queryset=ACILeafInterfaceSelector.objects.all(),
        required=False,
        label=_("ACI Leaf Interface Selector"),
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

    model = ACILeafPortBlock
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_leaf_interface_selector",
            "description",
            name=_("ACI Leaf Port Block"),
        ),
        FieldSet("nb_tenant", name=_("NetBox Tenancy")),
    )
    nullable_fields: tuple = (
        "comments",
        "description",
        "name_alias",
        "nb_tenant",
    )


class ACILeafPortBlockFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Leaf Port Block model."""

    model = ACILeafPortBlock
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
            "aci_leaf_interface_profile_id",
            "aci_leaf_interface_selector_id",
            "module_from",
            "module_to",
            "port_from",
            "port_to",
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
    # Top-level Fabric and Profile do not cascade into each other
    aci_fabric_id = DynamicModelMultipleChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    aci_leaf_interface_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACILeafInterfaceProfile.objects.all(),
        required=False,
        label=_("ACI Leaf Interface Profile"),
    )
    aci_leaf_interface_selector_id = DynamicModelMultipleChoiceField(
        queryset=ACILeafInterfaceSelector.objects.all(),
        query_params={
            "aci_leaf_interface_profile_id": "$aci_leaf_interface_profile_id"
        },
        required=False,
        label=_("ACI Leaf Interface Selector"),
    )
    module_from = forms.IntegerField(
        required=False,
        label=_("Module (from)"),
    )
    module_to = forms.IntegerField(
        required=False,
        label=_("Module (to)"),
    )
    port_from = forms.IntegerField(
        required=False,
        label=_("Port (from)"),
    )
    port_to = forms.IntegerField(
        required=False,
        label=_("Port (to)"),
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


class ACILeafPortBlockImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Leaf Port Block model."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
        help_text=_("Parent ACI Fabric of ACI Leaf Interface Profile."),
    )
    aci_leaf_interface_profile = CSVModelChoiceField(
        queryset=ACILeafInterfaceProfile.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Leaf Interface Profile"),
        help_text=_(
            "Parent ACI Leaf Interface Profile of ACI Leaf Interface Selector."
        ),
    )
    aci_leaf_interface_selector = CSVModelChoiceField(
        queryset=ACILeafInterfaceSelector.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Leaf Interface Selector"),
        help_text=_("Assigned ACI Leaf Interface Selector."),
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

    class Meta:
        model = ACILeafPortBlock
        fields: tuple = (
            "name",
            "name_alias",
            "aci_fabric",
            "aci_leaf_interface_profile",
            "aci_leaf_interface_selector",
            "description",
            "module_from",
            "module_to",
            "port_from",
            "port_to",
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

        # Limit ACILeafInterfaceProfile by parent ACIFabric, and
        # ACILeafInterfaceSelector by both
        profile_queryset = None
        selector_queryset = None
        if data.get("aci_fabric") and data.get("aci_leaf_interface_profile"):
            profile_queryset = ACILeafInterfaceProfile.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
            selector_queryset = ACILeafInterfaceSelector.objects.filter(
                aci_leaf_interface_profile__aci_fabric__name=data["aci_fabric"],
                aci_leaf_interface_profile__name=data["aci_leaf_interface_profile"],
            )
        elif data.get("aci_leaf_interface_selector") and self.instance.pk:
            # A sparse update row may omit aci_fabric and
            # aci_leaf_interface_profile entirely
            stored_profile = (
                self.instance.aci_leaf_interface_selector.aci_leaf_interface_profile
            )
            if data.get("aci_leaf_interface_profile"):
                # Such a row may still move the ACI Leaf Port Block to
                # another ACILeafInterfaceProfile of the stored ACIFabric
                profile_queryset = ACILeafInterfaceProfile.objects.filter(
                    aci_fabric_id=stored_profile.aci_fabric_id
                )
                selector_queryset = ACILeafInterfaceSelector.objects.filter(
                    aci_leaf_interface_profile__in=profile_queryset,
                    aci_leaf_interface_profile__name=data["aci_leaf_interface_profile"],
                )
            elif data.get("aci_fabric"):
                # Such a row may also move the ACI Leaf Port Block to
                # another ACIFabric
                profile_queryset = ACILeafInterfaceProfile.objects.filter(
                    aci_fabric__name=data["aci_fabric"]
                )
                selector_queryset = ACILeafInterfaceSelector.objects.filter(
                    aci_leaf_interface_profile__in=profile_queryset
                )
            else:
                selector_queryset = ACILeafInterfaceSelector.objects.filter(
                    aci_leaf_interface_profile=stored_profile
                )

        if profile_queryset is not None:
            self.fields["aci_leaf_interface_profile"].queryset = profile_queryset
        if selector_queryset is not None:
            self.fields["aci_leaf_interface_selector"].queryset = selector_queryset
