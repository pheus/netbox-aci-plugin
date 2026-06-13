# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from utilities.testing import TableTestCases

from ....tables.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroupTable,
    ACIEsgEndpointGroupSelectorTable,
    ACIEsgEndpointSelectorTable,
)


class ACIEndpointSecurityGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIEndpointSecurityGroupTable


class ACIEsgEndpointGroupSelectorTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIEsgEndpointGroupSelectorTable


class ACIEsgEndpointSelectorTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIEsgEndpointSelectorTable
