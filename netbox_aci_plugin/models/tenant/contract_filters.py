# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ...choices import (
    ContractFilterARPOpenPeripheralCodesChoices,
    ContractFilterEtherTypeChoices,
    ContractFilterICMPv4TypesChoices,
    ContractFilterICMPv6TypesChoices,
    ContractFilterIPProtocolChoices,
    ContractFilterPortChoices,
    ContractFilterTCPRulesChoices,
    QualityOfServiceDSCPChoices,
)
from ...validators import (
    validate_contract_filter_ip_protocol,
    validate_contract_filter_port,
    validate_contract_filter_tcp_rules,
)
from ..base import ACIBaseModel
from .tenants import ACITenant


def default_contract_filter_entry_tcp_rules() -> list[str]:
    """Return a default list for TCP rules."""
    return [
        ContractFilterTCPRulesChoices.TCP_UNSPECIFIED,
    ]


class ACIContractFilter(ACIBaseModel):
    """NetBox model for ACI Contract Filter."""

    aci_tenant = models.ForeignKey(
        to=ACITenant,
        on_delete=models.PROTECT,
        related_name="aci_contract_filters",
        verbose_name=_("ACI Tenant"),
    )

    clone_fields: tuple = ACIBaseModel.clone_fields + ("aci_tenant",)
    prerequisite_models: tuple = ("netbox_aci_plugin.ACITenant",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_tenant", "name"),
                name="%(app_label)s_%(class)s_unique_per_aci_tenant",
            ),
        ]
        ordering: tuple = ("aci_tenant", "name")
        verbose_name: str = _("ACI Contract Filter")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        if self.aci_tenant.name == "common":
            return f"{self.name} ({self.aci_tenant.name})"
        return self.name

    @property
    def parent_object(self) -> ACIBaseModel:
        """Return the parent object of the instance."""
        return self.aci_tenant


