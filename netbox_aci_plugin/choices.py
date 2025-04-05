# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from utilities.choices import ChoiceSet

#
# Choice utilities
#


def add_custom_choice(choices) -> tuple:
    """Add a custom choice to the end of a ChoiceSet."""
    return tuple(choices) + ((None, _("custom")),)


#
# Bridge Domain
#


class BDMultiDestinationFloodingChoices(ChoiceSet):
    """Choice set of Bridge Domain multi destination flooding."""

    # default "bd-flood"
    FLOOD_BD = "bd-flood"
    FLOOD_ENCAP = "encap-flood"
    FLOOD_DROP = "drop"

    CHOICES = (
        (FLOOD_BD, _("bd-flood"), "blue"),
        (FLOOD_ENCAP, _("encap-flood"), "yellow"),
        (FLOOD_DROP, _("drop"), "red"),
    )


class BDUnknownMulticastChoices(ChoiceSet):
    """Choice set of Bridge Domain unknown multicast forwarding method."""

    # default "flood"
    UNKNOWN_MULTI_FLOOD = "flood"
    UNKNOWN_MULTI_OPT_FLOOD = "opt-flood"

    CHOICES = (
        (UNKNOWN_MULTI_FLOOD, _("flood"), "yellow"),
        (UNKNOWN_MULTI_OPT_FLOOD, _("opt-flood"), "blue"),
    )


class BDUnknownUnicastChoices(ChoiceSet):
    """Choice set of Bridge Domain unknown unicast forwarding method."""

    # default "proxy"
    UNKNOWN_UNI_PROXY = "proxy"
    UNKNOWN_UNI_FLOOD = "flood"

    CHOICES = (
        (UNKNOWN_UNI_PROXY, _("proxy"), "blue"),
        (UNKNOWN_UNI_FLOOD, _("flood"), "yellow"),
    )


#
# Contract Filter
#


class ContractFilterARPOpenPeripheralCodesChoices(ChoiceSet):
    """Choice set of Contract Filter ARP open peripheral codes."""

    # default "unspecified"
    OPC_UNSPECIFIED = "unspecified"
    OPC_REQUEST = "req"
    OPC_REPLY = "reply"

    CHOICES = (
        (OPC_UNSPECIFIED, _("unspecified")),
        (OPC_REQUEST, _("ARP Request")),
        (OPC_REPLY, _("ARP Reply")),
    )


class ContractFilterEtherTypeChoices(ChoiceSet):
    """Choice set of Contract Filter ether types."""

    # default "unspecified"
    TYPE_UNSPECIFIED = "unspecified"
    TYPE_ARP = "arp"
    TYPE_FCOE = "fcoe"
    TYPE_IP = "ip"
    TYPE_IPV4 = "ipv4"
    TYPE_IPV6 = "ipv6"
    TYPE_MAC_SEC = "mac_security"
    TYPE_MPLS_UCAST = "mpls_ucast"
    TYPE_TRILL = "trill"

    CHOICES = (
        (TYPE_UNSPECIFIED, _("unspecified")),
        (TYPE_ARP, _("ARP")),
        (TYPE_FCOE, _("FCOE")),
        (TYPE_IP, _("IP")),
        (TYPE_IPV4, _("IPv4")),
        (TYPE_IPV6, _("IPv6")),
        (TYPE_MAC_SEC, _("MAC Security")),
        (TYPE_MPLS_UCAST, _("MPLS Unicast")),
        (TYPE_TRILL, _("Trill")),
    )


class ContractFilterICMPv4TypesChoices(ChoiceSet):
    """Choice set of Contract Filter ICMPv4 message types."""

    # default "unspecified"
    ICMP_V4_UNSPECIFIED = "unspecified"
    ICMP_V4_DST_UNREACHABLE = "dst-unreach"
    ICMP_V4_ECHO_REQUEST = "echo"
    ICMP_V4_ECHO_REPLY = "echo-rep"
    ICMP_V4_SRC_QUENCH = "src-quench"
    ICMP_V4_TIME_EXCEEDED = "time-exceeded"

    CHOICES = (
        (ICMP_V4_UNSPECIFIED, _("unspecified")),
        (ICMP_V4_DST_UNREACHABLE, _("destination unreachable")),
        (ICMP_V4_ECHO_REQUEST, _("echo request")),
        (ICMP_V4_ECHO_REPLY, _("echo reply")),
        (ICMP_V4_SRC_QUENCH, _("source quench")),
        (ICMP_V4_TIME_EXCEEDED, _("time exceeded")),
    )


class ContractFilterICMPv6TypesChoices(ChoiceSet):
    """Choice set of Contract Filter ICMPv6 message types."""

    # default "unspecified"
    ICMP_V6_UNSPECIFIED = "unspecified"
    ICMP_V6_DST_UNREACHABLE = "dst-unreach"
    ICMP_V6_ECHO_REQUEST = "echo-req"
    ICMP_V6_ECHO_REPLY = "echo-rep"
    ICMP_V6_NBR_ADVERT = "nbr-advert"
    ICMP_V6_NBR_SOLICIT = "nbr-solicit"
    ICMP_V6_TIME_EXCEEDED = "time-exceeded"

    CHOICES = (
        (ICMP_V6_UNSPECIFIED, _("unspecified")),
        (ICMP_V6_DST_UNREACHABLE, _("destination unreachable")),
        (ICMP_V6_ECHO_REQUEST, _("echo request")),
        (ICMP_V6_ECHO_REPLY, _("echo reply")),
        (ICMP_V6_NBR_ADVERT, _("neighbor advertisement")),
        (ICMP_V6_NBR_SOLICIT, _("neighbor solicitation")),
        (ICMP_V6_TIME_EXCEEDED, _("time exceeded")),
    )


class ContractFilterIPProtocolChoices(ChoiceSet):
    """Choice set of Contract Filter IP protocols."""

    # default "unspecified"
    PROT_UNSPECIFIED = "unspecified"
    PROT_EGP = "egp"
    PROT_EIGRP = "eigrp"
    PROT_ICMP_V4 = "icmp"
    PROT_ICMP_V6 = "icmpv6"
    PROT_IGMP = "igmp"
    PROT_IGP = "igp"
    PROT_L2TP = "l2tp"
    PROT_OSPF = "ospfigp"
    PROT_PIM = "pim"
    PROT_TCP = "tcp"
    PROT_UDP = "udp"

    CHOICES = (
        (PROT_UNSPECIFIED, _("unspecified")),
        (PROT_EGP, _("EGP")),
        (PROT_EIGRP, _("EIGRP")),
        (PROT_ICMP_V4, _("ICMPv4")),
        (PROT_ICMP_V6, _("ICMPv6")),
        (PROT_IGMP, _("IGMP")),
        (PROT_IGP, _("IGP")),
        (PROT_L2TP, _("L2TP")),
        (PROT_OSPF, _("OSPF")),
        (PROT_PIM, _("PIM")),
        (PROT_TCP, _("TCP")),
        (PROT_UDP, _("UDP")),
    )


class ContractFilterPortChoices(ChoiceSet):
    """Choice set of Contract Filter ports."""

    # default "unspecified"
    PORT_UNSPECIFIED = "unspecified"
    PORT_DNS = "dns"
    PORT_FTP_DATA = "ftpData"
    PORT_HTTP = "http"
    PORT_HTTPS = "https"
    PORT_POP3 = "pop3"
    PORT_RTSP = "rtsp"
    PORT_SMTP = "smtp"
    PORT_SSH = "ssh"

    CHOICES = (
        (PORT_UNSPECIFIED, _("unspecified")),
        (PORT_DNS, _("DNS")),
        (PORT_FTP_DATA, _("FTP Data")),
        (PORT_HTTP, _("HTTP")),
        (PORT_HTTPS, _("HTTPS")),
        (PORT_POP3, _("POP3")),
        (PORT_RTSP, _("RTSP")),
        (PORT_SMTP, _("SMTP")),
        (PORT_SSH, _("SSH")),
    )


