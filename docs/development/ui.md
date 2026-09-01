# UI

Detail pages live under `netbox_aci_plugin/ui/panels/<domain>/<module>.py`,
one module per model layer file, mirroring `tables/` rather than the
aggregator layers (`models/`, `views/`, ...): panels are consumed only by
views, so each domain package stays a 0-byte `__init__.py` with direct
submodule imports (`from ...ui.panels.tenant.contracts import
ACIContractPanel`).

Two small partial groups survive from the old template-per-model layout
and are covered at the end of this page: `attrs/` (a handful of
`TemplatedAttr` fragments) and `buttons/` and `widgets/` (unrelated to
detail pages, see [Surviving partials](#surviving-partials)).

Reference examples:

- A plain domain: `netbox_aci_plugin/ui/panels/access_policies/vlan_pools.py`
  and `netbox_aci_plugin/views/access_policies/vlan_pools.py`.
- A GFK card: `netbox_aci_plugin/ui/panels/access_policies/aaep.py`
  (`ACIAAEPDomainBindingPanel`).
- A computed table card: `ACILeafSelectorView` and `ACILeafNodeBlockView`
  in `netbox_aci_plugin/views/access_policies/leaf_switch_profiles.py`.
- The conditional-action triad:
  `netbox_aci_plugin/ui/panels/fabric/node_interfaces.py`
  (`ACINodeInterfaceOverridePanel`) and `netbox_aci_plugin/ui/actions.py`.

## Layouts

Every detail view sets two class attributes:

```python
from netbox.ui import layout

template_name = "generic/object.html"
layout = layout.SimpleLayout(
    breadcrumbs=[...],
    left_panels=[...],
    right_panels=[...],
    bottom_panels=[...],
)
```

`template_name` is mandatory. `ObjectView.get_template_name()` falls back
to `<app_label>/<model_name>.html`, and this plugin keeps no per-model
detail template for that fallback to resolve, so a view without an
explicit `template_name` returns a 500. `generic/object.html` reads the
`layout` attribute directly; it is plain context, not a template block
override.

Always `layout.SimpleLayout`, never a bespoke `Layout`. `SimpleLayout`
auto-appends a `PluginContentPanel` to every column, which is what keeps
another installed plugin's `PluginTemplateExtension` hooks rendering on
a ported page. A bespoke `Layout` silently drops that panel.

`left_panels` and `right_panels` map to the page's two-column row,
exactly the `col col-md-6` pair the retired templates hand-rolled.
`bottom_panels` is a full-width row below it, for content that does not
fit the two-column layout (a wide entries table, for example).

## Panels

One `ObjectAttributesPanel` subclass per attribute card, declared in the
retired template's card order:

```python
from netbox.ui import attrs, panels

class ACIVLANPoolPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI VLAN Pool detail view."""

    title = _("ACI VLAN Pool")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    ...
```

Rules:

- **No shared panel base.** Every panel subclasses
  `panels.ObjectAttributesPanel` directly. `ObjectAttributesPanelMeta`
  builds a panel's attribute dict by walking base classes first and only
  then adding the class body's own declarations, so an inherited
  attribute always renders above a locally declared one, with no reorder
  hook. A shared base (`description`, `nb_tenant`, ...) would jump those
  rows to the top of every card that used it, regardless of where the
  retired template put them. Declaring every attribute inline, even when
  it repeats across panels, keeps row order under explicit control.
- **Always declare `title` explicitly**, copied verbatim from the
  retired card's header. The implicit title is `title(verbose_name)`
  (`utilities.string.title`), which title-cases the model's
  `verbose_name` and can mangle an embedded abbreviation (it turns "ACI
  uSeg Endpoint Group" into "ACI USeg Endpoint Group"). Do not rely on a
  verbose name happening to survive that transform unscathed.
- **Naming:** `ACI<Model>Panel` for the model's own card. A model with
  more than one card gives the extra ones a descriptive infix
  (`ACINodeInfrastructurePanel`, `ACIBridgeDomainRoutingPanel`).
- **Standard tail panels**, appended after the attribute cards in
  whichever column the retired template's include block sat in:
  `extras.ui.panels.CustomFieldsPanel()`,
  `netbox.ui.panels.TagsPanel()`,
  `netbox.ui.panels.CommentsPanel()`. Add
  `netbox.ui.panels.RelatedObjectsPanel()` only on a view that mixes in
  `utilities.views.GetRelatedModelsMixin` and returns `related_models`
  from `get_extra_context()` (see [Views - `GetRelatedModelsMixin` for
  cross-cutting counts](views.md#getrelatedmodelsmixin-for-cross-cutting-counts)).

### Hiding a panel that cannot have content

Override `should_render(context)` when the panel's backing query is
impossible for some objects, rather than letting the card render empty.
`ACINodeSwitchProfilesPanel` does this: only a leaf can sit in a Leaf
Switch Profile, so on a Spine or an APIC the card would otherwise
appear, headed with a leaf-only concept and holding nothing. Chain the
parent's check rather than replacing it, since the base class uses it
for its own permission gate, and give both branches a test:

```python
def should_render(self, context) -> bool:
    """Hide the card on Nodes whose role no Profile can cover."""
    return (
        super().should_render(context)
        and context["object"].role == NodeRoleChoices.ROLE_LEAF
    )
```

## Attribute mapping

| Retired template construct | Declarative attribute |
|---|---|
| plain value row | `attrs.TextAttr(accessor)` |
| a number | `attrs.NumericAttr(accessor)` |
| `\|linkify` FK row | `attrs.RelatedObjectAttr(accessor, linkify=True)` |
| `nb_tenant.group / nb_tenant` pair | `attrs.RelatedObjectAttr("nb_tenant", linkify=True, grouped_by="group")` |
| `get_x_display` badge | `attrs.ChoiceAttr("x")` (badged automatically when the model defines `get_x_color()`) |
| `{% checkmark %}` | `attrs.BooleanAttr(accessor)` |
| a list field (for example `security_domains`) | `attrs.ArrayAttr(accessor)` |
| a list of related objects | `attrs.RelatedObjectListAttr(accessor, linkify=True)` |
| GFK type + object row pair | one `attrs.GenericForeignKeyAttr(gfk_name, linkify=True)`, collapsing both rows into one |
| `\|placeholder` and empty values | automatic: every base attribute renders the placeholder dash for `None` or `""` |
| a computed or conditional value | a small partial under `templates/netbox_aci_plugin/attrs/` with `attrs.TemplatedAttr(accessor, template_name=...)`, or a plain model property read by a stock attr class |

Two traps worth naming:

- **A GFK's content type moves from an inline parenthesis to a muted
  sub-line**, and a GFK that the retired template split across two rows
  (a "type" row and an "object" row) collapses into the single
  `GenericForeignKeyAttr` row above. Reproducing the two-row layout is
  not supported and not attempted.
- **A property accessor gets no template-engine mercy.** Django's
  template engine silently swallows a `RelatedObjectDoesNotExist` on a
  reverse one-to-one; a Python attribute access does not. Route a
  reverse one-to-one or any other access that can legitimately be unset
  through a `None`-safe model property before wiring it to an attr,
  rather than letting the panel raise.

## Breadcrumbs

One `Breadcrumb` per ancestor level, in the order the retired template's
`breadcrumbs` block authored them:

```python
from netbox.ui.breadcrumbs import Breadcrumb, filtered_list_url

layout = layout.SimpleLayout(
    breadcrumbs=[
        Breadcrumb(
            "aci_fabric",
            url=filtered_list_url(
                "plugins:netbox_aci_plugin:acivlanpoolrange_list", "aci_fabric_id"
            ),
        ),
    ],
    ...
)
```

`filtered_list_url(viewname, filter_param)` reproduces exactly what the
old hand-rolled crumb did: link the ancestor's label to **this model's
own list view**, filtered by that ancestor's primary key, never to the
ancestor's own detail page. Confirm the filter param is a real field on
the target model's `FilterSet` before wiring it in.

The accessor resolves against the object being viewed:

- Pass a **plain string** when the model already exposes the ancestor as
  a direct FK or as one of its `aci_fabric` / `aci_tenant` shortcut
  properties (see [Models - Class
  hierarchy](models.md#class-hierarchy)). This is the common case.
- Pass a **lambda** (`lambda obj: obj.some_fk.some_other_fk`) when no
  such shortcut exists. Do not add a new model property solely to give a
  breadcrumb a one-hop accessor; the `aci_fabric` / `aci_tenant`
  shortcut contract does not extend to every intermediate ancestor, and
  a lambda is the established way to reach one anyway (see
  `ACINodeInterfaceView` and `ACILeafInterfaceOverrideView` for
  precedent).

## Panel actions

A panel's `actions=[...]` list renders in its card header, in the exact
chrome the retired templates' hand-rolled `card-actions` markup
imitated.

For a plain "Add" button, gated on the add permission and prefilling the
child form's cascading dropdowns:

```python
from netbox.ui import actions

actions = [
    actions.AddObject(
        "netbox_aci_plugin.ACIBridgeDomainSubnet",
        label=_("Add a Subnet"),
        url_params={
            "aci_bridge_domain": lambda ctx: ctx["object"].pk,
            "aci_vrf": lambda ctx: ctx["object"].aci_vrf_id,
        },
    ),
]
```

`actions.AddObject` derives the add view and the add permission from the
model label, accepts an optional `label=` override, and appends
`return_url` to the parent's detail page automatically. Every
`url_params` value is a callable receiving the template context, exactly
like a children tab's `add_child_action()` (see [Views - Parent-specific
children view](views.md#parent-specific-children-view)); the two are
independent constructs that happen to share the same calling
convention.

Stock `actions.LinkAction` cannot express a *conditional* action: its
`view_kwargs` are resolved once at construction and it has no visibility
hook beyond a permission check. Where a card needs a button that
switches between two states depending on the object (the ACI Node
Interface Leaf Interface Override triad: an Add link that must hide once
an Override exists, paired with Edit and Delete links that need the
opposite), use `netbox_aci_plugin.ui.actions.ACIObjectLinkAction`
instead. It adds two things stock `LinkAction` lacks:

- `view_kwargs` values may be callables receiving the template context,
  resolved in `get_url()`.
- An optional `condition` callable receiving the context gates
  `render()` before the permission check.

```python
from ...ui.actions import ACIObjectLinkAction

actions = [
    ACIObjectLinkAction(
        "plugins:netbox_aci_plugin:acileafinterfaceoverride_edit",
        condition=lambda ctx: ctx["object"].leaf_interface_override is not None,
        permissions=["netbox_aci_plugin.change_acileafinterfaceoverride"],
        label=_("Edit"),
        button_class="warning",
        button_icon="pencil",
        view_kwargs={"pk": lambda ctx: ctx["object"].leaf_interface_override.pk},
    ),
]
```

`ACIObjectLinkAction` carries no knowledge of any specific panel or
model; it is a generic extension of `LinkAction`. Reach for it only when
a card genuinely needs a condition beyond a permission check.

If a `LinkAction` (stock or `ACIObjectLinkAction`) needs an icon, set
`button_icon` explicitly. Only `actions.AddObject` sets a default one,
and the panel template renders the glyph only when it is set.

## Embedded child tables

Two panels render a child table on the parent's detail page, and the
choice between them is a cost and a data-shape question, not a style
preference:

- **`panels.ObjectsTablePanel(model, filters, include_columns,
  exclude_columns, actions=[...])`** for a child list the model's own
  `FilterSet` can already express. It renders only an htmx container;
  the rows load in a second request against the child's own list view,
  with that view's pagination, sorting, and per-user column
  preferences. It hides itself entirely for a user without `view`
  permission on the child model. `filters` values are callables
  (`{"aci_bridge_domain_id": lambda ctx: ctx["object"].pk}`), not
  accessor strings. Use `exclude_columns` to trim the child's standard
  columns back toward parity with what the retired card showed, and add
  `include_columns` too when the retired card kept a column the child's
  `default_columns` excludes.
- **`panels.ContextTablePanel(table, title=...)`** for a table no list
  filter can express, most often a computed membership set (a leaf node
  range, for example). The view keeps building the table itself in
  `get_extra_context()`, exactly as it did before the port, and the
  panel renders it eagerly in the same request and response, at the
  same cost as the old `{% render_table %}` include. `table` is either a
  context-key string or a `callable(context)`.

```python
def get_extra_context(self, request, instance) -> dict:
    """Return the resolved ACI Nodes as extra context."""
    aci_nodes_table = ACINodeReducedTable(
        instance.aci_nodes.restrict(request.user, "view").order_by("node_id")
    )
    aci_nodes_table.configure(request=request)
    return {"aci_nodes_table": aci_nodes_table}
```

```python
right_panels=[
    ContextTablePanel("aci_nodes_table", title=_("Resolved ACI Nodes")),
    ...
]
```

A `*ReducedTable` (see [Tables - Reduced
tables](tables.md#reduced-tables)) is the usual table class either panel
renders: the parent FK column is redundant on the parent's own detail
page.

**Object permissions can force the choice.** A `ContextTablePanel`
renders whatever its view put in the context, so that view has to call
`.restrict(request.user, "view")` itself and nothing enforces that it
did. An `ObjectsTablePanel` cannot get it wrong, because the rows come
from the child's own list view. An attribute row can never get it
right: `ObjectAttributesPanel.get_context()` passes each attr only
`name`, `perms` and `preferences`, so nothing in the attr chain ever
sees the request and no `RelatedObjectListAttr` can be restricted.

A resolved relation whose rows must respect object permissions
therefore needs a `FilterSet` key and an `ObjectsTablePanel`, even when
the relation is computed rather than stored.
`ACILeafSwitchProfileFilterSet.covering_aci_node_id` exists for that
reason: it resolves node-block coverage so the ACI Node page can list
its covering Profiles through the Profile list view instead of through
an attribute row. Give the filter method the model property to delegate
to, so the resolution rules stay in one place.

## Children tabs

A `ViewTab` child page is untouched by the declarative UI layer.
`generic.ObjectChildrenView` renders through `generic/object_children.html`
regardless of whether the parent's own detail page declares a `layout`,
and its "Add" button still goes through
`netbox_aci_plugin.object_actions.add_child_action()` and the
`AddChildObject` action class:

```python
from ...object_actions import add_child_action

actions = (
    add_child_action(
        "netbox_aci_plugin.ACIBridgeDomainSubnet",
        _("Add a BD Subnet"),
        url_params={
            "aci_bridge_domain": lambda ctx: ctx["object"].pk,
            "nb_tenant": lambda ctx: ctx["object"].nb_tenant_id,
        },
    ),
) + ACIBridgeDomainSubnetChildrenView.actions
```

See [Views - Children views (tabs)](views.md#children-views-tabs) for
the full base/parent-specific view split this action lives inside.

### Secondary-side parent-scope injection

When a child relation tab appears on the non-primary parent's detail
page (for example `ACIBridgeDomainL3OutBinding` listed from the L3Out
side), the "Add" button must inject the non-primary parent's scope
fields so the child form's cascading dropdowns prefill correctly. This
injection happens entirely in the view layer via `url_params` lambdas
on `add_child_action()`, the same construct shown above; no template is
involved (see [Forms - Single-mental-model relation
forms](forms.md#single-mental-model-relation-forms) for why the form
itself only models one parent side).

## Surviving partials

Two small groups of template fragments remain under
`templates/netbox_aci_plugin/`, and neither is a detail page:

- **`attrs/`**: a `TemplatedAttr`'s `template_name` fragment, for a row
  whose value needs more than a stock attr class can express (a
  compound object, a dynamic label). Keep the fragment minimal; it
  renders inside an existing attr-table row, not a full card.
- **`buttons/add_child.html`**: the anchor `AddChildObject` renders for
  a children tab's "Add" button, unrelated to panel actions above.
- **`widgets/`**: form-widget partials, such as
  `textinput_with_options.html`, rendered by a custom form field widget
  rather than by any view.

`netbox_aci_plugin/tests/ui/test_conventions.py` asserts that these
three directories are the only thing left under
`templates/netbox_aci_plugin/`; a new detail template placed there by
mistake fails that test.
