# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from dcim.models import Device
from ipam.models import IPAddress
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from tenancy.models import Tenant, TenantGroup
from users.models import Owner, OwnerGroup
from utilities.forms import GenericObjectFormMixin, add_blank_choice
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
from utilities.forms.rendering import FieldSet
from virtualization.models import VirtualMachine

from ...choices import NodeRoleChoices, NodeTypeChoices
from ...constants import (
    ACI_DESC_MAX_LEN,
    ACI_NAME_MAX_LEN,
    NODE_ID_MAX,
    NODE_ID_MIN,
    NODE_OBJECT_TYPES,
)
from ...models.fabric.fabrics import ACIFabric
from ...models.fabric.nodes import ACINode
from ...models.fabric.pods import ACIPod

#
# Node forms
#


class ACINodeEditForm(GenericObjectFormMixin, NetBoxModelForm):
    """NetBox edit form for ACI Node model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={"aci_pods": "$aci_pod"},
        required=False,
        label=_("ACI Fabric"),
    )
    aci_pod = DynamicModelChoiceField(
        queryset=ACIPod.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        label=_("ACI Pod"),
    )
    node_object = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(NODE_OBJECT_TYPES),
        selector=True,
        hx_target_id="node_object",
        label=_("Node Object"),
    )
    role = ChoiceField(
        choices=NodeRoleChoices,
        label=_("Role"),
        help_text=_(
            "The functional role of the node within the ACI fabric topology "
            "(e.g., Spine, Leaf, or APIC)."
        ),
    )
    node_type = ChoiceField(
        choices=NodeTypeChoices,
        label=_("Type"),
        help_text=_(
            "The specific deployment type of the node, such as a virtual leaf, "
            "a remote leaf over WAN, or a Tier-2 leaf."
        ),
    )
    tep_ip_address = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        selector=True,
        required=False,
        label=_("TEP IP Address"),
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
            "aci_pod",
            "description",
            "tags",
            name=_("ACI Node"),
        ),
        FieldSet(
            "node_object",
            name=_("Node"),
            html_id="node_object",
        ),
        FieldSet(
            "node_id",
            "role",
            "node_type",
            "tep_ip_address",
            name=_("Infrastructure"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACINode
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_pod",
            "node_id",
            "role",
            "node_type",
            "tep_ip_address",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACINodeBulkEditForm(GenericObjectFormMixin, NetBoxModelBulkEditForm):
    """NetBox bulk edit form for ACI Node model."""

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
    aci_pod = DynamicModelChoiceField(
        queryset=ACIPod.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        required=False,
        label=_("ACI Pod"),
    )
    node_id = forms.IntegerField(
        required=False,
        label=_("Node ID"),
        min_value=NODE_ID_MIN,
        max_value=NODE_ID_MAX,
    )
    node_object = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(NODE_OBJECT_TYPES),
        selector=True,
        required=False,
        hx_method="post",
        label=_("Node Object"),
    )
    role = ChoiceField(
        choices=add_blank_choice(NodeRoleChoices),
        required=False,
        label=_("Role"),
    )
    node_type = ChoiceField(
        choices=add_blank_choice(NodeTypeChoices),
        required=False,
        label=_("Type"),
    )
    tep_ip_address = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label=_("TEP IP Address"),
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

    model = ACINode
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_fabric",
            "aci_pod",
            "description",
            name=_("ACI Node"),
        ),
        FieldSet(
            "node_object",
            name=_("Node"),
        ),
        FieldSet(
            "node_id",
            "role",
            "node_type",
            "tep_ip_address",
            name=_("Infrastructure"),
        ),
        FieldSet(
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )
    nullable_fields = (
        "name_alias",
        "description",
        "tep_ip_address",
        "nb_tenant",
        "comments",
    )


class ACINodeFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Node model."""

    model = ACINode
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
            "aci_pod_id",
            name=_("Attributes"),
        ),
        FieldSet(
            "device_id",
            "virtual_machine_id",
            name=_("Node"),
        ),
        FieldSet(
            "node_id",
            "role",
            "node_type",
            "tep_ip_address_id",
            name=_("Infrastructure"),
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
    aci_pod_id = DynamicModelMultipleChoiceField(
        queryset=ACIPod.objects.all(),
        required=False,
        label=_("ACI Pod"),
    )
    node_id = forms.IntegerField(
        required=False,
        label=_("Node ID"),
        min_value=NODE_ID_MIN,
        max_value=NODE_ID_MAX,
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_("Device"),
    )
    virtual_machine_id = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label=_("Virtual Machine"),
    )
    role = MultipleChoiceField(
        choices=add_blank_choice(NodeRoleChoices),
        required=False,
        label=_("Role"),
    )
    node_type = MultipleChoiceField(
        choices=add_blank_choice(NodeTypeChoices),
        required=False,
        label=_("Type"),
    )
    tep_ip_address_id = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label=_("TEP IP Address"),
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


class ACINodeImportForm(NetBoxModelImportForm):
    """NetBox import form for ACINode."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
        help_text=_("Parent ACI Fabric of ACI Pod"),
    )
    aci_pod = CSVModelChoiceField(
        queryset=ACIPod.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Pod"),
        help_text=_("Parent ACI Pod of ACI Node"),
    )
    node_object_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(NODE_OBJECT_TYPES),
        label=_("Node Object Type (app & model)"),
    )
    node_object_id = forms.IntegerField(
        label=_("Node Object ID"),
    )
    role = CSVChoiceField(
        choices=NodeRoleChoices,
        label=_("Role"),
        help_text=_(
            "The functional role of the node within the ACI fabric topology "
            "(e.g., Spine, Leaf, or APIC)."
        ),
    )
    node_type = CSVChoiceField(
        choices=NodeTypeChoices,
        label=_("Type"),
        help_text=_(
            "The specific deployment type of the node, such as a virtual leaf, "
            "a remote leaf over WAN, or a Tier-2 leaf."
        ),
    )
    tep_ip_address = CSVModelChoiceField(
        queryset=IPAddress.objects.all(),
        to_field_name="address",
        required=False,
        label=_("TEP IP Address"),
        help_text=_("Assigned TEP IP Address"),
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
        model = ACINode
        fields: tuple = (
            "name",
            "name_alias",
            "aci_fabric",
            "aci_pod",
            "description",
            "node_id",
            "node_object_type",
            "node_object_id",
            "role",
            "node_type",
            "tep_ip_address",
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

        if data.get("aci_fabric") and data.get("aci_pod"):
            # Limit ACIPod queryset by parent ACIFabric
            self.fields["aci_pod"].queryset = ACIPod.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
