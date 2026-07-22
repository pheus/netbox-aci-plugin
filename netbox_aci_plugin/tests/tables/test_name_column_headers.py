# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Guard tests for the table column header conventions."""

import importlib
import pkgutil
import re

from django.test import SimpleTestCase

from netbox.tables import NetBoxTable

from ... import tables as tables_pkg

ACI_PREFIX_ALLOWED_RE = re.compile(r"^ACI (Tenant|VRF)( \([^)]+\))?$")


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


def _aci_collision_family(column_name: str) -> str | None:
    """Returns the NetBox-core collision family of a column name."""
    # Property-backed columns carry no resolvable accessor, so the
    # collision family keys on the column name instead of the binding.
    if not column_name.startswith("aci_"):
        return None
    if column_name == "aci_tenant" or column_name.endswith("_tenant"):
        return "ACI Tenant"
    if column_name == "aci_vrf" or column_name.endswith("_vrf"):
        return "ACI VRF"
    return None


class TableNameColumnHeaderTestCase(SimpleTestCase):
    """Test cases for the column header conventions of all ACI tables."""

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
                if not ACI_PREFIX_ALLOWED_RE.match(header):
                    self.assertFalse(
                        header.startswith("ACI "),
                        "name column header must not carry the ACI prefix",
                    )

    def test_columns_do_not_carry_unwarranted_aci_prefix(self) -> None:
        """Test that column headers do not carry an unwarranted ACI prefix."""
        for table_class in _aci_table_classes():
            for column_name, column in table_class.base_columns.items():
                if column_name == "name" or column.verbose_name is None:
                    continue
                header = str(column.verbose_name)
                if not header.startswith("ACI "):
                    continue
                family = _aci_collision_family(column_name)
                if (
                    family is not None
                    and header.startswith(family)
                    and ACI_PREFIX_ALLOWED_RE.match(header)
                ):
                    continue
                with self.subTest(table=table_class.__name__, column=column_name):
                    self.fail(
                        f"column {column_name!r} header {header!r} must not "
                        "carry the ACI prefix without a NetBox-core collision"
                    )

    def test_core_collision_columns_keep_the_aci_prefix(self) -> None:
        """Test that Tenant and VRF columns keep the ACI prefix."""
        for table_class in _aci_table_classes():
            for column_name, column in table_class.base_columns.items():
                family = _aci_collision_family(column_name)
                if family is None or column.verbose_name is None:
                    continue
                header = str(column.verbose_name)
                with self.subTest(table=table_class.__name__, column=column_name):
                    self.assertTrue(
                        header.startswith(family),
                        f"column {column_name!r} header {header!r} must "
                        f"carry the {family} prefix (NetBox-core collision)",
                    )
