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
    CSVMultipleChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet, TabbedGroups

from ...choices import (
    ContractFilterARPOpenPeripheralCodesChoices,
    ContractFilterEtherTypeChoices,
    ContractFilterICMPv4TypesChoices,
    ContractFilterICMPv6TypesChoices,
    ContractFilterIPProtocolChoices,
    ContractFilterPortChoices,
    ContractFilterTCPRulesChoices,
    QualityOfServiceDSCPChoices,
    add_custom_choice,
)
from ...models.tenant.contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from ...models.tenant.tenants import ACITenant
from ...validators import (
    validate_contract_filter_ip_protocol,
    validate_contract_filter_port,
)
from ..widgets.misc import TextInputWithOptions

#
# Contract Filter forms
#


class ACIContractFilterEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Contract Filter model."""

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
            name=_("ACI Contract Filter"),
        ),
        FieldSet(
            "nb_tenant_group",
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )

    class Meta:
        model = ACIContractFilter
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "nb_tenant",
            "comments",
            "tags",
        )


class ACIContractFilterBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Contract Filter model."""

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

    model = ACIContractFilter
    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant",
            "description",
            "tags",
            name=_("ACI Contract Filter"),
        ),
        FieldSet(
            "nb_tenant",
            name=_("NetBox Tenancy"),
        ),
    )
    nullable_fields = (
        "name_alias",
        "description",
        "nb_tenant",
        "comments",
    )


class ACIContractFilterFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Contract Filter model."""

    model = ACIContractFilter
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
    tag = TagFilterField(model)


class ACIContractFilterImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Contract Filter model."""

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
        model = ACIContractFilter
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
# Contract Filter Entry forms
#


