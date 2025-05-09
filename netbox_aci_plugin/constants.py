# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db.models import Q

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
