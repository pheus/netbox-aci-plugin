# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....tables.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroupTable,
    ACIEsgEndpointGroupSelectorTable,
    ACIEsgEndpointSelectorTable,
)
from .. import base


class ACIEndpointSecurityGroupTableTestCase(base.StandardTableTestCase):
    table = ACIEndpointSecurityGroupTable


class ACIEsgEndpointGroupSelectorTableTestCase(base.StandardTableTestCase):
    table = ACIEsgEndpointGroupSelectorTable


class ACIEsgEndpointSelectorTableTestCase(base.StandardTableTestCase):
    table = ACIEsgEndpointSelectorTable
