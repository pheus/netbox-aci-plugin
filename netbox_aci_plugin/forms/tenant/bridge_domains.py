# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _
from ipam.models import VRF, IPAddress
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

from ...choices import (
    BDMultiDestinationFloodingChoices,
    BDUnknownMulticastChoices,
    BDUnknownUnicastChoices,
)
from ...models.tenant.bridge_domains import (
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF

#
# Bridge Domain forms
#


class ACIBridgeDomainEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Bridge Domain model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        label=_("ACI Tenant"),
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
    advertise_host_routes_enabled = forms.BooleanField(
        required=False,
        label=_("Advertise host routes enabled"),
        help_text=_(
            "Advertise associated endpoints as host routes (/32 prefixes) "
            "out of the L3Outs. Default is disabled."
        ),
    )
    arp_flooding_enabled = forms.BooleanField(
        required=False,
        label=_("ARP flooding enabled"),
        help_text=_(
            "Allow Address Resolution Protocol (ARP) to flood in this Bridge "
            "Domain. Default is disabled."
        ),
    )
    clear_remote_mac_enabled = forms.BooleanField(
        required=False,
        label=_("Clear remote MAC entries enabled"),
        help_text=_(
            "Enables deletion of MAC EP on remote leaves, when EP gets "
            "deleted from local leaf. Default is disabled."
        ),
    )
    ep_move_detection_enabled = forms.BooleanField(
        required=False,
        label=_("EP move detection enabled"),
        help_text=_(
            "Enables Gratuitous ARP (GARP) to detect endpoint move. "
            "Default is disabled."
        ),
    )
    ip_data_plane_learning_enabled = forms.BooleanField(
        required=False,
        label=_("IP data plane learning enabled"),
        help_text=_(
            "Whether IP data plane learning is enabled for Bridge Domain. "
            "Default is enabled."
        ),
    )
    limit_ip_learn_to_subnet = forms.BooleanField(
        required=False,
        label=_("Limit IP learning to subnet"),
        help_text=_(
            "IP learning is limited to the Bridge Domain's subnets. Default is enabled."
        ),
    )
    multi_destination_flooding = forms.ChoiceField(
        choices=BDMultiDestinationFloodingChoices,
        required=False,
        label=_("Multi destination flooding"),
        help_text=_(
            "Forwarding method for L2 multicast, broadcast, and link layer "
            "traffic. Default is 'bd-flood'."
        ),
    )
    pim_ipv4_enabled = forms.BooleanField(
        label=_("PIM (multicast) IPv4 enabled"),
        required=False,
        help_text=_(
            "Multicast routing enabled for the Bridge Domain. Default is disabled."
        ),
    )
    pim_ipv6_enabled = forms.BooleanField(
        label=_("PIM (multicast) IPv6 enabled"),
        required=False,
        help_text=_(
            "Multicast routing enabled for the Bridge Domain. Default is disabled."
        ),
    )
    unicast_routing_enabled = forms.BooleanField(
        label=_("Unicast routing enabled"),
        required=False,
        help_text=_(
            "Whether IP forwarding is enabled for this Bridge Domain. "
            "Default is enabled."
        ),
    )
    unknown_ipv4_multicast = forms.ChoiceField(
        choices=BDUnknownMulticastChoices,
        required=False,
        label=_("Unknown IPv4 multicast"),
        help_text=_(
            "Defines the IPv4 unknown multicast forwarding method. Default is 'flood'."
        ),
    )
    unknown_ipv6_multicast = forms.ChoiceField(
        choices=BDUnknownMulticastChoices,
        required=False,
        label=_("Unknown IPv6 multicast"),
        help_text=_(
            "Defines the IPv6 unknown multicast forwarding method. Default is 'flood'."
        ),
    )
    unknown_unicast = forms.ChoiceField(
        choices=BDUnknownUnicastChoices,
        required=False,
        label=_("Unknown unicast"),
        help_text=_(
            "Defines the layer 2 unknown unicast forwarding method. Default is 'proxy'."
        ),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
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
            "name_alias",
            "description",
            "aci_tenant",
            "aci_vrf",
            "nb_tenant",
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

    def clean(self) -> None:
        """Clean and validate the ACI Bridge Domain form."""
        super().clean()

        aci_tenant = self.cleaned_data.get("aci_tenant")
        aci_vrf = self.cleaned_data.get("aci_vrf")

        # Ensure aci_tenant and aci_vrf are present before validating
        if aci_tenant and aci_vrf:
            # Check if the ACI Tenant IDs mismatch
            aci_tenant_mismatch = aci_tenant.id != aci_vrf.aci_tenant.id
            # Check if the ACI VRF Tenant name is not 'common'
            not_aci_tenant_common = aci_vrf.aci_tenant.name != "common"

            # Raise validation error if both conditions are met
            if aci_tenant_mismatch and not_aci_tenant_common:
                self.add_error(
                    "aci_vrf",
                    _(
                        "A VRF can only be assigned belonging to the same ACI "
                        "Tenant as the Bridge Domain or to the special ACI "
                        "Tenant 'common'."
                    ),
                )


class ACIBridgeDomainBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Bridge Domain model."""

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
    advertise_host_routes_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Advertise host routes enabled"),
    )
    arp_flooding_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("ARP flooding enabled"),
    )
    clear_remote_mac_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Clear remote MAC entries enabled"),
    )
    dhcp_labels = forms.CharField(
        required=False,
        label=_("DHCP labels"),
    )
    ep_move_detection_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("EP move detection enabled"),
    )
    igmp_interface_policy_name = forms.CharField(
        required=False,
        label=_("IGMP interface policy name"),
    )
    igmp_snooping_policy_name = forms.CharField(
        required=False,
        label=_("IGMP snooping policy name"),
    )
    ip_data_plane_learning_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("IP data plane learning enabled"),
    )
    limit_ip_learn_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Limit IP learning to subnet enabled"),
    )
    mac_address = forms.CharField(
        required=False,
        label=_("MAC address"),
    )
    multi_destination_flooding = forms.ChoiceField(
        choices=add_blank_choice(BDMultiDestinationFloodingChoices),
        required=False,
        label=_("Multi destination flooding"),
    )
    pim_ipv4_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("PIM (multicast) IPv4 enabled"),
    )
    pim_ipv4_destination_filter = forms.CharField(
        required=False,
        label=_("PIM destination filter"),
    )
    pim_ipv4_source_filter = forms.CharField(
        required=False,
        label=_("PIM source filter"),
    )
    pim_ipv6_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("PIM (multicast) IPv6 enabled"),
    )
    unicast_routing_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Unicast routing enabled"),
    )
    unknown_ipv4_multicast = forms.ChoiceField(
        choices=add_blank_choice(BDUnknownMulticastChoices),
        required=False,
        label=_("Unknown IPv4 multicast"),
    )
    unknown_ipv6_multicast = forms.ChoiceField(
        choices=add_blank_choice(BDUnknownMulticastChoices),
        required=False,
        label=_("Unknown IPv6 multicast"),
    )
    unknown_unicast = forms.ChoiceField(
        choices=add_blank_choice(BDUnknownUnicastChoices),
        required=False,
        label=_("Unknown unicast"),
    )
    virtual_mac_address = forms.CharField(
        required=False,
        label=_("Virtual MAC address"),
    )
    comments = CommentField()

    model = ACIBridgeDomain
    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
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
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )
    nullable_fields: tuple = (
        "name_alias",
        "description",
        "nb_tenant",
        "dhcp_labels",
        "igmp_interface_policy_name",
        "igmp_snooping_policy_name",
        "pim_ipv4_destination_filter",
        "pim_ipv4_source_filter",
        "virtual_mac_address",
        "comments",
    )


class ACIBridgeDomainFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Bridge Domain model."""

    model = ACIBridgeDomain
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
            "aci_vrf_id",
            "description",
            name="Attributes",
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
    advertise_host_routes_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Advertise host routes enabled"),
    )
    arp_flooding_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("ARP flooding enabled"),
    )
    clear_remote_mac_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Clear remote MAC entries enabled"),
    )
    dhcp_labels = forms.CharField(
        required=False,
        label=_("DHCP labels"),
    )
    ep_move_detection_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("EP move detection enabled"),
    )
    ip_data_plane_learning_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("IP data plane learning enabled"),
    )
    limit_ip_learn_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Limit IP learning to subnet enabled"),
    )
    multi_destination_flooding = forms.ChoiceField(
        choices=add_blank_choice(BDMultiDestinationFloodingChoices),
        required=False,
        label=_("Multi destination flooding"),
    )
    pim_ipv4_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("PIM (multicast) IPv4 enabled"),
    )
    pim_ipv6_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("PIM (multicast) IPv6 enabled"),
    )
    unicast_routing_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Unicast routing enabled"),
    )
    unknown_ipv4_multicast = forms.ChoiceField(
        choices=add_blank_choice(BDUnknownMulticastChoices),
        required=False,
        label=_("Unknown IPv4 multicast"),
    )
    unknown_ipv6_multicast = forms.ChoiceField(
        choices=add_blank_choice(BDUnknownMulticastChoices),
        required=False,
        label=_("Unknown IPv6 multicast"),
    )
    unknown_unicast = forms.ChoiceField(
        choices=add_blank_choice(BDUnknownUnicastChoices),
        required=False,
        label=_("Unknown unicast"),
    )
    tag = TagFilterField(model)


class ACIBridgeDomainImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Bridge Domain model."""

    aci_tenant = CSVModelChoiceField(
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Tenant"),
        help_text=_("Assigned ACI Tenant"),
    )
    aci_vrf = CSVModelChoiceField(
        queryset=ACIVRF.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI VRF"),
        help_text=_("Assigned ACI VRF"),
    )
    is_aci_vrf_in_common = forms.BooleanField(
        required=False,
        label=_("Is ACI VRF in 'common'"),
        help_text=_("Assigned ACI VRF is in ACI Tenant 'common'"),
    )
    nb_tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox Tenant"),
        help_text=_("Assigned NetBox Tenant"),
    )
    multi_destination_flooding = CSVChoiceField(
        choices=BDMultiDestinationFloodingChoices,
        required=True,
        label=_("Multi destination flooding"),
        help_text=_(
            "Forwarding method for L2 multicast, broadcast, and link layer traffic."
        ),
    )
    unknown_ipv4_multicast = CSVChoiceField(
        choices=BDUnknownMulticastChoices,
        required=True,
        label=_("Unknown IPv4 multicast"),
        help_text=_("Defines the IPv4 unknown multicast forwarding method."),
    )
    unknown_ipv6_multicast = CSVChoiceField(
        choices=BDUnknownMulticastChoices,
        required=True,
        label=_("Unknown IPv6 multicast"),
        help_text=_("Defines the IPv6 unknown multicast forwarding method."),
    )
    unknown_unicast = CSVChoiceField(
        choices=BDUnknownUnicastChoices,
        required=True,
        label=_("Unknown unicast"),
        help_text=_("Defines the layer 2 unknown unicast forwarding method."),
    )

    class Meta:
        model = ACIBridgeDomain
        fields: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "aci_vrf",
            "description",
            "nb_tenant",
            "is_aci_vrf_in_common",
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

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)

        if not data:
            return

        # Limit ACIVRF queryset by "common" ACITenant
        if data.get("is_aci_vrf_in_common") == "true":
            self.fields["aci_vrf"].queryset = ACIVRF.objects.filter(
                aci_tenant__name="common"
            )
        # Limit ACIVRF queryset by parent ACITenant
        elif data.get("aci_tenant"):
            self.fields["aci_vrf"].queryset = ACIVRF.objects.filter(
                aci_tenant__name=data["aci_tenant"]
            )


#
# Bridge Domain Subnet forms
#


class ACIBridgeDomainSubnetEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Bridge Domain Subnet model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        initial_params={"aci_bridge_domains": "$aci_bridge_domain"},
        required=False,
        label=_("ACI Tenant"),
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
    nb_vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        query_params={"nb_tenant_id": "$nb_tenant"},
        required=False,
        label=_("NetBox VRF"),
    )
    gateway_ip_address = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        query_params={"present_in_vrf_id": "$nb_vrf"},
        label=_("Gateway IP address"),
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
    advertised_externally_enabled = forms.BooleanField(
        required=False,
        label=_("Advertised externally enabled"),
        help_text=_(
            "Advertises the subnet to the outside to any associated L3Outs "
            "(public scope). Default is disabled."
        ),
    )
    igmp_querier_enabled = forms.BooleanField(
        required=False,
        label=_("IGMP querier enabled"),
        help_text=_(
            "Treat the gateway IP address as an IGMP querier source IP. "
            "Default is disabled."
        ),
    )
    ip_data_plane_learning_enabled = forms.BooleanField(
        required=False,
        label=_("IP data plane learning enabled"),
        help_text=_(
            "Whether IP data plane learning is enabled for Bridge Domain. "
            "Default is enabled."
        ),
    )
    no_default_gateway = forms.BooleanField(
        required=False,
        label=_("No default gateway enabled"),
        help_text=_(
            "Remove the default gateway functionality of this gateway address. "
            "Default is disabled."
        ),
    )
    nd_ra_enabled = forms.BooleanField(
        required=False,
        label=_("ND RA enabled"),
        help_text=_(
            "Enables the gateway IP as a IPv6 Neighbor Discovery Router "
            "Advertisement Prefix. Default is enabled."
        ),
    )
    preferred_ip_address_enabled = forms.BooleanField(
        required=False,
        label=_("Preferred (primary) IP enabled"),
        help_text=_(
            "Make this the preferred (primary) IP gateway of the Bridge "
            "Domain. Default is disabled."
        ),
    )
    shared_enabled = forms.BooleanField(
        required=False,
        label=_("Shared enabled"),
        help_text=_(
            "Controls communication to the shared VRF (inter-VRF route "
            "leaking). Default is disabled."
        ),
    )
    virtual_ip_enabled = forms.BooleanField(
        required=False,
        label=_("Virtual IP enabled"),
        help_text=_("Treat the gateway IP as virtual IP. Default is disabled."),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant",
            "aci_vrf",
            "aci_bridge_domain",
            "nb_vrf",
            "gateway_ip_address",
            "description",
            "tags",
            "preferred_ip_address_enabled",
            "virtual_ip_enabled",
            name=_("ACI Bridge Domain Subnet"),
        ),
        FieldSet(
            "advertised_externally_enabled",
            "shared_enabled",
            name=_("Scope Settings"),
        ),
        FieldSet(
            "igmp_querier_enabled",
            "no_default_gateway",
            name=_("Subnet Control Settings"),
        ),
        FieldSet(
            "ip_data_plane_learning_enabled",
            name=_("Endpoint Learning Settings"),
        ),
        FieldSet(
            "nd_ra_enabled",
            "nd_ra_prefix_policy_name",
            name=_("IPv6 Settings"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIBridgeDomainSubnet
        fields: tuple = (
            "name",
            "name_alias",
            "gateway_ip_address",
            "aci_bridge_domain",
            "description",
            "aci_vrf",
            "nb_tenant",
            "advertised_externally_enabled",
            "igmp_querier_enabled",
            "ip_data_plane_learning_enabled",
            "no_default_gateway",
            "nd_ra_enabled",
            "nd_ra_prefix_policy_name",
            "preferred_ip_address_enabled",
            "shared_enabled",
            "virtual_ip_enabled",
            "comments",
            "tags",
        )


class ACIBridgeDomainSubnetBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for ACI Bridge Domain Subnet model."""

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
    advertised_externally_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Advertised externally enabled"),
    )
    igmp_querier_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("IGMP querier enabled"),
    )
    ip_data_plane_learning_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("IP data plane learning enabled"),
    )
    no_default_gateway = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("No default SVI gateway"),
    )
    nd_ra_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("ND RA enabled"),
    )
    nd_ra_prefix_policy_name = forms.CharField(
        required=False,
        label=_("ND RA prefix policy name"),
    )
    preferred_ip_address_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Preferred (Primary) IP address enabled"),
    )
    shared_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Shared enabled"),
    )
    virtual_ip_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Virtual IP enabled"),
    )
    comments = CommentField()

    model = ACIBridgeDomainSubnet
    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_bridge_domain",
            "gateway_ip_address",
            "description",
            "tags",
            "preferred_ip_address_enabled",
            "virtual_ip_enabled",
            name=_("ACI Bridge Domain Subnet"),
        ),
        FieldSet(
            "advertised_externally_enabled",
            "shared_enabled",
            name=_("Scope Settings"),
        ),
        FieldSet(
            "igmp_querier_enabled",
            "no_default_gateway",
            name=_("Subnet Control Settings"),
        ),
        FieldSet(
            "ip_data_plane_learning_enabled",
            name=_("Endpoint Learning Settings"),
        ),
        FieldSet(
            "nd_ra_enabled",
            "nd_ra_prefix_policy_name",
            name=_("IPv6 Settings"),
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
        "nd_ra_prefix_policy_name",
        "comments",
    )


class ACIBridgeDomainSubnetFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Bridge Domain Subnet model."""

    model = ACIBridgeDomainSubnet
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
            "aci_vrf_id",
            "aci_bridge_domain_id",
            "nb_vrf_id",
            "gateway_ip_address",
            "description",
            "preferred_ip_address_enabled",
            "virtual_ip_enabled",
            name="Attributes",
        ),
        FieldSet(
            "advertised_externally_enabled",
            "shared_enabled",
            name=_("Scope Settings"),
        ),
        FieldSet(
            "igmp_querier_enabled",
            "no_default_gateway",
            name=_("Subnet Control Settings"),
        ),
        FieldSet(
            "ip_data_plane_learning_enabled",
            name=_("Endpoint Learning Settings"),
        ),
        FieldSet(
            "nd_ra_enabled",
            "nd_ra_prefix_policy_name",
            name=_("IPv6 Settings"),
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
    gateway_ip_address = forms.CharField(
        required=False,
        label=_("Gateway IP address"),
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
    advertised_externally_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Advertised externally enabled"),
    )
    igmp_querier_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("IGMP querier enabled"),
    )
    ip_data_plane_learning_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("IP data plane learning enabled"),
    )
    no_default_gateway = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("No default SVI gateway"),
    )
    nd_ra_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("ND RA enabled"),
    )
    nd_ra_prefix_policy_name = forms.CharField(
        required=False,
        label=_("ND RA prefix policy name"),
    )
    preferred_ip_address_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Preferred (Primary) IP address enabled"),
    )
    shared_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Shared enabled"),
    )
    virtual_ip_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Virtual IP enabled"),
    )
    tag = TagFilterField(model)


class ACIBridgeDomainSubnetImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Bridge Domain Subnet model."""

    aci_tenant = CSVModelChoiceField(
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Tenant"),
        help_text=_("Parent ACI Tenant of ACI VRF"),
    )
    aci_vrf = CSVModelChoiceField(
        queryset=ACIVRF.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI VRF"),
        help_text=_("Parent ACI VRF of ACI Bridge Domain"),
    )
    aci_bridge_domain = CSVModelChoiceField(
        queryset=ACIBridgeDomain.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Bridge Domain"),
        help_text=_("Assigned ACI Bridge Domain"),
    )
    gateway_ip_address = CSVModelChoiceField(
        queryset=IPAddress.objects.all(),
        to_field_name="address",
        required=True,
        label=_("Gateway IP address"),
        help_text=_("Assigned IP Address (as gateway IP address)"),
    )
    nb_tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("NetBox Tenant"),
        help_text=_("Assigned NetBox Tenant"),
    )

    class Meta:
        model = ACIBridgeDomainSubnet
        fields: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "aci_vrf",
            "aci_bridge_domain",
            "gateway_ip_address",
            "description",
            "nb_tenant",
            "advertised_externally_enabled",
            "igmp_querier_enabled",
            "ip_data_plane_learning_enabled",
            "no_default_gateway",
            "nd_ra_enabled",
            "nd_ra_prefix_policy_name",
            "preferred_ip_address_enabled",
            "shared_enabled",
            "virtual_ip_enabled",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)

        if not data:
            return

        # Limit ACIBridgeDomain queryset by parent ACIVRF and ACITenant
        if data.get("aci_tenant") and data.get("aci_vrf"):
            # Limit ACIVRF queryset by parent ACITenant
            self.fields["aci_vrf"].queryset = ACIVRF.objects.filter(
                aci_tenant__name=data["aci_tenant"]
            )
            # Limit ACIBridgeDomain queryset by parent ACIVRF and ACITenant
            aci_bd_queryset = ACIBridgeDomain.objects.filter(
                aci_tenant__name=data["aci_tenant"],
                aci_vrf__name=data["aci_vrf"],
            )
            self.fields["aci_bridge_domain"].queryset = aci_bd_queryset
