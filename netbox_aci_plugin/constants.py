# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Final

from django.db.models import Q

#
# Validation
#

ACI_NAME_MAX_LEN: Final[int] = 64
ACI_DESC_MAX_LEN: Final[int] = 128

NAME_CHAR_CLASS: Final[str] = r"[A-Za-z0-9_.:-]"
DESC_CHAR_CLASS: Final[str] = r"[A-Za-z0-9!#$%()*,-./:;@ _{|}~?&+]"

VLAN_VID_MIN: Final[int] = 1
VLAN_VID_MAX: Final[int] = 4094

FABRIC_ID_MIN: Final[int] = 1
FABRIC_ID_MAX: Final[int] = 128

POD_ID_MIN: Final[int] = 1
POD_ID_MAX: Final[int] = 255

NODE_ID_MIN: Final[int] = 1
NODE_ID_MAX: Final[int] = 4000

# ACI Nodes reserve 1-100 for APIC controllers, so Leaf Nodes start at 101
LEAF_NODE_ID_MIN: Final[int] = 101

NODE_INTERFACE_MODULE_MIN: Final[int] = 1
NODE_INTERFACE_MODULE_MAX: Final[int] = 255
NODE_INTERFACE_PORT_MIN: Final[int] = 1
NODE_INTERFACE_PORT_MAX: Final[int] = 127
NODE_INTERFACE_SUB_PORT_NONE: Final[int] = 0
NODE_INTERFACE_SUB_PORT_MAX: Final[int] = 64

VPC_LOGICAL_PAIR_ID_MIN: Final[int] = 1
VPC_LOGICAL_PAIR_ID_MAX: Final[int] = 1000

#
# Contract Relation
#

# Contract relation to possible ACI object types
CONTRACT_RELATION_OBJECT_TYPES = Q(
    app_label="netbox_aci_plugin",
    model__in=(
        "aciendpointgroup",
        "aciendpointsecuritygroup",
        "aciexternalendpointgroup",
        "aciusegendpointgroup",
        "acivrf",
    ),
)


#
# Endpoint Security Group
#

# Endpoint Group (EPG) Selectors
ESG_ENDPOINT_GROUP_SELECTORS_MODELS = Q(
    Q(
        app_label="netbox_aci_plugin",
        model__in=(
            "aciendpointgroup",
            "aciusegendpointgroup",
        ),
    )
)

# IP Subnet Selectors
ESG_ENDPOINT_SELECTORS_MODELS = Q(
    Q(
        app_label="ipam",
        model__in=(
            "prefix",
            "ipaddress",
        ),
    )
)


#
# uSeg Endpoint Group Attributes
#

# Network Attributes
USEG_NETWORK_ATTRIBUTES_MODELS = Q(
    Q(
        app_label="ipam",
        model__in=(
            "prefix",
            "ipaddress",
        ),
    )
    | Q(app_label="dcim", model="macaddress")
)

#
# Node
#

# Node assignment to possible object types
NODE_OBJECT_TYPES = Q(
    Q(app_label="dcim", model="device")
    | Q(app_label="virtualization", model="virtualmachine")
)


#
# AAEP Domain Binding
#

# AAEP domain binding to possible ACI domain object types
AAEP_DOMAIN_OBJECT_TYPES = Q(
    app_label="netbox_aci_plugin",
    model__in=(
        "aciphysicaldomain",
        "acirouteddomain",
    ),
)


#
# Endpoint Group Domain Binding
#

# EPG domain binding to possible ACI endpoint group object types
EPG_DOMAIN_BINDING_EPG_OBJECT_TYPES = Q(
    app_label="netbox_aci_plugin",
    model__in=(
        "aciendpointgroup",
        "aciusegendpointgroup",
    ),
)

# EPG domain binding to possible ACI domain object types
# (excludes acirouteddomain: L3 domains associate to L3Outs, not EPGs;
# add acivmmdomain when VMM domains ship)
EPG_DOMAIN_BINDING_DOMAIN_OBJECT_TYPES = Q(
    app_label="netbox_aci_plugin",
    model__in=("aciphysicaldomain",),
)
