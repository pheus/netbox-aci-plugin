# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import strawberry
from netbox.graphql.filter_lookups import ArrayLookup

from .enums import ContractFilterTCPRulesEnum


@strawberry.input(
    one_of=True,
    description="Lookup for Array fields. Only one of the lookup fields can be set.",
)
class TCPRulesArrayLookup(ArrayLookup[ContractFilterTCPRulesEnum]):
    pass
