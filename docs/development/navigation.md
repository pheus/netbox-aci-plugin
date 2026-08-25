# Navigation

`navigation.py` registers one menu item per primary model, grouped into
sections that mirror the ACI policy tree. The structure is mechanical;
the value lies in keeping every entry consistent so contributors can
add a new model in seconds by copying the nearest neighbor.

## Menu items

One `PluginMenuItem` per model. Variable named `<modellower>_item`,
preceded by a `# <Verbose Model Name>` section comment.

```python
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
```

Rules:

- `link` points to the model's list view:
  `plugins:netbox_aci_plugin:<model>_list`.
- `link_text` is the plural verbose name as an **English literal**. The
  NetBox plugin menu does not translate these, so do not wrap with `_()`.
- `permissions` is `[netbox_aci_plugin.view_<model>]`.
- Buttons:
  - **Add** (`*_add`, `mdi mdi-plus-thick`): only when the add view
    exists.
  - **Import** (`*_bulk_import`, `mdi mdi-upload`): only when the bulk
    import view exists.
  - Button `permissions` uses the matching `add_<model>` codename.

## Menu groups

At the bottom of `navigation.py`, items are assembled into the plugin
menu via `PluginMenu(label=..., groups=(...))`. Each group is a
`(label, items_tuple)` pair; group labels are also English literals.

```python
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
        ...
    ),
    icon_class="mdi mdi-router",
)
```

Group order follows the ACI policy hierarchy (Tenants, Tenant
Application Profiles, Tenant Networking, Tenant External, Tenant
Contracts, Fabric Inventory, Fabric Policies, Fabric Access Policies),
not alphabetical. New groups go where they belong in the policy
hierarchy. The fabric split mirrors APIC's own: Inventory holds the
physical objects, Fabric Policies holds fabric-wide switch policy, and
Access Policies holds the interface and switch profile chain.

!!! note "Core helper caveat"
    NetBox core ships `get_model_item` / `get_model_buttons` helpers,
    but in NetBox 4.5 / 4.6 they build core `MenuItem` objects and
    non-plugin view names. They do not replace `PluginMenuItem` /
    `PluginMenuButton` for this plugin yet. Keep the manual plugin menu
    entries until NetBox exposes plugin-aware helpers.
