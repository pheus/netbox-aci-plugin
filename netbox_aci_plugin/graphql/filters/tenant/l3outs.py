# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""GraphQL filters for tenant L3Out models."""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from django.db.models import Q
from netaddr.core import AddrFormatError
from netaddr.ip import IPNetwork
from strawberry.scalars import ID
from strawberry_django import BaseFilterLookup, FilterLookup

try:
    from strawberry_django import StrFilterLookup
except ImportError:  # pragma: no cover
    from strawberry_django import FilterLookup as StrFilterLookup

from .... import models
from ..mixins import ACIBaseFilterMixin

if TYPE_CHECKING:
    from ipam.graphql.filters import PrefixFilter

    from ...enums import QualityOfServiceClassEnum, QualityOfServiceDSCPEnum
    from ..access_policies.domains import ACIRoutedDomainFilter
    from .tenants import ACITenantFilter
    from .vrfs import ACIVRFFilter

__all__ = (
    "ACIExternalEndpointGroupFilter",
    "ACIExternalSubnetFilter",
    "ACIL3OutFilter",
)


@strawberry_django.filter_type(models.ACIL3Out, lookups=True)
class ACIL3OutFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIL3Out model."""

    aci_tenant: (
        Annotated[
            "ACITenantFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_tenant_id: ID | None = strawberry_django.filter_field()
    aci_vrf: (
        Annotated["ACIVRFFilter", strawberry.lazy("netbox_aci_plugin.graphql.filters")]
        | None
    ) = strawberry_django.filter_field()
    aci_vrf_id: ID | None = strawberry_django.filter_field()
    aci_routed_domain: (
        Annotated[
            "ACIRoutedDomainFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_routed_domain_id: ID | None = strawberry_django.filter_field()
    target_dscp: (
        BaseFilterLookup[
            Annotated[
                "QualityOfServiceDSCPEnum",
                strawberry.lazy("netbox_aci_plugin.graphql.enums"),
            ]
        ]
        | None
    ) = strawberry_django.filter_field()
    import_route_control_enforcement_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    export_route_control_enforcement_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    bgp_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    ospf_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    eigrp_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    l3_multicast_ipv4_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    l3_multicast_ipv6_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    multipod_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    bfd_policy_name: StrFilterLookup[str] | None = strawberry_django.filter_field()
    custom_qos_policy_name: StrFilterLookup[str] | None = (
        strawberry_django.filter_field()
    )
    egress_data_plane_policing_policy_name: StrFilterLookup[str] | None = (
        strawberry_django.filter_field()
    )
    eigrp_interface_policy_name: StrFilterLookup[str] | None = (
        strawberry_django.filter_field()
    )
    igmp_interface_policy_name: StrFilterLookup[str] | None = (
        strawberry_django.filter_field()
    )
    ingress_data_plane_policing_policy_name: StrFilterLookup[str] | None = (
        strawberry_django.filter_field()
    )
    interleak_route_map_name: StrFilterLookup[str] | None = (
        strawberry_django.filter_field()
    )
    ospf_external_policy_name: StrFilterLookup[str] | None = (
        strawberry_django.filter_field()
    )
    pim_policy_name: StrFilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ACIExternalEndpointGroup, lookups=True)
class ACIExternalEndpointGroupFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIExternalEndpointGroup model."""

    aci_l3out: (
        Annotated[
            "ACIL3OutFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_l3out_id: ID | None = strawberry_django.filter_field()
    qos_class: (
        BaseFilterLookup[
            Annotated[
                "QualityOfServiceClassEnum",
                strawberry.lazy("netbox_aci_plugin.graphql.enums"),
            ]
        ]
        | None
    ) = strawberry_django.filter_field()
    preferred_group_member_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    target_dscp: (
        BaseFilterLookup[
            Annotated[
                "QualityOfServiceDSCPEnum",
                strawberry.lazy("netbox_aci_plugin.graphql.enums"),
            ]
        ]
        | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ACIExternalSubnet, lookups=True)
class ACIExternalSubnetFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACIExternalSubnet model."""

    aci_external_endpoint_group: (
        Annotated[
            "ACIExternalEndpointGroupFilter",
            strawberry.lazy("netbox_aci_plugin.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    aci_external_endpoint_group_id: ID | None = strawberry_django.filter_field()
    matched_prefix: StrFilterLookup[str] | None = strawberry_django.filter_field()
    nb_prefix: (
        Annotated["PrefixFilter", strawberry.lazy("ipam.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    nb_prefix_id: ID | None = strawberry_django.filter_field()
    import_route_control_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    export_route_control_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    shared_route_control_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    import_security_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    shared_security_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    aggregate_import_route_control_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    aggregate_export_route_control_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    aggregate_shared_route_control_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    bgp_route_summarization_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    bgp_route_summarization_policy_name: StrFilterLookup[str] | None = (
        strawberry_django.filter_field()
    )
    ospf_route_summarization_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )
    ospf_route_summarization_policy_name: StrFilterLookup[str] | None = (
        strawberry_django.filter_field()
    )
    eigrp_route_summarization_enabled: FilterLookup[bool] | None = (
        strawberry_django.filter_field()
    )

    @strawberry_django.filter_field()
    def contains(self, value: list[str], prefix) -> Q:  # pragma: no cover
        """Return Q for prefixes containing any of the given subnets."""
        if not value:
            return Q()
        q = Q()
        for subnet in value:
            try:
                query = str(IPNetwork(subnet.strip()).cidr)
            except (AddrFormatError, ValueError):
                continue
            q |= Q(**{f"{prefix}matched_prefix__net_contains": query})
        return q
