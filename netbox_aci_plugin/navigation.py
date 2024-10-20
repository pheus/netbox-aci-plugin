# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

# ACI Tenant
acitenant_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:acitenant_list",
    link_text="Tenants",
    permissions=["netbox_aci_plugin.view_acitenant"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acitenant_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_aci_plugin.add_acitenant"],
        ),
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acitenant_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_aci_plugin.add_acitenant"],
        ),
    ),
)

# ACI Application Profile
aciappprofile_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:aciappprofile_list",
    link_text="Application Profiles",
    permissions=["netbox_aci_plugin.view_aciappprofile"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:aciappprofile_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_aci_plugin.add_aciappprofile"],
        ),
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:aciappprofile_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_aci_plugin.add_aciappprofile"],
        ),
    ),
)

# ACI Bridge Domain
acibd_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:acibridgedomain_list",
    link_text="Bridge Domains",
    permissions=["netbox_aci_plugin.view_acibridgedomain"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acibridgedomain_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_aci_plugin.add_acibridgedomain"],
        ),
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acibridgedomain_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_aci_plugin.add_acibridgedomain"],
        ),
    ),
)

# ACI Bridge Domain Subnet
acibdsubnet_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:acibridgedomainsubnet_list",
    link_text="Bridge Domain Subnets",
    permissions=["netbox_aci_plugin.view_acibridgedomainsubnet"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acibridgedomainsubnet_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_aci_plugin.add_acibridgedomainsubnet"],
        ),
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acibridgedomainsubnet_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_aci_plugin.add_acibridgedomainsubnet"],
        ),
    ),
)

# ACI Endpoint Group
aciendpointgroup_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:aciendpointgroup_list",
    link_text="Endpoint Groups",
    permissions=["netbox_aci_plugin.view_aciendpointgroup"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:aciendpointgroup_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_aci_plugin.add_aciendpointgroup"],
        ),
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:aciendpointgroup_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_aci_plugin.add_aciendpointgroup"],
        ),
    ),
)

# ACI VRF
acivrf_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:acivrf_list",
    link_text="VRFs",
    permissions=["netbox_aci_plugin.view_acivrf"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acivrf_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_aci_plugin.add_acivrf"],
        ),
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acivrf_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_aci_plugin.add_acivrf"],
        ),
    ),
)

# ACI Contract Filter
acicontractfilter_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:acicontractfilter_list",
    link_text="Contract Filters",
    permissions=["netbox_aci_plugin.view_acicontractfilter"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acicontractfilter_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_aci_plugin.add_acicontractfilter"],
        ),
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acicontractfilter_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_aci_plugin.add_acicontractfilter"],
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
                acicontractfilter_item,
            ),
        ),
    ),
    icon_class="mdi mdi-router",
)
