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
    from ipam.graphql.filters import IPAddressFilter
    from netbox.graphql.filter_lookups import StringArrayLookup

    from ...enums import (
        BDMultiDestinationFloodingEnum,
        BDUnknownMulticastEnum,
        BDUnknownUnicastEnum,
    )
    from .tenants import ACITenantFilter
    from .vrfs import ACIVRFFilter


__all__ = (
    "ACIBridgeDomainFilter",
    "ACIBridgeDomainSubnetFilter",
)


@strawberry_django.filter(models.ACIBridgeDomain, lookups=True)
class ACIBridgeDomainFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIBridgeDomain model."""

    aci_tenant: (
        Annotated[
            "ACITenantFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_tenant_id: ID | None = strawberry_django.filter_field()
    aci_vrf: (
        Annotated[
            "ACIVRFFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_vrf_id: ID | None = strawberry_django.filter_field()
    advertise_host_routes_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    arp_flooding_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    clear_remote_mac_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    dhcp_labels: (
        Annotated[
            "StringArrayLookup",
            strawberry.lazy("netbox.graphql.filter_lookups"),
        ]
        | None
    ) = strawberry_django.filter_field()
    ep_move_detection_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    igmp_interface_policy_name: FilterLookup[str] | None = (
        strawberry_django.filter_field()
    )
    igmp_snooping_policy_name: FilterLookup[str] | None = (
        strawberry_django.filter_field()
    )
    ip_data_plane_learning_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    limit_ip_learn_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    mac_address: FilterLookup[str] | None = strawberry_django.filter_field()
    multi_destination_flooding: (
        Annotated[
            "BDMultiDestinationFloodingEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    pim_ipv4_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    pim_ipv4_destination_filter: FilterLookup[str] | None = (
        strawberry_django.filter_field()
    )
    pim_ipv4_source_filter: FilterLookup[str] | None = strawberry_django.filter_field()
    pim_ipv6_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    pim_ipv6_destination_filter: FilterLookup[str] | None = (
        strawberry_django.filter_field()
    )
    pim_ipv6_source_filter: FilterLookup[str] | None = strawberry_django.filter_field()
    unknown_ipv4_multicast: (
        Annotated[
            "BDUnknownMulticastEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    unknown_ipv6_multicast: (
        Annotated[
            "BDUnknownMulticastEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    unknown_unicast: (
        Annotated[
            "BDUnknownUnicastEnum",
            strawberry.lazy("netbox_aci_plugin.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    virtual_mac_address: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.ACIBridgeDomainSubnet, lookups=True)
class ACIBridgeDomainSubnetFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIBridgeDomainSubnet model."""

    aci_bridge_domain: (
        Annotated[
            "ACIBridgeDomainFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_bridge_domain_id: ID | None = strawberry_django.filter_field()
    gateway_ip_address: (
        Annotated["IPAddressFilter", strawberry.lazy("ipam.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    gateway_ip_address_id: ID | None = strawberry_django.filter_field()
    advertise_externally_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    igmp_querier_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    ip_data_plane_learning_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    no_default_gateway: FilterLookup[bool] | None = strawberry_django.filter_field()
    nd_ra_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    nd_ra_prefix_policy_name: FilterLookup[str] | None = (
        strawberry_django.filter_field()
    )
    preferred_ip_address_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    shared_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    virtual_ip_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
