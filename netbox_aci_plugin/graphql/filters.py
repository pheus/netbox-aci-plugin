# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional

import strawberry_django
from netbox.graphql.filter_mixins import BaseFilterMixin, autotype_decorator

from ..filtersets.tenant_app_profiles import (
    ACIAppProfileFilterSet,
    ACIEndpointGroupFilterSet,
)
from ..filtersets.tenant_contract_filters import (
    ACIContractFilterEntryFilterSet,
    ACIContractFilterFilterSet,
)
from ..filtersets.tenant_contracts import ACIContractFilterSet
from ..filtersets.tenant_networks import (
    ACIBridgeDomainFilterSet,
    ACIBridgeDomainSubnetFilterSet,
    ACIVRFFilterSet,
)
from ..filtersets.tenants import ACITenantFilterSet
from ..models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup
from ..models.tenant_contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from ..models.tenant_contracts import ACIContract
from ..models.tenant_networks import (
    ACIVRF,
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)
from ..models.tenants import ACITenant


@strawberry_django.filter(ACITenant, lookups=True)
@autotype_decorator(ACITenantFilterSet)
class ACITenantFilter(BaseFilterMixin):
    """GraphQL filter definition for the ACITenant model."""

    pass


@strawberry_django.filter(ACIAppProfile, lookups=True)
@autotype_decorator(ACIAppProfileFilterSet)
class ACIAppProfileFilter(BaseFilterMixin):
    """GraphQL filter definition for the ACIAppProfile model."""

    pass


@strawberry_django.filter(ACIVRF, lookups=True)
@autotype_decorator(ACIVRFFilterSet)
class ACIVRFFilter(BaseFilterMixin):
    """GraphQL filter definition for the ACIVRF model."""

    dns_labels: Optional[list[str]]


@strawberry_django.filter(ACIBridgeDomain, lookups=True)
@autotype_decorator(ACIBridgeDomainFilterSet)
class ACIBridgeDomainFilter(BaseFilterMixin):
    """GraphQL filter definition for the Bridge Domain model."""

    dhcp_labels: Optional[list[str]]
    mac_address: Optional[str]
    virtual_mac_address: Optional[str]


@strawberry_django.filter(ACIBridgeDomainSubnet, lookups=True)
@autotype_decorator(ACIBridgeDomainSubnetFilterSet)
class ACIBridgeDomainSubnetFilter(BaseFilterMixin):
    """GraphQL filter definition for the Bridge Domain Subnet model."""

    pass


@strawberry_django.filter(ACIEndpointGroup, lookups=True)
@autotype_decorator(ACIEndpointGroupFilterSet)
class ACIEndpointGroupFilter(BaseFilterMixin):
    """GraphQL filter definition for the Endpoint Group model."""

    pass


@strawberry_django.filter(ACIContractFilter, lookups=True)
@autotype_decorator(ACIContractFilterFilterSet)
class ACIContractFilterFilter(BaseFilterMixin):
    """GraphQL filter definition for the Contract Filter model."""

    pass


@strawberry_django.filter(ACIContractFilterEntry, lookups=True)
@autotype_decorator(ACIContractFilterEntryFilterSet)
class ACIContractFilterEntryFilter(BaseFilterMixin):
    """GraphQL filter definition for the Contract Filter Entry model."""

    pass


@strawberry_django.filter(ACIContract, lookups=True)
@autotype_decorator(ACIContractFilterSet)
class ACIContractFilter(BaseFilterMixin):
    """GraphQL filter definition for the Contract model."""

    pass
