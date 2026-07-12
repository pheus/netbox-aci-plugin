# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import BaseFilterLookup

from netbox.graphql.filters import NetBoxModelFilter

from .... import models

if TYPE_CHECKING:
    from core.graphql.filters import ContentTypeFilter

    from ...enums import DeploymentImmediacyEnum, ResolutionImmediacyEnum


__all__ = ("ACIEndpointGroupDomainBindingFilter",)


@strawberry_django.filter_type(models.ACIEndpointGroupDomainBinding, lookups=True)
class ACIEndpointGroupDomainBindingFilter(NetBoxModelFilter):
    """GraphQL filter definition for ACIEndpointGroupDomainBinding."""

    aci_epg_object_type: (
        Annotated["ContentTypeFilter", strawberry.lazy("core.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    aci_epg_object_id: ID | None = strawberry_django.filter_field()
    aci_domain_object_type: (
        Annotated["ContentTypeFilter", strawberry.lazy("core.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    aci_domain_object_id: ID | None = strawberry_django.filter_field()
    deployment_immediacy: (
        BaseFilterLookup[
            Annotated[
                "DeploymentImmediacyEnum",
                strawberry.lazy("netbox_aci_plugin.graphql.enums"),
            ]
        ]
        | None
    ) = strawberry_django.filter_field()
    resolution_immediacy: (
        BaseFilterLookup[
            Annotated[
                "ResolutionImmediacyEnum",
                strawberry.lazy("netbox_aci_plugin.graphql.enums"),
            ]
        ]
        | None
    ) = strawberry_django.filter_field()
