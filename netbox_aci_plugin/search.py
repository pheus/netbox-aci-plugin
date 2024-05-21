# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.search import SearchIndex, register_search

from .models.tenant_app_profiles import ACIAppProfile
from .models.tenant_networks import ACIVRF, ACIBridgeDomain
from .models.tenants import ACITenant


@register_search
class ACITenantIndex(SearchIndex):
    """NetBox search definition for ACI Tenant model."""

    model = ACITenant

    fields: tuple = (
        ("name", 100),
        ("alias", 300),
        ("description", 500),
    )
    display_attrs: tuple = (
        "name",
        "alias",
        "description",
        "nb_tenant",
    )


@register_search
class ACIAppProfileIndex(SearchIndex):
    """NetBox search definition for ACI Application Profile model."""

    model = ACIAppProfile

    fields: tuple = (
        ("name", 100),
        ("alias", 300),
        ("description", 500),
    )
    display_attrs: tuple = (
        "name",
        "alias",
        "description",
        "aci_tenant",
        "nb_tenant",
    )


@register_search
class ACIVRFIndex(SearchIndex):
    """NetBox search definition for ACI VRF model."""

    model = ACIVRF

    fields: tuple = (
        ("name", 100),
        ("alias", 300),
        ("description", 500),
    )
    display_attrs: tuple = (
        "name",
        "alias",
        "description",
        "aci_tenant",
        "nb_tenant",
        "nb_vrf",
    )


@register_search
class ACIBridgeDomainIndex(SearchIndex):
    """NetBox search definition for ACI Bridge Domain model."""

    model = ACIBridgeDomain

    fields: tuple = (
        ("name", 100),
        ("alias", 300),
        ("description", 500),
    )
    display_attrs: tuple = (
        "name",
        "alias",
        "description",
        "aci_vrf",
        "nb_tenant",
    )
