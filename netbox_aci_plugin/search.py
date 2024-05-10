# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.search import SearchIndex, register_search

from .models.tenant_app_profiles import ACIAppProfile
from .models.tenants import ACITenant


@register_search
class ACITenantIndex(SearchIndex):
    """NetBox search definition for ACI Tenant model."""

    model = ACITenant

    fields = (
        ("name", 100),
        ("alias", 300),
        ("description", 500),
        ("comments", 5000),
    )
    display_attrs = (
        "name",
        "alias",
        "description",
    )


@register_search
class ACIAppProfileIndex(SearchIndex):
    """NetBox search definition for ACI Application Profile model."""

    model = ACIAppProfile

    fields = (
        ("name", 100),
        ("alias", 300),
        ("description", 500),
        ("comments", 5000),
    )
    display_attrs = (
        "name",
        "alias",
        "description",
    )
