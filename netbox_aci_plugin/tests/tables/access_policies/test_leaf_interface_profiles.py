# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Table tests for access-policy Leaf Interface Profile models."""

from ....tables.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfileTable,
    ACILeafInterfaceSelectorTable,
    ACILeafPortBlockTable,
)
from .. import base


class ACILeafInterfaceProfileTableTestCase(base.StandardTableTestCase):
    table = ACILeafInterfaceProfileTable


class ACILeafInterfaceSelectorTableTestCase(base.StandardTableTestCase):
    table = ACILeafInterfaceSelectorTable


class ACILeafPortBlockTableTestCase(base.StandardTableTestCase):
    table = ACILeafPortBlockTable
