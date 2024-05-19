# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _
from ipam.models import VRF
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from tenancy.models import Tenant, TenantGroup
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from ..choices import (
    VRFPCEnforcementDirectionChoices,
    VRFPCEnforcementPreferenceChoices,
)
from ..models.tenant_networks import ACIVRF
from ..models.tenants import ACITenant


class ACIVRFForm(NetBoxModelForm):
    """NetBox form for ACI VRF model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        label=_("ACI Tenant"),
        query_params={"nb_tenant_id": "$nb_tenant"},
    )
    nb_tenant_group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_("NetBox tenant group"),
        initial_params={"tenants": "$nb_tenant"},
    )
    nb_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("NetBox tenant"),
        query_params={"group_id": "$nb_tenant_group"},
    )
    nb_vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_("NetBox VRF"),
        query_params={"nb_tenant_id": "$nb_tenant"},
    )
    bd_enforcement_enabled = forms.BooleanField(
        label=_("Bridge Domain enforcement enabled"),
        required=False,
        help_text=_(
            "Allow EP to ping only gateways within associated bridge domain. "
            "Default is disabled."
        ),
    )
    ip_data_plane_learning_enabled = forms.BooleanField(
        label=_("IP data plane learning enabled"),
        help_text=_(
            "Whether IP data plane learning is enabled for VRF. "
            "Default is enabled."
        ),
        required=False,
    )
    pc_enforcement_direction = forms.ChoiceField(
        choices=VRFPCEnforcementDirectionChoices,
        label=_("Enforcement direction"),
        help_text=_(
            "Controls policy enforcement direction for VRF. "
            "Default is 'ingress'."
        ),
        required=False,
    )
    pc_enforcement_preference = forms.ChoiceField(
        choices=VRFPCEnforcementPreferenceChoices,
        label=_("Enforcement preference"),
        help_text=_(
            "Controls policy enforcement preference for VRF. "
            "Default is 'enforced'."
        ),
        required=False,
    )
    pim_ipv4_enabled = forms.BooleanField(
        label=_("PIM (multicast) IPv4 enabled"),
        help_text=_(
            "Multicast routing enabled for the VRF. Default is false."
        ),
        required=False,
    )
    pim_ipv6_enabled = forms.BooleanField(
        label=_("PIM (multicast) IPv6 enabled"),
        help_text=_(
            "Multicast routing enabled for the VRF. Default is false."
        ),
        required=False,
    )
    preferred_group_enabled = forms.BooleanField(
        label=_("Preferred group enabled"),
        help_text=_(
            "Whether preferred group feature is enabled for the VRF. "
            "Default is false."
        ),
        required=False,
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "alias",
            "aci_tenant",
            "description",
            "tags",
            name=_("ACI VRF"),
        ),
        FieldSet(
            "dns_labels",
            "pc_enforcement_direction",
            "pc_enforcement_preference",
            "bd_enforcement_enabled",
            "ip_data_plane_learning_enabled",
            "pim_ipv4_enabled",
            "pim_ipv6_enabled",
            "preferred_group_enabled",
            name=_("ACI VRF Settings"),
        ),
        FieldSet(
            "nb_vrf",
            name=_("NetBox Networking"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIVRF
        fields: tuple = (
            "name",
            "alias",
            "description",
            "aci_tenant",
            "nb_tenant",
            "nb_vrf",
            "bd_enforcement_enabled",
            "dns_labels",
            "ip_data_plane_learning_enabled",
            "pim_ipv4_enabled",
            "pim_ipv6_enabled",
            "pc_enforcement_direction",
            "pc_enforcement_preference",
            "preferred_group_enabled",
            "comments",
            "tags",
        )


class ACIVRFFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for ACI VRF model."""

    model = ACIVRF
    fieldsets: tuple = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "alias",
            "aci_tenant_id",
            "description",
            name="Attributes",
        ),
        FieldSet(
            "dns_labels",
            "pc_enforcement_direction",
            "pc_enforcement_preference",
            "bd_enforcement_enabled",
            "ip_data_plane_learning_enabled",
            "pim_ipv4_enabled",
            "pim_ipv6_enabled",
            "preferred_group_enabled",
            name=_("ACI VRF Settings"),
        ),
        FieldSet(
            "nb_vrf_id",
            name=_("NetBox Networking"),
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
    alias = forms.CharField(
        required=False,
    )
    description = forms.CharField(
        required=False,
    )
    aci_tenant_id = DynamicModelMultipleChoiceField(
        queryset=ACITenant.objects.all(),
        required=False,
        null_option="None",
        query_params={"tenant_id": "$nb_tenant_id"},
        label=_("ACI Tenant"),
    )
    nb_tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        null_option="None",
        label=_("NetBox tenant group"),
    )
    nb_tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        null_option="None",
        query_params={"group_id": "$nb_tenant_group_id"},
        label=_("NetBox tenant"),
    )
    nb_vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        null_option="None",
        query_params={"tenant_id": "$nb_tenant_id"},
        label=_("NetBox VRF"),
    )
    bd_enforcement_enabled = forms.BooleanField(
        label=_("Enabled Bridge Domain enforcement"),
        required=False,
    )
    dns_labels = forms.CharField(
        label=_("DNS labels"),
        required=False,
    )
    ip_data_plane_learning_enabled = forms.BooleanField(
        label=_("Enabled IP data plane learning"),
        required=False,
    )
    pc_enforcement_direction = forms.ChoiceField(
        choices=VRFPCEnforcementDirectionChoices,
        label=_("Policy control enforcement direction"),
        required=False,
    )
    pc_enforcement_preference = forms.ChoiceField(
        choices=VRFPCEnforcementPreferenceChoices,
        label=_("Policy control enforcement preference"),
        required=False,
    )
    pim_ipv4_enabled = forms.BooleanField(
        label=_("Enabled PIM (multicast) IPv4"),
        required=False,
    )
    pim_ipv6_enabled = forms.BooleanField(
        label=_("Enabled PIM (multicast) IPv6"),
        required=False,
    )
    preferred_group_enabled = forms.BooleanField(
        label=_("Enabled preferred group"),
        required=False,
    )
    tag = TagFilterField(ACITenant)
