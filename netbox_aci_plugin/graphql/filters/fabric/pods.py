# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from dcim.graphql.filter_mixins import ScopedFilterMixin
from strawberry.scalars import ID
from strawberry_django import ComparisonFilterLookup

from .... import models
from ..mixins import ACIBaseFilterMixin

if TYPE_CHECKING:
    from ipam.graphql.filters import PrefixFilter

    from .fabrics import ACIFabricFilter


__all__ = ("ACIPodFilter",)


@strawberry_django.filter(models.ACIPod, lookups=True)
class ACIPodFilter(ScopedFilterMixin, ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIPod model."""

    aci_fabric: (
        Annotated[
            "ACIFabricFilter", strawberry.lazy("netbox_aci_plugin.graphql.filters")
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_fabric_id: ID | None = strawberry_django.filter_field()
    pod_id: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()
    tep_pool: (
        Annotated["PrefixFilter", strawberry.lazy("ipam.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    tep_pool_id: ID | None = strawberry_django.filter_field()
