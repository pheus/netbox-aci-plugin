# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import strawberry

from ..choices import (
    BDMultiDestinationFloodingChoices,
    BDUnknownMulticastChoices,
    BDUnknownUnicastChoices,
    ContractFilterARPOpenPeripheralCodesChoices,
    ContractFilterEtherTypeChoices,
    ContractFilterICMPv4TypesChoices,
    ContractFilterICMPv6TypesChoices,
    ContractFilterIPProtocolChoices,
    ContractFilterPortChoices,
    ContractFilterTCPRulesChoices,
    ContractRelationRoleChoices,
    ContractScopeChoices,
    ContractSubjectFilterActionChoices,
    ContractSubjectFilterApplyDirectionChoices,
    ContractSubjectFilterPriorityChoices,
    QualityOfServiceClassChoices,
    QualityOfServiceDSCPChoices,
    USegAttributeMatchOperatorChoices,
    USegAttributeTypeChoices,
    VRFPCEnforcementDirectionChoices,
    VRFPCEnforcementPreferenceChoices,
)

__all__ = (
    "BDMultiDestinationFloodingEnum",
    "BDUnknownMulticastEnum",
    "BDUnknownUnicastEnum",
    "ContractFilterARPOpenPeripheralCodesEnum",
    "ContractFilterEtherTypeEnum",
    "ContractFilterICMPv4TypesEnum",
    "ContractFilterICMPv6TypesEnum",
    "ContractFilterIPProtocolEnum",
    "ContractFilterPortEnum",
    "ContractFilterTCPRulesEnum",
    "ContractRelationRoleEnum",
    "ContractScopeEnum",
    "ContractSubjectFilterActionEnum",
    "ContractSubjectFilterApplyDirectionEnum",
    "ContractSubjectFilterPriorityEnum",
    "QualityOfServiceClassEnum",
    "QualityOfServiceDSCPEnum",
    "USegAttributeMatchOperatorEnum",
    "USegAttributeTypeEnum",
    "VRFPCEnforcementDirectionEnum",
    "VRFPCEnforcementPreferenceEnum",
)

#
# Bridge Domain
#

BDMultiDestinationFloodingEnum = strawberry.enum(
    BDMultiDestinationFloodingChoices.as_enum()
)
BDUnknownMulticastEnum = strawberry.enum(BDUnknownMulticastChoices.as_enum())
BDUnknownUnicastEnum = strawberry.enum(BDUnknownUnicastChoices.as_enum())

#
# Contract Filter
#

ContractFilterARPOpenPeripheralCodesEnum = strawberry.enum(
    ContractFilterARPOpenPeripheralCodesChoices.as_enum()
)
ContractFilterEtherTypeEnum = strawberry.enum(ContractFilterEtherTypeChoices.as_enum())
ContractFilterICMPv4TypesEnum = strawberry.enum(
    ContractFilterICMPv4TypesChoices.as_enum()
)
ContractFilterICMPv6TypesEnum = strawberry.enum(
    ContractFilterICMPv6TypesChoices.as_enum()
)
ContractFilterIPProtocolEnum = strawberry.enum(
    ContractFilterIPProtocolChoices.as_enum()
)
ContractFilterPortEnum = strawberry.enum(ContractFilterPortChoices.as_enum())
ContractFilterTCPRulesEnum = strawberry.enum(ContractFilterTCPRulesChoices.as_enum())

#
# Contract
#

ContractScopeEnum = strawberry.enum(ContractScopeChoices.as_enum())

#
# Contract Relation
#

ContractRelationRoleEnum = strawberry.enum(ContractRelationRoleChoices.as_enum())

#
# Contract Subject Filter
#

ContractSubjectFilterActionEnum = strawberry.enum(
    ContractSubjectFilterActionChoices.as_enum()
)
ContractSubjectFilterApplyDirectionEnum = strawberry.enum(
    ContractSubjectFilterApplyDirectionChoices.as_enum()
)
ContractSubjectFilterPriorityEnum = strawberry.enum(
    ContractSubjectFilterPriorityChoices.as_enum()
)

#
# Quality of Service (QoS)
#

QualityOfServiceClassEnum = strawberry.enum(QualityOfServiceClassChoices.as_enum())
QualityOfServiceDSCPEnum = strawberry.enum(QualityOfServiceDSCPChoices.as_enum())

#
# uSeg EPG
#

USegAttributeMatchOperatorEnum = strawberry.enum(
    USegAttributeMatchOperatorChoices.as_enum()
)

#
# uSeg Attribute
#

USegAttributeTypeEnum = strawberry.enum(USegAttributeTypeChoices.as_enum())

#
# VRF
#

VRFPCEnforcementDirectionEnum = strawberry.enum(
    VRFPCEnforcementDirectionChoices.as_enum()
)
VRFPCEnforcementPreferenceEnum = strawberry.enum(
    VRFPCEnforcementPreferenceChoices.as_enum()
)
