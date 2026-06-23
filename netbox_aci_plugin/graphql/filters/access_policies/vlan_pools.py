# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import BaseFilterLookup, ComparisonFilterLookup

from netbox.graphql.filters import NetBoxModelFilter

from .... import models
from ..mixins import ACIBaseFilterMixin

if TYPE_CHECKING:
    from ipam.graphql.filters import VLANGroupFilter

    from ...enums import (
        VLANAllocationModeEnum,
        VLANPoolRangeAllocationModeEnum,
        VLANPoolRangeRoleEnum,
    )
    from ..fabric.fabrics import ACIFabricFilter


__all__ = (
    "ACIVLANPoolFilter",
    "ACIVLANPoolRangeFilter",
)


@strawberry_django.filter_type(models.ACIVLANPool, lookups=True)
class ACIVLANPoolFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIVLANPool model."""

    aci_fabric: (
        Annotated[
            "ACIFabricFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_fabric_id: ID | None = strawberry_django.filter_field()
    allocation_mode: (
        BaseFilterLookup[
            Annotated[
                "VLANAllocationModeEnum",
                strawberry.lazy("netbox_aci_plugin.graphql.enums"),
            ]
        ]
        | None
    ) = strawberry_django.filter_field()
    nb_vlan_group: (
        Annotated["VLANGroupFilter", strawberry.lazy("ipam.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    nb_vlan_group_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ACIVLANPoolRange, lookups=True)
class ACIVLANPoolRangeFilter(NetBoxModelFilter):
    """GraphQL filter definition for the ACIVLANPoolRange model."""

    aci_vlan_pool: (
        Annotated[
            "ACIVLANPoolFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_vlan_pool_id: ID | None = strawberry_django.filter_field()
    vlan_id_from: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()
    vlan_id_to: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()
    allocation_mode: (
        BaseFilterLookup[
            Annotated[
                "VLANPoolRangeAllocationModeEnum",
                strawberry.lazy("netbox_aci_plugin.graphql.enums"),
            ]
        ]
        | None
    ) = strawberry_django.filter_field()
    role: (
        BaseFilterLookup[
            Annotated[
                "VLANPoolRangeRoleEnum",
                strawberry.lazy("netbox_aci_plugin.graphql.enums"),
            ]
        ]
        | None
    ) = strawberry_django.filter_field()
