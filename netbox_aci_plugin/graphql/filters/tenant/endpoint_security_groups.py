# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from core.graphql.filters import ContentTypeFilter
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from .... import models
from ..mixins import ACIBaseFilterMixin

if TYPE_CHECKING:
    from .app_profiles import ACIAppProfileFilter
    from .vrfs import ACIVRFFilter


__all__ = (
    "ACIEndpointSecurityGroupFilter",
    "ACIEsgEndpointGroupSelectorFilter",
    "ACIEsgEndpointSelectorFilter",
)


@strawberry_django.filter(models.ACIEndpointSecurityGroup, lookups=True)
class ACIEndpointSecurityGroupFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIEndpointSecurityGroup model."""

    aci_app_profile: (
        Annotated[
            "ACIAppProfileFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_app_profile_id: ID | None = strawberry_django.filter_field()
    aci_vrf: (
        Annotated[
            "ACIVRFFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_vrf_id: ID | None = strawberry_django.filter_field()
    admin_shutdown: FilterLookup[bool] | None = strawberry_django.filter_field()
    intra_esg_isolation_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    preferred_group_member_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class ACIEsgSelectorBaseFilterMixin(ACIBaseFilterMixin):
    """Base GraphQL filter mixin for ACI ESG Selector models."""

    aci_endpoint_security_group: (
        Annotated[
            "ACIEndpointSecurityGroupFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_endpoint_security_group_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter(models.ACIEsgEndpointGroupSelector, lookups=True)
class ACIEsgEndpointGroupSelectorFilter(ACIEsgSelectorBaseFilterMixin):
    """GraphQL filter definition for the ACIEsgEndpointGroupSelector model."""

    aci_epg_object_type: (
        Annotated["ContentTypeFilter", strawberry.lazy("core.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    aci_epg_object_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter(models.ACIEsgEndpointSelector, lookups=True)
class ACIEsgEndpointSelectorFilter(ACIEsgSelectorBaseFilterMixin):
    """GraphQL filter definition for the ACIEsgEndpointSelector model."""

    ep_object_type: (
        Annotated["ContentTypeFilter", strawberry.lazy("core.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    ep_object_id: ID | None = strawberry_django.filter_field()
