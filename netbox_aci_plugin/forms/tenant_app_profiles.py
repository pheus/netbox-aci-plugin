# SPDX-FileCopyrightText: 2024 Martin Hauser
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
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, add_blank_choice
from utilities.forms.fields import (
    CommentField,
    CSVChoiceField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from ..choices import QualityOfServiceClassChoices
from ..models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup
from ..models.tenant_networks import ACIVRF, ACIBridgeDomain
from ..models.tenants import ACITenant

#
# Application Profile forms
#


class ACIAppProfileEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Application Profile model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        label=_("ACI Tenant"),
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
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant",
            "description",
            "tags",
            name=_("Application Profile"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIAppProfile
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "nb_tenant",
            "comments",
            "tags",
        )


class ACIAppProfileBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Application Profile model."""

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
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        required=False,
        label=_("ACI Tenant"),
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox Tenant"),
    )
    comments = CommentField()

    model = ACIAppProfile
    fieldsets: tuple = (
        FieldSet(
            "name_alias",
            "aci_tenant",
            "description",
            name=_("ACI Application Profile"),
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


class ACIAppProfileFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Application Profile model."""

    model = ACIAppProfile
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
            "description",
            name="Attributes",
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
    tag = TagFilterField(ACIAppProfile)


class ACIAppProfileImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Application Profile model."""

    aci_tenant = CSVModelChoiceField(
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Tenant"),
        help_text=_("Assigned ACI Tenant"),
    )
    nb_tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox Tenant"),
        help_text=_("Assigned NetBox Tenant"),
    )

    class Meta:
        model = ACIAppProfile
        fields: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "description",
            "nb_tenant",
            "comments",
            "tags",
        )


#
# Endpoint Group forms
#


class ACIEndpointGroupEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Endpoint Group model."""

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
        initial_params={"aci_bridge_domains": "$aci_bridge_domain"},
        required=False,
        label=_("ACI VRF"),
    )
    aci_bridge_domain = DynamicModelChoiceField(
        queryset=ACIBridgeDomain.objects.all(),
        query_params={
            "present_in_aci_tenant_or_common_id": "$aci_tenant",
            "aci_vrf_id": "$aci_vrf",
        },
        label=_("ACI Bridge Domain"),
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
            "Whether the EPG is in shutdown mode removing all policy "
            "configuration from all switches. Default is disabled."
        ),
    )
    flood_in_encap_enabled = forms.BooleanField(
        required=False,
        label=_("Flood in encapsulation enabled"),
        help_text=_(
            "Limits the flooding traffic to the encapsulation of the "
            "EPG. Default is disabled."
        ),
    )
    intra_epg_isolation_enabled = forms.BooleanField(
        required=False,
        label=_("Intra-EPG isolation enabled"),
        help_text=_(
            "Prevents communication between endpoints in an EPG when "
            "enabled. Default is disabled."
        ),
    )
    qos_class = forms.ChoiceField(
        choices=QualityOfServiceClassChoices,
        required=False,
        label=_("QoS class"),
        help_text=_(
            "Assignment of the ACI Quality-of-Service level for "
            "traffic sourced in the EPG. Default is 'unspecified'."
        ),
    )
    preferred_group_member_enabled = forms.BooleanField(
        required=False,
        label=_("Preferred group member enabled"),
        help_text=_(
            "Whether this EPG is a member of the preferred group and allows "
            "communication without contracts. Default is disabled."
        ),
    )
    proxy_arp_enabled = forms.BooleanField(
        required=False,
        label=_("Proxy ARP enabled"),
        help_text=_(
            "Whether proxy ARP is enabled for the EPG. Default is disabled."
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
            "aci_bridge_domain",
            "description",
            "tags",
            "admin_shutdown",
            name=_("ACI Endpoint Group"),
        ),
        FieldSet(
            "preferred_group_member_enabled",
            "intra_epg_isolation_enabled",
            name=_("Policy Enforcement Settings"),
        ),
        FieldSet(
            "flood_in_encap_enabled",
            "proxy_arp_enabled",
            name=_("Endpoint Forwarding Settings"),
        ),
        FieldSet(
            "qos_class",
            "custom_qos_policy_name",
            name=_("Quality of Service (QoS) Settings"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIEndpointGroup
        fields: tuple = (
            "name",
            "name_alias",
            "aci_app_profile",
            "aci_bridge_domain",
            "description",
            "nb_tenant",
            "admin_shutdown",
            "custom_qos_policy_name",
            "flood_in_encap_enabled",
            "intra_epg_isolation_enabled",
            "qos_class",
            "preferred_group_member_enabled",
            "proxy_arp_enabled",
            "comments",
            "tags",
        )

    def clean(self):
        """Cleaning and validation of ACI Endpoint Group Form."""
        super().clean()

        aci_app_profile = self.cleaned_data.get("aci_app_profile")
        aci_bridge_domain = self.cleaned_data.get("aci_bridge_domain")

        # Ensure aci_app_profile and aci_bridge_domain are present before validating
        if aci_app_profile and aci_bridge_domain:
            # Check if the ACI Tenant IDs mismatch
            aci_tenant_mismatch = (
                aci_app_profile.aci_tenant.id
                != aci_bridge_domain.aci_tenant.id
            )
            # Check if the ACI Bridge Domain Tenant name is not 'common'
            not_aci_tenant_common = (
                aci_bridge_domain.aci_tenant.name != "common"
            )
            # Raise validation error if both conditions are met
            if aci_tenant_mismatch and not_aci_tenant_common:
                self.add_error(
                    "aci_bridge_domain",
                    _(
                        "A Bridge Domain can only be assigned belonging to "
                        "same ACI Tenant as the Application Profile or to the "
                        "special ACI Tenant 'common'."
                    ),
                )


class ACIEndpointGroupBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Endpoint Group model."""

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
    aci_bridge_domain = DynamicModelChoiceField(
        queryset=ACIBridgeDomain.objects.all(),
        required=False,
        label=_("ACI Bridge Domain"),
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
    flood_in_encap_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Flood in encapsulation enabled"),
    )
    intra_epg_isolation_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Intra-EPG isolation enabled"),
    )
    qos_class = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("Quality of Service (QoS) class"),
    )
    custom_qos_policy_name = forms.CharField(
        required=False,
        label=_("Custom QoS policy name"),
    )
    preferred_group_member_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Preferred group member enabled"),
    )
    proxy_arp_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Proxy ARP enabled"),
    )
    comments = CommentField()

    model = ACIEndpointGroup
    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_app_profile",
            "aci_bridge_domain",
            "description",
            "tags",
            "admin_shutdown",
            name=_("ACI Endpoint Group"),
        ),
        FieldSet(
            "preferred_group_member_enabled",
            "intra_epg_isolation_enabled",
            name=_("Policy Enforcement Settings"),
        ),
        FieldSet(
            "flood_in_encap_enabled",
            "proxy_arp_enabled",
            name=_("Endpoint Forwarding Settings"),
        ),
        FieldSet(
            "qos_class",
            "custom_qos_policy_name",
            name=_("Quality of Service (QoS) Settings"),
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
        "custom_qos_policy_name",
        "comments",
    )


class ACIEndpointGroupFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Endpoint Group model."""

    model = ACIEndpointGroup
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
            "aci_bridge_domain_id",
            "description",
            "admin_shutdown",
            name="Attributes",
        ),
        FieldSet(
            "preferred_group_member_enabled",
            "intra_epg_isolation_enabled",
            name=_("Policy Enforcement Settings"),
        ),
        FieldSet(
            "flood_in_encap_enabled",
            "proxy_arp_enabled",
            name=_("Endpoint Forwarding Settings"),
        ),
        FieldSet(
            "qos_class",
            "custom_qos_policy_name",
            name=_("Quality of Service (QoS) Settings"),
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
    aci_bridge_domain_id = DynamicModelMultipleChoiceField(
        queryset=ACIBridgeDomain.objects.all(),
        query_params={"aci_vrf_id": "$aci_vrf_id"},
        null_option="None",
        required=False,
        label=_("ACI Bridge Domain"),
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
    flood_in_encap_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Flood in encapsulation enabled"),
    )
    intra_epg_isolation_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Intra-EPG isolation enabled"),
    )
    qos_class = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceClassChoices),
        required=False,
        label=_("Quality of Service (QoS) class"),
    )
    preferred_group_member_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Preferred group member enabled"),
    )
    proxy_arp_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Proxy ARP enabled"),
    )
    tag = TagFilterField(ACIEndpointGroup)


class ACIEndpointGroupImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Endpoint Group model."""

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
    aci_bridge_domain = CSVModelChoiceField(
        queryset=ACIBridgeDomain.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Bridge Domain"),
        help_text=_("Assigned ACI Bridge Domain"),
    )
    is_aci_bd_in_common = forms.BooleanField(
        label=_("Is ACI Bridge Domain in 'common'"),
        required=False,
        help_text=_("Assigned ACI Bridge Domain is in ACI Tenant 'common'"),
    )
    nb_tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox Tenant"),
        help_text=_("Assigned NetBox Tenant"),
    )
    qos_class = CSVChoiceField(
        choices=QualityOfServiceClassChoices,
        required=True,
        label=_("QoS class"),
        help_text=_(
            "Assignment of the ACI Quality-of-Service level for "
            "traffic sourced in the EPG."
        ),
    )

    class Meta:
        model = ACIEndpointGroup
        fields: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_bridge_domain",
            "description",
            "nb_tenant",
            "is_aci_bd_in_common",
            "admin_shutdown",
            "custom_qos_policy_name",
            "flood_in_encap_enabled",
            "intra_epg_isolation_enabled",
            "qos_class",
            "preferred_group_member_enabled",
            "proxy_arp_enabled",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)

        if not data:
            return

        # Limit ACIEndpointGroup queryset by parent ACIAppProfile and ACITenant
        if data.get("aci_tenant") and data.get("aci_app_profile"):
            # Limit ACIAppProfile queryset by parent ACITenant
            aci_appprofile_queryset = ACIAppProfile.objects.filter(
                aci_tenant__name=data["aci_tenant"]
            )
            self.fields["aci_app_profile"].queryset = aci_appprofile_queryset

        # Limit ACIBridgeDomain queryset by "common" ACITenant
        if data.get("is_aci_bd_in_common") == "true":
            aci_bd_queryset = ACIBridgeDomain.objects.filter(
                aci_tenant__name="common"
            )
            self.fields["aci_bridge_domain"].queryset = aci_bd_queryset
        # Limit ACIBridgeDomain queryset by ACITenant
        elif data.get("aci_tenant") and data.get("aci_bridge_domain"):
            # Limit ACIBridgeDomain queryset by parent ACITenant
            aci_bd_queryset = ACIBridgeDomain.objects.filter(
                aci_tenant__name=data["aci_tenant"]
            )
            self.fields["aci_bridge_domain"].queryset = aci_bd_queryset
