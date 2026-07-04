# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Table tests for access-policy AAEP models."""

from ....tables.access_policies.aaep import (
    ACIAAEPDomainBindingTable,
    ACIAttachableAccessEntityProfileTable,
)
from .. import base


class ACIAttachableAccessEntityProfileTableTestCase(base.StandardTableTestCase):
    table = ACIAttachableAccessEntityProfileTable


class ACIAAEPDomainBindingTableTestCase(base.StandardTableTestCase):
    table = ACIAAEPDomainBindingTable
