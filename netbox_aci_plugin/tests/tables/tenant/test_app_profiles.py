# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Table tests for tenant Application Profile models."""

from ....tables.tenant.app_profiles import ACIAppProfileTable
from .. import base


class ACIAppProfileTableTestCase(base.StandardTableTestCase):
    table = ACIAppProfileTable
