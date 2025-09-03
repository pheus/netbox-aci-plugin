# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from .... import models
from ...filter_lookups import TCPRulesArrayLookup
from ..mixins import ACIBaseFilterMixin

if TYPE_CHECKING:
    from ...enums import (
        ContractFilterARPOpenPeripheralCodesEnum,
        ContractFilterEtherTypeEnum,
        ContractFilterICMPv4TypesEnum,
        ContractFilterICMPv6TypesEnum,
        ContractFilterIPProtocolEnum,
        QualityOfServiceDSCPEnum,
    )
    from .tenants import ACITenantFilter


__all__ = (
    "ACIContractFilterFilter",
    "ACIContractFilterEntryFilter",
)


@strawberry_django.filter(models.ACIContractFilter, lookups=True)
class ACIContractFilterFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIContractFilter model."""

    aci_tenant: (
        Annotated[
            "ACITenantFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_tenant_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter(models.ACIContractFilterEntry, lookups=True)
class ACIContractFilterEntryFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIContractFilterEntry model."""

    aci_contract_filter: (
        Annotated[
            "ACIContractFilterFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_contract_filter_id: ID | None = strawberry_django.filter_field()
    arp_opc: (
        Annotated[
            "ContractFilterARPOpenPeripheralCodesEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    destination_from_port: FilterLookup[str] | None = strawberry_django.filter_field()
    destination_to_port: FilterLookup[str] | None = strawberry_django.filter_field()
    ether_type: (
        Annotated[
            "ContractFilterEtherTypeEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    icmp_v4_type: (
        Annotated[
            "ContractFilterICMPv4TypesEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    icmp_v6_type: (
        Annotated[
            "ContractFilterICMPv6TypesEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    ip_protocol: (
        Annotated[
            "ContractFilterIPProtocolEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    match_dscp: (
        Annotated[
            "QualityOfServiceDSCPEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    match_only_fragments_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    source_from_port: FilterLookup[str] | None = strawberry_django.filter_field()
    source_to_port: FilterLookup[str] | None = strawberry_django.filter_field()
    stateful_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    tcp_rules: (
        Annotated[
            "TCPRulesArrayLookup",
            strawberry.lazy("netbox_aci_plugin.graphql.filter_lookups"),
        ]
        | None
    ) = strawberry_django.filter_field()