class ACIContractFilterEntryEditForm(NetBoxModelForm):
    """NetBox edit form for the ACI Contract Filter Entry model."""

    aci_tenant = DynamicModelChoiceField(
        queryset=ACITenant.objects.all(),
        initial_params={"aci_contract_filters": "$aci_contract_filter"},
        required=False,
        label=_("ACI Tenant"),
    )
    aci_contract_filter = DynamicModelChoiceField(
        queryset=ACIContractFilter.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        label=_("ACI Contract Filter"),
    )
    arp_opc = forms.ChoiceField(
        choices=ContractFilterARPOpenPeripheralCodesChoices,
        required=False,
        label=_("ARP open peripheral codes"),
        help_text=_(
            "Specifies the ARP flag (for ether type 'ARP'). Default is 'unspecified'."
        ),
    )
    destination_from_port = forms.ChoiceField(
        choices=add_custom_choice(ContractFilterPortChoices),
        required=False,
        label=_("Destination from-port"),
        help_text=_(
            "Set the start of the destination port range, when the "
            "IP protocol is TCP or UDP. Default is 'unspecified'."
        ),
    )
    destination_from_port_custom = forms.IntegerField(
        min_value=1,
        max_value=65535,
        required=False,
        label=_("Destination from-port (custom)"),
        help_text=_(
            "Set the start of the destination port range, when the "
            "IP protocol is TCP or UDP. "
            "(Valid values 1-65535). Default is 'unspecified'."
        ),
    )
    destination_to_port = forms.ChoiceField(
        choices=add_custom_choice(ContractFilterPortChoices),
        required=False,
        label=_("Destination to-port"),
        help_text=_(
            "Set the end of the destination port range, when the "
            "IP protocol is TCP or UDP. Default is 'unspecified'."
        ),
    )
    destination_to_port_custom = forms.IntegerField(
        min_value=1,
        max_value=65535,
        required=False,
        label=_("Destination to-port (custom)"),
        help_text=_(
            "Set the end of the destination port range, when the "
            "IP protocol is TCP or UDP. "
            "(Valid values 1-65535). Default is 'unspecified'."
        ),
    )
    ether_type = forms.ChoiceField(
        choices=ContractFilterEtherTypeChoices,
        required=False,
        label=_("Ether type"),
        help_text=_(
            "Specify the Ethernet type for the filter entry. Default is 'unspecified'."
        ),
    )
    icmp_v4_type = forms.ChoiceField(
        choices=ContractFilterICMPv4TypesChoices,
        required=False,
        label=_("ICMPv4 type"),
        help_text=_(
            "Match the specific ICMPv4 message type (for IP protocol "
            "'ICMPv4'). Default is 'unspecified'."
        ),
    )
    icmp_v6_type = forms.ChoiceField(
        choices=ContractFilterICMPv6TypesChoices,
        required=False,
        label=_("ICMPv6 type"),
        help_text=_(
            "Match the specific ICMPv6 message type (for IP protocol "
            "'ICMPv6'). Default is 'unspecified'."
        ),
    )
    ip_protocol = forms.ChoiceField(
        choices=add_custom_choice(ContractFilterIPProtocolChoices),
        required=False,
        label=_("IP protocol"),
        help_text=_(
            "Set the Layer 3 IP protocol (for ether type 'IP'). "
            "Default is 'unspecified'."
        ),
    )
    ip_protocol_custom = forms.IntegerField(
        min_value=1,
        max_value=255,
        required=False,
        label=_("IP protocol (custom)"),
        help_text=_(
            "Set the Layer 3 IP protocol (for ether type 'IP'). "
            "(Valid values 1-255). Default is 'unspecified'."
        ),
    )
    match_dscp = forms.ChoiceField(
        choices=QualityOfServiceDSCPChoices,
        required=False,
        label=_("Match DSCP"),
        help_text=_(
            "Match the specific DSCP (Differentiated Services Code Point) "
            "value (for ether type 'IP'). Default is 'unspecified'."
        ),
    )
    match_only_fragments_enabled = forms.BooleanField(
        required=False,
        label=_("Match only fragments enabled"),
        help_text=_(
            "Rule matches only fragments with offset greater than 0 (all "
            "fragments except the first one). Default is disabled."
        ),
    )
    source_from_port = forms.ChoiceField(
        choices=add_custom_choice(ContractFilterPortChoices),
        required=False,
        label=_("Source from-port"),
        help_text=_(
            "Set the start of the source port range, when the "
            "IP protocol is TCP or UDP. Default is 'unspecified'."
        ),
    )
    source_from_port_custom = forms.IntegerField(
        min_value=1,
        max_value=65535,
        required=False,
        label=_("Source from-port (custom)"),
        help_text=_(
            "Set the start of the source port range, when the "
            "IP protocol is TCP or UDP. "
            "(Valid values 1-65535). Default is 'unspecified'."
        ),
    )
    source_to_port = forms.ChoiceField(
        choices=add_custom_choice(ContractFilterPortChoices),
        required=False,
        label=_("Source to-port"),
        help_text=_(
            "Set the end of the source port range, when the "
            "IP protocol is TCP or UDP. Default is 'unspecified'."
        ),
    )
    source_to_port_custom = forms.IntegerField(
        min_value=1,
        max_value=65535,
        required=False,
        label=_("Source to-port (custom)"),
        help_text=_(
            "Set the end of the source port range, when the "
            "IP protocol is TCP or UDP. "
            "(Valid values 1-65535). Default is 'unspecified'."
        ),
    )
    stateful_enabled = forms.BooleanField(
        required=False,
        label=_("Stateful enabled"),
        help_text=_(
            "Allows TCP packets from provider to consumer only if the TCP "
            "flag ACK is set. Default is disabled."
        ),
    )
    tcp_rules = forms.MultipleChoiceField(
        choices=ContractFilterTCPRulesChoices,
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "size": 6,
            }
        ),
        label=_("TCP rules"),
        help_text=_(
            "Specifies the matching TCP flag values. Default is 'unspecified'."
        ),
    )
    comments = CommentField()

    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant",
            "aci_contract_filter",
            "description",
            "tags",
            name=_("ACI Contract Filter Entry"),
        ),
        FieldSet(
            "ether_type",
            name=_("Ether Type"),
        ),
        FieldSet(
            "arp_opc",
            name=_("ARP"),
        ),
        FieldSet(
            TabbedGroups(
                FieldSet(
                    "ip_protocol",
                    name=_("IP Protocol"),
                ),
                FieldSet(
                    "ip_protocol_custom",
                    name=_("IP Protocol (custom)"),
                ),
            ),
            "match_dscp",
            "match_only_fragments_enabled",
            name=_("IP Protocol"),
        ),
        FieldSet(
            "icmp_v4_type",
            "icmp_v6_type",
            name=_("ICMP"),
        ),
        FieldSet(
            TabbedGroups(
                FieldSet(
                    "source_from_port",
                    "source_to_port",
                    name=_("Source port ranges"),
                ),
                FieldSet(
                    "source_from_port_custom",
                    "source_to_port_custom",
                    name=_("Source port ranges (custom)"),
                ),
            ),
            TabbedGroups(
                FieldSet(
                    "destination_from_port",
                    "destination_to_port",
                    name=_("Destination port ranges"),
                ),
                FieldSet(
                    "destination_from_port_custom",
                    "destination_to_port_custom",
                    name=_("Destination port ranges (custom)"),
                ),
            ),
            name=_("TCP/UDP Port Ranges"),
        ),
        FieldSet(
            "stateful_enabled",
            "tcp_rules",
            name=_("TCP"),
        ),
    )

    class Meta:
        model = ACIContractFilterEntry
        fields: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_contract_filter",
            "arp_opc",
            "destination_from_port",
            "destination_to_port",
            "ether_type",
            "icmp_v4_type",
            "icmp_v6_type",
            "ip_protocol",
            "match_dscp",
            "match_only_fragments_enabled",
            "source_from_port",
            "source_to_port",
            "stateful_enabled",
            "tcp_rules",
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the ACI Contract Filter Entry form."""
        # Initialize fields with custom values
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()
        if instance:
            # Initialize IP protocol fields
            protocol_choices = dict(ContractFilterIPProtocolChoices)
            if instance.ip_protocol not in protocol_choices:
                initial["ip_protocol"] = None
                initial["ip_protocol_custom"] = instance.ip_protocol

            # Initialize port fields
            port_choices = dict(ContractFilterPortChoices)
            if instance.destination_from_port not in port_choices:
                initial["destination_from_port"] = None
                initial["destination_from_port_custom"] = instance.destination_from_port
            if instance.destination_to_port not in port_choices:
                initial["destination_to_port"] = None
                initial["destination_to_port_custom"] = instance.destination_to_port
            if instance.source_from_port not in port_choices:
                initial["source_from_port"] = None
                initial["source_from_port_custom"] = instance.source_from_port
            if instance.source_to_port not in port_choices:
                initial["source_to_port"] = None
                initial["source_to_port_custom"] = instance.source_to_port
        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

    def clean(self) -> None:
        """Validate form fields for the ACI Contract Filter Entry form."""
        super().clean()

        # Validate IP protocol
        if not self.cleaned_data.get("ip_protocol"):
            ip_protocol_custom = self.cleaned_data.get("ip_protocol_custom")
            validate_contract_filter_ip_protocol(ip_protocol_custom)
            self.cleaned_data["ip_protocol"] = ip_protocol_custom

        # Validate destination ports
        if not self.cleaned_data.get("destination_from_port"):
            destination_from_port_custom = self.cleaned_data.get(
                "destination_from_port_custom"
            )
            validate_contract_filter_port(destination_from_port_custom)
            self.cleaned_data["destination_from_port"] = destination_from_port_custom
        if not self.cleaned_data.get("destination_to_port"):
            destination_to_port_custom = self.cleaned_data.get(
                "destination_to_port_custom"
            )
            validate_contract_filter_port(destination_to_port_custom)
            self.cleaned_data["destination_to_port"] = destination_to_port_custom

        # Validate source ports
        if not self.cleaned_data.get("source_from_port"):
            source_from_port_custom = self.cleaned_data.get("source_from_port_custom")
            validate_contract_filter_port(source_from_port_custom)
            self.cleaned_data["source_from_port"] = source_from_port_custom
        if not self.cleaned_data.get("source_to_port"):
            source_to_port_custom = self.cleaned_data.get("source_to_port_custom")
            validate_contract_filter_port(source_to_port_custom)
            self.cleaned_data["source_to_port"] = source_to_port_custom


class ACIContractFilterEntryBulkEditForm(NetBoxModelBulkEditForm):
    """NetBox bulk edit form for the ACI Contract Filter Entry model."""

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
    aci_contract_filter = DynamicModelChoiceField(
        queryset=ACIContractFilter.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant"},
        required=False,
        label=_("ACI Contract Filter"),
    )
    arp_opc = forms.ChoiceField(
        choices=add_blank_choice(ContractFilterARPOpenPeripheralCodesChoices),
        required=False,
        label=_("ARP open peripheral codes"),
    )
    destination_from_port = forms.CharField(
        required=False,
        label=_("Destination from-port"),
        help_text=_(
            "Set the start of the destination port range, when the "
            "IP protocol is TCP or UDP. "
            "(Valid values 1-65535). Default is 'unspecified'."
        ),
        widget=TextInputWithOptions(
            options=ContractFilterPortChoices,
        ),
    )
    destination_to_port = forms.CharField(
        required=False,
        label=_("Destination to-port"),
        help_text=_(
            "Set the end of the destination port range, when the "
            "IP protocol is TCP or UDP. "
            "(Valid values 1-65535). Default is 'unspecified'."
        ),
        widget=TextInputWithOptions(
            options=ContractFilterPortChoices,
        ),
    )
    ether_type = forms.ChoiceField(
        choices=add_blank_choice(ContractFilterEtherTypeChoices),
        required=False,
        label=_("Ether type"),
    )
    icmp_v4_type = forms.ChoiceField(
        choices=add_blank_choice(ContractFilterICMPv4TypesChoices),
        required=False,
        label=_("ICMPv4 type"),
    )
    icmp_v6_type = forms.ChoiceField(
        choices=add_blank_choice(ContractFilterICMPv6TypesChoices),
        required=False,
        label=_("ICMPv6 type"),
    )
    ip_protocol = forms.CharField(
        required=False,
        label=_("IP protocol"),
        help_text=_(
            "Set the Layer 3 IP protocol (for ether type 'IP'). (Valid values 1-255)."
        ),
        widget=TextInputWithOptions(
            options=ContractFilterIPProtocolChoices,
        ),
    )
    match_dscp = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Match DSCP"),
    )
    match_only_fragments_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Match only fragments enabled"),
    )
    source_from_port = forms.CharField(
        required=False,
        label=_("Source from-port"),
        help_text=_(
            "Set the start of the source port range, when the "
            "IP protocol is TCP or UDP. "
            "(Valid values 1-65535). Default is 'unspecified'."
        ),
        widget=TextInputWithOptions(
            options=ContractFilterPortChoices,
        ),
    )
    source_to_port = forms.CharField(
        required=False,
        label=_("Source to-port"),
        help_text=_(
            "Set the end of the source port range, when the "
            "IP protocol is TCP or UDP. "
            "(Valid values 1-65535). Default is 'unspecified'."
        ),
        widget=TextInputWithOptions(
            options=ContractFilterPortChoices,
        ),
    )
    stateful_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Stateful enabled"),
    )
    tcp_rules = forms.MultipleChoiceField(
        choices=ContractFilterTCPRulesChoices,
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "size": 6,
            }
        ),
        label=_("TCP rules"),
    )
    comments = CommentField()

    model = ACIContractFilterEntry
    fieldsets: tuple = (
        FieldSet(
            "name",
            "name_alias",
            "aci_tenant",
            "aci_contract_filter",
            "description",
            "tags",
            name=_("ACI Contract Filter Entry"),
        ),
        FieldSet(
            "ether_type",
            name=_("Ether Type"),
        ),
        FieldSet(
            "arp_opc",
            name=_("ARP"),
        ),
        FieldSet(
            "ip_protocol",
            "ip_protocol_custom",
            "match_dscp",
            "match_only_fragments_enabled",
            name=_("IP Protocol"),
        ),
        FieldSet(
            "icmp_v4_type",
            "icmp_v6_type",
            name=_("ICMP"),
        ),
        FieldSet(
            "source_from_port",
            "source_to_port",
            "destination_from_port",
            "destination_to_port",
            name=_("TCP/UDP Port Ranges"),
        ),
        FieldSet(
            "stateful_enabled",
            "tcp_rules",
            name=_("TCP"),
        ),
    )
    nullable_fields: tuple = (
        "name_alias",
        "description",
        "comments",
    )


class ACIContractFilterEntryFilterForm(NetBoxModelFilterSetForm):
    """NetBox filter form for the ACI Contract Filter model."""

    model = ACIContractFilterEntry
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
            "aci_contract_filter_id",
            "description",
            name="Attributes",
        ),
        FieldSet(
            "ether_type",
            name=_("Ether Type"),
        ),
        FieldSet(
            "arp_opc",
            name=_("ARP"),
        ),
        FieldSet(
            "ip_protocol",
            "ip_protocol_custom",
            "match_dscp",
            "match_only_fragments_enabled",
            name=_("IP Protocol"),
        ),
        FieldSet(
            "icmp_v4_type",
            "icmp_v6_type",
            name=_("ICMP"),
        ),
        FieldSet(
            "source_from_port",
            "source_from_port_custom",
            "source_to_port",
            "source_to_port_custom",
            "destination_from_port",
            "destination_from_port_custom",
            "destination_to_port",
            "destination_to_port_custom",
            name=_("TCP/UDP Port Ranges"),
        ),
        FieldSet(
            "stateful_enabled",
            "tcp_rules",
            name=_("TCP"),
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
    aci_contract_filter_id = DynamicModelMultipleChoiceField(
        queryset=ACIContractFilter.objects.all(),
        query_params={"aci_tenant_id": "$aci_tenant_id"},
        required=False,
        label=_("ACI Contract Filter"),
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
    arp_opc = forms.ChoiceField(
        choices=add_blank_choice(ContractFilterARPOpenPeripheralCodesChoices),
        required=False,
        label=_("ARP open peripheral codes"),
    )
    destination_from_port = forms.ChoiceField(
        choices=add_blank_choice(ContractFilterPortChoices),
        required=False,
        label=_("Destination from-port"),
    )
    destination_from_port_custom = forms.CharField(
        required=False,
        label=_("Destination from-port (custom)"),
    )
    destination_to_port = forms.ChoiceField(
        choices=add_blank_choice(ContractFilterPortChoices),
        required=False,
        label=_("Destination to-port"),
    )
    destination_to_port_custom = forms.CharField(
        required=False,
        label=_("Destination to-port (custom)"),
    )
    ether_type = forms.ChoiceField(
        choices=add_blank_choice(ContractFilterEtherTypeChoices),
        required=False,
        label=_("Ether type"),
    )
    icmp_v4_type = forms.ChoiceField(
        choices=add_blank_choice(ContractFilterICMPv4TypesChoices),
        required=False,
        label=_("ICMPv4 type"),
    )
    icmp_v6_type = forms.ChoiceField(
        choices=add_blank_choice(ContractFilterICMPv6TypesChoices),
        required=False,
        label=_("ICMPv6 type"),
    )
    ip_protocol = forms.ChoiceField(
        choices=add_blank_choice(ContractFilterIPProtocolChoices),
        required=False,
        label=_("IP protocol"),
    )
    ip_protocol_custom = forms.CharField(
        required=False,
        label=_("IP protocol (custom)"),
    )
    match_dscp = forms.ChoiceField(
        choices=add_blank_choice(QualityOfServiceDSCPChoices),
        required=False,
        label=_("Match DSCP"),
    )
    match_only_fragments_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Match only fragments enabled"),
    )
    source_from_port = forms.ChoiceField(
        choices=add_blank_choice(ContractFilterPortChoices),
        required=False,
        label=_("Source from-port"),
    )
    source_from_port_custom = forms.CharField(
        required=False,
        label=_("Source from-port (custom)"),
    )
    source_to_port = forms.ChoiceField(
        choices=add_blank_choice(ContractFilterPortChoices),
        required=False,
        label=_("Source to-port"),
    )
    source_to_port_custom = forms.CharField(
        required=False,
        label=_("Source to-port (custom)"),
    )
    stateful_enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES,
        ),
        label=_("Stateful enabled"),
    )
    tcp_rules = forms.MultipleChoiceField(
        choices=add_blank_choice(ContractFilterTCPRulesChoices),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "size": 7,
            }
        ),
        label=_("TCP rules"),
    )
    tag = TagFilterField(model)


class ACIContractFilterEntryImportForm(NetBoxModelImportForm):
    """NetBox import form for the ACI Contract Filter Entry model."""

    aci_tenant = CSVModelChoiceField(
        queryset=ACITenant.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Tenant"),
        help_text=_("Parent ACI Tenant of ACI Contract Filter"),
    )
    aci_contract_filter = CSVModelChoiceField(
        queryset=ACIContractFilter.objects.all(),
        to_field_name="name",
        required=True,
        label=_("ACI Tenant"),
        help_text=_("Assigned ACI Contract Filter"),
    )
    arp_opc = CSVChoiceField(
        choices=ContractFilterARPOpenPeripheralCodesChoices,
        required=False,
        label=_("ARP open peripheral codes"),
        help_text=_(
            "Specifies the ARP flag (for ether type 'ARP'). Default is 'unspecified'."
        ),
    )
    destination_from_port = forms.CharField(
        required=False,
        label=_("Destination from-port"),
        help_text=_(
            "Set the start of the destination port range, when the "
            "IP protocol is TCP or UDP. "
            "(Valid values 1-65535). Default is 'unspecified'."
        ),
    )
    destination_to_port = forms.CharField(
        required=False,
        label=_("Destination to-port"),
        help_text=_(
            "Set the end of the destination port range, when the "
            "IP protocol is TCP or UDP. "
            "(Valid values 1-65535). Default is 'unspecified'."
        ),
    )
    ether_type = CSVChoiceField(
        choices=ContractFilterEtherTypeChoices,
        required=False,
        label=_("Ether type"),
        help_text=_(
            "Specify the Ethernet type for the filter entry. Default is 'unspecified'."
        ),
    )
    ip_protocol = forms.CharField(
        required=False,
        label=_("IP protocol"),
        help_text=_(
            "Set the Layer 3 IP protocol (for ether type 'IP'). "
            "Valid values: 0-255. Default is 'unspecified'."
        ),
    )
    icmp_v4_type = CSVChoiceField(
        choices=ContractFilterICMPv4TypesChoices,
        required=False,
        label=_("ICMPv4 type"),
        help_text=_(
            "Match the specific ICMPv4 message type (for IP protocol "
            "'ICMPv4'). Default is 'unspecified'."
        ),
    )
    icmp_v6_type = CSVChoiceField(
        choices=ContractFilterICMPv6TypesChoices,
        required=False,
        label=_("ICMPv6 type"),
        help_text=_(
            "Match the specific ICMPv6 message type (for IP protocol "
            "'ICMPv6'). Default is 'unspecified'."
        ),
    )
    match_dscp = CSVChoiceField(
        choices=QualityOfServiceDSCPChoices,
        required=False,
        label=_("Match DSCP"),
        help_text=_(
            "Match the specific DSCP (Differentiated Services Code Point) "
            "value (for ether type 'IP'). Default is 'unspecified'."
        ),
    )
    match_only_fragments_enabled = forms.BooleanField(
        required=False,
        label=_("Match only fragments enabled"),
        help_text=_(
            "Rule matches only fragments with offset greater than 0 (all "
            "fragments except the first one). Default is disabled."
        ),
    )
    source_from_port = forms.CharField(
        required=False,
        label=_("Source from-port"),
        help_text=_(
            "Set the start of the source port range, when the "
            "IP protocol is TCP or UDP. "
            "(Valid values 1-65535). Default is 'unspecified'."
        ),
    )
    source_to_port = forms.CharField(
        required=False,
        label=_("Source to-port"),
        help_text=_(
            "Set the end of the source port range, when the "
            "IP protocol is TCP or UDP. "
            "(Valid values 1-65535). Default is 'unspecified'."
        ),
    )
    stateful_enabled = forms.BooleanField(
        required=False,
        label=_("Stateful enabled"),
        help_text=_(
            "Allows TCP packets from provider to consumer only if the TCP "
            "flag ACK is set. Default is disabled."
        ),
    )
    tcp_rules = CSVMultipleChoiceField(
        choices=ContractFilterTCPRulesChoices,
        required=False,
        label=_("TCP rules"),
        help_text=_(
            "Specify TCP rules for the filter entry. Default is 'unspecified'."
        ),
    )

    class Meta:
        model = ACIContractFilterEntry
        fields: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "aci_contract_filter",
            "description",
            "ether_type",
            "arp_opc",
            "ip_protocol",
            "match_dscp",
            "match_only_fragments_enabled",
            "icmp_v4_type",
            "icmp_v6_type",
            "source_from_port",
            "source_to_port",
            "destination_from_port",
            "destination_to_port",
            "stateful_enabled",
            "tcp_rules",
            "comments",
            "tags",
        )

    def __init__(self, data=None, *args, **kwargs) -> None:
        """Extend import data processing with enhanced query sets."""
        super().__init__(data, *args, **kwargs)

        if not data:
            return

        # Limit ACIContractFilter queryset by parent ACI objects
        if data.get("aci_tenant"):
            # Limit ACIContractFilter queryset by parent ACIContract
            aci_filter_queryset = ACIContractFilter.objects.filter(
                aci_tenant__name=data["aci_tenant"]
            )
            self.fields["aci_contract_filter"].queryset = aci_filter_queryset

    def _clean_field_default_unspecified(self, field_name) -> str:
        """Return default value for empty imported field."""
        field_value = self.cleaned_data.get(field_name, None)
        if not field_value:
            return "unspecified"
        return field_value

    def clean_arp_opc(self) -> str:
        """Return a cleaned and validated value for arp_opc."""
        return self._clean_field_default_unspecified("arp_opc")

    def clean_destination_from_port(self) -> str:
        """Return a cleaned and validated value for destination_from_port."""
        return self._clean_field_default_unspecified("destination_from_port")

    def clean_destination_to_port(self) -> str:
        """Return a cleaned and validated value for destination_to_port."""
        return self._clean_field_default_unspecified("destination_to_port")

    def clean_ether_type(self) -> str:
        """Return a cleaned and validated value for ether_type."""
        return self._clean_field_default_unspecified("ether_type")

    def clean_icmp_v4_type(self) -> str:
        """Return a cleaned and validated value for icmp_v4_type."""
        return self._clean_field_default_unspecified("icmp_v4_type")

    def clean_icmp_v6_type(self) -> str:
        """Return a cleaned and validated value for icmp_v6_type."""
        return self._clean_field_default_unspecified("icmp_v6_type")

    def clean_ip_protocol(self) -> str:
        """Return a cleaned and validated value for ip_protocol."""
        return self._clean_field_default_unspecified("ip_protocol")

    def clean_match_dscp(self) -> str:
        """Return a cleaned and validated value for match_dscp."""
        return self._clean_field_default_unspecified("match_dscp")

    def clean_source_from_port(self) -> str:
        """Return a cleaned and validated value for source_from_port."""
        return self._clean_field_default_unspecified("source_from_port")

    def clean_source_to_port(self) -> str:
        """Return a cleaned and validated value for source_to_port."""
        return self._clean_field_default_unspecified("source_to_port")

    def clean_tcp_rules(self) -> list[str] | None:
        """Return a cleaned and validated value for tcp_rules."""
        field_value = self.cleaned_data.get("tcp_rules", None)
        if not field_value:
            return ["unspecified"]
        return field_value
