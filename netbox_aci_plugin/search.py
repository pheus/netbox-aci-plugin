# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.search import SearchIndex, register_search

from .models.tenant.app_profiles import ACIAppProfile
from .models.tenant.bridge_domains import (
    ACIBridgeDomain,
    ACIBridgeDomainSubnet,
)
from .models.tenant.contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from .models.tenant.contracts import (
    ACIContract,
    ACIContractRelation,
    ACIContractSubject,
    ACIContractSubjectFilter,
)
from .models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
    ACIUSegNetworkAttribute,
)
from .models.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroup,
    ACIEsgEndpointGroupSelector,
    ACIEsgEndpointSelector,
)
from .models.tenant.tenants import ACITenant
from .models.tenant.vrfs import ACIVRF


@register_search
class ACITenantIndex(SearchIndex):
    """NetBox search definition for the ACI Tenant model."""

    model = ACITenant

    fields: tuple = (
        ("name", 100),
        ("name_alias", 300),
        ("description", 500),
    )
    display_attrs: tuple = (
        "name",
        "name_alias",
        "description",
        "nb_tenant",
    )


@register_search
class ACIAppProfileIndex(SearchIndex):
    """NetBox search definition for the ACI Application Profile model."""

    model = ACIAppProfile

    fields: tuple = (
        ("name", 100),
        ("name_alias", 300),
        ("description", 500),
    )
    display_attrs: tuple = (
        "name",
        "name_alias",
        "description",
        "aci_tenant",
        "nb_tenant",
    )


@register_search
class ACIVRFIndex(SearchIndex):
    """NetBox search definition for the ACI VRF model."""

    model = ACIVRF

    fields: tuple = (
        ("name", 100),
        ("name_alias", 300),
        ("description", 500),
    )
    display_attrs: tuple = (
        "name",
        "name_alias",
        "description",
        "aci_tenant",
        "nb_tenant",
        "nb_vrf",
    )


@register_search
class ACIBridgeDomainIndex(SearchIndex):
    """NetBox search definition for the ACI Bridge Domain model."""

    model = ACIBridgeDomain

    fields: tuple = (
        ("name", 100),
        ("name_alias", 300),
        ("description", 500),
    )
    display_attrs: tuple = (
        "name",
        "name_alias",
        "description",
        "aci_vrf",
        "nb_tenant",
    )


@register_search
class ACIBridgeDomainSubnetIndex(SearchIndex):
    """NetBox search definition for the ACI Bridge Domain Subnet model."""

    model = ACIBridgeDomainSubnet

    fields: tuple = (
        ("name", 100),
        ("name_alias", 300),
        ("description", 500),
    )
    display_attrs: tuple = (
        "name",
        "name_alias",
        "description",
        "aci_bridge_domain",
        "gateway_ip_address",
        "nb_tenant",
    )


@register_search
class ACIEndpointGroupIndex(SearchIndex):
    """NetBox search definition for the ACI Endpoint Group model."""

    model = ACIEndpointGroup

    fields: tuple = (
        ("name", 100),
        ("name_alias", 300),
        ("description", 500),
    )
    display_attrs: tuple = (
        "name",
        "name_alias",
        "description",
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
    )


@register_search
class ACIUSegEndpointGroupIndex(SearchIndex):
    """NetBox search definition for the ACI uSeg Endpoint Group model."""

    model = ACIUSegEndpointGroup

    fields: tuple = (
        ("name", 100),
        ("name_alias", 300),
        ("description", 500),
    )
    display_attrs: tuple = (
        "name",
        "name_alias",
        "description",
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
    )


@register_search
class ACIUSegNetworkAttributeIndex(SearchIndex):
    """NetBox search definition for the ACI uSeg Network Attribute model."""

    model = ACIUSegNetworkAttribute

    fields: tuple = (
        ("name", 100),
        ("name_alias", 300),
        ("description", 500),
        ("aci_useg_endpoint_group", 300),
        ("_ip_address", 300),
        ("_mac_address", 300),
        ("_prefix", 400),
    )
    display_attrs: tuple = (
        "name",
        "name_alias",
        "description",
        "aci_useg_endpoint_group",
        "attr_object",
        "nb_tenant",
    )


@register_search
class ACIEndpointSecurityGroupIndex(SearchIndex):
    """NetBox search definition for the ACI Endpoint Security Group model."""

    model = ACIEndpointSecurityGroup

    fields: tuple = (
        ("name", 100),
        ("name_alias", 300),
        ("description", 500),
    )
    display_attrs: tuple = (
        "name",
        "name_alias",
        "description",
        "aci_app_profile",
        "aci_vrf",
        "nb_tenant",
    )


@register_search
class ACIEsgEndpointGroupSelectorIndex(SearchIndex):
    """NetBox search definition for the ACI ESG EPG Selector model."""

    model = ACIEsgEndpointGroupSelector

    fields: tuple = (
        ("name", 100),
        ("name_alias", 300),
        ("description", 500),
        ("aci_endpoint_security_group", 300),
        ("_aci_endpoint_group", 400),
        ("_aci_useg_endpoint_group", 400),
    )
    display_attrs: tuple = (
        "name",
        "name_alias",
        "description",
        "aci_endpoint_security_group",
        "aci_epg_object",
        "nb_tenant",
    )


@register_search
class ACIEsgEndpointSelectorIndex(SearchIndex):
    """NetBox search definition for the ACI ESG Endpoint Selector model."""

    model = ACIEsgEndpointSelector

    fields: tuple = (
        ("name", 100),
        ("name_alias", 300),
        ("description", 500),
        ("aci_endpoint_security_group", 300),
        ("_ip_address", 400),
        ("_prefix", 400),
    )
    display_attrs: tuple = (
        "name",
        "name_alias",
        "description",
        "aci_endpoint_security_group",
        "ep_object",
        "nb_tenant",
    )


@register_search
class ACIContractFilterIndex(SearchIndex):
    """NetBox search definition for the ACI Contract Filter model."""

    model = ACIContractFilter

    fields: tuple = (
        ("name", 100),
        ("name_alias", 300),
        ("description", 500),
    )
    display_attrs: tuple = (
        "name",
        "name_alias",
        "description",
        "aci_tenant",
        "nb_tenant",
    )


@register_search
class ACIContractFilterEntryIndex(SearchIndex):
    """NetBox search definition for the ACI Contract Filter Entry model."""

    model = ACIContractFilterEntry

    fields: tuple = (
        ("name", 100),
        ("name_alias", 300),
        ("description", 500),
    )
    display_attrs: tuple = (
        "name",
        "name_alias",
        "description",
        "aci_contract_filter",
    )


@register_search
class ACIContractIndex(SearchIndex):
    """NetBox search definition for the ACI Contract model."""

    model = ACIContract

    fields: tuple = (
        ("name", 100),
        ("name_alias", 300),
        ("description", 500),
    )
    display_attrs: tuple = (
        "name",
        "name_alias",
        "description",
        "aci_tenant",
    )


@register_search
class ACIContractRelationIndex(SearchIndex):
    """NetBox search definition for the ACI Contract Relation model."""

    model = ACIContractRelation

    fields: tuple = (
        ("aci_contract", 100),
        ("_aci_endpoint_group", 300),
        ("_aci_useg_endpoint_group", 300),
        ("_aci_endpoint_security_group", 300),
        ("_aci_vrf", 400),
    )
    display_attrs: tuple = (
        "aci_contract",
        "aci_object",
        "role",
    )


@register_search
class ACIContractSubjectIndex(SearchIndex):
    """NetBox search definition for the ACI Contract Subject model."""

    model = ACIContractSubject

    fields: tuple = (
        ("name", 100),
        ("name_alias", 300),
        ("description", 500),
    )
    display_attrs: tuple = (
        "name",
        "name_alias",
        "description",
        "aci_contract",
    )


@register_search
class ACIContractSubjectFilterIndex(SearchIndex):
    """NetBox search definition for the ACI Contract Subject Filter model."""

    model = ACIContractSubjectFilter

    fields: tuple = (
        ("aci_contract_filter", 100),
        ("aci_contract_subject", 300),
    )
    display_attrs: tuple = (
        "aci_contract_filter",
        "aci_contract_subject",
    )
