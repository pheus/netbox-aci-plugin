# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

# ACI Tenant
acitenant_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:acitenant_list",
    link_text="Tenants",
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acitenant_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
        ),
    ),
)

# ACI Application Profile
aciappprofile_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:aciappprofile_list",
    link_text="Application Profiles",
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:aciappprofile_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
        ),
    ),
)

# ACI Bridge Domain
acibd_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:acibridgedomain_list",
    link_text="Bridge Domains",
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acibridgedomain_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
        ),
    ),
)

# ACI Bridge Domain Subnet
acibdsubnet_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:acibridgedomainsubnet_list",
    link_text="Bridge Domain Subnets",
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acibridgedomainsubnet_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
        ),
    ),
)

# ACI Endpoint Group
aciendpointgroup_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:aciendpointgroup_list",
    link_text="Endpoint Groups",
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:aciendpointgroup_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
        ),
    ),
)

# ACI VRF
acivrf_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:acivrf_list",
    link_text="VRFs",
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acivrf_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
        ),
    ),
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
                aciendpointgroup_item,
                acibd_item,
                acibdsubnet_item,
                acivrf_item,
            ),
        ),
    ),
    icon_class="mdi mdi-router",
)
