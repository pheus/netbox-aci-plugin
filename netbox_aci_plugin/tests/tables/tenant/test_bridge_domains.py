# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from utilities.testing import TableTestCases

from ....tables.tenant.bridge_domains import (
    ACIBridgeDomainL3OutBindingTable,
    ACIBridgeDomainSubnetTable,
    ACIBridgeDomainTable,
)


class ACIBridgeDomainTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIBridgeDomainTable


class ACIBridgeDomainSubnetTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIBridgeDomainSubnetTable


class ACIBridgeDomainL3OutBindingTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIBridgeDomainL3OutBindingTable
