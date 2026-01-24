# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.models import MACAddress
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
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
    add_blank_choice,
    get_field_value,
)
from utilities.forms.fields import (
    CommentField,
    ContentTypeChoiceField,
    CSVChoiceField,
    CSVContentTypeField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import HTMXSelect
from utilities.templatetags.builtins.filters import bettertitle

from ...choices import QualityOfServiceClassChoices
from ...constants import (
    ACI_DESC_MAX_LEN,
    ACI_NAME_MAX_LEN,
    USEG_NETWORK_ATTRIBUTES_MODELS,
)
from ...models.fabric.fabrics import ACIFabric
from ...models.tenant.app_profiles import ACIAppProfile
from ...models.tenant.bridge_domains import ACIBridgeDomain
from ...models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
    ACIUSegNetworkAttribute,
)
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF

#
# Endpoint Group forms
#


class ACIEndpointGroupEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Endpoint Group model."""

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
        initial_params={"aci_bridge_domains": "$aci_bridge_domain"},
        required=False,
        label=_("ACI VRF"),
    )
    aci_bridge_domain = DynamicModelChoiceField(
        queryset=ACIBridgeDomain.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "present_in_aci_tenant_or_common_id": "$aci_tenant",
            "aci_vrf_id": "$aci_vrf",
        },
        label=_("ACI Bridge Domain"),
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
        help_text=_("Whether proxy ARP is enabled for the EPG. Default is disabled."),
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
            "description",
            "aci_app_profile",
            "aci_bridge_domain",
            "admin_shutdown",
            "custom_qos_policy_name",
            "flood_in_encap_enabled",
            "intra_epg_isolation_enabled",
            "qos_class",
            "preferred_group_member_enabled",
            "proxy_arp_enabled",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACIEndpointGroupBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Endpoint Group model."""

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
    aci_bridge_domain = DynamicModelChoiceField(
        queryset=ACIBridgeDomain.objects.all(),
        required=False,
        label=_("ACI Bridge Domain"),
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
        "custom_qos_policy_name",
        "nb_tenant",
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
            "aci_fabric_id",
            "aci_tenant_id",
            "aci_app_profile_id",
            "aci_vrf_id",
            "aci_bridge_domain_id",
            "description",
            "admin_shutdown",
            name=_("Attributes"),
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
    aci_bridge_domain_id = DynamicModelMultipleChoiceField(
        queryset=ACIBridgeDomain.objects.all(),
        query_params={"aci_vrf_id": "$aci_vrf_id"},
        required=False,
        label=_("ACI Bridge Domain"),
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


class ACIEndpointGroupImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Endpoint Group model."""

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
    qos_class = CSVChoiceField(
        choices=QualityOfServiceClassChoices,
        required=True,
        label=_("QoS class"),
        help_text=_(
            "Assignment of the ACI Quality-of-Service level for "
            "traffic sourced in the EPG."
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
        model = ACIEndpointGroup
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_tenant",
            "aci_app_profile",
            "aci_bridge_domain",
            "is_aci_bd_in_common",
            "admin_shutdown",
            "custom_qos_policy_name",
            "flood_in_encap_enabled",
            "intra_epg_isolation_enabled",
            "qos_class",
            "preferred_group_member_enabled",
            "proxy_arp_enabled",
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

            if data.get("is_aci_bd_in_common") == "true":
                # Limit ACIBridgeDomain queryset by "common" ACITenant
                aci_bd_queryset = ACIBridgeDomain.objects.filter(
                    aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_tenant__name="common",
                )
                self.fields["aci_bridge_domain"].queryset = aci_bd_queryset
            else:
                # Limit ACIBridgeDomain queryset by parent ACITenant
                aci_bd_queryset = ACIBridgeDomain.objects.filter(
                    aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_tenant__name=data["aci_tenant"],
                )
                self.fields["aci_bridge_domain"].queryset = aci_bd_queryset


#
# uSEg Endpoint Group forms
#


class ACIUSegEndpointGroupEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI uSeg Endpoint Group model."""

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
        initial_params={"aci_bridge_domains": "$aci_bridge_domain"},
        required=False,
        label=_("ACI VRF"),
    )
    aci_bridge_domain = DynamicModelChoiceField(
        queryset=ACIBridgeDomain.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "present_in_aci_tenant_or_common_id": "$aci_tenant",
            "aci_vrf_id": "$aci_vrf",
        },
        label=_("ACI Bridge Domain"),
    )
    admin_shutdown = forms.BooleanField(
        required=False,
        label=_("Admin state shutdown"),
        help_text=_(
            "Whether the uSEg EPG is in shutdown mode removing all policy "
            "configuration from all switches. Default is disabled."
        ),
    )
    flood_in_encap_enabled = forms.BooleanField(
        required=False,
        label=_("Flood in encapsulation enabled"),
        help_text=_(
            "Limits the flooding traffic to the encapsulation of the "
            "uSeg EPG. Default is disabled."
        ),
    )
    intra_epg_isolation_enabled = forms.BooleanField(
        required=False,
        label=_("Intra-EPG isolation enabled"),
        help_text=_(
            "Prevents communication between endpoints in an uSeg EPG when "
            "enabled. Default is disabled."
        ),
    )
    qos_class = forms.ChoiceField(
        choices=QualityOfServiceClassChoices,
        required=False,
        label=_("QoS class"),
        help_text=_(
            "Assignment of the ACI Quality-of-Service level for "
            "traffic sourced in the uSeg EPG. Default is 'unspecified'."
        ),
    )
    preferred_group_member_enabled = forms.BooleanField(
        required=False,
        label=_("Preferred group member enabled"),
        help_text=_(
            "Whether this uSeg EPG is a member of the preferred group and "
            "allows communication without contracts. Default is disabled."
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
            "aci_tenant",
            "aci_app_profile",
            "aci_vrf",
            "aci_bridge_domain",
            "description",
            "tags",
            "admin_shutdown",
            name=_("ACI uSeg Endpoint Group"),
        ),
        FieldSet(
            "preferred_group_member_enabled",
            "intra_epg_isolation_enabled",
            name=_("Policy Enforcement Settings"),
        ),
        FieldSet(
            "flood_in_encap_enabled",
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
        model = ACIUSegEndpointGroup
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_app_profile",
            "aci_bridge_domain",
            "admin_shutdown",
            "custom_qos_policy_name",
            "flood_in_encap_enabled",
            "intra_epg_isolation_enabled",
            "qos_class",
            "preferred_group_member_enabled",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACIUSegEndpointGroupBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI uSeg Endpoint Group model."""

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
    aci_bridge_domain = DynamicModelChoiceField(
        queryset=ACIBridgeDomain.objects.all(),
        required=False,
        label=_("ACI Bridge Domain"),
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

    model = ACIUSegEndpointGroup
    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_app_profile",
            "aci_bridge_domain",
            "description",
            "tags",
            "admin_shutdown",
            name=_("ACI uSeg Endpoint Group"),
        ),
        FieldSet(
            "preferred_group_member_enabled",
            "intra_epg_isolation_enabled",
            name=_("Policy Enforcement Settings"),
        ),
        FieldSet(
            "flood_in_encap_enabled",
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
        "custom_qos_policy_name",
        "nb_tenant",
        "comments",
    )


class ACIUSegEndpointGroupFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI uSeg Endpoint Group model."""

    model = ACIUSegEndpointGroup
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
            "aci_tenant_id",
            "aci_app_profile_id",
            "aci_vrf_id",
            "aci_bridge_domain_id",
            "description",
            "admin_shutdown",
            name=_("Attributes"),
        ),
        FieldSet(
            "preferred_group_member_enabled",
            "intra_epg_isolation_enabled",
            name=_("Policy Enforcement Settings"),
        ),
        FieldSet(
            "flood_in_encap_enabled",
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
    aci_bridge_domain_id = DynamicModelMultipleChoiceField(
        queryset=ACIBridgeDomain.objects.all(),
        query_params={"aci_vrf_id": "$aci_vrf_id"},
        required=False,
        label=_("ACI Bridge Domain"),
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


class ACIUSegEndpointGroupImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI uSeg Endpoint Group model."""

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
    qos_class = CSVChoiceField(
        choices=QualityOfServiceClassChoices,
        required=True,
        label=_("QoS class"),
        help_text=_(
            "Assignment of the ACI Quality-of-Service level for "
            "traffic sourced in the uSeg EPG."
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
        model = ACIUSegEndpointGroup
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_tenant",
            "aci_app_profile",
            "aci_bridge_domain",
            "is_aci_bd_in_common",
            "admin_shutdown",
            "custom_qos_policy_name",
            "flood_in_encap_enabled",
            "intra_epg_isolation_enabled",
            "qos_class",
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
            aci_appprofile_queryset = ACIAppProfile.objects.filter(
                aci_tenant__aci_fabric__name=data["aci_fabric"],
                aci_tenant__name=data["aci_tenant"],
            )
            self.fields["aci_app_profile"].queryset = aci_appprofile_queryset

            if data.get("is_aci_bd_in_common") == "true":
                # Limit ACIBridgeDomain queryset by "common" ACITenant
                aci_bd_queryset = ACIBridgeDomain.objects.filter(
                    aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_tenant__name="common",
                )
                self.fields["aci_bridge_domain"].queryset = aci_bd_queryset
            else:
                # Limit ACIBridgeDomain queryset by parent ACITenant
                aci_bd_queryset = ACIBridgeDomain.objects.filter(
                    aci_tenant__aci_fabric__name=data["aci_fabric"],
                    aci_tenant__name=data["aci_tenant"],
                )
                self.fields["aci_bridge_domain"].queryset = aci_bd_queryset


#
# uSEg Network Attribute forms
#


class ACIUSegNetworkAttributeEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI uSeg Network Attribute model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={
            "aci_tenants__aci_app_profiles__aci_useg_endpoint_groups": "$aci_useg_endpoint_group"
        },
        required=False,
        label=_("ACI Fabric"),
    )
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        initial_params={
            "aci_app_profiles__aci_useg_endpoint_groups": "$aci_useg_endpoint_group"
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
        initial_params={"aci_useg_endpoint_groups": "$aci_useg_endpoint_group"},
        required=False,
        label=_("ACI Application Profile"),
    )
    aci_useg_endpoint_group = DynamicModelChoiceField(
        queryset=ACIUSegEndpointGroup.objects.all(),
        query_params={
            "aci_fabric_id": "$aci_fabric",
            "aci_tenant_id": "$aci_tenant",
            "aci_app_profile_id": "$aci_app_profile",
        },
        label=_("ACI uSeg Endpoint Group"),
    )
    attr_object_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(USEG_NETWORK_ATTRIBUTES_MODELS),
        required=False,
        widget=HTMXSelect(),
        label=_("Attribute Object Type"),
    )
    attr_object = DynamicModelChoiceField(
        queryset=IPAddress.objects.none(),  # Initial queryset
        selector=True,
        required=False,
        label=_("Attribute Object"),
        disabled=True,
    )
    use_epg_subnet = forms.BooleanField(
        required=False,
        label=_("Use EPG subnet"),
        help_text=_(
            "Whether the EPG subnet is applied as uSeg attribute. Default is disabled."
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
            "aci_tenant",
            "aci_app_profile",
            "aci_useg_endpoint_group",
            "description",
            "tags",
            name=_("ACI uSeg Network Attribute"),
        ),
        FieldSet(
            "use_epg_subnet",
            name=_("EPG Subnet Settings"),
        ),
        FieldSet(
            "attr_object_type",
            "attr_object",
            name=_("Attribute Assignment"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIUSegNetworkAttribute
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_useg_endpoint_group",
            "attr_object_type",
            "use_epg_subnet",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the ACI uSeg Network Attribute form."""
        # Initialize fields with initial values
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()

        if instance is not None and instance.attr_object:
            # Initialize Attribute object field
            initial["attr_object"] = instance.attr_object

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

        if attr_object_type_id := get_field_value(self, "attr_object_type"):
            try:
                # Retrieve the ContentType model class based on the Attribute
                # object type
                attr_object_type = ContentType.objects.get(pk=attr_object_type_id)
                attr_model = attr_object_type.model_class()

                # Configure the queryset and label for the attr_object field
                self.fields["attr_object"].queryset = attr_model.objects.all()
                self.fields["attr_object"].widget.attrs["selector"] = (
                    attr_model._meta.label_lower
                )
                self.fields["attr_object"].disabled = False
                self.fields["attr_object"].label = _(
                    bettertitle(attr_model._meta.verbose_name)
                )
            except ObjectDoesNotExist:
                pass

            # Clears the attr_object field if the selected type changes
            if (
                self.instance
                and self.instance.pk
                and attr_object_type_id != self.instance.attr_object_type_id
            ):
                self.initial["attr_object"] = None

    def clean(self):
        """Validate form fields for the ACI uSeg Network Attribute form."""
        super().clean()

        # Ensure the selected Attribute object gets assigned
        self.instance.attr_object = self.cleaned_data.get("attr_object")


class ACIUSegNetworkAttributeBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI uSeg Network Attribute model."""

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
    aci_useg_endpoint_group = DynamicModelChoiceField(
        queryset=ACIUSegEndpointGroup.objects.all(),
        query_params={"aci_app_profile_id": "$aci_app_profile"},
        required=False,
        label=_("ACI uSeg Endpoint Group"),
    )
    attr_object_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(USEG_NETWORK_ATTRIBUTES_MODELS),
        required=False,
        widget=HTMXSelect(method="post", attrs={"hx-select": "#form_fields"}),
        label=_("Attribute Object Type"),
    )
    attr_object = DynamicModelChoiceField(
        queryset=IPAddress.objects.none(),  # Initial queryset
        query_params={"aci_tenant_id": "$aci_tenant"},
        selector=True,
        required=False,
        label=_("Attribute Object"),
        disabled=True,
    )
    use_epg_subnet = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Use EPG subnet"),
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

    model = ACIUSegNetworkAttribute
    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_useg_endpoint_group",
            "description",
            "tags",
            name=_("ACI uSeg Network Attribute"),
        ),
        FieldSet(
            "use_epg_subnet",
            name=_("EPG Subnet Settings"),
        ),
        FieldSet(
            "attr_object_type",
            "attr_object",
            name=_("Attribute Assignment"),
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

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the ACI uSeg Network Attribute bulk edit form."""
        super().__init__(*args, **kwargs)

        if attr_object_type_id := get_field_value(self, "attr_object_type"):
            try:
                # Retrieve the ContentType model class based on the Attribute
                # object type
                attr_object_type = ContentType.objects.get(pk=attr_object_type_id)
                attr_model = attr_object_type.model_class()

                # Configure the queryset and label for the attr_object field
                self.fields["attr_object"].queryset = attr_model.objects.all()
                self.fields["attr_object"].widget.attrs["selector"] = (
                    attr_model._meta.label_lower
                )
                self.fields["attr_object"].disabled = False
                self.fields["attr_object"].label = _(
                    bettertitle(attr_model._meta.verbose_name)
                )
            except ObjectDoesNotExist:
                pass


class ACIUSegNetworkAttributeFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI uSeg Network Attribute model."""

    model = ACIUSegNetworkAttribute
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
            "aci_tenant_id",
            "aci_app_profile_id",
            "aci_useg_endpoint_group_id",
            "description",
            "tags",
            name=_("ACI uSeg Network Attribute"),
        ),
        FieldSet(
            "use_epg_subnet",
            name=_("EPG Subnet Settings"),
        ),
        FieldSet(
            "ip_address_vrf_id",
            "ip_address_id",
            "mac_address_id",
            "prefix_vrf_id",
            "prefix_id",
            name=_("Attribute Assignment"),
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
    aci_useg_endpoint_group_id = DynamicModelMultipleChoiceField(
        queryset=ACIUSegEndpointGroup.objects.all(),
        query_params={"aci_app_profile_id": "$aci_app_profile_id"},
        null_option="None",
        required=False,
        label=_("ACI uSeg Endpoint Group"),
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
    mac_address_id = DynamicModelMultipleChoiceField(
        queryset=MACAddress.objects.all(),
        null_option="None",
        required=False,
        label=_("MAC Address"),
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
    use_epg_subnet = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Use EPG subnet"),
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


class ACIUSegNetworkAttributeImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI uSeg Network Attribute model."""

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
    aci_useg_endpoint_group = CSVModelChoiceField(
        queryset=ACIUSegEndpointGroup.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI uSeg Endpoint Group"),
        help_text=_("Assigned ACI uSeg Endpoint Group"),
    )
    attr_object_id = forms.IntegerField(
        required=False,
        label=_("Attribute Object ID"),
    )
    attr_object_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(USEG_NETWORK_ATTRIBUTES_MODELS),
        required=False,
        label=_("Attribute Object Type (app & model)"),
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
        model = ACIUSegNetworkAttribute
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_tenant",
            "aci_app_profile",
            "aci_useg_endpoint_group",
            "attr_object_id",
            "attr_object_type",
            "use_epg_subnet",
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
            # Limit ACIUSegEndpointGroup queryset by parent ACIAppProfile
            aci_useg_endpoint_group_queryset = ACIUSegEndpointGroup.objects.filter(
                aci_app_profile__aci_tenant__aci_fabric__name=data["aci_fabric"],
                aci_app_profile__aci_tenant__name=data["aci_tenant"],
                aci_app_profile__name=data["aci_app_profile"],
            )
            self.fields[
                "aci_useg_endpoint_group"
            ].queryset = aci_useg_endpoint_group_queryset