class ContractFilterTCPRulesChoices(ChoiceSet):
    """Choice set of Contract Filter TCP rules."""

    # default "unspecified"
    TCP_UNSPECIFIED = "unspecified"
    TCP_ACK = "ack"
    TCP_ESTABLISHED = "est"
    TCP_FINISH = "fin"
    TCP_RESET = "rst"
    TCP_SYN = "syn"

    CHOICES = (
        (TCP_UNSPECIFIED, _("unspecified")),
        (TCP_ACK, _("acknowledgment")),
        (TCP_ESTABLISHED, _("established")),
        (TCP_FINISH, _("finish")),
        (TCP_RESET, _("reset")),
        (TCP_SYN, _("synchronize")),
    )


#
# Contract
#


class ContractScopeChoices(ChoiceSet):
    """Choice set of Contract scopes."""

    # default "context"
    SCOPE_VRF = "context"
    SCOPE_APP_PROFILE = "application-profile"
    SCOPE_TENANT = "tenant"
    SCOPE_GLOBAL = "global"

    CHOICES = (
        (SCOPE_VRF, _("VRF (Context)"), "blue"),
        (SCOPE_APP_PROFILE, _("Application Profile"), "green"),
        (SCOPE_TENANT, _("Tenant"), "orange"),
        (SCOPE_GLOBAL, _("Global"), "red"),
    )


#
# Contract Relation
#


class ContractRelationRoleChoices(ChoiceSet):
    """Choice set of Contract Relation roles."""

    # default "provider"
    ROLE_PROVIDER = "prov"
    ROLE_CONSUMER = "cons"

    CHOICES = (
        (ROLE_PROVIDER, _("Provider"), "blue"),
        (ROLE_CONSUMER, _("Consumer"), "yellow"),
    )


#
# Contract Subject Filter
#


class ContractSubjectFilterActionChoices(ChoiceSet):
    """Choice set of Contract Subject Filter actions."""

    # default "permit"
    ACTION_PERMIT = "permit"
    ACTION_DENY = "deny"

    CHOICES = (
        (ACTION_PERMIT, _("permit"), "green"),
        (ACTION_DENY, _("deny"), "red"),
    )


class ContractSubjectFilterApplyDirectionChoices(ChoiceSet):
    """Choice set of Contract Subject Filter apply directions."""

    # default "both"
    DIR_BOTH = "both"
    DIR_CONS_TO_PROV = "ctp"
    DIR_PROV_TO_CONS = "ptc"

    CHOICES = (
        (DIR_BOTH, _("both"), "green"),
        (DIR_CONS_TO_PROV, _("Consumer to Provider"), "blue"),
        (DIR_PROV_TO_CONS, _("Provider to Consumer"), "yellow"),
    )


class ContractSubjectFilterPriorityChoices(ChoiceSet):
    """Choice set of Quality of Service (QoS) classes."""

    # default "default"
    CLASS_DEFAULT = "default"
    CLASS_LEVEL_1 = "level1"
    CLASS_LEVEL_2 = "level2"
    CLASS_LEVEL_3 = "level3"

    CHOICES = (
        (CLASS_DEFAULT, _("default level"), "gray"),
        (CLASS_LEVEL_1, _("lowest priority"), "red"),
        (CLASS_LEVEL_2, _("medium priority"), "orange"),
        (CLASS_LEVEL_3, _("highest priority"), "yellow"),
    )


#
# Quality of Service (QoS)
#


class QualityOfServiceClassChoices(ChoiceSet):
    """Choice set of Quality of Service (QoS) classes."""

    # default "unspecified"
    CLASS_UNSPECIFIED = "unspecified"
    CLASS_LEVEL_1 = "level1"
    CLASS_LEVEL_2 = "level2"
    CLASS_LEVEL_3 = "level3"
    CLASS_LEVEL_4 = "level4"
    CLASS_LEVEL_5 = "level5"
    CLASS_LEVEL_6 = "level6"

    CHOICES = (
        (CLASS_UNSPECIFIED, _("unspecified"), "gray"),
        (CLASS_LEVEL_1, _("level 1"), "red"),
        (CLASS_LEVEL_2, _("level 2"), "orange"),
        (CLASS_LEVEL_3, _("level 3"), "yellow"),
        (CLASS_LEVEL_4, _("level 4"), "teal"),
        (CLASS_LEVEL_5, _("level 5"), "cyan"),
        (CLASS_LEVEL_6, _("level 6"), "blue"),
    )


class QualityOfServiceDSCPChoices(ChoiceSet):
    """Choice set of Quality of Service (QoS) DSCP values."""

    # default "unspecified"
    DSCP_UNSPECIFIED = "unspecified"
    DSCP_AF11 = "AF11"
    DSCP_AF12 = "AF12"
    DSCP_AF13 = "AF13"
    DSCP_AF21 = "AF21"
    DSCP_AF22 = "AF22"
    DSCP_AF23 = "AF23"
    DSCP_AF31 = "AF31"
    DSCP_AF32 = "AF32"
    DSCP_AF33 = "AF33"
    DSCP_AF41 = "AF41"
    DSCP_AF42 = "AF42"
    DSCP_AF43 = "AF43"
    DSCP_CS0 = "CS0"
    DSCP_CS1 = "CS1"
    DSCP_CS2 = "CS2"
    DSCP_CS3 = "CS3"
    DSCP_CS4 = "CS4"
    DSCP_CS5 = "CS5"
    DSCP_CS6 = "CS6"
    DSCP_CS7 = "CS7"
    DSCP_EF = "EF"
    DSCP_VA = "VA"

    CHOICES = (
        (DSCP_UNSPECIFIED, _("unspecified")),
        (DSCP_AF11, _("AF11 low drop")),
        (DSCP_AF12, _("AF11 medium drop")),
        (DSCP_AF13, _("AF12 high drop")),
        (DSCP_AF21, _("AF21 low drop")),
        (DSCP_AF22, _("AF22 medium drop")),
        (DSCP_AF23, _("AF23 high drop")),
        (DSCP_AF31, _("AF31 low drop")),
        (DSCP_AF32, _("AF32 medium drop")),
        (DSCP_AF33, _("AF33 high drop")),
        (DSCP_AF41, _("AF41 low drop")),
        (DSCP_AF42, _("AF42 medium drop")),
        (DSCP_AF43, _("AF43 high drop")),
        (DSCP_CS0, _("CS0 (best effort)")),
        (DSCP_CS1, _("CS1 (streaming)")),
        (DSCP_CS2, _("CS2 (OAM)")),
        (DSCP_CS3, _("CS3 (signaling)")),
        (DSCP_CS4, _("CS4 (policy plane, priority queue)")),
        (DSCP_CS5, _("CS5 (broadcast video)")),
        (DSCP_CS6, _("CS6 (network control)")),
        (DSCP_CS7, _("CS7")),
        (DSCP_EF, _("EF (Expedited Forwarding, low-loss, low-latency)")),
        (DSCP_VA, _("VA (Voice Admit)")),
    )


#
# uSeg EPG
#


class USegAttributeMatchOperatorChoices(ChoiceSet):
    """Choice set of uSeg EPG attribute match operator."""

    # default "any"
    MATCH_ANY = "any"
    MATCH_ALL = "all"

    CHOICES = (
        (MATCH_ANY, _("any"), "blue"),
        (MATCH_ALL, _("all"), "yellow"),
    )


#
# uSeg Attribute
#


class USegAttributeTypeChoices(ChoiceSet):
    """Choice set of uSeg EPG attribute type."""

    # default "mac"
    TYPE_MAC = "mac"
    TYPE_IP = "ip"
    TYPE_VM = "vm"

    CHOICES = (
        (TYPE_MAC, _("MAC"), "blue"),
        (TYPE_IP, _("IP"), "teal"),
        (TYPE_VM, _("Virtual Machine"), "yellow"),
    )


#
# VRF
#


class VRFPCEnforcementDirectionChoices(ChoiceSet):
    """Choice set of VRF policy control enforcement direction."""

    # default "ingress"
    DIR_INGRESS = "ingress"
    DIR_EGRESS = "egress"

    CHOICES = (
        (DIR_INGRESS, _("ingress"), "blue"),
        (DIR_EGRESS, _("egress"), "yellow"),
    )


class VRFPCEnforcementPreferenceChoices(ChoiceSet):
    """Choice set of VRF policy control enforcement preference."""

    # default "enforced"
    PREF_ENFORCED = "enforced"
    PREF_UNENFORCED = "unenforced"

    CHOICES = (
        (PREF_ENFORCED, _("enforced"), "green"),
        (PREF_UNENFORCED, _("unenforced"), "red"),
    )
