# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from netbox.graphql.filters import NetBoxModelFilter
from strawberry import ID

try:
    from strawberry_django import StrFilterLookup
except ImportError:
    from strawberry_django import FilterLookup as StrFilterLookup

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import TreeNodeFilter
    from tenancy.graphql.filters import TenantFilter, TenantGroupFilter

__all__ = ("ACIBaseFilterMixin",)


@dataclass
class ACIBaseFilterMixin(NetBoxModelFilter):
    """Base GraphQL filter mixin for ACI models."""

    name: StrFilterLookup[str] | None = strawberry_django.filter_field()
    name_alias: StrFilterLookup[str] | None = strawberry_django.filter_field()
    description: StrFilterLookup[str] | None = strawberry_django.filter_field()

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
