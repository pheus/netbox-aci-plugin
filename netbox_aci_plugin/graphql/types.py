# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated, List, Optional

import strawberry
import strawberry_django
from ipam.graphql.types import IPAddressType, VRFType
from netbox.graphql.types import NetBoxObjectType
from tenancy.graphql.types import TenantType

from .. import models
from .filters import (
    ACIAppProfileFilter,
    ACIBridgeDomainFilter,
    ACIBridgeDomainSubnetFilter,
    ACIContractFilter,
    ACIContractFilterEntryFilter,
    ACIContractFilterFilter,
    ACIContractSubjectFilter,
    ACIContractSubjectFilterFilter,
    ACIEndpointGroupFilter,
    ACITenantFilter,
    ACIVRFFilter,
)


@strawberry_django.type(
    models.ACITenant, fields="__all__", filters=ACITenantFilter
)
class ACITenantType(NetBoxObjectType):
    """GraphQL type definition for the ACITenant model."""

    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )


@strawberry_django.type(
    models.ACIAppProfile, fields="__all__", filters=ACIAppProfileFilter
)
class ACIAppProfileType(NetBoxObjectType):
    """GraphQL type definition for the ACIAppProfile model."""

    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )


@strawberry_django.type(models.ACIVRF, fields="__all__", filters=ACIVRFFilter)
class ACIVRFType(NetBoxObjectType):
    """GraphQL type definition for the ACIVRF model."""

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
    models.ACIBridgeDomain, fields="__all__", filters=ACIBridgeDomainFilter
)
class ACIBridgeDomainType(NetBoxObjectType):
    """GraphQL type definition for the ACIBridgeDomain model."""

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
    models.ACIBridgeDomainSubnet,
    fields="__all__",
    filters=ACIBridgeDomainSubnetFilter,
)
class ACIBridgeDomainSubnetType(NetBoxObjectType):
    """GraphQL type definition for the ACIBridgeDomainSubnet model."""

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
    models.ACIEndpointGroup,
    fields="__all__",
    filters=ACIEndpointGroupFilter,
)
class ACIEndpointGroupType(NetBoxObjectType):
    """GraphQL type definition for the ACIEndpointGroup model."""

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
    models.ACIContractFilter,
    fields="__all__",
    filters=ACIContractFilterFilter,
)
class ACIContractFilterType(NetBoxObjectType):
    """GraphQL type definition for the ACIContractFilter model."""

    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )


@strawberry_django.type(
    models.ACIContractFilterEntry,
    fields="__all__",
    filters=ACIContractFilterEntryFilter,
)
class ACIContractFilterEntryType(NetBoxObjectType):
    """GraphQL type definition for the ACIContractFilterEntry model."""

    aci_contract_filter: Annotated[
        "ACIContractFilterType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]


@strawberry_django.type(
    models.ACIContract,
    fields="__all__",
    filters=ACIContractFilter,
)
class ACIContractType(NetBoxObjectType):
    """GraphQL type definition for the ACIContract model."""

    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )


@strawberry_django.type(
    models.ACIContractSubject,
    fields="__all__",
    filters=ACIContractSubjectFilter,
)
class ACIContractSubjectType(NetBoxObjectType):
    """GraphQL type definition for the ACIContractSubject model."""

    aci_contract: Annotated[
        "ACIContractType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )


@strawberry_django.type(
    models.ACIContractSubjectFilter,
    fields="__all__",
    filters=ACIContractSubjectFilterFilter,
)
class ACIContractSubjectFilterType(NetBoxObjectType):
    """GraphQL type definition for the ACIContractSubjectFilter model."""

    aci_contract_filter: Annotated[
        "ACIContractFilterType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    aci_contract_subject: Annotated[
        "ACIContractSubjectType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
