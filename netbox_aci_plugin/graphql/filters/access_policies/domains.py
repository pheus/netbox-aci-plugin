# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID

from .... import models
from ..mixins import ACIBaseFilterMixin

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import StringArrayLookup

    from ..fabric.fabrics import ACIFabricFilter
    from .vlan_pools import ACIVLANPoolFilter


__all__ = (
    "ACIPhysicalDomainFilter",
    "ACIRoutedDomainFilter",
)


@strawberry_django.filter_type(models.ACIRoutedDomain, lookups=True)
class ACIRoutedDomainFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIRoutedDomain model."""

    aci_fabric: (
        Annotated[
            "ACIFabricFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_fabric_id: ID | None = strawberry_django.filter_field()
    aci_vlan_pool: (
        Annotated[
            "ACIVLANPoolFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_vlan_pool_id: ID | None = strawberry_django.filter_field()
    security_domains: (
        Annotated[
            "StringArrayLookup",
            strawberry.lazy("netbox.graphql.filter_lookups"),
        ]
        | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ACIPhysicalDomain, lookups=True)
class ACIPhysicalDomainFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIPhysicalDomain model."""

    aci_fabric: (
        Annotated[
            "ACIFabricFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_fabric_id: ID | None = strawberry_django.filter_field()
    aci_vlan_pool: (
        Annotated[
            "ACIVLANPoolFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_vlan_pool_id: ID | None = strawberry_django.filter_field()
    security_domains: (
        Annotated[
            "StringArrayLookup",
            strawberry.lazy("netbox.graphql.filter_lookups"),
        ]
        | None
    ) = strawberry_django.filter_field()
