# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Table tests for fabric VPC Protection Group models."""

from ....tables.fabric.vpc_protection_groups import ACIVPCProtectionGroupTable
from .. import base


class ACIVPCProtectionGroupTableTestCase(base.StandardTableTestCase):
    table = ACIVPCProtectionGroupTable
