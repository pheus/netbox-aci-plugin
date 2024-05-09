# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later
from typing import List

import strawberry
import strawberry_django

from ..models.tenant_app_profiles import ACIAppProfile
from ..models.tenants import ACITenant
from .types import ACIAppProfileType, ACITenantType


@strawberry.type
class ACITenantsQuery:
    """GraphQL query definition for ACITenant model."""

    @strawberry.field
    def aci_tenant(self, id: int) -> ACITenantType:
        return ACITenant.objects.get(pk=id)

    aci_tenant_list: List[ACITenantType] = strawberry_django.field()


@strawberry.type
class ACIAppProfilesQuery:
    """GraphQL query definition for ACIAppProfile model."""

    @strawberry.field
    def aci_application_profile(self, id: int) -> ACIAppProfileType:
        return ACIAppProfile.objects.get(pk=id)

    aci_application_profile_list: List[ACIAppProfileType] = (
        strawberry_django.field()
    )


schema = [ACITenantsQuery, ACIAppProfilesQuery]
