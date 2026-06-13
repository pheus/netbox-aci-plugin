# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....tables.fabric.pods import ACIPodTable
from .. import base


class ACIPodTableTestCase(base.StandardTableTestCase):
    table = ACIPodTable
