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
    from ..fabric.fabrics import ACIFabricFilter

__all__ = ("ACITenantFilter",)


@strawberry_django.filter(models.ACITenant, lookups=True)
class ACITenantFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACITenant model."""

    aci_fabric: (
        Annotated[
            "ACIFabricFilter", strawberry.lazy("netbox_aci_plugin.graphql.filters")
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_fabric_id: ID | None = strawberry_django.filter_field()
