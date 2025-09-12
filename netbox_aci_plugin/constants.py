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

#
# Contract Relation
#

# Contract relation to possible ACI object types
CONTRACT_RELATION_OBJECT_TYPES = Q(
    app_label="netbox_aci_plugin",
    model__in=(
        "aciendpointgroup",
        "aciendpointsecuritygroup",
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
