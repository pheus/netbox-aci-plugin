# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later


import strawberry_django
from netbox.graphql.types import NetBoxObjectType

from ..models.tenants import ACITenant
from .filters import ACITenantFilter


@strawberry_django.type(ACITenant, fields="__all__", filters=ACITenantFilter)
class ACITenantType(NetBoxObjectType):
    """GraphQL type definition for ACITenant model."""

    pass
