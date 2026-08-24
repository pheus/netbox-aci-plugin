# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID

try:
    from strawberry_django import StrFilterLookup
except ImportError:  # pragma: no cover
    from strawberry_django import FilterLookup as StrFilterLookup

from netbox.graphql.filters import NetBoxModelFilter

from .... import models

if TYPE_CHECKING:
    from ..fabric.node_interfaces import ACINodeInterfaceFilter
    from .interface_policy_groups import ACILeafInterfacePolicyGroupFilter


__all__ = ("ACILeafInterfaceOverrideFilter",)


@strawberry_django.filter_type(models.ACILeafInterfaceOverride, lookups=True)
class ACILeafInterfaceOverrideFilter(NetBoxModelFilter):
    """GraphQL filter definition for the ACILeafInterfaceOverride model."""

    aci_node_interface: (
        Annotated[
            "ACINodeInterfaceFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_node_interface_id: ID | None = strawberry_django.filter_field()
    aci_leaf_interface_policy_group: (
        Annotated[
            "ACILeafInterfacePolicyGroupFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_leaf_interface_policy_group_id: ID | None = strawberry_django.filter_field()
    description: StrFilterLookup[str] | None = strawberry_django.filter_field()
