# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from core.graphql.filters import ContentTypeFilter
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from .... import models
from ..mixins import ACIBaseFilterMixin

if TYPE_CHECKING:
    from ...enums import (
        ContractRelationRoleEnum,
        ContractScopeEnum,
        ContractSubjectFilterActionEnum,
        ContractSubjectFilterApplyDirectionEnum,
        ContractSubjectFilterPriorityEnum,
        QualityOfServiceClassEnum,
        QualityOfServiceDSCPEnum,
    )
    from .contract_filters import ACIContractFilterFilter
    from .tenants import ACITenantFilter


__all__ = (
    "ACIContractFilter",
    "ACIContractRelationFilter",
    "ACIContractSubjectFilter",
    "ACIContractSubjectFilterFilter",
)


@strawberry_django.filter(models.ACIContract, lookups=True)
class ACIContractFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIContract model."""

    aci_tenant: (
        Annotated[
            "ACITenantFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_tenant_id: ID | None = strawberry_django.filter_field()
    qos_class: (
        Annotated[
            "QualityOfServiceClassEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    scope: (
        Annotated[
            "ContractScopeEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    target_dscp: (
        Annotated[
            "QualityOfServiceDSCPEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter(models.ACIContractRelation, lookups=True)
class ACIContractRelationFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIContractRelation model."""

    aci_contract: (
        Annotated[
            "ACIContractFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_contract_id: ID | None = strawberry_django.filter_field()
    aci_object_type: (
        Annotated["ContentTypeFilter", strawberry.lazy("core.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    aci_object_id: ID | None = strawberry_django.filter_field()
    role: (
        Annotated[
            "ContractRelationRoleEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter(models.ACIContractSubject, lookups=True)
class ACIContractSubjectFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIContractSubject model."""

    aci_contract: (
        Annotated[
            "ACIContractFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_contract_id: ID | None = strawberry_django.filter_field()
    apply_both_directions_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    qos_class: (
        Annotated[
            "QualityOfServiceClassEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    qos_class_cons_to_prov: (
        Annotated[
            "QualityOfServiceClassEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    qos_class_prov_to_cons: (
        Annotated[
            "QualityOfServiceClassEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    reverse_filter_ports_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    service_graph_name: FilterLookup[str] | None = strawberry_django.filter_field()
    service_graph_name_cons_to_prov: FilterLookup[str] | None = (
        strawberry_django.filter_field()
    )
    service_graph_name_prov_to_cons: FilterLookup[str] | None = (
        strawberry_django.filter_field()
    )
    target_dscp: (
        Annotated[
            "QualityOfServiceDSCPEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    target_dscp_cons_to_prov: (
        Annotated[
            "QualityOfServiceDSCPEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    target_dscp_prov_to_cons: (
        Annotated[
            "QualityOfServiceDSCPEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter(models.ACIContractSubjectFilter, lookups=True)
class ACIContractSubjectFilterFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIContractSubjectFilter model."""

    aci_contract_filter: (
        Annotated[
            "ACIContractFilterFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_contract_filter_id: ID | None = strawberry_django.filter_field()
    aci_contract_subject: (
        Annotated[
            "ACIContractSubjectFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_contract_subject_id: ID | None = strawberry_django.filter_field()
    action: (
        Annotated[
            "ContractSubjectFilterActionEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    apply_direction: (
        Annotated[
            "ContractSubjectFilterApplyDirectionEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    log_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    policy_compression_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    priority: (
        Annotated[
            "ContractSubjectFilterPriorityEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
