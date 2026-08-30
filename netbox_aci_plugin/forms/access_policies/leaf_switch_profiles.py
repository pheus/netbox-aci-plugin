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
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet, InlineFields

from ...constants import (
    ACI_DESC_MAX_LEN,
    ACI_NAME_MAX_LEN,
    LEAF_NODE_ID_MIN,
    NODE_ID_MAX,
)
from ...models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
)
from ...models.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlock,
    ACILeafSelector,
    ACILeafSwitchProfile,
    ACILeafSwitchProfileInterfaceBinding,
)
from ...models.fabric.fabrics import ACIFabric

#
# Leaf Switch Profile forms
#


class ACILeafSwitchProfileEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Leaf Switch Profile model."""

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
            name=_("ACI Leaf Switch Profile"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACILeafSwitchProfile
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


class ACILeafSwitchProfileBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Leaf Switch Profile model."""

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

    model = ACILeafSwitchProfile
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_fabric",
            "description",
            name=_("ACI Leaf Switch Profile"),
        ),
        FieldSet("nb_tenant", name=_("NetBox Tenancy")),
    )
    nullable_fields: tuple = (
        "comments",
        "description",
        "name_alias",
        "nb_tenant",
    )


class ACILeafSwitchProfileFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Leaf Switch Profile model."""

    model = ACILeafSwitchProfile
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


class ACILeafSwitchProfileImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Leaf Switch Profile model."""

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
        model = ACILeafSwitchProfile
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
# Leaf Selector forms
#


class ACILeafSelectorEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Leaf Selector model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={"aci_leaf_switch_profiles": "$aci_leaf_switch_profile"},
        required=False,
        label=_("ACI Fabric"),
    )
    aci_leaf_switch_profile = DynamicModelChoiceField(
        queryset=ACILeafSwitchProfile.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        label=_("ACI Leaf Switch Profile"),
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
            "aci_leaf_switch_profile",
            "description",
            "tags",
            name=_("ACI Leaf Selector"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACILeafSelector
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_leaf_switch_profile",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACILeafSelectorBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Leaf Selector model."""

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
    aci_leaf_switch_profile = DynamicModelChoiceField(
        queryset=ACILeafSwitchProfile.objects.all(),
        required=False,
        label=_("ACI Leaf Switch Profile"),
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

    model = ACILeafSelector
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_leaf_switch_profile",
            "description",
            name=_("ACI Leaf Selector"),
        ),
        FieldSet("nb_tenant", name=_("NetBox Tenancy")),
    )
    nullable_fields: tuple = (
        "comments",
        "description",
        "name_alias",
        "nb_tenant",
    )


class ACILeafSelectorFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Leaf Selector model."""

    model = ACILeafSelector
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
            "aci_leaf_switch_profile_id",
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
    # Top-level Fabric and Profile stay flat with no cascade between
    # them, matching every other top-level filter form. Only
    # Profile -> Selector cascades, and nothing sits below Selector here.
    aci_fabric_id = DynamicModelMultipleChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    aci_leaf_switch_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACILeafSwitchProfile.objects.all(),
        required=False,
        label=_("ACI Leaf Switch Profile"),
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


class ACILeafSelectorImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Leaf Selector model."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
        help_text=_("Parent ACI Fabric of ACI Leaf Switch Profile."),
    )
    aci_leaf_switch_profile = CSVModelChoiceField(
        queryset=ACILeafSwitchProfile.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Leaf Switch Profile"),
        help_text=_("Assigned ACI Leaf Switch Profile."),
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
        model = ACILeafSelector
        fields: tuple = (
            "name",
            "name_alias",
            "aci_fabric",
            "aci_leaf_switch_profile",
            "description",
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

        # Limit ACILeafSwitchProfile by parent ACIFabric
        profile_queryset = None
        if data.get("aci_fabric") and data.get("aci_leaf_switch_profile"):
            profile_queryset = ACILeafSwitchProfile.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
        elif data.get("aci_leaf_switch_profile") and self.instance.pk:
            # A sparse update row may omit aci_fabric entirely
            profile_queryset = ACILeafSwitchProfile.objects.filter(
                aci_fabric_id=self.instance.aci_leaf_switch_profile.aci_fabric_id
            )

        if profile_queryset is not None:
            self.fields["aci_leaf_switch_profile"].queryset = profile_queryset


#
# Leaf Node Block forms
#


class ACILeafNodeBlockEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Leaf Node Block model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={
            "aci_leaf_switch_profiles__aci_leaf_selectors": "$aci_leaf_selector"
        },
        required=False,
        label=_("ACI Fabric"),
    )
    aci_leaf_switch_profile = DynamicModelChoiceField(
        queryset=ACILeafSwitchProfile.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        initial_params={"aci_leaf_selectors": "$aci_leaf_selector"},
        required=False,
        label=_("ACI Leaf Switch Profile"),
    )
    aci_leaf_selector = DynamicModelChoiceField(
        queryset=ACILeafSelector.objects.all(),
        query_params={"aci_leaf_switch_profile_id": "$aci_leaf_switch_profile"},
        label=_("ACI Leaf Selector"),
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
            "aci_leaf_switch_profile",
            "aci_leaf_selector",
            "description",
            "tags",
            name=_("ACI Leaf Node Block"),
        ),
        FieldSet(
            InlineFields(
                "node_id_from",
                "node_id_to",
                label=_("Node IDs"),
                help_text=format_lazy(
                    _("First and last Node ID of the block, from {min} to {max}."),
                    min=LEAF_NODE_ID_MIN,
                    max=NODE_ID_MAX,
                ),
            ),
            name=_("Node ID Range"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACILeafNodeBlock
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_leaf_selector",
            "node_id_from",
            "node_id_to",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACILeafNodeBlockBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Leaf Node Block model."""

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
    aci_leaf_selector = DynamicModelChoiceField(
        queryset=ACILeafSelector.objects.all(),
        required=False,
        label=_("ACI Leaf Selector"),
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

    model = ACILeafNodeBlock
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_leaf_selector",
            "description",
            name=_("ACI Leaf Node Block"),
        ),
        FieldSet("nb_tenant", name=_("NetBox Tenancy")),
    )
    nullable_fields: tuple = (
        "comments",
        "description",
        "name_alias",
        "nb_tenant",
    )


class ACILeafNodeBlockFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Leaf Node Block model."""

    model = ACILeafNodeBlock
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
            "aci_leaf_switch_profile_id",
            "aci_leaf_selector_id",
            "node_id_from",
            "node_id_to",
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
    # Fabric and Profile stay flat with each other. Only Selector
    # cascades from Profile.
    aci_fabric_id = DynamicModelMultipleChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    aci_leaf_switch_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACILeafSwitchProfile.objects.all(),
        required=False,
        label=_("ACI Leaf Switch Profile"),
    )
    aci_leaf_selector_id = DynamicModelMultipleChoiceField(
        queryset=ACILeafSelector.objects.all(),
        query_params={"aci_leaf_switch_profile_id": "$aci_leaf_switch_profile_id"},
        required=False,
        label=_("ACI Leaf Selector"),
    )
    node_id_from = forms.IntegerField(
        required=False,
        label=_("Node ID (from)"),
    )
    node_id_to = forms.IntegerField(
        required=False,
        label=_("Node ID (to)"),
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


class ACILeafNodeBlockImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Leaf Node Block model."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
        help_text=_("Parent ACI Fabric of ACI Leaf Switch Profile."),
    )
    aci_leaf_switch_profile = CSVModelChoiceField(
        queryset=ACILeafSwitchProfile.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Leaf Switch Profile"),
        help_text=_("Parent ACI Leaf Switch Profile of ACI Leaf Selector."),
    )
    aci_leaf_selector = CSVModelChoiceField(
        queryset=ACILeafSelector.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Leaf Selector"),
        help_text=_("Assigned ACI Leaf Selector."),
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
        model = ACILeafNodeBlock
        fields: tuple = (
            "name",
            "name_alias",
            "aci_fabric",
            "aci_leaf_switch_profile",
            "aci_leaf_selector",
            "description",
            "node_id_from",
            "node_id_to",
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

        # Limit ACILeafSwitchProfile by parent ACIFabric, and ACILeafSelector
        # by both
        profile_queryset = None
        selector_queryset = None
        if data.get("aci_fabric") and data.get("aci_leaf_switch_profile"):
            profile_queryset = ACILeafSwitchProfile.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
            selector_queryset = ACILeafSelector.objects.filter(
                aci_leaf_switch_profile__aci_fabric__name=data["aci_fabric"],
                aci_leaf_switch_profile__name=data["aci_leaf_switch_profile"],
            )
        elif data.get("aci_leaf_selector") and self.instance.pk:
            # A sparse update row may omit aci_fabric and
            # aci_leaf_switch_profile entirely
            stored_profile = self.instance.aci_leaf_selector.aci_leaf_switch_profile
            if data.get("aci_leaf_switch_profile"):
                # Such a row may still move the ACI Leaf Node Block to
                # another ACILeafSwitchProfile of the stored ACIFabric
                profile_queryset = ACILeafSwitchProfile.objects.filter(
                    aci_fabric_id=stored_profile.aci_fabric_id
                )
                selector_queryset = ACILeafSelector.objects.filter(
                    aci_leaf_switch_profile__in=profile_queryset,
                    aci_leaf_switch_profile__name=data["aci_leaf_switch_profile"],
                )
            elif data.get("aci_fabric"):
                # Such a row may also move the ACI Leaf Node Block to
                # another ACIFabric
                profile_queryset = ACILeafSwitchProfile.objects.filter(
                    aci_fabric__name=data["aci_fabric"]
                )
                selector_queryset = ACILeafSelector.objects.filter(
                    aci_leaf_switch_profile__in=profile_queryset
                )
            else:
                selector_queryset = ACILeafSelector.objects.filter(
                    aci_leaf_switch_profile=stored_profile
                )

        if profile_queryset is not None:
            self.fields["aci_leaf_switch_profile"].queryset = profile_queryset
        if selector_queryset is not None:
            self.fields["aci_leaf_selector"].queryset = selector_queryset


#
# Leaf Switch Profile Interface Binding forms
#


class ACILeafSwitchProfileInterfaceBindingEditForm(NetBoxModelForm):
    """NetBox edit form for the ACILeafSwitchProfileInterfaceBinding model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={"aci_leaf_switch_profiles": "$aci_leaf_switch_profile"},
        required=False,
        label=_("ACI Fabric"),
    )
    aci_leaf_switch_profile = DynamicModelChoiceField(
        queryset=ACILeafSwitchProfile.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        label=_("ACI Leaf Switch Profile"),
    )
    aci_leaf_interface_profile = DynamicModelChoiceField(
        queryset=ACILeafInterfaceProfile.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        label=_("ACI Leaf Interface Profile"),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "aci_fabric",
            "aci_leaf_switch_profile",
            "aci_leaf_interface_profile",
            "tags",
            name=_("ACI Leaf Switch Profile Interface Binding"),
        ),
    )

    class Meta:
        model = ACILeafSwitchProfileInterfaceBinding
        fields: tuple = (
            "aci_leaf_switch_profile",
            "aci_leaf_interface_profile",
            "comments",
            "tags",
        )


class ACILeafSwitchProfileInterfaceBindingBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the Leaf Switch Profile Interface Binding."""

    aci_leaf_switch_profile = DynamicModelChoiceField(
        queryset=ACILeafSwitchProfile.objects.all(),
        required=False,
        label=_("ACI Leaf Switch Profile"),
    )
    aci_leaf_interface_profile = DynamicModelChoiceField(
        queryset=ACILeafInterfaceProfile.objects.all(),
        required=False,
        label=_("ACI Leaf Interface Profile"),
    )
    comments = CommentField()

    model = ACILeafSwitchProfileInterfaceBinding
    fieldsets: tuple = (
        FieldSet(
            "aci_leaf_switch_profile",
            "aci_leaf_interface_profile",
            name=_("ACI Leaf Switch Profile Interface Binding"),
        ),
    )
    nullable_fields: tuple = ("comments",)


class ACILeafSwitchProfileInterfaceBindingFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the Leaf Switch Profile Interface Binding."""

    model = ACILeafSwitchProfileInterfaceBinding
    fieldsets: tuple = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet(
            "aci_fabric_id",
            "aci_leaf_switch_profile_id",
            "aci_leaf_interface_profile_id",
            name=_("Attributes"),
        ),
    )

    aci_fabric_id = DynamicModelMultipleChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    aci_leaf_switch_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACILeafSwitchProfile.objects.all(),
        required=False,
        label=_("ACI Leaf Switch Profile"),
    )
    aci_leaf_interface_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACILeafInterfaceProfile.objects.all(),
        required=False,
        label=_("ACI Leaf Interface Profile"),
    )
    tag = TagFilterField(model)


class ACILeafSwitchProfileInterfaceBindingImportForm(NetBoxModelImportForm):
    """NetBox import form for the Leaf Switch Profile Interface Binding."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
        help_text=_("Parent ACI Fabric of both ACI Leaf Profiles."),
    )
    aci_leaf_switch_profile = CSVModelChoiceField(
        queryset=ACILeafSwitchProfile.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Leaf Switch Profile"),
        help_text=_("Assigned ACI Leaf Switch Profile."),
    )
    aci_leaf_interface_profile = CSVModelChoiceField(
        queryset=ACILeafInterfaceProfile.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Leaf Interface Profile"),
        help_text=_("Assigned ACI Leaf Interface Profile."),
    )

    class Meta:
        model = ACILeafSwitchProfileInterfaceBinding
        fields: tuple = (
            "aci_fabric",
            "aci_leaf_switch_profile",
            "aci_leaf_interface_profile",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)

        if not data:
            return

        # Limit ACILeafSwitchProfile by parent ACIFabric
        switch_profile_queryset = None
        if data.get("aci_fabric") and data.get("aci_leaf_switch_profile"):
            switch_profile_queryset = ACILeafSwitchProfile.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
        elif data.get("aci_leaf_switch_profile") and self.instance.pk:
            # A sparse update row may omit aci_fabric entirely
            switch_profile_queryset = ACILeafSwitchProfile.objects.filter(
                aci_fabric_id=self.instance.aci_leaf_switch_profile.aci_fabric_id
            )
        if switch_profile_queryset is not None:
            self.fields["aci_leaf_switch_profile"].queryset = switch_profile_queryset

        # Limit ACILeafInterfaceProfile by parent ACIFabric
        interface_profile_queryset = None
        if data.get("aci_fabric") and data.get("aci_leaf_interface_profile"):
            interface_profile_queryset = ACILeafInterfaceProfile.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
        elif data.get("aci_leaf_interface_profile") and self.instance.pk:
            # A sparse update row may omit aci_fabric entirely
            interface_profile_queryset = ACILeafInterfaceProfile.objects.filter(
                aci_fabric_id=self.instance.aci_leaf_interface_profile.aci_fabric_id
            )
        if interface_profile_queryset is not None:
            self.fields[
                "aci_leaf_interface_profile"
            ].queryset = interface_profile_queryset
