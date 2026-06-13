# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from utilities.testing import TableTestCases

from ....tables.tenant.app_profiles import ACIAppProfileTable


class ACIAppProfileTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIAppProfileTable
