# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from utilities.choices import Choice, ChoiceSet

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
        Choice(
            FLOOD_BD,
            _("bd-flood"),
            color="blue",
            description=_("Flood in the Bridge Domain"),
        ),
        Choice(
            FLOOD_ENCAP,
            _("encap-flood"),
            color="yellow",
            description=_("Flood only in the ingress encapsulation"),
        ),
        Choice(FLOOD_DROP, _("drop"), color="red", description=_("Drop the traffic")),
    )


class BDUnknownMulticastChoices(ChoiceSet):
    """Choice set of Bridge Domain unknown multicast forwarding method."""

    # default "flood"
    UNKNOWN_MULTI_FLOOD = "flood"
    UNKNOWN_MULTI_OPT_FLOOD = "opt-flood"

    CHOICES = (
        Choice(
            UNKNOWN_MULTI_FLOOD,
            _("flood"),
            color="yellow",
            description=_("Flood to every port in the Bridge Domain"),
        ),
        Choice(
            UNKNOWN_MULTI_OPT_FLOOD,
            _("opt-flood"),
            color="blue",
            description=_("Flood only to ports with multicast receivers"),
        ),
    )


class BDUnknownUnicastChoices(ChoiceSet):
    """Choice set of Bridge Domain unknown unicast forwarding method."""

    # default "proxy"
    UNKNOWN_UNI_PROXY = "proxy"
    UNKNOWN_UNI_FLOOD = "flood"

    CHOICES = (
        Choice(
            UNKNOWN_UNI_PROXY,
            _("proxy"),
            color="blue",
            description=_("Forward to the spine proxy for endpoint lookup"),
        ),
        Choice(
            UNKNOWN_UNI_FLOOD,
            _("flood"),
            color="yellow",
            description=_("Flood in the Bridge Domain"),
        ),
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
        Choice(
            OPC_UNSPECIFIED, _("unspecified"), description=_("Match any ARP operation")
        ),
        Choice(OPC_REQUEST, _("ARP Request")),
        Choice(OPC_REPLY, _("ARP Reply")),
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
        Choice(
            TYPE_UNSPECIFIED, _("unspecified"), description=_("Match any ether type")
        ),
        Choice(TYPE_ARP, _("ARP")),
        Choice(TYPE_FCOE, _("FCOE")),
        Choice(TYPE_IP, _("IP")),
        Choice(TYPE_IPV4, _("IPv4")),
        Choice(TYPE_IPV6, _("IPv6")),
        Choice(TYPE_MAC_SEC, _("MAC Security")),
        Choice(TYPE_MPLS_UCAST, _("MPLS Unicast")),
        Choice(TYPE_TRILL, _("Trill")),
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
        Choice(
            ICMP_V4_UNSPECIFIED,
            _("unspecified"),
            description=_("Match any ICMPv4 message type"),
        ),
        Choice(ICMP_V4_DST_UNREACHABLE, _("destination unreachable")),
        Choice(ICMP_V4_ECHO_REQUEST, _("echo request")),
        Choice(ICMP_V4_ECHO_REPLY, _("echo reply")),
        Choice(ICMP_V4_SRC_QUENCH, _("source quench")),
        Choice(ICMP_V4_TIME_EXCEEDED, _("time exceeded")),
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
        Choice(
            ICMP_V6_UNSPECIFIED,
            _("unspecified"),
            description=_("Match any ICMPv6 message type"),
        ),
        Choice(ICMP_V6_DST_UNREACHABLE, _("destination unreachable")),
        Choice(ICMP_V6_ECHO_REQUEST, _("echo request")),
        Choice(ICMP_V6_ECHO_REPLY, _("echo reply")),
        Choice(ICMP_V6_NBR_ADVERT, _("neighbor advertisement")),
        Choice(ICMP_V6_NBR_SOLICIT, _("neighbor solicitation")),
        Choice(ICMP_V6_TIME_EXCEEDED, _("time exceeded")),
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
        Choice(
            PROT_UNSPECIFIED, _("unspecified"), description=_("Match any IP protocol")
        ),
        Choice(PROT_EGP, _("EGP")),
        Choice(PROT_EIGRP, _("EIGRP")),
        Choice(PROT_ICMP_V4, _("ICMPv4")),
        Choice(PROT_ICMP_V6, _("ICMPv6")),
        Choice(PROT_IGMP, _("IGMP")),
        Choice(PROT_IGP, _("IGP")),
        Choice(PROT_L2TP, _("L2TP")),
        Choice(PROT_OSPF, _("OSPF")),
        Choice(PROT_PIM, _("PIM")),
        Choice(PROT_TCP, _("TCP")),
        Choice(PROT_UDP, _("UDP")),
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
        Choice(PORT_UNSPECIFIED, _("unspecified"), description=_("Match any port")),
        Choice(PORT_DNS, _("DNS"), description=_("Port 53")),
        Choice(PORT_FTP_DATA, _("FTP Data"), description=_("Port 20")),
        Choice(PORT_HTTP, _("HTTP"), description=_("Port 80")),
        Choice(PORT_HTTPS, _("HTTPS"), description=_("Port 443")),
        Choice(PORT_POP3, _("POP3"), description=_("Port 110")),
        Choice(PORT_RTSP, _("RTSP"), description=_("Port 554")),
        Choice(PORT_SMTP, _("SMTP"), description=_("Port 25")),
        Choice(PORT_SSH, _("SSH"), description=_("Port 22")),
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
        Choice(TCP_UNSPECIFIED, _("unspecified"), description=_("Match any TCP flag")),
        Choice(TCP_ACK, _("acknowledgment"), description=_("Acknowledgment flag set")),
        Choice(
            TCP_ESTABLISHED,
            _("established"),
            description=_("Match established sessions"),
        ),
        Choice(TCP_FINISH, _("finish"), description=_("Finish flag set")),
        Choice(TCP_RESET, _("reset"), description=_("Reset flag set")),
        Choice(TCP_SYN, _("synchronize"), description=_("Synchronize flag set")),
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
        Choice(
            SCOPE_VRF,
            _("VRF"),
            color="blue",
            description=_("Applies within the VRF, known as a Context in the APIC"),
        ),
        Choice(
            SCOPE_APP_PROFILE,
            _("Application Profile"),
            color="green",
            description=_("Applies within the Application Profile"),
        ),
        Choice(
            SCOPE_TENANT,
            _("Tenant"),
            color="orange",
            description=_("Applies within the ACI Tenant"),
        ),
        Choice(
            SCOPE_GLOBAL,
            _("Global"),
            color="red",
            description=_("Applies across the whole fabric"),
        ),
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
        Choice(
            ROLE_PROVIDER,
            _("Provider"),
            color="blue",
            description=_("Offers the service the Contract describes"),
        ),
        Choice(
            ROLE_CONSUMER,
            _("Consumer"),
            color="yellow",
            description=_("Uses the service the Contract describes"),
        ),
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
        Choice(
            ACTION_PERMIT,
            _("permit"),
            color="green",
            description=_("Allow matching traffic"),
        ),
        Choice(
            ACTION_DENY, _("deny"), color="red", description=_("Drop matching traffic")
        ),
    )


class ContractSubjectFilterApplyDirectionChoices(ChoiceSet):
    """Choice set of Contract Subject Filter apply directions."""

    # default "both"
    DIR_BOTH = "both"
    DIR_CONS_TO_PROV = "ctp"
    DIR_PROV_TO_CONS = "ptc"

    CHOICES = (
        Choice(
            DIR_BOTH,
            _("both"),
            color="green",
            description=_("Apply in both directions"),
        ),
        Choice(
            DIR_CONS_TO_PROV,
            _("Consumer to Provider"),
            color="blue",
            description=_("Apply only to consumer to provider traffic"),
        ),
        Choice(
            DIR_PROV_TO_CONS,
            _("Provider to Consumer"),
            color="yellow",
            description=_("Apply only to provider to consumer traffic"),
        ),
    )


class ContractSubjectFilterPriorityChoices(ChoiceSet):
    """Choice set of Quality of Service (QoS) classes."""

    # default "default"
    CLASS_DEFAULT = "default"
    CLASS_LEVEL_1 = "level1"
    CLASS_LEVEL_2 = "level2"
    CLASS_LEVEL_3 = "level3"

    CHOICES = (
        Choice(
            CLASS_DEFAULT,
            _("default"),
            color="gray",
            description=_("Default level"),
        ),
        Choice(
            CLASS_LEVEL_1,
            _("level 1"),
            color="red",
            description=_("Lowest priority"),
        ),
        Choice(
            CLASS_LEVEL_2,
            _("level 2"),
            color="orange",
            description=_("Medium priority"),
        ),
        Choice(
            CLASS_LEVEL_3,
            _("level 3"),
            color="yellow",
            description=_("Highest priority"),
        ),
    )


