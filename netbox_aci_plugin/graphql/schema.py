# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later
from typing import List

import strawberry
import strawberry_django

from ..models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup
from ..models.tenant_networks import (
    ACIVRF,
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)
from ..models.tenants import ACITenant
from .types import (
    ACIAppProfileType,
    ACIBridgeDomainSubnetType,
    ACIBridgeDomainType,
    ACIEndpointGroupType,
    ACITenantType,
    ACIVRFType,
)


@strawberry.type
class ACITenantsQuery:
    """GraphQL query definition for ACITenant model."""

    aci_tenant_list: List[ACITenantType] = strawberry_django.field()

    @strawberry.field
    def aci_tenant(self, id: int) -> ACITenantType:
        return ACITenant.objects.get(pk=id)


@strawberry.type
class ACIAppProfilesQuery:
    """GraphQL query definition for ACIAppProfile model."""

    aci_application_profile_list: List[ACIAppProfileType] = (
        strawberry_django.field()
    )

    @strawberry.field
    def aci_application_profile(self, id: int) -> ACIAppProfileType:
        return ACIAppProfile.objects.get(pk=id)


@strawberry.type
class ACIVRFQuery:
    """GraphQL query definition for ACIVRF model."""

    aci_vrf_list: List[ACIVRFType] = strawberry_django.field()

    @strawberry.field
    def aci_vrf(self, id: int) -> ACIVRFType:
        return ACIVRF.objects.get(pk=id)


@strawberry.type
class ACIBridgeDomainQuery:
    """GraphQL query definition for ACIBridgeDomain model."""

    aci_bridge_domain_list: List[ACIBridgeDomainType] = (
        strawberry_django.field()
    )

    @strawberry.field
    def aci_bridge_domain(self, id: int) -> ACIBridgeDomainType:
        return ACIBridgeDomain.objects.get(pk=id)


@strawberry.type
class ACIBridgeDomainSubnetQuery:
    """GraphQL query definition for ACIBridgeDomainSubnet model."""

    aci_bridge_domain_subnet_list: List[ACIBridgeDomainSubnetType] = (
        strawberry_django.field()
    )

    @strawberry.field
    def aci_bridge_domain_subnet(self, id: int) -> ACIBridgeDomainSubnetType:
        return ACIBridgeDomainSubnet.objects.get(pk=id)


@strawberry.type
class ACIEndpointGroupQuery:
    """GraphQL query definition for ACIEndpointGroup model."""

    aci_endpoint_group_list: List[ACIEndpointGroupType] = (
        strawberry_django.field()
    )

    @strawberry.field
    def aci_endpoint_group(self, id: int) -> ACIEndpointGroupType:
        return ACIEndpointGroup.objects.get(pk=id)


schema: list = [
    ACITenantsQuery,
    ACIAppProfilesQuery,
    ACIBridgeDomainQuery,
    ACIBridgeDomainSubnetQuery,
    ACIEndpointGroupQuery,
    ACIVRFQuery,
]
