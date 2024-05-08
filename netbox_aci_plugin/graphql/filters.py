# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later


import strawberry_django
from netbox.graphql.filter_mixins import BaseFilterMixin, autotype_decorator

from ..filtersets.tenants import ACITenantFilterSet
from ..models.tenants import ACITenant


@strawberry_django.filter(ACITenant, lookups=True)
@autotype_decorator(ACITenantFilterSet)
class ACITenantFilter(BaseFilterMixin):
    """GraphQL filter definition for ACITenant model."""

    pass
