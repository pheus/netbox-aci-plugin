# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Table tests for fabric Node Interface models."""

from ....tables.fabric.node_interfaces import ACINodeInterfaceTable
from .. import base


class ACINodeInterfaceTableTestCase(base.StandardTableTestCase):
    table = ACINodeInterfaceTable
