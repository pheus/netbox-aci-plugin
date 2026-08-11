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
    from ..fabric.fabrics import ACIFabricFilter


__all__ = (
    "ACILeafNodeBlockFilter",
    "ACILeafSelectorFilter",
    "ACILeafSwitchProfileFilter",
)


@strawberry_django.filter_type(models.ACILeafSwitchProfile, lookups=True)
class ACILeafSwitchProfileFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACILeafSwitchProfile model."""

    aci_fabric: (
        Annotated[
            "ACIFabricFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_fabric_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ACILeafSelector, lookups=True)
class ACILeafSelectorFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACILeafSelector model."""

    aci_leaf_switch_profile: (
        Annotated[
            "ACILeafSwitchProfileFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_leaf_switch_profile_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ACILeafNodeBlock, lookups=True)
class ACILeafNodeBlockFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACILeafNodeBlock model."""

    aci_leaf_selector: (
        Annotated[
            "ACILeafSelectorFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_leaf_selector_id: ID | None = strawberry_django.filter_field()
    node_id_from: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()
    node_id_to: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()
