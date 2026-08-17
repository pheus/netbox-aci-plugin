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
    from .interface_policy_groups import ACILeafInterfacePolicyGroupFilter


__all__ = (
    "ACILeafInterfaceProfileFilter",
    "ACILeafInterfaceSelectorFilter",
    "ACILeafPortBlockFilter",
)


@strawberry_django.filter_type(models.ACILeafInterfaceProfile, lookups=True)
class ACILeafInterfaceProfileFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACILeafInterfaceProfile model."""

    aci_fabric: (
        Annotated[
            "ACIFabricFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_fabric_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ACILeafInterfaceSelector, lookups=True)
class ACILeafInterfaceSelectorFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACILeafInterfaceSelector model."""

    aci_leaf_interface_profile: (
        Annotated[
            "ACILeafInterfaceProfileFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_leaf_interface_profile_id: ID | None = strawberry_django.filter_field()
    aci_leaf_interface_policy_group: (
        Annotated[
            "ACILeafInterfacePolicyGroupFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_leaf_interface_policy_group_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ACILeafPortBlock, lookups=True)
class ACILeafPortBlockFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACILeafPortBlock model."""

    aci_leaf_interface_selector: (
        Annotated[
            "ACILeafInterfaceSelectorFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_leaf_interface_selector_id: ID | None = strawberry_django.filter_field()
    module_from: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()
    module_to: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()
    port_from: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()
    port_to: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()
