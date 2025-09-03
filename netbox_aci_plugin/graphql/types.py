# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated

import strawberry
import strawberry_django
from dcim.graphql.types import MACAddressType
from ipam.graphql.types import IPAddressType, PrefixType, VRFType
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
    ACIEndpointSecurityGroupFilter,
    ACIEsgEndpointGroupSelectorFilter,
    ACIEsgEndpointSelectorFilter,
    ACITenantFilter,
    ACIUSegEndpointGroupFilter,
    ACIUSegNetworkAttributeFilter,
    ACIVRFFilter,
)


@strawberry_django.type(models.ACITenant, fields="__all__", filters=ACITenantFilter)
class ACITenantType(NetBoxObjectType):
    """GraphQL type definition for the ACITenant model."""

    # Model fields
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_app_profiles: list[
        Annotated[
            "ACIAppProfileType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_bridge_domains: list[
        Annotated[
            "ACIBridgeDomainType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_contracts: list[
        Annotated[
            "ACIContractType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_contract_filters: list[
        Annotated[
            "ACIContractFilterType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_vrfs: list[
        Annotated["ACIVRFType", strawberry.lazy("netbox_aci_plugin.graphql.types")]
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
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_endpoint_groups: list[
        Annotated[
            "ACIEndpointGroupType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_endpoint_security_groups: list[
        Annotated[
            "ACIEndpointSecurityGroupType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_useg_endpoint_groups: list[
        Annotated[
            "ACIUSegEndpointGroupType",
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
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    nb_vrf: Annotated["VRFType", strawberry.lazy("ipam.graphql.types")] | None
    dns_labels: list[str] | None

    # Related models
    aci_bridge_domains: list[
        Annotated[
            "ACIBridgeDomainType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_contract_relations: list[
        Annotated[
            "ACIContractRelationType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_endpoint_security_groups: list[
        Annotated[
            "ACIEndpointSecurityGroupType",
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
    aci_vrf: Annotated["ACIVRFType", strawberry.lazy("netbox_aci_plugin.graphql.types")]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    dhcp_labels: list[str] | None
    mac_address: str | None
    virtual_mac_address: str | None

    # Related models
    aci_bridge_domain_subnets: list[
        Annotated[
            "ACIBridgeDomainSubnetType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_endpoint_groups: list[
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
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None


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
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_contract_relations: list[
        Annotated[
            "ACIContractRelationType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIUSegEndpointGroup,
    fields="__all__",
    filters=ACIUSegEndpointGroupFilter,
)
class ACIUSegEndpointGroupType(NetBoxObjectType):
    """GraphQL type definition for the ACIUSegEndpointGroup model."""

    # Model fields
    aci_app_profile: Annotated[
        "ACIAppProfileType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    aci_bridge_domain: Annotated[
        "ACIBridgeDomainType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_contract_relations: list[
        Annotated[
            "ACIContractRelationType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_useg_network_attributes: list[
        Annotated[
            "ACIUSegNetworkAttributeType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIUSegNetworkAttribute,
    exclude=[
        "attr_object_id",
        "attr_object_type",
        "_ip_address",
        "_mac_address",
        "_prefix",
    ],
    filters=ACIUSegNetworkAttributeFilter,
)
class ACIUSegNetworkAttributeType(NetBoxObjectType):
    """GraphQL type definition for the ACIUSegNetworkAttribute model."""

    # Model fields
    aci_useg_endpoint_group: Annotated[
        "ACIUSegEndpointGroupType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    @strawberry.field(description="Attribute Object")
    def attr_object(
        self,
    ) -> (
        Annotated[
            Annotated["IPAddressType", strawberry.lazy("ipam.graphql.types")]
            | Annotated["MACAddressType", strawberry.lazy("dcim.graphql.types")]
            | Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")],
            strawberry.union("ACIUSegNetworkAttributeObjectType"),
        ]
        | None
    ):
        """Return the attribute object."""
        return self.attr_object


@strawberry_django.type(
    models.ACIEndpointSecurityGroup,
    fields="__all__",
    filters=ACIEndpointSecurityGroupFilter,
)
class ACIEndpointSecurityGroupType(NetBoxObjectType):
    """GraphQL type definition for the ACIEndpointSecurityGroup model."""

    # Model fields
    aci_app_profile: Annotated[
        "ACIAppProfileType", strawberry.lazy("netbox_aci_plugin.graphql.types")
    ]
    aci_vrf: Annotated[
        "ACIVRFType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_contract_relations: list[
        Annotated[
            "ACIContractRelationType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_esg_endpoint_group_selectors: list[
        Annotated[
            "ACIEsgEndpointGroupSelectorType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_esg_endpoint_selectors: list[
        Annotated[
            "ACIEsgEndpointSelectorType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]


@strawberry_django.type(
    models.ACIEsgEndpointGroupSelector,
    exclude=[
        "aci_epg_object_id",
        "aci_epg_object_type",
        "_aci_endpoint_group",
        "_aci_useg_endpoint_group",
    ],
    filters=ACIEsgEndpointGroupSelectorFilter,
)
class ACIEsgEndpointGroupSelectorType(NetBoxObjectType):
    """GraphQL type definition for the ACIEsgEndpointGroupSelector model."""

    # Model fields
    aci_endpoint_security_group: Annotated[
        "ACIEndpointSecurityGroupType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    @strawberry.field(description="Endpoint Group Object")
    def aci_epg_object(
        self,
    ) -> (
        Annotated[
            Annotated[
                "ACIEndpointGroupType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ]
            | Annotated[
                "ACIUSegEndpointGroupType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ],
            strawberry.union("ACIEsgEndpointGroupSelectorObjectType"),
        ]
        | None
    ):
        """Return the Endpoint Group object."""
        return self.aci_epg_object


@strawberry_django.type(
    models.ACIEsgEndpointSelector,
    exclude=[
        "ep_object_id",
        "ep_object_type",
        "_ip_address",
        "_prefix",
    ],
    filters=ACIEsgEndpointSelectorFilter,
)
class ACIEsgEndpointSelectorType(NetBoxObjectType):
    """GraphQL type definition for the ACIEsgEndpointSelector model."""

    # Model fields
    aci_endpoint_security_group: Annotated[
        "ACIEndpointSecurityGroupType",
        strawberry.lazy("netbox_aci_plugin.graphql.types"),
    ]
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    @strawberry.field(description="Endpoint Object")
    def ep_object(
        self,
    ) -> (
        Annotated[
            Annotated["IPAddressType", strawberry.lazy("ipam.graphql.types")]
            | Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")],
            strawberry.union("ACIEsgEndpointSelectorObjectType"),
        ]
        | None
    ):
        """Return the Endpoint object."""
        return self.ep_object


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
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_contract_filter_entries: list[
        Annotated[
            "ACIContractFilterEntryType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_contract_subject_filters: list[
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
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None


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
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_contract_relations: list[
        Annotated[
            "ACIContractRelationType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]
    aci_contract_subjects: list[
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
        "_aci_endpoint_security_group",
        "_aci_useg_endpoint_group",
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
            Annotated[
                "ACIEndpointGroupType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ]
            | Annotated[
                "ACIEndpointSecurityGroupType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ]
            | Annotated[
                "ACIUSegEndpointGroupType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ]
            | Annotated[
                "ACIVRFType",
                strawberry.lazy("netbox_aci_plugin.graphql.types"),
            ],
            strawberry.union("ACIContractRelationObjectType"),
        ]
        | None
    ):
        """Return the ACI object."""
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
    nb_tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Related models
    aci_contract_subject_filters: list[
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
