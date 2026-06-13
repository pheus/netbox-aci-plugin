# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....tables.tenant.bridge_domains import (
    ACIBridgeDomainL3OutBindingTable,
    ACIBridgeDomainSubnetTable,
    ACIBridgeDomainTable,
)
from .. import base


class ACIBridgeDomainTableTestCase(base.StandardTableTestCase):
    table = ACIBridgeDomainTable


class ACIBridgeDomainSubnetTableTestCase(base.StandardTableTestCase):
    table = ACIBridgeDomainSubnetTable


class ACIBridgeDomainL3OutBindingTableTestCase(base.StandardTableTestCase):
    table = ACIBridgeDomainL3OutBindingTable
