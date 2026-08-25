# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Table tests for the access-policy Leaf Interface Override model."""

from ....tables.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverrideTable,
)
from .. import base


class ACILeafInterfaceOverrideTableTestCase(base.StandardTableTestCase):
    table = ACILeafInterfaceOverrideTable
