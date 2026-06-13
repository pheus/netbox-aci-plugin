# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from utilities.testing import TableTestCases

from ....tables.access_policies.domains import ACIRoutedDomainTable


class ACIRoutedDomainTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIRoutedDomainTable
