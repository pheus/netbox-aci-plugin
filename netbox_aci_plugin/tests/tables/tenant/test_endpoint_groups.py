# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....tables.tenant.endpoint_groups import (
    ACIEndpointGroupTable,
    ACIUSegEndpointGroupTable,
    ACIUSegNetworkAttributeTable,
)
from .. import base


class ACIEndpointGroupTableTestCase(base.StandardTableTestCase):
    table = ACIEndpointGroupTable


class ACIUSegEndpointGroupTableTestCase(base.StandardTableTestCase):
    table = ACIUSegEndpointGroupTable


class ACIUSegNetworkAttributeTableTestCase(base.StandardTableTestCase):
    table = ACIUSegNetworkAttributeTable
