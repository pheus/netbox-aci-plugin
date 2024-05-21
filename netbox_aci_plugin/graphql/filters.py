# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional

import strawberry_django
from netbox.graphql.filter_mixins import BaseFilterMixin, autotype_decorator

from ..filtersets.tenant_app_profiles import ACIAppProfileFilterSet
from ..filtersets.tenant_networks import (
    ACIBridgeDomainFilterSet,
    ACIVRFFilterSet,
)
from ..filtersets.tenants import ACITenantFilterSet
from ..models.tenant_app_profiles import ACIAppProfile
from ..models.tenant_networks import ACIVRF, ACIBridgeDomain
from ..models.tenants import ACITenant


@strawberry_django.filter(ACITenant, lookups=True)
@autotype_decorator(ACITenantFilterSet)
class ACITenantFilter(BaseFilterMixin):
    """GraphQL filter definition for ACITenant model."""

    pass


@strawberry_django.filter(ACIAppProfile, lookups=True)
@autotype_decorator(ACIAppProfileFilterSet)
class ACIAppProfileFilter(BaseFilterMixin):
    """GraphQL filter definition for ACIAppProfile model."""

    pass


@strawberry_django.filter(ACIVRF, lookups=True)
@autotype_decorator(ACIVRFFilterSet)
class ACIVRFFilter(BaseFilterMixin):
    """GraphQL filter definition for ACIVRF model."""

    dns_labels: Optional[list[str]]


@strawberry_django.filter(ACIBridgeDomain, lookups=True)
@autotype_decorator(ACIBridgeDomainFilterSet)
class ACIBridgeDomainFilter(BaseFilterMixin):
    """GraphQL filter definition for Bridge Domain model."""

    dhcp_labels: Optional[list[str]]
    mac_address: Optional[str]
    virtual_mac_address: Optional[str]
