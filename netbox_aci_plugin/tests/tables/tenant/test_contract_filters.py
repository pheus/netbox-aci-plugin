# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....tables.tenant.contract_filters import (
    ACIContractFilterEntryTable,
    ACIContractFilterTable,
)
from .. import base


class ACIContractFilterTableTestCase(base.StandardTableTestCase):
    table = ACIContractFilterTable


class ACIContractFilterEntryTableTestCase(base.StandardTableTestCase):
    table = ACIContractFilterEntryTable
