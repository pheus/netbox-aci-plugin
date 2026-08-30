# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""ACI extensions to NetBox's tenancy GraphQL types."""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django

from utilities.querysets import RestrictedPrefetch

from ..models.tenant.tenants import ACITenant

if TYPE_CHECKING:
    from ..graphql.types import ACITenantType

__all__ = ("TenantTypeExtension",)


@strawberry.type
class TenantTypeExtension:
    """ACI additions to NetBox's Tenant type."""

    models = ["tenancy.tenant"]

    @strawberry_django.field(
        prefetch_related=lambda info: RestrictedPrefetch(
            "acitenants",
            info.context.request.user,
            "view",
            queryset=ACITenant.objects.all(),
        ),
    )
    def aci_tenants(
        self,
    ) -> list[
        Annotated[
            "ACITenantType",
            strawberry.lazy("netbox_aci_plugin.graphql.types"),
        ]
    ]:
        """Return the ACI Tenants assigned to this NetBox tenant."""
        return self.acitenants.all()
