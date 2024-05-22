# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

# ACI Tenant
acitenant_buttons: tuple = (
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

# ACI Application Profile
aciappprofile_buttons: tuple = (
    PluginMenuButton(
        link="plugins:netbox_aci_plugin:aciappprofile_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    ),
)
aciappprofile_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:aciappprofile_list",
    link_text="Application Profiles",
    buttons=aciappprofile_buttons,
)

# ACI Bridge Domain
acibd_buttons: tuple = (
    PluginMenuButton(
        link="plugins:netbox_aci_plugin:acibridgedomain_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    ),
)
acibd_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:acibridgedomain_list",
    link_text="Bridge Domains",
    buttons=acibd_buttons,
)

# ACI VRF
acivrf_buttons: tuple = (
    PluginMenuButton(
        link="plugins:netbox_aci_plugin:acivrf_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    ),
)
acivrf_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:acivrf_list",
    link_text="VRFs",
    buttons=acivrf_buttons,
)

# Plugin Menu Items
menu = PluginMenu(
    label="ACI",
    groups=(
        (
            "Tenant",
            (
                acitenant_item,
                aciappprofile_item,
                acibd_item,
                acivrf_item,
            ),
        ),
    ),
    icon_class="mdi mdi-router",
)
