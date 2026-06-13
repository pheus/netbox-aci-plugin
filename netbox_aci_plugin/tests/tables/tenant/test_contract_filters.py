# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from utilities.testing import TableTestCases

from ....tables.tenant.contract_filters import (
    ACIContractFilterEntryTable,
    ACIContractFilterTable,
)


class ACIContractFilterTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIContractFilterTable


class ACIContractFilterEntryTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIContractFilterEntryTable
