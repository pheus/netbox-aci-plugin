# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _
from ipam.models import VRF
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from tenancy.models import Tenant, TenantGroup
from users.models import Owner, OwnerGroup
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

from ...choices import (
    VRFPCEnforcementDirectionChoices,
    VRFPCEnforcementPreferenceChoices,
)
from ...constants import ACI_DESC_MAX_LEN, ACI_NAME_MAX_LEN
from ...models.fabric.fabrics import ACIFabric
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF

#
# VRF forms
#


class ACIVRFEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI VRF model."""

    aci_fabric = DynamicModelChoiceField(
        queryset=ACIFabric.objects.all(),
        initial_params={"aci_tenants": "$aci_tenant"},
        required=False,
        label=_("ACI Fabric"),
    )
    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        query_params={"aci_fabric_id": "$aci_fabric"},
        label=_("ACI Tenant"),
    )
    nb_vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        query_params={"nb_tenant_id": "$nb_tenant"},
        required=False,
        label=_("NetBox VRF"),
    )
    bd_enforcement_enabled = forms.BooleanField(
        required=False,
        label=_("Bridge Domain enforcement enabled"),
        help_text=_(
            "Allow EP to ping only gateways within associated bridge domain. "
            "Default is disabled."
        ),
    )
    ip_data_plane_learning_enabled = forms.BooleanField(
        required=False,
        label=_("IP data plane learning enabled"),
        help_text=_(
            "Whether IP data plane learning is enabled for VRF. Default is enabled."
        ),
    )
    pc_enforcement_direction = forms.ChoiceField(
        choices=VRFPCEnforcementDirectionChoices,
        required=False,
        label=_("Enforcement direction"),
        help_text=_(
            "Controls policy enforcement direction for VRF. Default is 'ingress'."
        ),
    )
    pc_enforcement_preference = forms.ChoiceField(
        choices=VRFPCEnforcementPreferenceChoices,
        required=False,
        label=_("Enforcement preference"),
        help_text=_(
            "Controls policy enforcement preference for VRF. Default is 'enforced'."
        ),
    )
    pim_ipv4_enabled = forms.BooleanField(
        required=False,
        label=_("PIM (multicast) IPv4 enabled"),
        help_text=_("Multicast routing enabled for the VRF. Default is disabled."),
    )
    pim_ipv6_enabled = forms.BooleanField(
        required=False,
        label=_("PIM (multicast) IPv6 enabled"),
        help_text=_("Multicast routing enabled for the VRF. Default is disabled."),
    )
    preferred_group_enabled = forms.BooleanField(
        required=False,
        label=_("Preferred group enabled"),
        help_text=_(
            "Whether preferred group feature is enabled for the VRF. "
            "Default is disabled."
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
            "description",
            "tags",
            name=_("ACI VRF"),
        ),
        FieldSet(
            "pc_enforcement_direction",
            "pc_enforcement_preference",
            "bd_enforcement_enabled",
            "preferred_group_enabled",
            name=_("Policy Control Settings"),
        ),
        FieldSet(
            "ip_data_plane_learning_enabled",
            name=_("Endpoint Learning Settings"),
        ),
        FieldSet(
            "pim_ipv4_enabled",
            "pim_ipv6_enabled",
            name=_("Multicast Settings"),
        ),
        FieldSet(
            "dns_labels",
            name=_("Additional Settings"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
        FieldSet(
            "nb_vrf",
            name=_("NetBox Networking"),
        ),
    )

    class Meta:
        model = ACIVRF
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "nb_vrf",
            "bd_enforcement_enabled",
            "dns_labels",
            "ip_data_plane_learning_enabled",
            "pim_ipv4_enabled",
            "pim_ipv6_enabled",
            "pc_enforcement_direction",
            "pc_enforcement_preference",
            "preferred_group_enabled",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )


class ACIVRFBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI VRF model."""

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
    nb_vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_("NetBox VRF"),
    )
    bd_enforcement_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Enabled Bridge Domain enforcement"),
    )
    dns_labels = forms.CharField(
        required=False,
        label=_("DNS labels"),
    )
    ip_data_plane_learning_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Enabled IP data plane learning"),
    )
    pc_enforcement_direction = forms.ChoiceField(
        choices=add_blank_choice(VRFPCEnforcementDirectionChoices),
        required=False,
        label=_("Policy control enforcement direction"),
    )
    pc_enforcement_preference = forms.ChoiceField(
        choices=add_blank_choice(VRFPCEnforcementPreferenceChoices),
        required=False,
        label=_("Policy control enforcement preference"),
    )
    pim_ipv4_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Enabled PIM (multicast) IPv4"),
    )
    pim_ipv6_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Enabled PIM (multicast) IPv6"),
    )
    preferred_group_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Enabled preferred group"),
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

    model = ACIVRF
    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant",
            "description",
            "tags",
            name=_("ACI VRF"),
        ),
        FieldSet(
            "pc_enforcement_direction",
            "pc_enforcement_preference",
            "bd_enforcement_enabled",
            "preferred_group_enabled",
            name=_("Policy Control Settings"),
        ),
        FieldSet(
            "ip_data_plane_learning_enabled",
            name=_("Endpoint Learning Settings"),
        ),
        FieldSet(
            "pim_ipv4_enabled",
            "pim_ipv6_enabled",
            name=_("Multicast Settings"),
        ),
        FieldSet(
            "dns_labels",
            name=_("Additional Settings"),
        ),
        FieldSet(
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
        FieldSet(
            "nb_vrf",
            name=_("NetBox Networking"),
        ),
    )
    nullable_fields: tuple = (
        "name_alias",
        "description",
        "nb_vrf",
        "dns_labels",
        "nb_tenant",
        "comments",
    )


class ACIVRFFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI VRF model."""

    model = ACIVRF
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
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "pc_enforcement_direction",
            "pc_enforcement_preference",
            "bd_enforcement_enabled",
            "preferred_group_enabled",
            name=_("Policy Control Settings"),
        ),
        FieldSet(
            "ip_data_plane_learning_enabled",
            name=_("Endpoint Learning Settings"),
        ),
        FieldSet(
            "pim_ipv4_enabled",
            "pim_ipv6_enabled",
            name=_("Multicast Settings"),
        ),
        FieldSet(
            "dns_labels",
            name=_("Additional Settings"),
        ),
        FieldSet(
            "nb_vrf_id",
            name=_("NetBox Networking"),
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
    nb_vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        query_params={"tenant_id": "$nb_tenant_id"},
        null_option="None",
        required=False,
        label=_("NetBox VRF"),
    )
    bd_enforcement_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Enabled Bridge Domain enforcement"),
    )
    dns_labels = forms.CharField(
        required=False,
        label=_("DNS labels"),
    )
    ip_data_plane_learning_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Enabled IP data plane learning"),
    )
    pc_enforcement_direction = forms.ChoiceField(
        choices=add_blank_choice(VRFPCEnforcementDirectionChoices),
        required=False,
        label=_("Policy control enforcement direction"),
    )
    pc_enforcement_preference = forms.ChoiceField(
        choices=add_blank_choice(VRFPCEnforcementPreferenceChoices),
        required=False,
        label=_("Policy control enforcement preference"),
    )
    pim_ipv4_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Enabled PIM (multicast) IPv4"),
    )
    pim_ipv6_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Enabled PIM (multicast) IPv6"),
    )
    preferred_group_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Enabled preferred group"),
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


class ACIVRFImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI VRF model."""

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
        help_text=_("Assigned ACI Tenant"),
    )
    nb_vrf = CSVModelChoiceField(
        queryset=VRF.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox VRF"),
        help_text=_("Assigned NetBox VRF"),
    )
    pc_enforcement_direction = CSVChoiceField(
        choices=VRFPCEnforcementDirectionChoices,
        required=True,
        label=_("Policy control enforcement direction"),
        help_text=_("Controls policy enforcement direction for VRF."),
    )
    pc_enforcement_preference = CSVChoiceField(
        choices=VRFPCEnforcementPreferenceChoices,
        required=True,
        label=_("Policy control enforcement preference"),
        help_text=_("Controls policy enforcement preference for VRF."),
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
        model = ACIVRF
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_tenant",
            "nb_vrf",
            "bd_enforcement_enabled",
            "dns_labels",
            "ip_data_plane_learning_enabled",
            "pc_enforcement_direction",
            "pc_enforcement_preference",
            "pim_ipv4_enabled",
            "pim_ipv6_enabled",
            "preferred_group_enabled",
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
