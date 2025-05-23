# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import strawberry_django

from .... import models
from ..mixins import ACIBaseFilterMixin

__all__ = ("ACITenantFilter",)


@strawberry_django.filter(models.ACITenant, lookups=True)
class ACITenantFilter(ACIBaseFilterMixin):
    """GraphQL filter definition for the ACITenant model."""

    pass
