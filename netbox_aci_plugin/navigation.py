# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

# ACI Tenant
acitenant_buttons = (
    PluginMenuButton(
        link="plugins:netbox_aci_plugin:acitenant_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    ),
)
acitenant_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:acitenant_list",
    link_text="Tenants",
    buttons=acitenant_buttons,
)

# Plugin Menu Items
menu = PluginMenu(
    label="ACI",
    groups=(("Tenant", (acitenant_item,)),),
    icon_class="mdi mdi-router",
)
