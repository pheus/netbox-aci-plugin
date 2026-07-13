# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Table tests for ACI Endpoint Group domain bindings."""

from ....tables.tenant.endpoint_group_bindings import (
    ACIEndpointGroupAAEPBindingTable,
    ACIEndpointGroupDomainBindingTable,
)
from .. import base


class ACIEndpointGroupDomainBindingTableTestCase(base.StandardTableTestCase):
    table = ACIEndpointGroupDomainBindingTable


class ACIEndpointGroupAAEPBindingTableTestCase(base.StandardTableTestCase):
    table = ACIEndpointGroupAAEPBindingTable