#
# Endpoint Group Domain Binding
#


class DeploymentImmediacyChoices(ChoiceSet):
    """Choice set of ACI deployment immediacy."""

    # default "lazy"
    IMMEDIACY_IMMEDIATE = "immediate"
    IMMEDIACY_LAZY = "lazy"

    CHOICES = (
        Choice(
            IMMEDIACY_IMMEDIATE,
            _("Immediate"),
            color="green",
            description=_("Program the policy in hardware as soon as it is downloaded"),
        ),
        Choice(
            IMMEDIACY_LAZY,
            _("On Demand"),
            color="orange",
            description=_("Program the policy in hardware on the first packet"),
        ),
    )


class PortModeChoices(ChoiceSet):
    """Choice set of ACI port encapsulation modes."""

    # default "regular"
    MODE_REGULAR = "regular"
    MODE_NATIVE = "native"
    MODE_UNTAGGED = "untagged"

    CHOICES = (
        Choice(
            MODE_REGULAR,
            _("Trunk"),
            color="blue",
            description=_("Tagged with the VLAN encapsulation"),
        ),
        Choice(
            MODE_NATIVE,
            _("Access (802.1P)"),
            color="purple",
            description=_("Untagged on ingress and priority tagged on egress"),
        ),
        Choice(
            MODE_UNTAGGED,
            _("Access (untagged)"),
            color="gray",
            description=_("Untagged in both directions"),
        ),
    )


class ResolutionImmediacyChoices(ChoiceSet):
    """Choice set of ACI resolution immediacy."""

    # default "lazy"
    IMMEDIACY_IMMEDIATE = "immediate"
    IMMEDIACY_LAZY = "lazy"
    IMMEDIACY_PRE_PROVISION = "pre-provision"

    CHOICES = (
        Choice(
            IMMEDIACY_IMMEDIATE,
            _("Immediate"),
            color="green",
            description=_("Download the policy when the domain is attached"),
        ),
        Choice(
            IMMEDIACY_LAZY,
            _("On Demand"),
            color="orange",
            description=_("Download the policy only when an endpoint attaches"),
        ),
        Choice(
            IMMEDIACY_PRE_PROVISION,
            _("Pre-provision"),
            color="blue",
            description=_("Download the policy before any endpoint attaches"),
        ),
    )


#
# Node
#


class NodeRoleChoices(ChoiceSet):
    """Choice set of Node roles."""

    # default "leaf"
    ROLE_LEAF = "leaf"
    ROLE_SPINE = "spine"
    ROLE_APIC = "apic"

    CHOICES = (
        Choice(
            ROLE_LEAF,
            _("Leaf"),
            color="blue",
            description=_("Access layer switch that endpoints attach to"),
        ),
        Choice(
            ROLE_SPINE,
            _("Spine"),
            color="teal",
            description=_("Backbone switch connecting the leaf switches"),
        ),
        Choice(
            ROLE_APIC,
            _("APIC"),
            color="purple",
            description=_("Controller managing the fabric"),
        ),
    )


