# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from utilities.testing import TableTestCases

from ....tables.tenant.contracts import (
    ACIContractRelationTable,
    ACIContractSubjectFilterTable,
    ACIContractSubjectTable,
    ACIContractTable,
)


class ACIContractTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIContractTable


class ACIContractRelationTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIContractRelationTable


class ACIContractSubjectTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIContractSubjectTable


class ACIContractSubjectFilterTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIContractSubjectFilterTable
