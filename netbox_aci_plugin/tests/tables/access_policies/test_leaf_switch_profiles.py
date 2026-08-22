# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Table tests for access-policy Leaf Switch Profile models."""

from ....tables.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlockTable,
    ACILeafSelectorTable,
    ACILeafSwitchProfileInterfaceBindingTable,
    ACILeafSwitchProfileTable,
)
from .. import base


class ACILeafSwitchProfileTableTestCase(base.StandardTableTestCase):
    table = ACILeafSwitchProfileTable


class ACILeafSelectorTableTestCase(base.StandardTableTestCase):
    table = ACILeafSelectorTable


class ACILeafNodeBlockTableTestCase(base.StandardTableTestCase):
    table = ACILeafNodeBlockTable


class ACILeafSwitchProfileInterfaceBindingTableTestCase(base.StandardTableTestCase):
    table = ACILeafSwitchProfileInterfaceBindingTable
