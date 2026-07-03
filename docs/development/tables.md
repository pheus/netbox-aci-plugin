# Tables

Tables live under `netbox_aci_plugin/tables/<domain>/<model>.py`. Every
table extends `netbox.tables.NetBoxTable` and uses
`netbox.tables.columns` plus `django_tables2.Column` for column
declarations.

## Column conventions

### `accessor` over `render_*`

For FK traversal (e.g. showing the grandparent fabric on a child
table), prefer `accessor="parent__grandparent"` over a custom
`render_<column>()` method:

```python
aci_fabric = tables.Column(
    verbose_name=_("ACI Fabric"),
    accessor="aci_tenant__aci_fabric",
    linkify=True,
)
```

`accessor` is declarative, works with sorting and CSV export
automatically, and stays in one place. Reach for `render_*` only when
the cell needs computed HTML that `accessor` can't express.

### Linkify FKs and identifier columns

Use `linkify=True` on the `name`, `name_alias`, and any FK column.
NetBox's table machinery routes the link to the related object's
detail page automatically.

## Column-type catalog

Use these column classes consistently:

- `tables.Column`: plain string and FK fields. Pair it with `accessor`
  for traversal and `linkify=True` for clickability.
- `columns.BooleanColumn`: every `_enabled` / `_disabled` boolean field.
  Always pass a short `verbose_name`; the model's verbose name is too
  long for a table header.
- `columns.ChoiceFieldColumn`: any field backed by a `ChoiceSet`. It
  renders the badge with the color from `get_<field>_color()`.
- `columns.ArrayColumn`: list-typed fields such as `dhcp_labels`.
- `columns.TagColumn`: the model's `tags` ManyToMany. This is the
  second-to-last column (immediately before `comments`).
- `columns.MarkdownColumn`: the model's `comments` field. This is the
  standard last column.
- `columns.TemplateColumn`: cells that need composed HTML, such as
  nested links or conditional badges. Pair it with a module-level
  `template_code = """..."""` literal.

### `ArrayColumn` for `ArrayField` data

For model fields backed by Django's `ArrayField` (e.g.
`security_domains`, `dhcp_labels`), use `columns.ArrayColumn()`
instead of `tables.Column()` with a custom `render_*` method.
`ArrayColumn` handles comma-separated rendering automatically.

### `BooleanColumn` verbose-name shortening

Model boolean fields use verbose names like
`_("preferred group member enabled")`: descriptive but too long for a
table header. Inside the column declaration, drop the `enabled` suffix
and abbreviate where natural:

```python
arp_flooding_enabled = columns.BooleanColumn(verbose_name=_("ARP flooding"))
clear_remote_mac_enabled = columns.BooleanColumn(verbose_name=_("Clear remote MAC"))
ep_move_detection_enabled = columns.BooleanColumn(verbose_name=_("EP move detect"))
ip_data_plane_learning_enabled = columns.BooleanColumn(verbose_name=_("DP learning"))
```

See `tables/tenant/bridge_domains.py` for the full set of standard
abbreviations.

### `TemplateColumn` patterns

For inlined child renderings (e.g. "show all subnets of this BD in one
cell"), define a `template_code` literal near the top of the table
file and reference it from the column:

```python
BRIDGEDOMAIN_SUBNETS = """
{% for bd_subnet in value.all %}
    <a href="{% url 'plugins:netbox_aci_plugin:acibridgedomainsubnet'
        pk=bd_subnet.pk %}">
        {{ bd_subnet.gateway_ip_address }}
    </a>{% if not forloop.last %}<br />{% endif %}
{% endfor %}
"""

class ACIBridgeDomainTable(NetBoxTable):
    aci_bridge_domain_subnets = columns.TemplateColumn(
        verbose_name=_("BD Subnets"),
        orderable=False,
        template_code=BRIDGEDOMAIN_SUBNETS,
    )
```

`orderable=False` is required when the template iterates a queryset;
there's no scalar to order by.

## `Meta.fields` and `Meta.default_columns`

Every table declares **both** tuples on `Meta`:

- `fields`: every column the table can render. Includes hidden-by-
  default columns that users can opt into via the column picker.
  `pk` and `id` are always first; `tags` and `comments` are always
  last.
- `default_columns`: the columns visible without user customization.
  Shorter list; what shows up in a fresh install. Must include
  `"name_alias"` immediately after `"name"` on every model that has
  a `name_alias` field.
- Derived accessor-traversal columns (e.g. `aci_fabric` declared via
  `accessor="aci_tenant__aci_fabric"`) belong in `fields` too - they're
  columns like any other, and the column picker should be able to
  toggle them even though they resolve through a parent FK rather than
  a field on the model itself.

```python
class Meta(NetBoxTable.Meta):
    model = ACIBridgeDomain
    fields: tuple = (
        "pk",
        "id",
        "name",
        "name_alias",
        "description",
        "aci_tenant",
        "aci_vrf",
        "nb_tenant",
        "advertise_host_routes_enabled",
        # ... all other columns
        "owner",
        "tags",
        "comments",
    )
    default_columns: tuple = (
        "name",
        "name_alias",
        "aci_tenant",
        "aci_vrf",
        "nb_tenant",
        "description",
        "unicast_routing_enabled",
        "tags",
    )
```

Both tuples annotated `: tuple`.

## Reduced tables

When a detail view renders a child list inline (via
`get_extra_context()`, see [Views - Detail-view extra
context](views.md#detail-view-extra-context)), use a `*ReducedTable`
variant rather than the full table. The reduced version drops the
parent FK column (you're already on the parent's page) and shows only
the few columns that matter in context:

```python
class ACIBridgeDomainSubnetReducedTable(NetBoxTable):
    """Reduced NetBox table for the ACI Bridge Domain Subnet model."""

    name = tables.Column(verbose_name=_("Subnet Name"), linkify=True)
    gateway_ip_address = tables.Column(
        verbose_name=_("Gateway IP"), linkify=True,
    )

    class Meta(NetBoxTable.Meta):
        model = ACIBridgeDomainSubnet
        fields: tuple = ("pk", "id", "name", "gateway_ip_address")
        default_columns: tuple = ("name", "gateway_ip_address")
```

Naming: append `Reduced` before `Table`. Place the reduced table in
the same file as the full table.

## Table column kwarg ordering

Pass kwargs to `django_tables2.Column` in this order. Skip any that
aren't needed; don't reorder:

```text
verbose_name
accessor
default
visible
orderable
attrs
order_by
empty_values
localize
footer
exclude_from_export
linkify
initial_sort_descending
```

!!! tip "Future adoption"
    NetBox ships `LinkedCountColumn` (clickable badge counts linking to
    filtered lists), which could replace hand-rolled parent/child count
    displays in current tables.
