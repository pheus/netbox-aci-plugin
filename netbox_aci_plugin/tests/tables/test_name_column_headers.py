# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Guard tests for the table name column header convention."""

import importlib
import pkgutil

from django.test import SimpleTestCase

from netbox.tables import NetBoxTable

from ... import tables as tables_pkg

ACI_PREFIX_ALLOWED = {"ACI Tenant", "ACI VRF"}


def _aci_table_classes():
    """Imports all table modules and yields the plugin's table classes."""
    for module in pkgutil.walk_packages(
        tables_pkg.__path__, prefix=f"{tables_pkg.__name__}."
    ):
        importlib.import_module(module.name)
    seen = set()
    stack = [NetBoxTable]
    while stack:
        for subclass in stack.pop().__subclasses__():
            if subclass in seen:
                continue
            seen.add(subclass)
            stack.append(subclass)
            if subclass.__module__.startswith("netbox_aci_plugin."):
                yield subclass


class TableNameColumnHeaderTestCase(SimpleTestCase):
    """Test cases for the name column headers of all ACI tables."""

    def test_name_columns_have_explicit_short_headers(self) -> None:
        """Test that name columns set a short explicit verbose name."""
        for table_class in _aci_table_classes():
            name_column = table_class.base_columns.get("name")
            if name_column is None:
                continue
            with self.subTest(table=table_class.__name__):
                self.assertIsNotNone(
                    name_column.verbose_name,
                    "name column must set an explicit verbose_name",
                )
                header = str(name_column.verbose_name)
                if header not in ACI_PREFIX_ALLOWED:
                    self.assertFalse(
                        header.startswith("ACI "),
                        "name column header must not carry the ACI prefix",
                    )
