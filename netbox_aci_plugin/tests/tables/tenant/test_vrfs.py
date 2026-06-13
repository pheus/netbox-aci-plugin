# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from utilities.testing import TableTestCases

from ....tables.tenant.vrfs import ACIVRFTable


class ACIVRFTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIVRFTable
