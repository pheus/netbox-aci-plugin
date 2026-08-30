# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Extensions contributed to NetBox's own GraphQL types.

Kept out of the ``graphql`` package, whose ``__init__`` assembles the core
types before these register. No module here may import a core GraphQL
module at import time.
"""

from .dcim import InterfaceTypeExtension
from .tenancy import TenantTypeExtension

__all__ = (
    "InterfaceTypeExtension",
    "TenantTypeExtension",
    "type_extensions",
)

type_extensions = [
    InterfaceTypeExtension,
    TenantTypeExtension,
]
