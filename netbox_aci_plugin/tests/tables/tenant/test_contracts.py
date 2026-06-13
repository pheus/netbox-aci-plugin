# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....tables.tenant.contracts import (
    ACIContractRelationTable,
    ACIContractSubjectFilterTable,
    ACIContractSubjectTable,
    ACIContractTable,
)
from .. import base


class ACIContractTableTestCase(base.StandardTableTestCase):
    table = ACIContractTable


class ACIContractRelationTableTestCase(base.StandardTableTestCase):
    table = ACIContractRelationTable


class ACIContractSubjectTableTestCase(base.StandardTableTestCase):
    table = ACIContractSubjectTable


class ACIContractSubjectFilterTableTestCase(base.StandardTableTestCase):
    table = ACIContractSubjectFilterTable
