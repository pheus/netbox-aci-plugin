# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from .... import models
from ..mixins import ACIBaseFilterMixin

if TYPE_CHECKING:
    from ipam.graphql.filters import VRFFilter
    from netbox.graphql.filter_lookups import StringArrayLookup

    from ...enums import (
        VRFPCEnforcementDirectionEnum,
        VRFPCEnforcementPreferenceEnum,
    )
    from .tenants import ACITenantFilter


__all__ = ("ACIVRFFilter",)


@strawberry_django.filter(models.ACIVRF, lookups=True)
class ACIVRFFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIVRF model."""

    aci_tenant: (
        Annotated[
            "ACITenantFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_tenant_id: ID | None = strawberry_django.filter_field()
    nb_vrf: Annotated["VRFFilter", strawberry.lazy("ipam.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    nb_vrf_id: ID | None = strawberry_django.filter_field()
    bd_enforcement_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    dns_labels: (
        Annotated[
            "StringArrayLookup",
            strawberry.lazy("netbox.graphql.filter_lookups"),
        ]
        | None
    ) = strawberry_django.filter_field()
    ip_data_plane_learning_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    pc_enforcement_direction: (
        Annotated[
            "VRFPCEnforcementDirectionEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    pc_enforcement_preference: (
        Annotated[
            "VRFPCEnforcementPreferenceEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    pim_ipv4_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    pim_ipv6_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    preferred_group_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