class ACIContractFilterEntry(ACIBaseModel):
    """NetBox model for ACI Contract Filter Entry."""

    aci_contract_filter = models.ForeignKey(
        to=ACIContractFilter,
        on_delete=models.CASCADE,
        related_name="aci_contract_filter_entries",
        verbose_name=_("ACI Contract Filter"),
    )
    arp_opc = models.CharField(
        verbose_name=_("ARP open peripheral codes"),
        max_length=11,
        default=ContractFilterARPOpenPeripheralCodesChoices.OPC_UNSPECIFIED,
        choices=ContractFilterARPOpenPeripheralCodesChoices,
        help_text=_(
            "Specifies the ARP flag (for ether type 'ARP'). Default is 'unspecified'."
        ),
    )
    destination_from_port = models.CharField(
        verbose_name=_("destination from-port"),
        max_length=11,
        default=ContractFilterPortChoices.PORT_UNSPECIFIED,
        help_text=_(
            "Set the start of the destination port range, when the "
            "IP protocol is TCP or UDP. Default is 'unspecified'."
        ),
        validators=[validate_contract_filter_port],
    )
    destination_to_port = models.CharField(
        verbose_name=_("destination to-port"),
        max_length=11,
        default=ContractFilterPortChoices.PORT_UNSPECIFIED,
        help_text=_(
            "Set the end of the destination port range, when the "
            "IP protocol is TCP or UDP. Default is 'unspecified'."
        ),
        validators=[validate_contract_filter_port],
    )
    ether_type = models.CharField(
        verbose_name=_("ether type"),
        max_length=12,
        default=ContractFilterEtherTypeChoices.TYPE_UNSPECIFIED,
        choices=ContractFilterEtherTypeChoices,
        help_text=_(
            "Specify the Ethernet type for the filter entry. Default is 'unspecified'."
        ),
    )
    icmp_v4_type = models.CharField(
        verbose_name=_("ICMPv4 type"),
        max_length=13,
        default=ContractFilterICMPv4TypesChoices.ICMP_V4_UNSPECIFIED,
        choices=ContractFilterICMPv4TypesChoices,
        help_text=_(
            "Match the specific ICMPv4 message type (for IP protocol "
            "'ICMPv4'). Default is 'unspecified'."
        ),
    )
    icmp_v6_type = models.CharField(
        verbose_name=_("ICMPv6 type"),
        max_length=13,
        default=ContractFilterICMPv6TypesChoices.ICMP_V6_UNSPECIFIED,
        choices=ContractFilterICMPv6TypesChoices,
        help_text=_(
            "Match the specific ICMPv6 message type (for IP protocol "
            "'ICMPv6'). Default is 'unspecified'."
        ),
    )
    ip_protocol = models.CharField(
        verbose_name=_("IP protocol"),
        max_length=11,
        default=ContractFilterIPProtocolChoices.PROT_UNSPECIFIED,
        help_text=_(
            "Set the Layer 3 IP protocol (for ether type 'IP'). "
            "Valid values: 0-255. Default is 'unspecified'."
        ),
        validators=[validate_contract_filter_ip_protocol],
    )
    match_dscp = models.CharField(
        verbose_name=_("match DSCP"),
        max_length=11,
        default=QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED,
        choices=QualityOfServiceDSCPChoices,
        help_text=_(
            "Match the specific DSCP (Differentiated Services Code Point) "
            "value (for ether type 'IP'). Default is 'unspecified'."
        ),
    )
    match_only_fragments_enabled = models.BooleanField(
        verbose_name=_("match only fragments enabled"),
        default=False,
        help_text=_(
            "Rule matches only fragments with offset greater than 0 (all "
            "fragments except the first one). Default is disabled."
        ),
    )
    source_from_port = models.CharField(
        verbose_name=_("source from-port"),
        max_length=11,
        default=ContractFilterPortChoices.PORT_UNSPECIFIED,
        help_text=_(
            "Set the start of the source port range, when the "
            "IP protocol is TCP or UDP. Default is 'unspecified'."
        ),
        validators=[validate_contract_filter_port],
    )
    source_to_port = models.CharField(
        verbose_name=_("source to-port"),
        max_length=11,
        default=ContractFilterPortChoices.PORT_UNSPECIFIED,
        help_text=_(
            "Set the end of the source port range, when the "
            "IP protocol is TCP or UDP. Default is 'unspecified'."
        ),
        validators=[validate_contract_filter_port],
    )
    stateful_enabled = models.BooleanField(
        verbose_name=_("stateful enabled"),
        default=False,
        help_text=_(
            "Allows TCP packets from provider to consumer only if the TCP "
            "flag ACK is set. Default is disabled."
        ),
    )
    tcp_rules = ArrayField(
        base_field=models.CharField(
            max_length=11,
            choices=ContractFilterTCPRulesChoices,
        ),
        verbose_name=_("TCP session rules"),
        blank=True,
        default=default_contract_filter_entry_tcp_rules,
        help_text=_(
            "Specifies the matching TCP flag values. Default is 'unspecified'."
        ),
        validators=[validate_contract_filter_tcp_rules],
    )

    clone_fields: tuple = ACIBaseModel.clone_fields + (
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
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIContractFilter",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_contract_filter", "name"),
                name="%(app_label)s_%(class)s_unique_per_aci_contract_filter",
            ),
        ]
        ordering: tuple = ("aci_contract_filter", "name")
        verbose_name: str = _("ACI Contract Filter Entry")
        verbose_name_plural: str = _("ACI Contract Filter Entries")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return f"{self.name} ({self.aci_contract_filter.name})"

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        validation_errors = {}

        # Allowable IP ether types
        ip_ether_types = [
            ContractFilterEtherTypeChoices.TYPE_IP,
            ContractFilterEtherTypeChoices.TYPE_IPV4,
            ContractFilterEtherTypeChoices.TYPE_IPV6,
        ]

        # Validate arp_opc for ether_type 'arp'
        if (
            self.ether_type != ContractFilterEtherTypeChoices.TYPE_ARP
            and self.arp_opc
            != ContractFilterARPOpenPeripheralCodesChoices.OPC_UNSPECIFIED
        ):
            validation_errors["arp_opc"] = _(
                "ARP open peripheral codes must be 'unspecified' when "
                "Ethernet Type is not 'ARP'."
            )

        # Validate ip_protocol for ether_type 'ip', 'ipv4' or 'ipv6'
        if (
            self.ether_type not in ip_ether_types
            and self.ip_protocol != ContractFilterIPProtocolChoices.PROT_UNSPECIFIED
        ):
            validation_errors["ip_protocol"] = _(
                "IP protocol must be 'unspecified' when Ethernet Type is not "
                "'IP', 'IPv4', or 'IPv6'."
            )

        # Validate ports for ether_type 'ip', 'ipv4' or 'ipv6'
        # and ip_protocol 'tcp' or 'udp'
        if self.ether_type not in ip_ether_types or self.ip_protocol not in [
            ContractFilterIPProtocolChoices.PROT_TCP,
            ContractFilterIPProtocolChoices.PROT_UDP,
        ]:
            if self.destination_from_port != ContractFilterPortChoices.PORT_UNSPECIFIED:
                validation_errors["destination_from_port"] = _(
                    "Destination from-port must be set to 'unspecified' when "
                    "Ethernet Type is not 'IP', 'IPv4', or 'IPv6' or "
                    "IP Protocol is not 'TCP' or 'UDP'."
                )
            if self.destination_to_port != ContractFilterPortChoices.PORT_UNSPECIFIED:
                validation_errors["destination_to_port"] = _(
                    "Destination to-port must be set to 'unspecified' when "
                    "Ethernet Type is not 'IP', 'IPv4', or 'IPv6' or "
                    "IP Protocol is not 'TCP' or 'UDP'."
                )
            if self.source_from_port != ContractFilterPortChoices.PORT_UNSPECIFIED:
                validation_errors["source_from_port"] = _(
                    "Source from-port must be set to 'unspecified' when "
                    "Ethernet Type is not 'IP', 'IPv4', or 'IPv6' or "
                    "IP Protocol is not 'TCP' or 'UDP'."
                )
            if self.source_to_port != ContractFilterPortChoices.PORT_UNSPECIFIED:
                validation_errors["source_to_port"] = _(
                    "Source to-port must be set to 'unspecified' when "
                    "Ethernet Type is not 'IP', 'IPv4', or 'IPv6' or "
                    "IP Protocol is not 'TCP' or 'UDP'."
                )

        # Validate icmp_v4_type for ether_type 'ip', 'ipv4' or 'ipv6'
        # and ip_protocol 'icmp'
        if (
            self.ether_type not in ip_ether_types
            or self.ip_protocol != ContractFilterIPProtocolChoices.PROT_ICMP_V4
        ) and (
            self.icmp_v4_type != ContractFilterICMPv4TypesChoices.ICMP_V4_UNSPECIFIED
        ):
            validation_errors["icmp_v4_type"] = _(
                "ICMPv4 Type must be 'unspecified' when Ethernet Type is "
                "not 'IP', 'IPv4', or 'IPv6' or IP Protocol is not 'ICMP'."
            )

        # Validate icmp_v6_type for ether_type 'ip', 'ipv4' or 'ipv6'
        # and ip_protocol 'icmpv6'
        if (
            self.ether_type not in ip_ether_types
            or self.ip_protocol != ContractFilterIPProtocolChoices.PROT_ICMP_V6
        ) and (
            self.icmp_v6_type != ContractFilterICMPv6TypesChoices.ICMP_V6_UNSPECIFIED
        ):
            validation_errors["icmp_v6_type"] = _(
                "ICMPv6 Type must be 'unspecified' when Ethernet Type is "
                "not 'IP', 'IPv4', or 'IPv6' or IP Protocol is not "
                "'ICMPv6'."
            )

        # Validate match_dscp for ether_type 'ip', 'ipv4' or 'ipv6'
        if (
            self.ether_type not in ip_ether_types
            and self.match_dscp != QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED
        ):
            validation_errors["match_dscp"] = _(
                "Match DSCP must be 'unspecified' when Ethernet Type is not "
                "'IP', 'IPv4', or 'IPv6'."
            )

        # Validate match_only_fragments_enabled for ether_type 'ip', 'ipv4'
        # or 'ipv6'
        if self.ether_type not in ip_ether_types and self.match_only_fragments_enabled:
            validation_errors["match_only_fragments_enabled"] = _(
                "Match only fragments enabled must be false when "
                "Ethernet Type is not 'IP', 'IPv4', or 'IPv6'."
            )

        # Validate stateful_enabled and tcp_rules for ether_type 'ip', 'ipv4'
        # or 'ipv6' and ip_protocol 'tcp'
        if (
            self.ether_type not in ip_ether_types
            or self.ip_protocol != ContractFilterIPProtocolChoices.PROT_TCP
        ):
            if self.stateful_enabled:
                validation_errors["stateful_enabled"] = _(
                    "Stateful enabled must be false when Ethernet Type is "
                    "not 'IP', 'IPv4', or 'IPv6' or IP Protocol is not 'TCP'."
                )
            if self.tcp_rules != default_contract_filter_entry_tcp_rules():
                validation_errors["tcp_rules"] = _(
                    "TCP rules must be 'unspecified' when Ethernet Type is "
                    "not 'IP', 'IPv4', or 'IPv6' or IP Protocol is not 'TCP'."
                )

        if validation_errors:
            raise ValidationError(validation_errors)

    @property
    def aci_tenant(self) -> ACITenant:
        """Return the ACITenant instance of related ACIContractFilter."""
        return self.aci_contract_filter.aci_tenant

    @property
    def parent_object(self) -> ACIBaseModel:
        """Return the parent object of the instance."""
        return self.aci_contract_filter

    def get_destination_from_port_display(self) -> str:
        """Return the associated string representation from the ChoiceSet."""
        destination_from_port_choices = dict(ContractFilterPortChoices)
        return destination_from_port_choices.get(
            self.destination_from_port, self.destination_from_port
        )

    def get_destination_to_port_display(self) -> str:
        """Return the associated string representation from the ChoiceSet."""
        destination_to_port_choices = dict(ContractFilterPortChoices)
        return destination_to_port_choices.get(
            self.destination_to_port, self.destination_to_port
        )

    def get_ip_protocol_display(self) -> str:
        """Return the associated string representation from the ChoiceSet."""
        ip_protocol_choices = dict(ContractFilterIPProtocolChoices)
        return ip_protocol_choices.get(self.ip_protocol, self.ip_protocol)

    def get_source_from_port_display(self) -> str:
        """Return the associated string representation from the ChoiceSet."""
        source_from_port_choices = dict(ContractFilterPortChoices)
        return source_from_port_choices.get(
            self.source_from_port, self.source_from_port
        )

    def get_source_to_port_display(self) -> str:
        """Return the associated string representation from the ChoiceSet."""
        source_to_port_choices = dict(ContractFilterPortChoices)
        return source_to_port_choices.get(self.source_to_port, self.source_to_port)

    def get_tcp_rules_display(self) -> list[str]:
        """Return the associated string representation from the ChoiceSet."""
        tcp_rules_choices = dict(ContractFilterTCPRulesChoices)
        return [tcp_rules_choices.get(rule) for rule in self.tcp_rules]
