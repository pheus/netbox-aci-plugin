# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import ComparisonFilterLookup

from .... import models
from ..mixins import ACIBaseFilterMixin

if TYPE_CHECKING:
    from .fabrics import ACIFabricFilter
    from .nodes import ACINodeFilter


__all__ = ("ACIVPCProtectionGroupFilter",)


@strawberry_django.filter_type(models.ACIVPCProtectionGroup, lookups=True)
class ACIVPCProtectionGroupFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIVPCProtectionGroup model."""

    aci_fabric: (
        Annotated[
            "ACIFabricFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_fabric_id: ID | None = strawberry_django.filter_field()
    logical_pair_id: ComparisonFilterLookup[int] | None = (
        strawberry_django.filter_field()
    )
    aci_node_a: (
        Annotated["ACINodeFilter", strawberry.lazy("netbox_aci_plugin.graphql.filters")]
        | None
    ) = strawberry_django.filter_field()
    aci_node_a_id: ID | None = strawberry_django.filter_field()
    aci_node_b: (
        Annotated["ACINodeFilter", strawberry.lazy("netbox_aci_plugin.graphql.filters")]
        | None
    ) = strawberry_django.filter_field()
    aci_node_b_id: ID | None = strawberry_django.filter_field()
