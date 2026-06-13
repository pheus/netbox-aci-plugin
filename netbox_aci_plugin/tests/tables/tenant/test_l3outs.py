# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from utilities.testing import TableTestCases

from ....tables.tenant.l3outs import (
    ACIExternalEndpointGroupTable,
    ACIExternalSubnetTable,
    ACIL3OutTable,
)


class ACIL3OutTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIL3OutTable


class ACIExternalEndpointGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIExternalEndpointGroupTable


class ACIExternalSubnetTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIExternalSubnetTable
