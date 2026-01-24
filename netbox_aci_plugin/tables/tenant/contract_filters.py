# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns

from ...models.tenant.contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)


class ACIContractFilterTable(NetBoxTable):
    """NetBox table for the ACI Contract Filter model."""

    name = tables.Column(
        verbose_name=_("Contract Filter"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    aci_fabric = tables.Column(
        verbose_name=_("ACI Fabric"),
        accessor="aci_tenant__aci_fabric",
        linkify=True,
    )
    aci_tenant = tables.Column(
        linkify=True,
    )
    nb_tenant = tables.Column(
        linkify=True,
    )
    owner_group = tables.Column(
        accessor="owner__group",
        linkify=True,
        verbose_name=_("Owner Group"),
    )
    owner = tables.Column(
        linkify=True,
        verbose_name=_("Owner"),
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIContractFilter
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "nb_tenant",
            "owner",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "nb_tenant",
            "description",
            "tags",
        )


class ACIContractFilterEntryTable(NetBoxTable):
    """NetBox table for the ACI Contract Filter Entry model."""

    name = tables.Column(
        verbose_name=_("Entry"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    aci_fabric = tables.Column(
        verbose_name=_("ACI Fabric"),
        accessor="aci_contract_filter__aci_tenant__aci_fabric",
        linkify=True,
    )
    aci_tenant = tables.Column(
        verbose_name=_("ACI Tenant"),
        linkify=True,
    )
    aci_contract_filter = tables.Column(
        verbose_name=_("Filter"),
        linkify=True,
    )
    arp_opc = columns.ChoiceFieldColumn(
        verbose_name=_("ARP Flag"),
    )
    destination_from_port = tables.Column(
        verbose_name=_("Dst from"),
    )
    destination_to_port = tables.Column(
        verbose_name=_("Dst to"),
    )
    ether_type = columns.ChoiceFieldColumn(
        verbose_name=_("Ether type"),
    )
    icmp_v4_type = columns.ChoiceFieldColumn(
        verbose_name=_("ICMPv4 type"),
    )
    icmp_v6_type = columns.ChoiceFieldColumn(
        verbose_name=_("ICMPv6 type"),
    )
    ip_protocol = tables.Column(
        verbose_name=_("IP protocol"),
    )
    match_dscp = columns.ChoiceFieldColumn(
        verbose_name=_("Match DSCP"),
    )
    match_only_fragments_enabled = columns.BooleanColumn(
        verbose_name=_("Match only fragments"),
    )
    source_from_port = tables.Column(
        verbose_name=_("Src from"),
    )
    source_to_port = tables.Column(
        verbose_name=_("Src to"),
    )
    stateful_enabled = columns.BooleanColumn(
        verbose_name=_("Stateful"),
    )
    tcp_rules = columns.ArrayColumn(
        verbose_name=_("TCP rules"),
    )
    nb_tenant = tables.Column(
        linkify=True,
    )
    owner_group = tables.Column(
        accessor="owner__group",
        linkify=True,
        verbose_name=_("Owner Group"),
    )
    owner = tables.Column(
        linkify=True,
        verbose_name=_("Owner"),
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIContractFilterEntry
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
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
            "nb_tenant",
            "owner",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "aci_contract_filter",
            "ether_type",
            "arp_opc",
            "ip_protocol",
            "source_from_port",
            "source_to_port",
            "destination_from_port",
            "destination_to_port",
            "stateful_enabled",
            "description",
            "tags",
        )


class ACIContractFilterEntryReducedTable(NetBoxTable):
    """Reduced NetBox table for the ACI Contract Filter Entry model."""

    name = tables.Column(
        verbose_name=_("Entry"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    arp_opc = columns.ChoiceFieldColumn(
        verbose_name=_("ARP Flag"),
    )
    destination_from_port = tables.Column(
        verbose_name=_("Dst from"),
    )
    destination_to_port = tables.Column(
        verbose_name=_("Dst to"),
    )
    ether_type = columns.ChoiceFieldColumn(
        verbose_name=_("Ether"),
    )
    ip_protocol = tables.Column(
        verbose_name=_("IP Prot"),
    )
    match_only_fragments_enabled = columns.BooleanColumn(
        verbose_name=_("Only frag"),
    )
    source_from_port = tables.Column(
        verbose_name=_("Src from"),
    )
    source_to_port = tables.Column(
        verbose_name=_("Src to"),
    )
    stateful_enabled = columns.BooleanColumn(
        verbose_name=_("Stateful"),
    )
    tcp_rules = columns.ArrayColumn(
        verbose_name=_("TCP"),
    )

    class Meta(NetBoxTable.Meta):
        model = ACIContractFilterEntry
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "ether_type",
            "arp_opc",
            "ip_protocol",
            "match_only_fragments_enabled",
            "source_from_port",
            "source_to_port",
            "destination_from_port",
            "destination_to_port",
            "stateful_enabled",
            "tcp_rules",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "ether_type",
            "arp_opc",
            "ip_protocol",
            "match_only_fragments_enabled",
            "source_from_port",
            "source_to_port",
            "destination_from_port",
            "destination_to_port",
            "stateful_enabled",
            "tcp_rules",
        )
