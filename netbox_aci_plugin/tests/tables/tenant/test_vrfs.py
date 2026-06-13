# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....tables.tenant.vrfs import ACIVRFTable
from .. import base


class ACIVRFTableTestCase(base.StandardTableTestCase):
    table = ACIVRFTable