class NodeTypeChoices(ChoiceSet):
    """Choice set of Node types."""

    # default "unknown"
    TYPE_UNKNOWN = "unknown"
    TYPE_TIER_2_LEAF = "tier-2-leaf"
    TYPE_REMOTE_LEAF_WAN = "remote-leaf-wan"
    TYPE_VIRTUAL = "virtual"

    CHOICES = (
        Choice(
            TYPE_UNKNOWN,
            _("Unknown"),
            color="gray",
            description=_("Standard node with no special deployment type"),
        ),
        Choice(
            TYPE_TIER_2_LEAF,
            _("Tier 2 Leaf"),
            color="blue",
            description=_("Leaf attached to another leaf rather than a spine"),
        ),
        Choice(
            TYPE_REMOTE_LEAF_WAN,
            _("Remote Leaf WAN"),
            color="teal",
            description=_("Leaf connected to the fabric across a WAN"),
        ),
        Choice(
            TYPE_VIRTUAL,
            _("Virtual"),
            color="purple",
            description=_("Leaf running as a software instance"),
        ),
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
        Choice(
            CLASS_UNSPECIFIED,
            _("unspecified"),
            color="gray",
            description=_("Use the default QoS class"),
        ),
        Choice(CLASS_LEVEL_1, _("level 1"), color="red"),
        Choice(CLASS_LEVEL_2, _("level 2"), color="orange"),
        Choice(CLASS_LEVEL_3, _("level 3"), color="yellow"),
        Choice(CLASS_LEVEL_4, _("level 4"), color="teal"),
        Choice(CLASS_LEVEL_5, _("level 5"), color="cyan"),
        Choice(CLASS_LEVEL_6, _("level 6"), color="blue"),
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
        Choice(
            DSCP_UNSPECIFIED,
            _("unspecified"),
            description=_("Do not rewrite the DSCP value"),
        ),
        Choice(
            DSCP_AF11,
            _("AF11"),
            description=_("Assured Forwarding class 1, low drop probability"),
        ),
        Choice(
            DSCP_AF12,
            _("AF12"),
            description=_("Assured Forwarding class 1, medium drop probability"),
        ),
        Choice(
            DSCP_AF13,
            _("AF13"),
            description=_("Assured Forwarding class 1, high drop probability"),
        ),
        Choice(
            DSCP_AF21,
            _("AF21"),
            description=_("Assured Forwarding class 2, low drop probability"),
        ),
        Choice(
            DSCP_AF22,
            _("AF22"),
            description=_("Assured Forwarding class 2, medium drop probability"),
        ),
        Choice(
            DSCP_AF23,
            _("AF23"),
            description=_("Assured Forwarding class 2, high drop probability"),
        ),
        Choice(
            DSCP_AF31,
            _("AF31"),
            description=_("Assured Forwarding class 3, low drop probability"),
        ),
        Choice(
            DSCP_AF32,
            _("AF32"),
            description=_("Assured Forwarding class 3, medium drop probability"),
        ),
        Choice(
            DSCP_AF33,
            _("AF33"),
            description=_("Assured Forwarding class 3, high drop probability"),
        ),
        Choice(
            DSCP_AF41,
            _("AF41"),
            description=_("Assured Forwarding class 4, low drop probability"),
        ),
        Choice(
            DSCP_AF42,
            _("AF42"),
            description=_("Assured Forwarding class 4, medium drop probability"),
        ),
        Choice(
            DSCP_AF43,
            _("AF43"),
            description=_("Assured Forwarding class 4, high drop probability"),
        ),
        Choice(
            DSCP_CS0,
            _("CS0"),
            description=_("Class Selector 0, best effort"),
        ),
        Choice(
            DSCP_CS1,
            _("CS1"),
            description=_("Class Selector 1, streaming"),
        ),
        Choice(
            DSCP_CS2,
            _("CS2"),
            description=_("Class Selector 2, OAM"),
        ),
        Choice(
            DSCP_CS3,
            _("CS3"),
            description=_("Class Selector 3, signaling"),
        ),
        Choice(
            DSCP_CS4,
            _("CS4"),
            description=_("Class Selector 4, policy plane and priority queue"),
        ),
        Choice(
            DSCP_CS5,
            _("CS5"),
            description=_("Class Selector 5, broadcast video"),
        ),
        Choice(
            DSCP_CS6,
            _("CS6"),
            description=_("Class Selector 6, network control"),
        ),
        Choice(
            DSCP_CS7,
            _("CS7"),
            description=_("Class Selector 7, reserved"),
        ),
        Choice(
            DSCP_EF,
            _("EF"),
            description=_("Expedited Forwarding, low loss and low latency"),
        ),
        Choice(DSCP_VA, _("VA"), description=_("Voice Admit")),
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
        Choice(
            MATCH_ANY,
            _("any"),
            color="blue",
            description=_("An endpoint matches if any attribute matches"),
        ),
        Choice(
            MATCH_ALL,
            _("all"),
            color="yellow",
            description=_("An endpoint matches only if every attribute matches"),
        ),
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
        Choice(
            TYPE_MAC,
            _("MAC"),
            color="blue",
            description=_("Match endpoints by MAC address"),
        ),
        Choice(
            TYPE_IP,
            _("IP"),
            color="teal",
            description=_("Match endpoints by IP address or subnet"),
        ),
        Choice(
            TYPE_VM,
            _("Virtual Machine"),
            color="yellow",
            description=_("Match endpoints by virtual machine attribute"),
        ),
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
        Choice(
            DIR_INGRESS,
            _("ingress"),
            color="blue",
            description=_("Apply the policy on the ingress leaf"),
        ),
        Choice(
            DIR_EGRESS,
            _("egress"),
            color="yellow",
            description=_("Apply the policy on the egress leaf"),
        ),
    )


class VRFPCEnforcementPreferenceChoices(ChoiceSet):
    """Choice set of VRF policy control enforcement preference."""

    # default "enforced"
    PREF_ENFORCED = "enforced"
    PREF_UNENFORCED = "unenforced"

    CHOICES = (
        Choice(
            PREF_ENFORCED,
            _("enforced"),
            color="green",
            description=_("Contracts are required between Endpoint Groups"),
        ),
        Choice(
            PREF_UNENFORCED,
            _("unenforced"),
            color="red",
            description=_("Traffic flows without a Contract"),
        ),
    )


#
# VLAN Pool
#


class VLANAllocationModeChoices(ChoiceSet):
    """Choice set of VLAN pool allocation modes."""

    # default "static"
    MODE_STATIC = "static"
    MODE_DYNAMIC = "dynamic"

    CHOICES = (
        Choice(
            MODE_STATIC,
            _("static"),
            color="blue",
            description=_("VLAN IDs are assigned manually"),
        ),
        Choice(
            MODE_DYNAMIC,
            _("dynamic"),
            color="green",
            description=_("VLAN IDs are assigned by the APIC"),
        ),
    )


class VLANPoolRangeAllocationModeChoices(ChoiceSet):
    """Choice set of VLAN pool range allocation modes."""

    # default "inherit"
    MODE_INHERIT = "inherit"
    MODE_STATIC = "static"
    MODE_DYNAMIC = "dynamic"

    CHOICES = (
        Choice(
            MODE_INHERIT,
            _("inherit"),
            color="gray",
            description=_("Follow the allocation mode of the parent VLAN Pool"),
        ),
        Choice(
            MODE_STATIC,
            _("static"),
            color="blue",
            description=_("VLAN IDs are assigned manually"),
        ),
        Choice(
            MODE_DYNAMIC,
            _("dynamic"),
            color="green",
            description=_("VLAN IDs are assigned by the APIC"),
        ),
    )


class VLANPoolRangeRoleChoices(ChoiceSet):
    """Choice set of VLAN pool range roles."""

    # default "external"
    ROLE_EXTERNAL = "external"
    ROLE_INTERNAL = "internal"

    CHOICES = (
        Choice(
            ROLE_EXTERNAL,
            _("external"),
            color="blue",
            description=_("Encapsulation used on the wire"),
        ),
        Choice(
            ROLE_INTERNAL,
            _("internal"),
            color="purple",
            description=_("Encapsulation used internally by a VMM domain"),
        ),
    )


#
# Leaf Interface Policy Group
#


class LeafInterfacePolicyGroupTypeChoices(ChoiceSet):
    """Choice set of Leaf Interface Policy Group types."""

    # No default. The type is required and immutable after creation.
    TYPE_ACCESS = "access"
    TYPE_PC = "pc"
    TYPE_VPC = "vpc"

    CHOICES = (
        Choice(
            TYPE_ACCESS,
            _("Access"),
            color="blue",
            description=_("Single interface per leaf"),
        ),
        Choice(
            TYPE_PC,
            _("Port Channel"),
            color="cyan",
            description=_("Bundled interfaces on one leaf"),
        ),
        Choice(
            TYPE_VPC,
            _("Virtual Port Channel"),
            color="purple",
            description=_("Bundled interfaces across a leaf pair"),
        ),
    )
