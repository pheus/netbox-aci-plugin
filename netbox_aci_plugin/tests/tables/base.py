# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

try:
    from utilities.testing import TableTestCases

    StandardTableTestCase = TableTestCases.StandardTableTestCase
except ImportError:  # NetBox < 4.5.10 ships no table test base
    from django.test import SimpleTestCase as StandardTableTestCase  # noqa: F401
