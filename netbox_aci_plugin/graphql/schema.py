# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later
from typing import List

import strawberry
import strawberry_django

from .types import (
    ACIAppProfileType,
    ACIBridgeDomainSubnetType,
    ACIBridgeDomainType,
    ACIContractFilterEntryType,
    ACIContractFilterType,
    ACIContractRelationType,
    ACIContractSubjectFilterType,
    ACIContractSubjectType,
    ACIContractType,
    ACIEndpointGroupType,
    ACITenantType,
    ACIVRFType,
)


@strawberry.type(name="Query")
class NetBoxACIQuery:
    """GraphQL query definition for the NetBox ACI Plugin."""

    aci_tenant: ACITenantType = strawberry_django.field()
    aci_tenant_list: List[ACITenantType] = strawberry_django.field()

    aci_application_profile: ACIAppProfileType = strawberry_django.field()
    aci_application_profile_list: List[ACIAppProfileType] = (
        strawberry_django.field()
    )

    aci_vrf: ACIVRFType = strawberry_django.field()
    aci_vrf_list: List[ACIVRFType] = strawberry_django.field()

    aci_bridge_domain: ACIBridgeDomainType = strawberry_django.field()
    aci_bridge_domain_list: List[ACIBridgeDomainType] = (
        strawberry_django.field()
    )

    aci_bridge_domain_subnet: ACIBridgeDomainSubnetType = (
        strawberry_django.field()
    )
    aci_bridge_domain_subnet_list: List[ACIBridgeDomainSubnetType] = (
        strawberry_django.field()
    )

    aci_endpoint_group: ACIEndpointGroupType = strawberry_django.field()
    aci_endpoint_group_list: List[ACIEndpointGroupType] = (
        strawberry_django.field()
    )

    aci_contract_filter: ACIContractFilterType = strawberry_django.field()
    aci_contract_filter_list: List[ACIContractFilterType] = (
        strawberry_django.field()
    )

    aci_contract_filter_entry: ACIContractFilterEntryType = (
        strawberry_django.field()
    )
    aci_contract_filter_entry_list: List[ACIContractFilterEntryType] = (
        strawberry_django.field()
    )

    aci_contract: ACIContractType = strawberry_django.field()
    aci_contract_list: List[ACIContractType] = strawberry_django.field()

    aci_contract_relation: ACIContractRelationType = strawberry_django.field()
    aci_contract_relation_list: List[ACIContractRelationType] = (
        strawberry_django.field()
    )

    aci_contract_subject: ACIContractSubjectType = strawberry_django.field()
    aci_contract_subject_list: List[ACIContractSubjectType] = (
        strawberry_django.field()
    )

    aci_contract_subject_filter: ACIContractSubjectFilterType = (
        strawberry_django.field()
    )
    aci_contract_subject_filter_list: List[ACIContractSubjectFilterType] = (
        strawberry_django.field()
    )
