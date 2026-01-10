# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.forms.mixins import ScopedBulkEditForm, ScopedForm, ScopedImportForm
from dcim.models import Location, Region, Site, SiteGroup
from django import forms
from django.utils.translation import gettext_lazy as _
from ipam.models import VLAN, Prefix, VLANGroup
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
from utilities.forms.rendering import FieldSet

from ...constants import (
    ACI_DESC_MAX_LEN,
    FABRIC_ID_MAX,
    FABRIC_ID_MIN,
    VLAN_VID_MAX,
    VLAN_VID_MIN,
)
from ...models.fabric.fabrics import ACIFabric

#
# Fabric forms
#


class ACIFabricEditForm(ScopedForm, NetBoxModelForm):
    """NetBox edit form for ACI Fabric model."""

    infra_vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        initial_params={"vlans": "$infra_vlan"},
        required=False,
        label=_("Infrastructure VLAN group"),
    )
    infra_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        query_params={"group_id": "$infra_vlan_group"},
        required=False,
        label=_("Infrastructure VLAN"),
        help_text=_("Optional: reference a NetBox VLAN that documents the same ID."),
    )
    gipo_pool = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label=_("GIPo pool"),
        help_text=_("Fabric-wide multicast pool (GIPo), e.g. 225.0.0.0/15"),
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
        label=_("Owner group"),
        queryset=OwnerGroup.objects.all(),
        required=False,
        null_option="None",
        initial_params={"members": "$owner"},
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
            "description",
            "tags",
            name=_("ACI Fabric"),
        ),
        FieldSet(
            "fabric_id",
            "infra_vlan_vid",
            "infra_vlan_group",
            "infra_vlan",
            "gipo_pool",
            name=_("Infrastructure"),
        ),
        FieldSet(
            "scope_type",
            "scope",
            name=_("Scope"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIFabric
        fields: tuple = (
            "name",
            "description",
            "fabric_id",
            "infra_vlan_vid",
            "infra_vlan",
            "gipo_pool",
            "scope_type",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACIFabricBulkEditForm(ScopedBulkEditForm, NetBoxModelBulkEditForm):
    """NetBox bulk edit form for ACI Fabric model."""

    description = forms.CharField(
        max_length=ACI_DESC_MAX_LEN,
        required=False,
        label=_("Description"),
    )
    fabric_id = forms.IntegerField(
        required=False,
        label=_("Fabric ID"),
        min_value=FABRIC_ID_MIN,
        max_value=FABRIC_ID_MAX,
    )
    infra_vlan_vid = forms.IntegerField(
        required=False,
        label=_("Infrastructure VLAN ID"),
        min_value=VLAN_VID_MIN,
        max_value=VLAN_VID_MAX,
    )
    infra_vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        initial_params={"vlans": "$infra_vlan"},
        required=False,
        label=_("Infrastructure VLAN group"),
    )
    infra_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        query_params={"group_id": "$infra_vlan_group"},
        required=False,
        label=_("Infrastructure VLAN"),
        help_text=_("Optional: reference a NetBox VLAN that documents the same ID."),
    )
    gipo_pool = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label=_("GIPo pool"),
        help_text=_("Fabric-wide multicast pool (GIPo), e.g. 225.0.0.0/15"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        query_params={"group_id": "$owner_group"},
        label=_("Owner"),
    )
    comments = CommentField()

    model = ACIFabric
    fieldsets: tuple = (
        FieldSet(
            "description",
            "tags",
            name=_("ACI Fabric"),
        ),
        FieldSet(
            "fabric_id",
            "infra_vlan_vid",
            "infra_vlan_group",
            "infra_vlan",
            "gipo_pool",
            name=_("Infrastructure"),
        ),
        FieldSet(
            "scope_type",
            "scope",
            name=_("Scope"),
        ),
        FieldSet(
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )
    nullable_fields = (
        "description",
        "infra_vlan",
        "gipo_pool",
        "scope",
        "nb_tenant",
        "comments",
    )


class ACIFabricFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Fabric model."""

    model = ACIFabric
    fieldsets: tuple = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "fabric_id",
            "infra_vlan_vid",
            "infra_vlan_id",
            "gipo_pool_id",
            name=_("Infrastructure"),
        ),
        FieldSet(
            "region_id",
            "site_group_id",
            "site_id",
            "location_id",
            name=_("Scope"),
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
    description = forms.CharField(
        required=False,
    )
    fabric_id = forms.IntegerField(
        required=False,
        label=_("Fabric ID"),
        min_value=FABRIC_ID_MIN,
        max_value=FABRIC_ID_MAX,
    )
    infra_vlan_vid = forms.IntegerField(
        required=False,
        label=_("Infrastructure VLAN VID"),
        min_value=VLAN_VID_MIN,
        max_value=VLAN_VID_MAX,
    )
    infra_vlan_id = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label=_("Infrastructure VLAN"),
    )
    gipo_pool_id = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label=_("GIPo pool"),
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_("Region"),
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_("Site group"),
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_("Site"),
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label=_("Location"),
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
        required=False,
        null_option="None",
        label=_("Owner Group"),
    )
    owner_id = DynamicModelMultipleChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        null_option="None",
        query_params={"group_id": "$owner_group_id"},
        label=_("Owner"),
    )
    tag = TagFilterField(model)


class ACIFabricImportForm(ScopedImportForm, NetBoxModelImportForm):
    """NetBox import form for ACIFabric."""

    infra_vlan = CSVModelChoiceField(
        queryset=VLAN.objects.all(),
        to_field_name="vid",
        required=False,
        label=_("Infrastructure VLAN"),
        help_text=_("Assigned NetBox VLAN"),
    )
    gipo_pool = CSVModelChoiceField(
        queryset=Prefix.objects.all(),
        to_field_name="prefix",
        required=False,
        label=_("GIPo pool"),
        help_text=_("Assigned NetBox Prefix"),
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
        model = ACIFabric
        fields = (
            "name",
            "description",
            "fabric_id",
            "infra_vlan_vid",
            "infra_vlan",
            "gipo_pool",
            "scope_type",
            "scope_id",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )
