# SPDX-FileCopyrightText: 2025 Martin Hauser
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
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES
from utilities.forms.fields import (
    CommentField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from ...models.tenant.app_profiles import ACIAppProfile
from ...models.tenant.endpoint_security_groups import ACIEndpointSecurityGroup
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF

#
# Endpoint Security Group forms
#


class ACIEndpointSecurityGroupEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Endpoint Security Group model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        initial_params={"aci_app_profiles": "$aci_app_profile"},
        required=False,
        label=_("ACI Tenant"),
    )
    aci_app_profile = DynamicModelChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        label=_("ACI Application Profile"),
    )
    aci_vrf = DynamicModelChoiceField(
        queryset=ACIVRF.objects.all(),
        query_params={"present_in_aci_tenant_or_common_id": "$aci_tenant"},
        label=_("ACI VRF"),
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
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
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
            "aci_app_profile",
            "aci_vrf",
            "description",
            "nb_tenant",
            "admin_shutdown",
            "intra_esg_isolation_enabled",
            "preferred_group_member_enabled",
            "comments",
            "tags",
        )

    def clean(self):
        """Cleaning and validation of ACI Endpoint Security Group Form."""
        super().clean()

        aci_app_profile = self.cleaned_data.get("aci_app_profile")
        aci_vrf = self.cleaned_data.get("aci_vrf")

        # Ensure aci_app_profile and aci_vrf are present before validating
        if aci_app_profile and aci_vrf:
            # Check if the ACI Tenant IDs mismatch
            aci_tenant_mismatch = (
                aci_app_profile.aci_tenant.id != aci_vrf.aci_tenant.id
            )
            # Check if the ACI VRF Tenant name is not 'common'
            not_aci_tenant_common = aci_vrf.aci_tenant.name != "common"
            # Raise the validation error if both conditions are met
            if aci_tenant_mismatch and not_aci_tenant_common:
                self.add_error(
                    "aci_vrf",
                    _(
                        "A VRF can only be assigned belonging to same"
                        "ACI Tenant as the Application Profile or to the "
                        "special ACI Tenant 'common'."
                    ),
                )


class ACIEndpointSecurityGroupBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Endpoint Security Group model."""

    name_alias = forms.CharField(
        max_length=64,
        required=False,
        label=_("Name Alias"),
    )
    description = forms.CharField(
        max_length=128,
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
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
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
    comments = CommentField()

    model = ACIEndpointSecurityGroup
    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_app_profile",
            "aci_vrf",
            "description",
            "tags",
            "admin_shutdown",
            name=_("ACI Endpoint Security Group"),
        ),
        FieldSet(
            "preferred_group_member_enabled",
            "intra_epg_isolation_enabled",
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
            "aci_tenant_id",
            "aci_app_profile_id",
            "aci_vrf_id",
            "description",
            "admin_shutdown",
            name="Attributes",
        ),
        FieldSet(
            "preferred_group_member_enabled",
            "intra_esg_isolation_enabled",
            name=_("Policy Enforcement Settings"),
        ),
        FieldSet(
            "nb_tenant_group_id",
            "nb_tenant_id",
            name="NetBox Tenancy",
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
    aci_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        null_option="None",
        required=False,
        label=_("ACI Tenant"),
    )
    aci_app_profile_id = DynamicModelMultipleChoiceField(
        queryset=ACIAppProfile.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant_id"},
        null_option="None",
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_vrf_id = DynamicModelMultipleChoiceField(
        queryset=ACIVRF.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant_id"},
        null_option="None",
        required=False,
        label=_("ACI VRF"),
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
    tag = TagFilterField(ACIEndpointSecurityGroup)


class ACIEndpointSecurityGroupImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Endpoint Security Group model."""

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

    class Meta:
        model = ACIEndpointSecurityGroup
        fields: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_vrf",
            "description",
            "nb_tenant",
            "is_aci_vrf_in_common",
            "admin_shutdown",
            "intra_esg_isolation_enabled",
            "preferred_group_member_enabled",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)

        if not data:
            return

        # Limit ACIEndpointSecurityGroup queryset by parent ACIAppProfile and ACITenant
        if data.get("aci_tenant") and data.get("aci_app_profile"):
            # Limit ACIAppProfile queryset by parent ACITenant
            aci_appprofile_queryset = ACIAppProfile.objects.filter(
                aci_tenant__name=data["aci_tenant"]
            )
            self.fields["aci_app_profile"].queryset = aci_appprofile_queryset

        # Limit ACIVRF queryset by "common" ACITenant
        if data.get("is_aci_vrf_in_common") == "true":
            aci_vrf_queryset = ACIVRF.objects.filter(aci_tenant__name="common")
            self.fields["aci_vrf"].queryset = aci_vrf_queryset
        # Limit ACIVRF queryset by ACITenant
        elif data.get("aci_tenant") and data.get("aci_vrf"):
            # Limit ACIVRF queryset by parent ACITenant
            aci_vrf_queryset = ACIVRF.objects.filter(
                aci_tenant__name=data["aci_tenant"]
            )
            self.fields["aci_vrf"].queryset = aci_vrf_queryset
