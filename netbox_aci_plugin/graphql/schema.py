# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later


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
    ACIEndpointSecurityGroupType,
    ACIEsgEndpointGroupSelectorType,
    ACIEsgEndpointSelectorType,
    ACITenantType,
    ACIUSegEndpointGroupType,
    ACIUSegNetworkAttributeType,
    ACIVRFType,
)


@strawberry.type(name="Query")
class NetBoxACIQuery:
    """GraphQL query definition for the NetBox ACI Plugin."""

    aci_tenant: ACITenantType = strawberry_django.field()
    aci_tenant_list: list[ACITenantType] = strawberry_django.field()

    aci_application_profile: ACIAppProfileType = strawberry_django.field()
    aci_application_profile_list: list[ACIAppProfileType] = strawberry_django.field()

    aci_vrf: ACIVRFType = strawberry_django.field()
    aci_vrf_list: list[ACIVRFType] = strawberry_django.field()

    aci_bridge_domain: ACIBridgeDomainType = strawberry_django.field()
    aci_bridge_domain_list: list[ACIBridgeDomainType] = strawberry_django.field()

    aci_bridge_domain_subnet: ACIBridgeDomainSubnetType = strawberry_django.field()
    aci_bridge_domain_subnet_list: list[ACIBridgeDomainSubnetType] = (
        strawberry_django.field()
    )

    aci_endpoint_group: ACIEndpointGroupType = strawberry_django.field()
    aci_endpoint_group_list: list[ACIEndpointGroupType] = strawberry_django.field()

    aci_useg_endpoint_group: ACIUSegEndpointGroupType = strawberry_django.field()
    aci_useg_endpoint_group_list: list[ACIUSegEndpointGroupType] = (
        strawberry_django.field()
    )

    aci_useg_network_attribute: ACIUSegNetworkAttributeType = strawberry_django.field()
    aci_useg_network_attribute_list: list[ACIUSegNetworkAttributeType] = (
        strawberry_django.field()
    )

    aci_endpoint_security_group: ACIEndpointSecurityGroupType = (
        strawberry_django.field()
    )
    aci_endpoint_security_group_list: list[ACIEndpointSecurityGroupType] = (
        strawberry_django.field()
    )

    aci_esg_endpoint_group_selector: ACIEsgEndpointGroupSelectorType = (
        strawberry_django.field()
    )
    aci_esg_endpoint_group_selector_list: list[ACIEsgEndpointGroupSelectorType] = (
        strawberry_django.field()
    )

    aci_esg_endpoint_selector: ACIEsgEndpointSelectorType = strawberry_django.field()
    aci_esg_endpoint_selector_list: list[ACIEsgEndpointSelectorType] = (
        strawberry_django.field()
    )

    aci_contract_filter: ACIContractFilterType = strawberry_django.field()
    aci_contract_filter_list: list[ACIContractFilterType] = strawberry_django.field()

    aci_contract_filter_entry: ACIContractFilterEntryType = strawberry_django.field()
    aci_contract_filter_entry_list: list[ACIContractFilterEntryType] = (
        strawberry_django.field()
    )

    aci_contract: ACIContractType = strawberry_django.field()
    aci_contract_list: list[ACIContractType] = strawberry_django.field()

    aci_contract_relation: ACIContractRelationType = strawberry_django.field()
    aci_contract_relation_list: list[ACIContractRelationType] = (
        strawberry_django.field()
    )

    aci_contract_subject: ACIContractSubjectType = strawberry_django.field()
    aci_contract_subject_list: list[ACIContractSubjectType] = strawberry_django.field()

    aci_contract_subject_filter: ACIContractSubjectFilterType = (
        strawberry_django.field()
    )
    aci_contract_subject_filter_list: list[ACIContractSubjectFilterType] = (
        strawberry_django.field()
    )
