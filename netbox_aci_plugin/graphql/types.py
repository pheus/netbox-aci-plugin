# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated, List, Optional

import strawberry
import strawberry_django
from ipam.graphql.types import IPAddressType, VRFType
from netbox.graphql.types import NetBoxObjectType
from tenancy.graphql.types import TenantType

from ..models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup
from ..models.tenant_contract_filters import ACIContractFilter
from ..models.tenant_networks import (
    ACIVRF,
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)
from ..models.tenants import ACITenant
from .filters import (
    ACIAppProfileFilter,
    ACIBridgeDomainFilter,
    ACIBridgeDomainSubnetFilter,
    ACIContractFilterFilter,
    ACIEndpointGroupFilter,
    ACITenantFilter,
    ACIVRFFilter,
)


@strawberry_django.type(ACITenant, fields="__all__", filters=ACITenantFilter)
class ACITenantType(NetBoxObjectType):
    """GraphQL type definition for ACITenant model."""

    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )


@strawberry_django.type(
    ACIAppProfile, fields="__all__", filters=ACIAppProfileFilter
)
class ACIAppProfileType(NetBoxObjectType):
    """GraphQL type definition for ACIAppProfile model."""

    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )


@strawberry_django.type(ACIVRF, fields="__all__", filters=ACIVRFFilter)
class ACIVRFType(NetBoxObjectType):
    """GraphQL type definition for ACIVRF model."""

    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )
    nb_vrf: Annotated["VRFType", strawberry.lazy("ipam.graphql.types")] | None
    dns_labels: Optional[List[str]]


@strawberry_django.type(
    ACIBridgeDomain, fields="__all__", filters=ACIBridgeDomainFilter
)
class ACIBridgeDomainType(NetBoxObjectType):
    """GraphQL type definition for ACIBridgeDomain model."""

    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    aci_vrf: Annotated[
        "ACIVRFType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )
    dhcp_labels: Optional[List[str]]
    mac_address: Optional[str]
    virtual_mac_address: Optional[str]


@strawberry_django.type(
    ACIBridgeDomainSubnet,
    fields="__all__",
    filters=ACIBridgeDomainSubnetFilter,
)
class ACIBridgeDomainSubnetType(NetBoxObjectType):
    """GraphQL type definition for ACIBridgeDomainSubnet model."""

    aci_bridge_domain: Annotated[
        "ACIBridgeDomainType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    gateway_ip_address: Annotated[
        "IPAddressType", strawberry.lazy("ipam.graphql.types")
    ]
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )


@strawberry_django.type(
    ACIEndpointGroup,
    fields="__all__",
    filters=ACIEndpointGroupFilter,
)
class ACIEndpointGroupType(NetBoxObjectType):
    """GraphQL type definition for ACIEndpointGroup model."""

    aci_app_profile: Annotated[
        "ACIAppProfileType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    aci_bridge_domain: Annotated[
        "ACIBridgeDomainType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )


@strawberry_django.type(
    ACIContractFilter,
    fields="__all__",
    filters=ACIContractFilterFilter,
)
class ACIContractFilterType(NetBoxObjectType):
    """GraphQL type definition for ACIContractFilter model."""

    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )
