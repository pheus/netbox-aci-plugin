# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later


from typing import Optional

import strawberry_django
from netbox.graphql.types import NetBoxObjectType
from tenancy.graphql.types import TenantType

from ..models.tenant_app_profiles import ACIAppProfile
from ..models.tenants import ACITenant
from .filters import ACIAppProfileFilter, ACITenantFilter


@strawberry_django.type(ACITenant, fields="__all__", filters=ACITenantFilter)
class ACITenantType(NetBoxObjectType):
    """GraphQL type definition for ACITenant model."""

    nb_tenant: Optional[TenantType]


@strawberry_django.type(
    ACIAppProfile, fields="__all__", filters=ACIAppProfileFilter
)
class ACIAppProfileType(NetBoxObjectType):
    """GraphQL type definition for ACIAppProfile model."""

    aci_tenant: ACITenantType
    nb_tenant: Optional[TenantType]
