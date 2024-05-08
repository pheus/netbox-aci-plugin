# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later
from typing import List

import strawberry
import strawberry_django

from ..models.tenants import ACITenant
from .types import ACITenantType


@strawberry.type
class ACITenantsQuery:
    """GraphQL query definition for ACITenant model."""

    @strawberry.field
    def acitenant(self, id: int) -> ACITenantType:
        return ACITenant.objects.get(pk=id)

    acitenant_list: List[ACITenantType] = strawberry_django.field()


schema = [
    ACITenantsQuery,
]
