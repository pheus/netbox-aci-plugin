# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the tenant ACI Contract Filter models."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = (
    "ACIContractFilterEntryARPPanel",
    "ACIContractFilterEntryEthernetPanel",
    "ACIContractFilterEntryICMPPanel",
    "ACIContractFilterEntryIPProtocolPanel",
    "ACIContractFilterEntryPanel",
    "ACIContractFilterEntryPortRangePanel",
    "ACIContractFilterEntryTCPPanel",
    "ACIContractFilterPanel",
)


class ACIContractFilterPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Contract Filter detail view."""

    title = _("ACI Contract Filter")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACIContractFilterEntryPanel(panels.ObjectAttributesPanel):
    """Identity attribute panel for the ACI Contract Filter Entry detail view.

    The retired template never rendered a NetBox Tenant row for this
    model, unlike its siblings, so none is declared here either.
    """

    title = _("ACI Contract Filter Entry")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    aci_contract_filter = attrs.RelatedObjectAttr(
        "aci_contract_filter", linkify=True, label=_("ACI Contract Filter")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))


class ACIContractFilterEntryEthernetPanel(panels.ObjectAttributesPanel):
    """Ethernet panel for the ACI Contract Filter Entry detail view."""

    title = _("Ethernet")

    ether_type = attrs.ChoiceAttr("ether_type", label=_("Ether Type"))


class ACIContractFilterEntryARPPanel(panels.ObjectAttributesPanel):
    """ARP attribute panel for the ACI Contract Filter Entry detail view."""

    title = _("Address Resolution Protocol")

    arp_opc = attrs.ChoiceAttr("arp_opc", label=_("ARP Flags"))


class ACIContractFilterEntryIPProtocolPanel(panels.ObjectAttributesPanel):
    """IP protocol panel for the ACI Contract Filter Entry detail view."""

    title = _("IP Protocol")

    ip_protocol = attrs.ChoiceAttr("ip_protocol", label=_("IP Protocol"))
    match_dscp = attrs.ChoiceAttr("match_dscp", label=_("Match DSCP"))
    match_only_fragments_enabled = attrs.BooleanAttr(
        "match_only_fragments_enabled", label=_("Match only fragments")
    )


class ACIContractFilterEntryICMPPanel(panels.ObjectAttributesPanel):
    """ICMP attribute panel for the ACI Contract Filter Entry detail view."""

    title = _("ICMP")

    icmp_v4_type = attrs.ChoiceAttr("icmp_v4_type", label=_("ICMPv4 Type"))
    icmp_v6_type = attrs.ChoiceAttr("icmp_v6_type", label=_("ICMPv6 Type"))


class ACIContractFilterEntryPortRangePanel(panels.ObjectAttributesPanel):
    """Port range panel for the ACI Contract Filter Entry detail view."""

    title = _("TCP/UDP Port range")

    source_from_port = attrs.ChoiceAttr("source_from_port", label=_("Source Port from"))
    source_to_port = attrs.ChoiceAttr("source_to_port", label=_("Source Port to"))
    destination_from_port = attrs.ChoiceAttr(
        "destination_from_port", label=_("Destination Port from")
    )
    destination_to_port = attrs.ChoiceAttr(
        "destination_to_port", label=_("Destination Port to")
    )


class ACIContractFilterEntryTCPPanel(panels.ObjectAttributesPanel):
    """TCP settings panel for the ACI Contract Filter Entry detail view."""

    title = _("TCP settings")

    stateful_enabled = attrs.BooleanAttr("stateful_enabled", label=_("Stateful"))
    tcp_rules = attrs.TextAttr("tcp_rules_display", label=_("Rules"))
