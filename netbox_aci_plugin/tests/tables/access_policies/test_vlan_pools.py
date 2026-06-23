# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....tables.access_policies.vlan_pools import (
    ACIVLANPoolRangeTable,
    ACIVLANPoolTable,
)
from .. import base


class ACIVLANPoolTableTestCase(base.StandardTableTestCase):
    table = ACIVLANPoolTable


class ACIVLANPoolRangeTableTestCase(base.StandardTableTestCase):
    table = ACIVLANPoolRangeTable
