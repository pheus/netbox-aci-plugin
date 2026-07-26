# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Table tests for access-policy Leaf Interface Policy Group models."""

from ....tables.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroupTable,
)
from .. import base


class ACILeafInterfacePolicyGroupTableTestCase(base.StandardTableTestCase):
    table = ACILeafInterfacePolicyGroupTable
