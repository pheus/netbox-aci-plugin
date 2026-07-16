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
    from ipam.graphql.filters import VLANFilter

    from ...enums import DeploymentImmediacyEnum, PortModeEnum, ResolutionImmediacyEnum
    from ..access_policies.aaep import ACIAttachableAccessEntityProfileFilter
    from .endpoint_groups import ACIEndpointGroupFilter


__all__ = (
    "ACIEndpointGroupAAEPBindingFilter",
    "ACIEndpointGroupDomainBindingFilter",
)


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


@strawberry_django.filter_type(models.ACIEndpointGroupAAEPBinding, lookups=True)
class ACIEndpointGroupAAEPBindingFilter(NetBoxModelFilter):
    """GraphQL filter definition for ACIEndpointGroupAAEPBinding."""

    aci_endpoint_group: (
        Annotated[
            "ACIEndpointGroupFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_endpoint_group_id: ID | None = strawberry_django.filter_field()
    aci_aaep: (
        Annotated[
            "ACIAttachableAccessEntityProfileFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_aaep_id: ID | None = strawberry_django.filter_field()
    nb_vlan: Annotated["VLANFilter", strawberry.lazy("ipam.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    nb_vlan_id: ID | None = strawberry_django.filter_field()
    primary_nb_vlan: (
        Annotated["VLANFilter", strawberry.lazy("ipam.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    primary_nb_vlan_id: ID | None = strawberry_django.filter_field()
    mode: (
        BaseFilterLookup[
            Annotated[
                "PortModeEnum", strawberry.lazy("netbox_aci_plugin.graphql.enums")
            ]
        ]
        | None
    ) = strawberry_django.filter_field()
    deployment_immediacy: (
        BaseFilterLookup[
            Annotated[
                "DeploymentImmediacyEnum",
                strawberry.lazy("netbox_aci_plugin.graphql.enums"),
            ]
        ]
        | None
    ) = strawberry_django.filter_field()
