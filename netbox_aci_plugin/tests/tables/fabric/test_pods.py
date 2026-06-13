# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from utilities.testing import TableTestCases

from ....tables.fabric.pods import ACIPodTable


class ACIPodTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIPodTable
