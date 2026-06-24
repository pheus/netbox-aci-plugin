# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....tables.access_policies.domains import (
    ACIPhysicalDomainTable,
    ACIRoutedDomainTable,
)
from .. import base


class ACIRoutedDomainTableTestCase(base.StandardTableTestCase):
    table = ACIRoutedDomainTable


class ACIPhysicalDomainTableTestCase(base.StandardTableTestCase):
    table = ACIPhysicalDomainTable
