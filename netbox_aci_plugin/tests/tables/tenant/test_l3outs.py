# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....tables.tenant.l3outs import (
    ACIExternalEndpointGroupTable,
    ACIExternalSubnetTable,
    ACIL3OutTable,
)
from .. import base


class ACIL3OutTableTestCase(base.StandardTableTestCase):
    table = ACIL3OutTable


class ACIExternalEndpointGroupTableTestCase(base.StandardTableTestCase):
    table = ACIExternalEndpointGroupTable


class ACIExternalSubnetTableTestCase(base.StandardTableTestCase):
    table = ACIExternalSubnetTable
