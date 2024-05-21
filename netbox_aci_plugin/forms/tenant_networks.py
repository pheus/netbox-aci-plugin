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
    BDMultiDestinationFloodingChoices,
    BDUnknownMulticastChoices,
    BDUnknownUnicastChoices,
    VRFPCEnforcementDirectionChoices,
    VRFPCEnforcementPreferenceChoices,
)
from ..models.tenant_networks import ACIVRF, ACIBridgeDomain
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
            "Multicast routing enabled for the VRF. Default is disabled."
        ),
        required=False,
    )
    pim_ipv6_enabled = forms.BooleanField(
        label=_("PIM (multicast) IPv6 enabled"),
        help_text=_(
            "Multicast routing enabled for the VRF. Default is disabled."
        ),
        required=False,
    )
    preferred_group_enabled = forms.BooleanField(
        label=_("Preferred group enabled"),
        help_text=_(
            "Whether preferred group feature is enabled for the VRF. "
            "Default is disabled."
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
            "nb_tenant_group_id",
            "nb_tenant_id",
            name="NetBox Tenancy",
        ),
        FieldSet(
            "nb_vrf_id",
            name=_("NetBox Networking"),
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


class ACIBridgeDomainForm(NetBoxModelForm):
    """NetBox form for ACI Bridge Domain model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        required=False,
        label=_("ACI Tenant"),
        # query_params={"nb_tenant_id": "$nb_tenant"},
        initial_params={"aci_vrfs": "$aci_vrf"},
    )
    aci_vrf = DynamicModelChoiceField(
        queryset=ACIVRF.objects.all(),
        label=_("ACI VRF"),
        query_params={"aci_tenant_id": "$aci_tenant"},
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
    advertise_host_routes_enabled = forms.BooleanField(
        label=_("Advertise host routes enabled"),
        help_text=_(
            "Advertise associated endpoints as host routes (/32 prefixes) "
            "out of the L3Outs. Default is disabled."
        ),
        required=False,
    )
    arp_flooding_enabled = forms.BooleanField(
        label=_("ARP flooding enabled"),
        help_text=_(
            "Allow Address Resolution Protocol (ARP) to flood in this Bridge "
            "Domain. Default is disabled."
        ),
        required=False,
    )
    clear_remote_mac_enabled = forms.BooleanField(
        label=_("Clear remote MAC entries enabled"),
        help_text=_(
            "Enables deletion of MAC EP on remote leaves, when EP gets "
            "deleted from local leaf. Default is disabled."
        ),
        required=False,
    )
    ep_move_detection_enabled = forms.BooleanField(
        label=_("EP move detection enabled"),
        help_text=_(
            "Enables Gratuitous ARP (GARP) to detect endpoint move. "
            "Default is disabled."
        ),
        required=False,
    )
    ip_data_plane_learning_enabled = forms.BooleanField(
        label=_("IP data plane learning enabled"),
        help_text=_(
            "Whether IP data plane learning is enabled for Bridge Domain. "
            "Default is enabled."
        ),
        required=False,
    )
    limit_ip_learn_to_subnet = forms.BooleanField(
        label=_("Limit IP learning to subnet"),
        help_text=_(
            "IP learning is limited to the Bridge Domain's subnets. "
            "Default is enabled."
        ),
        required=False,
    )
    multi_destination_flooding = forms.ChoiceField(
        choices=BDMultiDestinationFloodingChoices,
        label=_("Multi destination flooding"),
        help_text=_(
            "Forwarding methof for L2 multicast, broadcast, and link layer "
            "traffic. Default is 'bd-flood'."
        ),
        required=False,
    )
    pim_ipv4_enabled = forms.BooleanField(
        label=_("PIM (multicast) IPv4 enabled"),
        help_text=_(
            "Multicast routing enabled for the Bridge Domain. "
            "Default is disabled."
        ),
        required=False,
    )
    pim_ipv6_enabled = forms.BooleanField(
        label=_("PIM (multicast) IPv6 enabled"),
        help_text=_(
            "Multicast routing enabled for the Bridge Domain. "
            "Default is disabled."
        ),
        required=False,
    )
    unicast_routing_enabled = forms.BooleanField(
        label=_("Unicast routing enabled"),
        help_text=_(
            "Whether IP forwarding is enabled for this Bridge Domain. "
            "Default is enabled."
        ),
        required=False,
    )
    unknown_ipv4_multicast = forms.ChoiceField(
        choices=BDUnknownMulticastChoices,
        label=_("Unknown IPv4 multicast"),
        help_text=_(
            "Defines the IPv4 unknown multicast forwarding method. "
            "Default is 'flood'."
        ),
        required=False,
    )
    unknown_ipv6_multicast = forms.ChoiceField(
        choices=BDUnknownMulticastChoices,
        label=_("Unknown IPv6 multicast"),
        help_text=_(
            "Defines the IPv6 unknown multicast forwarding method. "
            "Default is 'flood'."
        ),
        required=False,
    )
    unknown_unicast = forms.ChoiceField(
        choices=BDUnknownUnicastChoices,
        label=_("Unknown unicast"),
        help_text=_(
            "Defines the layer 2 unknown unicast forwarding method. "
            "Default is 'proxy'."
        ),
        required=False,
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "alias",
            "aci_tenant",
            "aci_vrf",
            "description",
            "tags",
            name=_("ACI Bridge Domain"),
        ),
        FieldSet(
            "unicast_routing_enabled",
            "advertise_host_routes_enabled",
            "ep_move_detection_enabled",
            "mac_address",
            "virtual_mac_address",
            name=_("Routing Settings"),
        ),
        FieldSet(
            "arp_flooding_enabled",
            "unknown_unicast",
            "unknown_ipv4_multicast",
            "unknown_ipv6_multicast",
            "multi_destination_flooding",
            name=_("Forwarding Method Settings"),
        ),
        FieldSet(
            "ip_data_plane_learning_enabled",
            "limit_ip_learn_enabled",
            "clear_remote_mac_enabled",
            name=_("Endpoint Learning Settings"),
        ),
        FieldSet(
            "pim_ipv4_enabled",
            "pim_ipv6_enabled",
            "igmp_interface_policy_name",
            "igmp_snooping_policy_name",
            "pim_ipv4_source_filter",
            "pim_ipv4_destination_filter",
            name=_("Multicast Settings"),
        ),
        FieldSet(
            "dhcp_labels",
            name=_("Additional Settings"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIBridgeDomain
        fields: tuple = (
            "name",
            "alias",
            "description",
            "aci_vrf",
            "advertise_host_routes_enabled",
            "arp_flooding_enabled",
            "clear_remote_mac_enabled",
            "dhcp_labels",
            "ep_move_detection_enabled",
            "igmp_interface_policy_name",
            "igmp_snooping_policy_name",
            "ip_data_plane_learning_enabled",
            "limit_ip_learn_enabled",
            "mac_address",
            "multi_destination_flooding",
            "pim_ipv4_enabled",
            "pim_ipv4_destination_filter",
            "pim_ipv4_source_filter",
            "pim_ipv6_enabled",
            "unicast_routing_enabled",
            "unknown_ipv4_multicast",
            "unknown_ipv6_multicast",
            "unknown_unicast",
            "virtual_mac_address",
            "comments",
            "tags",
        )
