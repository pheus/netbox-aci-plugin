# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional

import strawberry_django
from netbox.graphql.filter_mixins import BaseFilterMixin, autotype_decorator

from .. import models
from ..filtersets.tenant.app_profiles import ACIAppProfileFilterSet
from ..filtersets.tenant.bridge_domains import (
    ACIBridgeDomainFilterSet,
    ACIBridgeDomainSubnetFilterSet,
)
from ..filtersets.tenant.contract_filters import (
    ACIContractFilterEntryFilterSet,
    ACIContractFilterFilterSet,
)
from ..filtersets.tenant.contracts import (
    ACIContractFilterSet,
    ACIContractRelationFilterSet,
    ACIContractSubjectFilterFilterSet,
    ACIContractSubjectFilterSet,
)
from ..filtersets.tenant.endpoint_groups import (
    ACIEndpointGroupFilterSet,
    ACIUSegEndpointGroupFilterSet,
    ACIUSegNetworkAttributeFilterSet,
)
from ..filtersets.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroupFilterSet,
    ACIEsgEndpointGroupSelectorFilterSet,
)
from ..filtersets.tenant.tenants import ACITenantFilterSet
from ..filtersets.tenant.vrfs import ACIVRFFilterSet


@strawberry_django.filter(models.ACITenant, lookups=True)
@autotype_decorator(ACITenantFilterSet)
class ACITenantFilter(BaseFilterMixin):
    """GraphQL filter definition for the ACITenant model."""

    pass


@strawberry_django.filter(models.ACIAppProfile, lookups=True)
@autotype_decorator(ACIAppProfileFilterSet)
class ACIAppProfileFilter(BaseFilterMixin):
    """GraphQL filter definition for the ACIAppProfile model."""

    pass


@strawberry_django.filter(models.ACIVRF, lookups=True)
@autotype_decorator(ACIVRFFilterSet)
class ACIVRFFilter(BaseFilterMixin):
    """GraphQL filter definition for the ACIVRF model."""

    dns_labels: Optional[list[str]]


@strawberry_django.filter(models.ACIBridgeDomain, lookups=True)
@autotype_decorator(ACIBridgeDomainFilterSet)
class ACIBridgeDomainFilter(BaseFilterMixin):
    """GraphQL filter definition for the Bridge Domain model."""

    dhcp_labels: Optional[list[str]]
    mac_address: Optional[str]
    virtual_mac_address: Optional[str]


@strawberry_django.filter(models.ACIBridgeDomainSubnet, lookups=True)
@autotype_decorator(ACIBridgeDomainSubnetFilterSet)
class ACIBridgeDomainSubnetFilter(BaseFilterMixin):
    """GraphQL filter definition for the Bridge Domain Subnet model."""

    pass


@strawberry_django.filter(models.ACIEndpointGroup, lookups=True)
@autotype_decorator(ACIEndpointGroupFilterSet)
class ACIEndpointGroupFilter(BaseFilterMixin):
    """GraphQL filter definition for the Endpoint Group model."""

    pass


@strawberry_django.filter(models.ACIUSegEndpointGroup, lookups=True)
@autotype_decorator(ACIUSegEndpointGroupFilterSet)
class ACIUSegEndpointGroupFilter(BaseFilterMixin):
    """GraphQL filter definition for the uSeg Endpoint Group model."""

    pass


@strawberry_django.filter(models.ACIUSegNetworkAttribute, lookups=True)
@autotype_decorator(ACIUSegNetworkAttributeFilterSet)
class ACIUSegNetworkAttributeFilter(BaseFilterMixin):
    """GraphQL filter definition for the uSeg Network Attribute model."""

    pass


@strawberry_django.filter(models.ACIEndpointSecurityGroup, lookups=True)
@autotype_decorator(ACIEndpointSecurityGroupFilterSet)
class ACIEndpointSecurityGroupFilter(BaseFilterMixin):
    """GraphQL filter definition for the Endpoint Security Group model."""

    pass


@strawberry_django.filter(models.ACIEsgEndpointGroupSelector, lookups=True)
@autotype_decorator(ACIEsgEndpointGroupSelectorFilterSet)
class ACIEsgEndpointGroupSelectorFilter(BaseFilterMixin):
    """GraphQL filter definition for the ESG EPG Selector model."""

    pass


@strawberry_django.filter(models.ACIContractFilter, lookups=True)
@autotype_decorator(ACIContractFilterFilterSet)
class ACIContractFilterFilter(BaseFilterMixin):
    """GraphQL filter definition for the Contract Filter model."""

    pass


@strawberry_django.filter(models.ACIContractFilterEntry, lookups=True)
@autotype_decorator(ACIContractFilterEntryFilterSet)
class ACIContractFilterEntryFilter(BaseFilterMixin):
    """GraphQL filter definition for the Contract Filter Entry model."""

    pass


@strawberry_django.filter(models.ACIContract, lookups=True)
@autotype_decorator(ACIContractFilterSet)
class ACIContractFilter(BaseFilterMixin):
    """GraphQL filter definition for the Contract model."""

    pass


@strawberry_django.filter(models.ACIContractRelation, lookups=True)
@autotype_decorator(ACIContractRelationFilterSet)
class ACIContractRelationFilter(BaseFilterMixin):
    """GraphQL filter definition for the Contract Relation model."""

    pass


@strawberry_django.filter(models.ACIContractSubject, lookups=True)
@autotype_decorator(ACIContractSubjectFilterSet)
class ACIContractSubjectFilter(BaseFilterMixin):
    """GraphQL filter definition for the Contract Subject model."""

    pass


@strawberry_django.filter(models.ACIContractSubjectFilter, lookups=True)
@autotype_decorator(ACIContractSubjectFilterFilterSet)
class ACIContractSubjectFilterFilter(BaseFilterMixin):
    """GraphQL filter definition for the Contract Subject Filter model."""

    pass
