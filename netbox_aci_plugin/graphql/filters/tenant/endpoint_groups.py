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
    from ...enums import (
        QualityOfServiceClassEnum,
        USegAttributeMatchOperatorEnum,
        USegAttributeTypeEnum,
    )
    from .app_profiles import ACIAppProfileFilter
    from .bridge_domains import ACIBridgeDomainFilter


__all__ = (
    "ACIEndpointGroupFilter",
    "ACIUSegEndpointGroupFilter",
    "ACIUSegNetworkAttributeFilter",
)


@dataclass
class ACIEndpointGroupBaseFilterMixin(ACIBaseFilterMixin):
    """Base GraphQL filter mixin for ACI Endpoint Group models."""

    aci_app_profile: (
        Annotated[
            "ACIAppProfileFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_app_profile_id: ID | None = strawberry_django.filter_field()
    aci_bridge_domain: (
        Annotated[
            "ACIBridgeDomainFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_bridge_domain_id: ID | None = strawberry_django.filter_field()
    admin_shutdown: FilterLookup[bool] | None = strawberry_django.filter_field()
    custom_qos_policy_name: FilterLookup[str] | None = strawberry_django.filter_field()
    flood_in_encap_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    intra_epg_isolation_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    qos_class: (
        Annotated[
            "QualityOfServiceClassEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    preferred_group_member_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.ACIEndpointGroup, lookups=True)
class ACIEndpointGroupFilter(ACIEndpointGroupBaseFilterMixin):
    """GraphQL filter definition for the ACIEndpointGroup model."""

    proxy_arp_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.ACIUSegEndpointGroup, lookups=True)
class ACIUSegEndpointGroupFilter(ACIEndpointGroupBaseFilterMixin):
    """GraphQL filter definition for the ACIUSegEndpointGroup model."""

    match_operator: (
        Annotated[
            "USegAttributeMatchOperatorEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()


@dataclass
class ACIUSegAttributeBaseFilterMixin(ACIBaseFilterMixin):
    """Base GraphQL filter mixin for ACI uSeg Attribute models."""

    aci_useg_endpoint_group: (
        Annotated[
            "ACIUSegEndpointGroupFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_useg_endpoint_group_id: ID | None = strawberry_django.filter_field()
    type: (
        Annotated[
            "USegAttributeTypeEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter(models.ACIUSegNetworkAttribute, lookups=True)
class ACIUSegNetworkAttributeFilter(ACIUSegAttributeBaseFilterMixin):
    """GraphQL filter definition for the ACIUSegNetworkAttribute model."""

    attr_object_type: (
        Annotated["ContentTypeFilter", strawberry.lazy("core.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    attr_object_id: ID | None = strawberry_django.filter_field()
    use_epg_subnet: FilterLookup[bool] | None = strawberry_django.filter_field()
