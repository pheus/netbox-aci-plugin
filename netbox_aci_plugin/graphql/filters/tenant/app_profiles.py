# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID

from .... import models
from ..mixins import ACIBaseFilterMixin

if TYPE_CHECKING:
    from .tenants import ACITenantFilter


__all__ = ("ACIAppProfileFilter",)


@strawberry_django.filter(models.ACIAppProfile, lookups=True)
class ACIAppProfileFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIAppProfile model."""

    aci_tenant: (
        Annotated[
            "ACITenantFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_tenant_id: ID | None = strawberry_django.filter_field()
