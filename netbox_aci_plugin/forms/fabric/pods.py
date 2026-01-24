# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.forms.mixins import ScopedBulkEditForm, ScopedForm, ScopedImportForm
from dcim.models import Location, Region, Site, SiteGroup
from django import forms
from django.utils.translation import gettext_lazy as _
from ipam.models import Prefix
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
    ACI_NAME_MAX_LEN,
    POD_ID_MAX,
    POD_ID_MIN,
)
from ...models.fabric.fabrics import ACIFabric
from ...models.fabric.pods import ACIPod

#
# Pod forms
#


class ACIPodEditForm(ScopedForm, NetBoxModelForm):
    """NetBox edit form for ACI Pod model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        label=_("ACI Fabric"),
    )
    tep_pool = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label=_("TEP Pool"),
        help_text=_(
            "The internal TEP pool used to assign Tunnel Endpoint (TEP) "
            "addresses to leaf and spine nodes within the pod."
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
            "name_alias",
            "aci_fabric",
            "description",
            "tags",
            name=_("ACI Pod"),
        ),
        FieldSet(
            "pod_id",
            "tep_pool",
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
        model = ACIPod
        fields: tuple = (
            "name",
            "name_alias",
            "aci_fabric",
            "description",
            "nb_tenant",
            "pod_id",
            "tep_pool",
            "scope_type",
            "owner",
            "comments",
            "tags",
        )


class ACIPodBulkEditForm(ScopedBulkEditForm, NetBoxModelBulkEditForm):
    """NetBox bulk edit form for ACI Pod model."""

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
    pod_id = forms.IntegerField(
        required=False,
        label=_("Pod ID"),
        min_value=POD_ID_MIN,
        max_value=POD_ID_MAX,
    )
    tep_pool = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label=_("TEP pool"),
        help_text=_(
            "The internal TEP pool used to assign Tunnel Endpoint (TEP) "
            "addresses to leaf and spine nodes within the pod."
        ),
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

    model = ACIPod
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_fabric",
            "description",
            "tags",
            name=_("ACI Pod"),
        ),
        FieldSet(
            "pod_id",
            "tep_pool",
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
        "name_alias",
        "description",
        "tep_pool",
        "scope",
        "nb_tenant",
        "comments",
    )


class ACIPodFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Pod model."""

    model = ACIPod
    fieldsets: tuple = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "name_alias",
            "aci_fabric_id",
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "pod_id",
            "tep_pool_id",
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
    pod_id = forms.IntegerField(
        required=False,
        label=_("Pod ID"),
        min_value=POD_ID_MIN,
        max_value=POD_ID_MAX,
    )
    tep_pool_id = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label=_("TEP pool"),
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


class ACIPodImportForm(ScopedImportForm, NetBoxModelImportForm):
    """NetBox import form for ACIPod."""

    aci_fabric = CSVModelChoiceField(
        queryset=ACIFabric.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Fabric"),
        help_text=_("Parent ACI Fabric of ACI Pod"),
    )
    tep_pool = CSVModelChoiceField(
        queryset=Prefix.objects.all(),
        to_field_name="prefix",
        required=False,
        label=_("TEP pool"),
        help_text=_(
            "The internal TEP pool used to assign Tunnel Endpoint (TEP) "
            "addresses to leaf and spine nodes within the pod."
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
        model = ACIPod
        fields = (
            "name",
            "name_alias",
            "aci_fabric",
            "description",
            "pod_id",
            "tep_pool",
            "scope_type",
            "scope_id",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )
