# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from dcim.graphql.filter_mixins import ScopedFilterMixin
from netbox.graphql.filters import NetBoxModelFilter
from strawberry.scalars import ID
from strawberry_django import ComparisonFilterLookup, FilterLookup

from .... import models

if TYPE_CHECKING:
    from ipam.graphql.filters import PrefixFilter, VLANFilter
    from netbox.graphql.filter_lookups import TreeNodeFilter
    from tenancy.graphql.filters import TenantFilter, TenantGroupFilter


__all__ = ("ACIFabricFilter",)


@strawberry_django.filter(models.ACIFabric, lookups=True)
class ACIFabricFilter(ScopedFilterMixin, NetBoxModelFilter):
    """GraphQL filter definition for the ACIFabric model."""

    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    fabric_id: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()
    infra_vlan_vid: ComparisonFilterLookup[int] | None = (
        strawberry_django.filter_field()
    )
    infra_vlan: (
        Annotated["VLANFilter", strawberry.lazy("ipam.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    infra_vlan_id: ID | None = strawberry_django.filter_field()
    gipo_pool: (
        Annotated["PrefixFilter", strawberry.lazy("ipam.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    gipo_pool_id: ID | None = strawberry_django.filter_field()
    nb_tenant: (
        Annotated["TenantFilter", strawberry.lazy("tenancy.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    nb_tenant_id: ID | None = strawberry_django.filter_field()
    nb_tenant_group: (
        Annotated["TenantGroupFilter", strawberry.lazy("tenancy.graphql.filters")]
        | None
    ) = strawberry_django.filter_field()
    nb_tenant_group_id: (
        Annotated["TreeNodeFilter", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
