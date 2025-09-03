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
    menu_group_count: int = 4
    menu_name: str = "ACI"
    # Menu group: Tenants
    menu_group_tenants_item_count: int = 1
    # Menu group: Tenant Application Profiles
    menu_group_tenant_app_profiles_item_count: int = 4
    # Menu group: Tenant Contracts
    menu_group_tenant_contracts_item_count: int = 4
    # Menu group: Tenant Networking
    menu_group_tenant_networking_item_count: int = 3

    def test_configuration(self) -> None:
        """Test for plugin configuration in NetBox."""
        self.assertIn(f"netbox_aci_plugin.{self.config_name}", settings.INSTALLED_APPS)

    def test_menu(self) -> None:
        """Test for the main menu entry of the plugin in NetBox UI."""
        menu_plugin_reg = registry["plugins"]["menus"][0]
        self.assertIsInstance(menu_plugin_reg, PluginMenu)
        self.assertEqual(menu_plugin_reg.label, self.menu_name)

    def test_menu_group_items(self) -> None:
        """Test for submenu entries of the plugin in NetBox UI."""
        menu_plugin_reg_groups = registry["plugins"]["menus"][0].groups
        self.assertEqual(len(menu_plugin_reg_groups), self.menu_group_count)

    def test_menu_group_tenants_items(self) -> None:
        """Test for group 0 submenu entries of the plugin in NetBox UI."""
        menu_plugin_reg_groups = registry["plugins"]["menus"][0].groups
        # Menu group: Tenants
        self.assertEqual(menu_plugin_reg_groups[0].label, "Tenants")
        self.assertEqual(
            len(menu_plugin_reg_groups[0].items),
            self.menu_group_tenants_item_count,
        )
        self.assertIsInstance(menu_plugin_reg_groups[0].items[0], PluginMenuItem)

    def test_menu_group_tenant_appprofiles_items(self) -> None:
        """Test for group 1 submenu entries of the plugin in NetBox UI."""
        menu_plugin_reg_groups = registry["plugins"]["menus"][0].groups
        # Menu group: Tenants
        self.assertEqual(menu_plugin_reg_groups[1].label, "Tenant Application Profiles")
        self.assertEqual(
            len(menu_plugin_reg_groups[1].items),
            self.menu_group_tenant_app_profiles_item_count,
        )
        self.assertIsInstance(menu_plugin_reg_groups[1].items[0], PluginMenuItem)

    def test_menu_group_tenant_networking_items(self) -> None:
        """Test for group 2 submenu entries of the plugin in NetBox UI."""
        menu_plugin_reg_groups = registry["plugins"]["menus"][0].groups
        # Menu group: Tenants
        self.assertEqual(menu_plugin_reg_groups[2].label, "Tenant Networking")
        self.assertEqual(
            len(menu_plugin_reg_groups[2].items),
            self.menu_group_tenant_networking_item_count,
        )
        self.assertIsInstance(menu_plugin_reg_groups[2].items[0], PluginMenuItem)

    def test_menu_group_tenant_contracts_items(self) -> None:
        """Test for group 3 submenu entries of the plugin in NetBox UI."""
        menu_plugin_reg_groups = registry["plugins"]["menus"][0].groups
        # Menu group: Tenants
        self.assertEqual(menu_plugin_reg_groups[3].label, "Tenant Contracts")
        self.assertEqual(
            len(menu_plugin_reg_groups[3].items),
            self.menu_group_tenant_contracts_item_count,
        )
        self.assertIsInstance(menu_plugin_reg_groups[3].items[0], PluginMenuItem)
