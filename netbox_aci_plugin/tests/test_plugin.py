# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.conf import settings
from django.test import TestCase
from netbox.plugins.navigation import PluginMenu, PluginMenuItem
from netbox.registry import registry


class PluginTest(TestCase):
    """Test case for plugin integration in NetBox."""

    config_name: str = "ACIConfig"
    menu_group_count: int = 1
    menu_name: str = "ACI"
    menu_tenant_item_count = 7

    def test_configuration(self) -> None:
        """Test for plugin configuration in NetBox."""
        self.assertIn(
            f"netbox_aci_plugin.{self.config_name}", settings.INSTALLED_APPS
        )

    def test_menu(self) -> None:
        """Test for main menu entry of plugin in NetBox UI."""
        menu_plugin_reg = registry["plugins"]["menus"][0]
        self.assertIsInstance(menu_plugin_reg, PluginMenu)
        self.assertEqual(menu_plugin_reg.label, self.menu_name)

    def test_menu_items(self) -> None:
        """Test for sub menu entries of plugin in NetBox UI."""
        menu_plugin_reg_groups = registry["plugins"]["menus"][0].groups
        self.assertEqual(len(menu_plugin_reg_groups), self.menu_group_count)
        self.assertEqual(menu_plugin_reg_groups[0].label, "Tenant")
        self.assertEqual(
            len(menu_plugin_reg_groups[0].items), self.menu_tenant_item_count
        )
        self.assertIsInstance(
            menu_plugin_reg_groups[0].items[0], PluginMenuItem
        )
