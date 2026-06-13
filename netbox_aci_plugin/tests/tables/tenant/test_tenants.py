# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....tables.tenant.tenants import ACITenantTable
from .. import base


class ACITenantTableTestCase(base.StandardTableTestCase):
    table = ACITenantTable
