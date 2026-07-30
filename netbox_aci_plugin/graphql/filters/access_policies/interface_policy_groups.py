# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import BaseFilterLookup

from .... import models
from ..mixins import ACIBaseFilterMixin

if TYPE_CHECKING:
    from ...enums import LeafInterfacePolicyGroupTypeEnum
    from ..fabric.fabrics import ACIFabricFilter
    from .aaep import ACIAttachableAccessEntityProfileFilter


__all__ = ("ACILeafInterfacePolicyGroupFilter",)


@strawberry_django.filter_type(models.ACILeafInterfacePolicyGroup, lookups=True)
class ACILeafInterfacePolicyGroupFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACILeafInterfacePolicyGroup model."""

    aci_fabric: (
        Annotated[
            "ACIFabricFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_fabric_id: ID | None = strawberry_django.filter_field()
    group_type: (
        BaseFilterLookup[
            Annotated[
                "LeafInterfacePolicyGroupTypeEnum",
                strawberry.lazy("netbox_aci_plugin.graphql.enums"),
            ]
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_aaep: (
        Annotated[
            "ACIAttachableAccessEntityProfileFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_aaep_id: ID | None = strawberry_django.filter_field()
