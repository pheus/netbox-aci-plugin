# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from tenancy.models import Tenant, TenantGroup
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from ..choices import EPGQualityOfServiceClassChoices
from ..models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup
from ..models.tenant_networks import ACIVRF, ACIBridgeDomain
from ..models.tenants import ACITenant


class ACIAppProfileForm(NetBoxModelForm):
    """NetBox form for ACI Application Profile model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"nb_tenant_id": "$nb_tenant"},
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


class ACIAppProfileFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for ACI Application Profile model."""

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
        query_params={"nb_tenant_id": "$nb_tenant_id"},
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
    tag = TagFilterField(ACITenant)


class ACIEndpointGroupForm(NetBoxModelForm):
    """NetBox form for ACI Endpoint Group model."""

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
        query_params={"aci_tenant_id": "$aci_tenant"},
        initial_params={"aci_bridge_domains": "$aci_bridge_domain"},
        required=False,
        label=_("ACI VRF"),
    )
    aci_bridge_domain = DynamicModelChoiceField(
        queryset=ACIBridgeDomain.objects.all(),
        query_params={
            "aci_tenant_id": "$aci_tenant",
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
            "Wether the EPG is in shutdown mode removing all policy "
            "configuration from all switches. Default is disabled."
        ),
    )
    flood_in_encap_enabled = forms.BooleanField(
        required=False,
        label=_("Floot in encapsulation enabled"),
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
        choices=EPGQualityOfServiceClassChoices,
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
            "Whether this EPG is a member of the preferred group and allow "
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


class ACIEndpointGroupFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for ACI Endpoint Group model."""

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
        query_params={"nb_tenant_id": "$nb_tenant_id"},
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
        label=_("Admin shutdown"),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
    )
    flood_in_encap_enabled = forms.NullBooleanField(
        required=False,
        label=_("Flood in encapsulation enabled"),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
    )
    intra_epg_isolation_enabled = forms.NullBooleanField(
        required=False,
        label=_("Intra-EPG isolation enabled"),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
    )
    qos_class = forms.ChoiceField(
        choices=EPGQualityOfServiceClassChoices,
        required=False,
        label=_("Quality of Service (QoS) class"),
    )
    preferred_group_member_enabled = forms.NullBooleanField(
        required=False,
        label=_("Preferred group member enabled"),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
    )
    proxy_arp_enabled = forms.NullBooleanField(
        required=False,
        label=_("Proxy ARP enabled"),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
    )
    tag = TagFilterField(ACIEndpointGroup)
