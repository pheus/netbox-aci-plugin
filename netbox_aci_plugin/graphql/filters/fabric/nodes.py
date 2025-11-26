# SPDX-FileCopyrightText: 2025 Martin Hauser
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
    from core.graphql.filters import ContentTypeFilter
    from ipam.graphql.filters import IPAddressFilter

    from ...enums import NodeRoleEnum, NodeTypeEnum
    from .pods import ACIPodFilter


__all__ = ("ACINodeFilter",)


@strawberry_django.filter(models.ACINode, lookups=True)
class ACINodeFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACINode model."""

    aci_pod: (
        Annotated["ACIPodFilter", strawberry.lazy("netbox_aci_plugin.graphql.filters")]
        | None
    ) = strawberry_django.filter_field()
    aci_pod_id: ID | None = strawberry_django.filter_field()
    node_id: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()
    node_object_type: (
        Annotated["ContentTypeFilter", strawberry.lazy("core.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    node_object_id: ID | None = strawberry_django.filter_field()
    role: (
        Annotated["NodeRoleEnum", strawberry.lazy("netbox_aci_plugin.graphql.enums")]
        | None
    ) = strawberry_django.filter_field()
    node_type: (
        Annotated["NodeTypeEnum", strawberry.lazy("netbox_aci_plugin.graphql.enums")]
        | None
    ) = strawberry_django.filter_field()
    tep_ip_address: (
        Annotated["IPAddressFilter", strawberry.lazy("ipam.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    tep_ip_address_id: ID | None = strawberry_django.filter_field()
