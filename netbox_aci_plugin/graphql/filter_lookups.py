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
    """Represents a specialized lookup functionality for TCP rules in an array.

    This class is used to perform lookups on array fields specifically designed
    for TCP rules.
    It enforces that only one of the lookup fields can be set at a time,
    ensuring clearer and more valid querying operations.
    """

    pass
