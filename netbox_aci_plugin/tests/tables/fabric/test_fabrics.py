# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from utilities.testing import TableTestCases

from ....tables.fabric.fabrics import ACIFabricTable


class ACIFabricTableTestCase(TableTestCases.StandardTableTestCase):
    table = ACIFabricTable
