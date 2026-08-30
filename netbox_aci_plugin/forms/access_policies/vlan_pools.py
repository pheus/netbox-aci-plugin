# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _

from ipam.models import VLANGroup
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
    ChoiceField,
    CommentField,
    CSVChoiceField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    MultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet, InlineFields

from ...choices import (
    VLANAllocationModeChoices,
    VLANPoolRangeAllocationModeChoices,
    VLANPoolRangeRoleChoices,
)
from ...constants import (
    ACI_DESC_MAX_LEN,
    ACI_NAME_MAX_LEN,
    VLAN_VID_MAX,
    VLAN_VID_MIN,
)
from ...models.access_policies.vlan_pools import ACIVLANPool, ACIVLANPoolRange
from ...models.fabric.fabrics import ACIFabric
from ...validators import (
    ACIPolicyDescriptionValidator,
    ACIPolicyNameRequiredValidator,
)


class ACIVLANPoolEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI VLAN Pool model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        label=_("ACI Fabric"),
    )
    allocation_mode = ChoiceField(
        choices=VLANAllocationModeChoices,
        label=_("Allocation mode"),
        help_text=_(
            "Dynamic pools let the APIC assign VLANs automatically (typically "
            "for VMM domains). Static pools use manually defined ranges."
        ),
    )
    nb_vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label=_("NetBox VLAN group"),
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
            "allocation_mode",
            "nb_vlan_group",
            "description",
            "tags",
            name=_("ACI VLAN Pool"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIVLANPool
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "allocation_mode",
            "nb_vlan_group",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACIVLANPoolBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI VLAN Pool model."""

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
    allocation_mode = ChoiceField(
        choices=add_blank_choice(VLANAllocationModeChoices),
        required=False,
        label=_("Allocation mode"),
    )
    nb_vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label=_("NetBox VLAN group"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox tenant"),
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        label=_("Owner"),
    )
    comments = CommentField()

    model = ACIVLANPool
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_fabric",
            "allocation_mode",
            "nb_vlan_group",
            "description",
            name=_("ACI VLAN Pool"),
        ),
        FieldSet("nb_tenant", name=_("NetBox Tenancy")),
    )
    nullable_fields: tuple = (
        "comments",
        "description",
        "name_alias",
        "nb_tenant",
        "nb_vlan_group",
    )


class ACIVLANPoolFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI VLAN Pool model."""

    model = ACIVLANPool
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
            "allocation_mode",
            "nb_vlan_group_id",
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
    allocation_mode = MultipleChoiceField(
        choices=add_blank_choice(VLANAllocationModeChoices),
        required=False,
        label=_("Allocation mode"),
    )
    nb_vlan_group_id = DynamicModelMultipleChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label=_("NetBox VLAN group"),
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


class ACIVLANPoolImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI VLAN Pool model."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
        help_text=_("Assigned ACI Fabric."),
    )
    allocation_mode = CSVChoiceField(
        choices=VLANAllocationModeChoices,
        required=False,
        label=_("Allocation mode"),
        help_text=_("Static or APIC-managed dynamic allocation."),
    )
    nb_vlan_group = CSVModelChoiceField(
        queryset=VLANGroup.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox VLAN group"),
        help_text=_("Backing NetBox VLAN group."),
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
        label=_("Owner"),
        help_text=_("Name of the object's owner."),
    )

    class Meta:
        model = ACIVLANPool
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "allocation_mode",
            "nb_vlan_group",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACIVLANPoolRangeEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI VLAN Pool Range model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={"aci_vlan_pools": "$aci_vlan_pool"},
        required=False,
        label=_("ACI Fabric"),
    )
    aci_vlan_pool = DynamicModelChoiceField(
        queryset=ACIVLANPool.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        label=_("ACI VLAN Pool"),
    )
    allocation_mode = ChoiceField(
        choices=VLANPoolRangeAllocationModeChoices,
        label=_("Allocation mode"),
        help_text=_(
            "Overrides the pool allocation mode for this block. 'inherit' uses "
            "the pool setting."
        ),
    )
    role = ChoiceField(
        choices=VLANPoolRangeRoleChoices,
        label=_("Role"),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "aci_fabric",
            "aci_vlan_pool",
            "tags",
            name=_("ACI VLAN Pool"),
        ),
        FieldSet(
            InlineFields(
                "vlan_id_from",
                "vlan_id_to",
                label=_("VLAN IDs"),
                help_text=_(
                    "First and last VLAN ID of the range, from {min} to {max}."
                ).format(min=VLAN_VID_MIN, max=VLAN_VID_MAX),
            ),
            "allocation_mode",
            "role",
            name=_("Encapsulation Block"),
        ),
    )

    class Meta:
        model = ACIVLANPoolRange
        fields: tuple = (
            "aci_vlan_pool",
            "vlan_id_from",
            "vlan_id_to",
            "allocation_mode",
            "role",
            "comments",
            "tags",
        )


class ACIVLANPoolRangeBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI VLAN Pool Range model."""

    aci_vlan_pool = DynamicModelChoiceField(
        queryset=ACIVLANPool.objects.all(),
        required=False,
        label=_("ACI VLAN Pool"),
    )
    allocation_mode = ChoiceField(
        choices=add_blank_choice(VLANPoolRangeAllocationModeChoices),
        required=False,
        label=_("Allocation mode"),
    )
    role = ChoiceField(
        choices=add_blank_choice(VLANPoolRangeRoleChoices),
        required=False,
        label=_("Role"),
    )
    comments = CommentField()

    model = ACIVLANPoolRange
    fieldsets: tuple = (
        FieldSet(
            "aci_vlan_pool",
            "allocation_mode",
            "role",
            name=_("ACI VLAN Pool Range"),
        ),
    )
    nullable_fields: tuple = ("comments",)


class ACIVLANPoolRangeFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI VLAN Pool Range model."""

    model = ACIVLANPoolRange
    fieldsets: tuple = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "aci_fabric_id",
            "aci_vlan_pool_id",
            "vlan_id_from",
            "vlan_id_to",
            "allocation_mode",
            "role",
            name=_("Attributes"),
        ),
    )

    aci_fabric_id = DynamicModelMultipleChoiceField(
        queryset=ACIFabric.objects.all(),
        required=False,
        label=_("ACI Fabric"),
    )
    aci_vlan_pool_id = DynamicModelMultipleChoiceField(
        queryset=ACIVLANPool.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric_id"},
        required=False,
        label=_("ACI VLAN Pool"),
    )
    vlan_id_from = forms.IntegerField(
        required=False,
        label=_("VLAN ID (from)"),
    )
    vlan_id_to = forms.IntegerField(
        required=False,
        label=_("VLAN ID (to)"),
    )
    allocation_mode = MultipleChoiceField(
        choices=add_blank_choice(VLANPoolRangeAllocationModeChoices),
        required=False,
        label=_("Allocation mode"),
    )
    role = MultipleChoiceField(
        choices=add_blank_choice(VLANPoolRangeRoleChoices),
        required=False,
        label=_("Role"),
    )
    tag = TagFilterField(model)


class ACIVLANPoolRangeImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI VLAN Pool Range model."""

    aci_vlan_pool = CSVModelChoiceField(
        queryset=ACIVLANPool.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI VLAN Pool"),
        help_text=_("Assigned ACI VLAN Pool."),
    )
    allocation_mode = CSVChoiceField(
        choices=VLANPoolRangeAllocationModeChoices,
        required=False,
        label=_("Allocation mode"),
        help_text=_("Block allocation mode. Inherit uses the pool setting."),
    )
    role = CSVChoiceField(
        choices=VLANPoolRangeRoleChoices,
        required=False,
        label=_("Role"),
    )

    class Meta:
        model = ACIVLANPoolRange
        fields: tuple = (
            "aci_vlan_pool",
            "vlan_id_from",
            "vlan_id_to",
            "allocation_mode",
            "role",
            "comments",
            "tags",
        )
