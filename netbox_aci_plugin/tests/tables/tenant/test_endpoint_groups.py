# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from utilities.testing import TableTestCases

from ....tables.tenant.endpoint_groups import (
    ACIEndpointGroupTable,
    ACIUSegEndpointGroupTable,
    ACIUSegNetworkAttributeTable,
)


class ACIEndpointGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIEndpointGroupTable


class ACIUSegEndpointGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIUSegEndpointGroupTable


class ACIUSegNetworkAttributeTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIUSegNetworkAttributeTable
