# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....tables.fabric.fabrics import ACIFabricTable
from .. import base


class ACIFabricTableTestCase(base.StandardTableTestCase):
    table = ACIFabricTable
