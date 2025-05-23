# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass

import strawberry_django
from netbox.graphql.filter_mixins import NetBoxModelFilterMixin
from strawberry_django import FilterLookup
from tenancy.graphql.filter_mixins import TenancyFilterMixin

__all__ = ("ACIBaseFilterMixin",)


@dataclass
class ACIBaseFilterMixin(TenancyFilterMixin, NetBoxModelFilterMixin):
    """Base GraphQL filter mixin for ACI models."""

    name: FilterLookup[str] | None = strawberry_django.filter_field()
    name_alias: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
