# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated, List, Optional, Union

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
    ACIContractRelationFilter,
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

    # Model fields
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )

    # Related models
    aci_app_profiles: List[
        Annotated[
            "ACIAppProfileType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_bridge_domains: List[
        Annotated[
            "ACIBridgeDomainType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_contracts: List[
        Annotated[
            "ACIContractType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_contract_filters: List[
        Annotated[
            "ACIContractFilterType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_vrfs: List[
        Annotated[
            "ACIVRFType", strawberry.lazy("netbox_aci_plugin.graphql.types")
        ]
    ]


@strawberry_django.type(
    models.ACIAppProfile, fields="__all__", filters=ACIAppProfileFilter
)
class ACIAppProfileType(NetBoxObjectType):
    """GraphQL type definition for the ACIAppProfile model."""

    # Model fields
    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )

    # Related models
    aci_endpoint_groups: List[
        Annotated[
            "ACIEndpointGroupType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(models.ACIVRF, fields="__all__", filters=ACIVRFFilter)
class ACIVRFType(NetBoxObjectType):
    """GraphQL type definition for the ACIVRF model."""

    # Model fields
    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )
    nb_vrf: Annotated["VRFType", strawberry.lazy("ipam.graphql.types")] | None
    dns_labels: Optional[List[str]]

    # Related models
    aci_bridge_domains: List[
        Annotated[
            "ACIBridgeDomainType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_contract_relations: List[
        Annotated[
            "ACIContractRelationType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIBridgeDomain, fields="__all__", filters=ACIBridgeDomainFilter
)
class ACIBridgeDomainType(NetBoxObjectType):
    """GraphQL type definition for the ACIBridgeDomain model."""

    # Model fields
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

    # Related models
    aci_bridge_domain_subnets: List[
        Annotated[
            "ACIBridgeDomainSubnetType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_endpoint_groups: List[
        Annotated[
            "ACIEndpointGroupType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIBridgeDomainSubnet,
    fields="__all__",
    filters=ACIBridgeDomainSubnetFilter,
)
class ACIBridgeDomainSubnetType(NetBoxObjectType):
    """GraphQL type definition for the ACIBridgeDomainSubnet model."""

    # Model fields
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

    # Model fields
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

    # Related models
    aci_contract_relations: List[
        Annotated[
            "ACIContractRelationType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIContractFilter,
    fields="__all__",
    filters=ACIContractFilterFilter,
)
class ACIContractFilterType(NetBoxObjectType):
    """GraphQL type definition for the ACIContractFilter model."""

    # Model fields
    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )

    # Related models
    aci_contract_filter_entries: List[
        Annotated[
            "ACIContractFilterEntryType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_contract_subject_filters: List[
        Annotated[
            "ACIContractSubjectFilterType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIContractFilterEntry,
    fields="__all__",
    filters=ACIContractFilterEntryFilter,
)
class ACIContractFilterEntryType(NetBoxObjectType):
    """GraphQL type definition for the ACIContractFilterEntry model."""

    # Model fields
    aci_contract_filter: Annotated[
        "ACIContractFilterType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )


@strawberry_django.type(
    models.ACIContract,
    fields="__all__",
    filters=ACIContractFilter,
)
class ACIContractType(NetBoxObjectType):
    """GraphQL type definition for the ACIContract model."""

    # Model fields
    aci_tenant: Annotated[
        "ACITenantType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )

    # Related models
    aci_contract_relations: List[
        Annotated[
            "ACIContractRelationType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_contract_subjects: List[
        Annotated[
            "ACIContractSubjectType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIContractRelation,
    exclude=[
        "aci_object_id",
        "aci_object_type",
        "_aci_endpoint_group",
        "_aci_vrf",
    ],
    filters=ACIContractRelationFilter,
)
class ACIContractRelationType(NetBoxObjectType):
    """GraphQL type definition for the ACIContractRelation model."""

    # Model fields
    aci_contract: Annotated[
        "ACIContractType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]

    @strawberry.field(description="ACI Object")
    def aci_object(
        self,
    ) -> (
        Annotated[
            Union[
                Annotated[
                    "ACIEndpointGroupType",
                    strawberry.lazy("netbox_aci_plugin.graphql.types"),
                ],
                Annotated[
                    "ACIVRFType",
                    strawberry.lazy("netbox_aci_plugin.graphql.types"),
                ],
            ],
            strawberry.union("ACIContractRelationObjectType"),
        ]
        | None
    ):
        return self.aci_object


@strawberry_django.type(
    models.ACIContractSubject,
    fields="__all__",
    filters=ACIContractSubjectFilter,
)
class ACIContractSubjectType(NetBoxObjectType):
    """GraphQL type definition for the ACIContractSubject model."""

    # Model fields
    aci_contract: Annotated[
        "ACIContractType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    nb_tenant: (
        Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")]
        | None
    )

    # Related models
    aci_contract_subject_filters: List[
        Annotated[
            "ACIContractSubjectFilterType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIContractSubjectFilter,
    fields="__all__",
    filters=ACIContractSubjectFilterFilter,
)
class ACIContractSubjectFilterType(NetBoxObjectType):
    """GraphQL type definition for the ACIContractSubjectFilter model."""

    # Model fields
    aci_contract_filter: Annotated[
        "ACIContractFilterType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    aci_contract_subject: Annotated[
        "ACIContractSubjectType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
