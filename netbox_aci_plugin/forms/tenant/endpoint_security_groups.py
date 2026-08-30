# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from ipam.models import VRF, IPAddress, Prefix
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
)
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

from ...constants import (
    ACI_DESC_MAX_LEN,
    ACI_NAME_MAX_LEN,
    ESG_ENDPOINT_GROUP_SELECTORS_MODELS,
    ESG_ENDPOINT_SELECTORS_MODELS,
)
from ...models.fabric.fabrics import ACIFabric
from ...models.tenant.app_profiles import ACIAppProfile
from ...models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
)
from ...models.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroup,
    ACIEsgEndpointGroupSelector,
    ACIEsgEndpointSelector,
)
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF

#
# Endpoint Security Group forms
#


class ACIEndpointSecurityGroupEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Endpoint Security Group model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={"aci_tenants__aci_app_profiles": "$aci_app_profile"},
        required=False,
        label=_("ACI Fabric"),
    )
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        initial_params={"aci_app_profiles": "$aci_app_profile"},
        required=False,
        label=_("ACI Tenant"),
    )
    aci_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "aci_tenant_id": "$aci_tenant",
        },
        label=_("ACI Application Profile"),
    )
    aci_vrf = DynamicModelChoiceField(
        queryset=ACIVRF.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "present_in_aci_tenant_or_common_id": "$aci_tenant",
        },
        label=_("ACI VRF"),
    )
    admin_shutdown = forms.BooleanField(
        required=False,
        label=_("Admin state shutdown"),
        help_text=_(
            "Whether the ESG is in shutdown mode removing all policy "
            "configuration from all switches. Default is disabled."
        ),
    )
    intra_esg_isolation_enabled = forms.BooleanField(
        required=False,
        label=_("Intra-ESG isolation enabled"),
        help_text=_(
            "Prevents communication between endpoints in an ESG when "
            "enabled. Default is disabled."
        ),
    )
    preferred_group_member_enabled = forms.BooleanField(
        required=False,
        label=_("Preferred Group member enabled"),
        help_text=_(
            "Whether this ESG is a member of the preferred group and allows "
            "communication without contracts. Default is disabled."
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
            "aci_app_profile",
            "aci_vrf",
            "description",
            "tags",
            "admin_shutdown",
            name=_("ACI Endpoint Security Group"),
        ),
        FieldSet(
            "preferred_group_member_enabled",
            "intra_esg_isolation_enabled",
            name=_("Policy Enforcement Settings"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIEndpointSecurityGroup
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_app_profile",
            "aci_vrf",
            "admin_shutdown",
            "intra_esg_isolation_enabled",
            "preferred_group_member_enabled",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACIEndpointSecurityGroupBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Endpoint Security Group model."""

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
    aci_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_vrf = DynamicModelChoiceField(
        queryset=ACIVRF.objects.all(),
        required=False,
        label=_("ACI VRF"),
    )
    admin_shutdown = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Admin shutdown"),
    )
    intra_esg_isolation_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Intra-ESG isolation enabled"),
    )
    preferred_group_member_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Preferred group member enabled"),
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

    model = ACIEndpointSecurityGroup
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_app_profile",
            "aci_vrf",
            "description",
            "admin_shutdown",
            name=_("ACI Endpoint Security Group"),
        ),
        FieldSet(
            "preferred_group_member_enabled",
            "intra_esg_isolation_enabled",
            name=_("Policy Enforcement Settings"),
        ),
        FieldSet(
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )
    nullable_fields: tuple = (
        "name_alias",
        "description",
        "nb_tenant",
        "comments",
    )


class ACIEndpointSecurityGroupFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Endpoint Security Group model."""

    model = ACIEndpointSecurityGroup
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
            "aci_app_profile_id",
            "aci_vrf_id",
            "admin_shutdown",
            name=_("Attributes"),
        ),
        FieldSet(
            "preferred_group_member_enabled",
            "intra_esg_isolation_enabled",
            name=_("Policy Enforcement Settings"),
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
    aci_app_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant_id"},
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_vrf_id = DynamicModelMultipleChoiceField(
        queryset=ACIVRF.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant_id"},
        required=False,
        label=_("ACI VRF"),
    )
    admin_shutdown = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Admin shutdown"),
    )
    intra_esg_isolation_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Intra-ESG isolation enabled"),
    )
    preferred_group_member_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Preferred group member enabled"),
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


class ACIEndpointSecurityGroupImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Endpoint Security Group model."""

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
        help_text=_("Parent ACI Tenant of ACI Application Profile"),
    )
    aci_app_profile = CSVModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Application Profile"),
        help_text=_("Assigned ACI Application Profile"),
    )
    aci_vrf = CSVModelChoiceField(
        queryset=ACIVRF.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI VRF"),
        help_text=_("Assigned ACI VRF"),
    )
    is_aci_vrf_in_common = forms.BooleanField(
        label=_("Is ACI VRF in 'common'"),
        required=False,
        help_text=_("Assigned ACI VRF is in ACI Tenant 'common'"),
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
        model = ACIEndpointSecurityGroup
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_tenant",
            "aci_app_profile",
            "aci_vrf",
            "is_aci_vrf_in_common",
            "admin_shutdown",
            "intra_esg_isolation_enabled",
            "preferred_group_member_enabled",
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
            # Limit ACIAppProfile queryset by parent ACITenant
            self.fields["aci_app_profile"].queryset = ACIAppProfile.objects.filter(
                aci_tenant__aci_fabric__name=data["aci_fabric"],
                aci_tenant__name=data["aci_tenant"],
            )

            if data.get("is_aci_vrf_in_common") == "true":
                # Limit ACIVRF queryset by "common" ACITenant
                aci_vrf_queryset = ACIVRF.objects.filter(
                    aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_tenant__name="common",
                )
                self.fields["aci_vrf"].queryset = aci_vrf_queryset
            else:
                # Limit ACIVRF queryset by parent ACITenant
                aci_vrf_queryset = ACIVRF.objects.filter(
                    aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_tenant__name=data["aci_tenant"],
                )
                self.fields["aci_vrf"].queryset = aci_vrf_queryset


#
# ESG Endpoint Group (EPG) Selector forms
#


class ACIEsgEndpointGroupSelectorEditForm(GenericObjectFormMixin, NetBoxModelForm):
    """NetBox edit form for the ACI ESG Endpoint Group (EPG) Selector model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={
            "aci_tenants__aci_app_profiles__aci_endpoint_security_groups": (
                "$aci_endpoint_security_group"
            )
        },
        required=False,
        label=_("ACI Fabric"),
    )
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        initial_params={
            "aci_app_profiles__aci_endpoint_security_groups": (
                "$aci_endpoint_security_group"
            )
        },
        required=False,
        label=_("ACI Tenant"),
    )
    aci_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "aci_tenant_id": "$aci_tenant",
        },
        initial_params={"aci_endpoint_security_groups": "$aci_endpoint_security_group"},
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_endpoint_security_group = DynamicModelChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "aci_tenant_id": "$aci_tenant",
            "aci_app_profile_id": "$aci_app_profile",
        },
        label=_("ACI Endpoint Security Group"),
    )
    aci_epg_object_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "aci_tenant_id": "$aci_tenant",
        },
        required=False,
        label=_("ACI Application Profile of Endpoint Group"),
    )
    aci_epg_object = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(
            ESG_ENDPOINT_GROUP_SELECTORS_MODELS
        ),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "aci_tenant_id": "$aci_tenant",
            "aci_app_profile_id": "$aci_epg_object_app_profile",
            "shares_aci_vrf_with_aci_esg_id": "$aci_endpoint_security_group",
        },
        selector=True,
        hx_target_id="aci_epg_object",
        label=_("ACI EPG Object"),
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
            "aci_app_profile",
            "aci_endpoint_security_group",
            "description",
            "tags",
            name=_("ACI ESG Endpoint Group (EPG) Selector"),
        ),
        FieldSet(
            "aci_epg_object_app_profile",
            "aci_epg_object",
            name=_("Endpoint Group Assignment"),
            html_id="aci_epg_object",
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIEsgEndpointGroupSelector
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_endpoint_security_group",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACIEsgEndpointGroupSelectorBulkEditForm(
    GenericObjectFormMixin, NetBoxModelBulkEditForm
):
    """NetBox bulk edit form for the ACI ESG EPG Selector model."""

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
    aci_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_endpoint_security_group = DynamicModelChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        query_params={
            "aci_tenant_id": "$aci_tenant",
            "aci_app_profile_id": "$aci_app_profile",
        },
        required=False,
        label=_("ACI Endpoint Security Group"),
    )
    aci_epg_object_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        required=False,
        label=_("ACI Application Profile of Endpoint Group"),
    )
    aci_epg_object = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(
            ESG_ENDPOINT_GROUP_SELECTORS_MODELS
        ),
        query_params={
            "aci_tenant_id": "$aci_tenant",
            "aci_app_profile_id": "$aci_epg_object_app_profile",
        },
        selector=True,
        required=False,
        hx_method="post",
        label=_("ACI EPG Object"),
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

    model = ACIEsgEndpointGroupSelector
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_endpoint_security_group",
            "description",
            name=_("ACI ESG Endpoint Group (EPG) Selector"),
        ),
        FieldSet(
            "aci_epg_object_app_profile",
            "aci_epg_object",
            name=_("Endpoint Group Assignment"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )
    nullable_fields: tuple = (
        "name_alias",
        "description",
        "nb_tenant",
        "comments",
    )


class ACIEsgEndpointGroupSelectorFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI ESG Endpoint Group Selector model."""

    model = ACIEsgEndpointGroupSelector
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
            "aci_app_profile_id",
            "aci_endpoint_security_group_id",
            name=_("Attributes"),
        ),
        FieldSet(
            "aci_endpoint_group_app_profile_id",
            "aci_endpoint_group_id",
            name=_("Endpoint Group Assignment"),
        ),
        FieldSet(
            "aci_useg_endpoint_group_app_profile_id",
            "aci_useg_endpoint_group_id",
            name=_("uSeg Endpoint Group Assignment"),
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
    aci_app_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant_id"},
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_endpoint_security_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        query_params={"aci_app_profile_id": "$aci_app_profile_id"},
        required=False,
        label=_("ACI Endpoint Security Group"),
    )
    aci_endpoint_group_app_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACIAppProfile.objects.all(),
        required=False,
        label=_("ACI Application Profile of Endpoint Group"),
    )
    aci_endpoint_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIEndpointGroup.objects.all(),
        required=False,
        label=_("ACI Endpoint Group"),
    )
    aci_useg_endpoint_group_app_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACIAppProfile.objects.all(),
        required=False,
        label=_("ACI Application Profile of uSeg Endpoint Group"),
    )
    aci_useg_endpoint_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIUSegEndpointGroup.objects.all(),
        required=False,
        label=_("ACI uSeg Endpoint Group"),
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


class ACIEsgEndpointGroupSelectorImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI ESG EPG Selector model."""

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
        help_text=_("Parent ACI Tenant of ACI Application Profile"),
    )
    aci_app_profile = CSVModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Application Profile"),
        help_text=_("Parent ACI Application Profile of ACI Endpoint Security Group"),
    )
    aci_endpoint_security_group = CSVModelChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Endpoint Security Group"),
        help_text=_("Assigned ACI Endpoint Security Group"),
    )
    aci_epg_object_id = forms.IntegerField(
        required=True,
        label=_("ACI Endpoint Group Object ID"),
    )
    aci_epg_object_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(ESG_ENDPOINT_GROUP_SELECTORS_MODELS),
        required=True,
        label=_("ACI Endpoint Group Object Type (app & model)"),
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
        model = ACIEsgEndpointGroupSelector
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_tenant",
            "aci_app_profile",
            "aci_endpoint_security_group",
            "aci_epg_object_id",
            "aci_epg_object_type",
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

        if (
            data.get("aci_fabric")
            and data.get("aci_tenant")
            and data.get("aci_app_profile")
        ):
            # Limit ACITenant queryset by parent ACIFabric
            self.fields["aci_tenant"].queryset = ACITenant.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
            # Limit ACIAppProfile queryset by parent ACITenant
            self.fields["aci_app_profile"].queryset = ACIAppProfile.objects.filter(
                aci_tenant__aci_fabric__name=data["aci_fabric"],
                aci_tenant__name=data["aci_tenant"],
            )
            # Limit ACIEndpointSecurityGroup queryset by parent ACIAppProfile
            aci_endpoint_security_group_queryset = (
                ACIEndpointSecurityGroup.objects.filter(
                    aci_app_profile__aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_app_profile__aci_tenant__name=data["aci_tenant"],
                    aci_app_profile__name=data["aci_app_profile"],
                )
            )
            self.fields[
                "aci_endpoint_security_group"
            ].queryset = aci_endpoint_security_group_queryset


#
# ESG Endpoint Selector forms
#


class ACIEsgEndpointSelectorEditForm(GenericObjectFormMixin, NetBoxModelForm):
    """NetBox edit form for the ACI ESG Endpoint Selector model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={
            "aci_tenants__aci_app_profiles__aci_endpoint_security_groups": (
                "$aci_endpoint_security_group"
            )
        },
        required=False,
        label=_("ACI Fabric"),
    )
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        initial_params={
            "aci_app_profiles__aci_endpoint_security_groups": (
                "$aci_endpoint_security_group"
            )
        },
        required=False,
        label=_("ACI Tenant"),
    )
    aci_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "aci_tenant_id": "$aci_tenant",
        },
        initial_params={"aci_endpoint_security_groups": "$aci_endpoint_security_group"},
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_endpoint_security_group = DynamicModelChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "aci_tenant_id": "$aci_tenant",
            "aci_app_profile_id": "$aci_app_profile",
        },
        label=_("ACI Endpoint Security Group"),
    )
    ep_object = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(ESG_ENDPOINT_SELECTORS_MODELS),
        selector=True,
        hx_target_id="ep_object",
        label=_("Endpoint Object"),
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
            "aci_app_profile",
            "aci_endpoint_security_group",
            "description",
            "tags",
            name=_("ACI ESG Endpoint Selector"),
        ),
        FieldSet(
            "ep_object",
            name=_("Endpoint Assignment"),
            html_id="ep_object",
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIEsgEndpointSelector
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_endpoint_security_group",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACIEsgEndpointSelectorBulkEditForm(
    GenericObjectFormMixin, NetBoxModelBulkEditForm
):
    """NetBox bulk edit form for the ACI ESG Endpoint Selector model."""

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
    aci_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_endpoint_security_group = DynamicModelChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        query_params={"aci_app_profile_id": "$aci_app_profile"},
        required=False,
        label=_("ACI Endpoint Security Group"),
    )
    ep_object = GenericObjectChoiceField(
        content_type_queryset=ContentType.objects.filter(ESG_ENDPOINT_SELECTORS_MODELS),
        selector=True,
        required=False,
        hx_method="post",
        label=_("Endpoint Object"),
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

    model = ACIEsgEndpointSelector
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_endpoint_security_group",
            "description",
            name=_("ACI ESG Endpoint Selector"),
        ),
        FieldSet(
            "ep_object",
            name=_("Endpoint Assignment"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )
    nullable_fields: tuple = (
        "name_alias",
        "description",
        "nb_tenant",
        "comments",
    )


class ACIEsgEndpointSelectorFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI ESG Endpoint Selector model."""

    model = ACIEsgEndpointSelector
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
            "aci_app_profile_id",
            "aci_endpoint_security_group_id",
            name=_("Attributes"),
        ),
        FieldSet(
            "ip_address_vrf_id",
            "ip_address_id",
            "prefix_vrf_id",
            "prefix_id",
            name=_("Endpoint Assignment"),
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
    aci_app_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACIAppProfile.objects.all(),
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_endpoint_security_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        required=False,
        label=_("ACI Endpoint Security Group"),
    )
    ip_address_vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        null_option="None",
        required=False,
        label=_("VRF of IP Address"),
    )
    ip_address_id = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        query_params={"vrf_id": "$ip_address_vrf_id"},
        null_option="None",
        required=False,
        label=_("IP Address"),
    )
    prefix_vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        null_option="None",
        required=False,
        label=_("VRF of Prefix"),
    )
    prefix_id = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        query_params={"vrf_id": "$prefix_vrf_id"},
        null_option="None",
        required=False,
        label=_("Prefix"),
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


class ACIEsgEndpointSelectorImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI ESG Endpoint Selector model."""

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
        help_text=_("Parent ACI Tenant of ACI Application Profile"),
    )
    aci_app_profile = CSVModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Application Profile"),
        help_text=_("Assigned ACI Application Profile"),
    )
    aci_endpoint_security_group = CSVModelChoiceField(
        queryset=ACIEndpointSecurityGroup.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Endpoint Security Group"),
        help_text=_("Assigned ACI Endpoint Security Group"),
    )
    ep_object_id = forms.IntegerField(
        required=True,
        label=_("Endpoint Object ID"),
    )
    ep_object_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(ESG_ENDPOINT_SELECTORS_MODELS),
        required=True,
        label=_("Endpoint Object Type (app & model)"),
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
        model = ACIEsgEndpointSelector
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_tenant",
            "aci_app_profile",
            "aci_endpoint_security_group",
            "ep_object_id",
            "ep_object_type",
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

        if (
            data.get("aci_fabric")
            and data.get("aci_tenant")
            and data.get("aci_app_profile")
        ):
            # Limit ACITenant queryset by parent ACIFabric
            self.fields["aci_tenant"].queryset = ACITenant.objects.filter(
                aci_fabric__name=data["aci_fabric"]
            )
            # Limit ACIAppProfile queryset by parent ACITenant
            self.fields["aci_app_profile"].queryset = ACIAppProfile.objects.filter(
                aci_tenant__aci_fabric__name=data["aci_fabric"],
                aci_tenant__name=data["aci_tenant"],
            )
            # Limit ACIEndpointSecurityGroup queryset by parent ACIAppProfile
            aci_endpoint_security_group_queryset = (
                ACIEndpointSecurityGroup.objects.filter(
                    aci_app_profile__aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_app_profile__aci_tenant__name=data["aci_tenant"],
                    aci_app_profile__name=data["aci_app_profile"],
                )
            )
            self.fields[
                "aci_endpoint_security_group"
            ].queryset = aci_endpoint_security_group_queryset
