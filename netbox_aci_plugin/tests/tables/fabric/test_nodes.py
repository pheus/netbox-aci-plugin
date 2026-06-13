# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....tables.fabric.nodes import ACINodeTable
from .. import base


class ACINodeTableTestCase(base.StandardTableTestCase):
    table = ACINodeTable
