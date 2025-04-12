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
            link="plugins:netbox_aci_plugin:acitenant_bulk_import",
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
            link="plugins:netbox_aci_plugin:aciappprofile_bulk_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_aci_plugin.add_aciappprofile"],
        ),
    ),
)

# ACI Bridge Domain
acibridgedomain_item = PluginMenuItem(
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
            link="plugins:netbox_aci_plugin:acibridgedomain_bulk_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_aci_plugin.add_acibridgedomain"],
        ),
    ),
)

# ACI Bridge Domain Subnet
acibridgedomainsubnet_item = PluginMenuItem(
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
            link="plugins:netbox_aci_plugin:acibridgedomainsubnet_bulk_import",
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
            link="plugins:netbox_aci_plugin:aciendpointgroup_bulk_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_aci_plugin.add_aciendpointgroup"],
        ),
    ),
)

# ACI uSeg Endpoint Group
aciusegendpointgroup_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:aciusegendpointgroup_list",
    link_text="uSeg Endpoint Groups",
    permissions=["netbox_aci_plugin.vieusegw_aciendpointgroup"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:aciusegendpointgroup_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_aci_plugin.adduseg_aciendpointgroup"],
        ),
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:aciusegendpointgroup_bulk_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_aci_plugin.adduseg_aciendpointgroup"],
        ),
    ),
)

# ACI Endpoint Security Group
aciendpointsecuritygroup_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:aciendpointsecuritygroup_list",
    link_text="Endpoint Security Groups",
    permissions=["netbox_aci_plugin.view_aciendpointsecuritygroup"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:aciendpointsecuritygroup_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_aci_plugin.add_aciendpointsecuritygroup"],
        ),
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:aciendpointsecuritygroup_bulk_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_aci_plugin.add_aciendpointsecuritygroup"],
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
            link="plugins:netbox_aci_plugin:acivrf_bulk_import",
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
            link="plugins:netbox_aci_plugin:acicontractfilter_bulk_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_aci_plugin.add_acicontractfilter"],
        ),
    ),
)

# ACI Contract Filter Entry
acicontractfilterentry_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:acicontractfilterentry_list",
    link_text="Contract Filter Entries",
    permissions=["netbox_aci_plugin.view_acicontractfilterentry"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acicontractfilterentry_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_aci_plugin.add_acicontractfilterentry"],
        ),
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acicontractfilterentry_bulk_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_aci_plugin.add_acicontractfilterentry"],
        ),
    ),
)

# ACI Contract
acicontract_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:acicontract_list",
    link_text="Contract",
    permissions=["netbox_aci_plugin.view_acicontract"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acicontract_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_aci_plugin.add_acicontract"],
        ),
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acicontract_bulk_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_aci_plugin.add_acicontract"],
        ),
    ),
)

# ACI Contract Subject
acicontractsubject_item = PluginMenuItem(
    link="plugins:netbox_aci_plugin:acicontractsubject_list",
    link_text="Contract Subjects",
    permissions=["netbox_aci_plugin.view_acicontractsubject"],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acicontractsubject_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_aci_plugin.add_acicontractsubject"],
        ),
        PluginMenuButton(
            link="plugins:netbox_aci_plugin:acicontractsubject_bulk_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_aci_plugin.add_acicontractsubject"],
        ),
    ),
)

# Plugin Menu Items
menu = PluginMenu(
    label="ACI",
    groups=(
        (
            "Tenants",
            (acitenant_item,),
        ),
        (
            "Tenant Application Profiles",
            (
                aciappprofile_item,
                aciendpointgroup_item,
                aciusegendpointgroup_item,
                aciendpointsecuritygroup_item,
            ),
        ),
        (
            "Tenant Networking",
            (
                acibridgedomain_item,
                acibridgedomainsubnet_item,
                acivrf_item,
            ),
        ),
        (
            "Tenant Contracts",
            (
                acicontract_item,
                acicontractsubject_item,
                acicontractfilter_item,
                acicontractfilterentry_item,
            ),
        ),
    ),
    icon_class="mdi mdi-router",
)
