# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import List, Optional

import strawberry_django
from ipam.graphql.types import IPAddressType, VRFType
from netbox.graphql.types import NetBoxObjectType
from tenancy.graphql.types import TenantType

from ..models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup
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
    ACIEndpointGroupFilter,
    ACITenantFilter,
    ACIVRFFilter,
)


@strawberry_django.type(ACITenant, fields="__all__", filters=ACITenantFilter)
class ACITenantType(NetBoxObjectType):
    """GraphQL type definition for ACITenant model."""

    nb_tenant: Optional[TenantType]


@strawberry_django.type(
    ACIAppProfile, fields="__all__", filters=ACIAppProfileFilter
)
class ACIAppProfileType(NetBoxObjectType):
    """GraphQL type definition for ACIAppProfile model."""

    aci_tenant: ACITenantType
    nb_tenant: Optional[TenantType]


@strawberry_django.type(ACIVRF, fields="__all__", filters=ACIVRFFilter)
class ACIVRFType(NetBoxObjectType):
    """GraphQL type definition for ACIVRF model."""

    aci_tenant: ACITenantType
    nb_tenant: Optional[TenantType]
    nb_vrf: Optional[VRFType]
    dns_labels: Optional[List[str]]


@strawberry_django.type(
    ACIBridgeDomain, fields="__all__", filters=ACIBridgeDomainFilter
)
class ACIBridgeDomainType(NetBoxObjectType):
    """GraphQL type definition for ACIBridgeDomain model."""

    aci_vrf: ACIVRFType
    nb_tenant: Optional[TenantType]
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

    aci_bridge_domain: ACIBridgeDomainType
    gateway_ip_address: IPAddressType
    nb_tenant: Optional[TenantType]


@strawberry_django.type(
    ACIEndpointGroup,
    fields="__all__",
    filters=ACIEndpointGroupFilter,
)
class ACIEndpointGroupType(NetBoxObjectType):
    """GraphQL type definition for ACIEndpointGroup model."""

    aci_app_profile: ACIAppProfileType
    aci_bridge_domain: ACIBridgeDomainType
    nb_tenant: Optional[TenantType]
