# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import ComparisonFilterLookup, StrFilterLookup

from netbox.graphql.filters import NetBoxModelFilter

from .... import models

if TYPE_CHECKING:
    from dcim.graphql.filters import InterfaceFilter
    from netbox.graphql.filter_lookups import TreeNodeFilter
    from tenancy.graphql.filters import TenantFilter, TenantGroupFilter

    from .nodes import ACINodeFilter


__all__ = ("ACINodeInterfaceFilter",)


@strawberry_django.filter_type(models.ACINodeInterface, lookups=True)
class ACINodeInterfaceFilter(NetBoxModelFilter):
    """GraphQL filter definition for the ACINodeInterface model."""

    aci_node: (
        Annotated["ACINodeFilter", strawberry.lazy("netbox_aci_plugin.graphql.filters")]
        | None
    ) = strawberry_django.filter_field()
    aci_node_id: ID | None = strawberry_django.filter_field()
    nb_interface: (
        Annotated["InterfaceFilter", strawberry.lazy("dcim.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    nb_interface_id: ID | None = strawberry_django.filter_field()
    module: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()
    port: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()
    sub_port: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()
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
