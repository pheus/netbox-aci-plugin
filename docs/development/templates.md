# Templates

Templates live under `netbox_aci_plugin/templates/netbox_aci_plugin/`.
Three groups to know:

- **Detail templates** at `<model>.html`: the full page for an object.
- **Button fragments** at `buttons/add_child.html`: the reusable "Add"
  button rendered by `AddChildObject` for children tabs.
- **Widget fragments** at `widgets/`: form-widget partials such as
  `textinput_with_options.html`.

Reference examples:

- Detail: `templates/netbox_aci_plugin/acibridgedomain.html`,
  `acirouteddomain.html`.
- Button fragment: `buttons/add_child.html` (rendered by
  `AddChildObject.template_name`, built via `add_child_action()`).

## Detail templates

### Loads and extends

Most detail templates start with these load lines:

```django
{% extends 'generic/object.html' %}
{% load render_table from django_tables2 %}
{% load helpers %}
{% load i18n %}
```

Most detail templates load `render_table` whether or not the page
actually renders an inline child table - treat the load line as a
standard include and don't strip it just because a given object has
no child list. `{% load helpers %}` is optional - roughly half the
templates omit it (e.g. `acitenant.html`); include it only when the
template uses tags provided by the plugin's own helpers module.

A leading blank line before `{% extends %}` is common but not
required; Django ignores it either way. Match the surrounding file
rather than adding or stripping it for its own sake.

### Breadcrumbs

Extend `block.super` and add the linked parent chain in policy order
(Fabric, Tenant, VRF, BD, and so on):

```django
{% block breadcrumbs %}
  {{ block.super }}
  {% url 'plugins:netbox_aci_plugin:acibridgedomain_list' as bd_list_url %}
  <li class="breadcrumb-item">
    <a href="{{ bd_list_url }}?aci_fabric_id={{ object.aci_fabric.pk }}">
      {{ object.aci_fabric }}
    </a>
  </li>
  <li class="breadcrumb-item">
    <a href="{{ bd_list_url }}?aci_tenant_id={{ object.aci_tenant.pk }}">
      {{ object.aci_tenant }}
    </a>
  </li>
  <li class="breadcrumb-item">
    <a href="{{ bd_list_url }}?aci_vrf_id={{ object.aci_vrf.pk }}">
      {{ object.aci_vrf }}
    </a>
  </li>
{% endblock breadcrumbs %}
```

Each crumb's `href` filters the model's list view by the parent (so
clicking "ACIFabric1" shows all BDs in that fabric). Reuse this
pattern verbatim: link the crumb to the **current model's list view**
with a filter query parameter (`?aci_fabric_id={{ object.aci_fabric.pk }}`),
**not** to the parent's detail URL
(`{{ object.aci_fabric.get_absolute_url }}`).

### Card headers

Always use `<h2 class="card-header">` for card section headings.
NetBox core uses `<h2>` exclusively (via `inc/panel_table.html` and
all detail templates). Never use `<h5>` or other heading levels for
card headers.

### Two-column content layout

Use a **single `<div class="row">`** wrapping two `<div class="col
col-md-6">` columns. Stack all cards vertically inside each column:

```django
{% block content %}
  <div class="row">
    <div class="col col-md-6">
      <div class="card">
        <h2 class="card-header">{% trans "..." %}</h2>
        <table class="table table-hover attr-table">
          ...
        </table>
      </div>
      <div class="card">...</div>
      {% include 'inc/panels/custom_fields.html' %}
    </div>
    <div class="col col-md-6">
      <div class="card">...</div>
      {% include 'inc/panels/tags.html' %}
      {% include 'inc/panels/comments.html' %}
    </div>
  </div>
{% endblock content %}
```

!!! warning "Don't wrap each card pair in its own `<div class="row">`"
    Forcing each card pair into its own row creates awkward vertical
    gaps when one column has more content than the other. Bootstrap
    columns flow naturally, so let them. Only start a new row when the
    layout actually changes (e.g. a 2-column section followed by a
    full-width section below).

### Row pattern

Inside an attr-table card, every row uses multi-line `<tr>` with
`<th scope="row">` on every header cell. Do not use inline single-line
rows like `<tr><th>Label</th><td>value</td></tr>`:

```django
<tr>
  <th scope="row">{% trans "Label" %}</th>
  <td>{{ object.field|placeholder }}</td>
</tr>
```

For linked FKs, append `|linkify`:

```django
<td>{{ object.aci_tenant|linkify }}</td>
```

### Cell helpers

- `{% checkmark object.flag %}`: render a boolean as a green check or
  red cross.
- `{% badge object.get_<field>_display bg_color=object.get_<field>_color %}`:
  render a `ChoiceSet`-backed field as a colored badge using the
  choice's color.
- `|placeholder`: render a muted placeholder dash for empty values
  instead of blank space.
- `|linkify`: wrap the value in an `<a>` to the object's detail page.

### Required panel includes

The right column ends with these standard panels in this order:

```django
{% include 'inc/panels/tags.html' %}
{% include 'inc/panels/comments.html' %}
```

Custom fields live in the left column (it's typically denser):

```django
{% include 'inc/panels/custom_fields.html' %}
```

Add `'inc/panels/related_objects.html'` to whichever column has room
when the model has related-object panels (typically via
`GetRelatedModelsMixin`, see [Views - Detail-view extra
context](views.md#detail-view-extra-context)).

### Wrap child tables in `table-responsive`

Tables rendered inline (not via the `ViewTab` child view) overflow the
card on narrow viewports. Wrap them:

```django
<div class="table-responsive">
  {% render_table subnets_table %}
</div>
```

## Add-child buttons

### Tab-level "Add" buttons via `add_child_action`

The `ViewTab` children views on each parent detail page render their
"Add" button through `AddChildObject`, a reusable `ObjectAction`
subclass. Build one with the `add_child_action()` factory from
`netbox_aci_plugin.object_actions`.

The resulting action class has
`template_name = "netbox_aci_plugin/buttons/add_child.html"`, which
renders a standard `btn btn-primary` anchor pointing to the child
model's add URL with prefilled query parameters. The template itself is
minimal:

```django
{% if url %}
  <a
    href="{{ url }}{% if url_params %}?{{ url_params.urlencode }}{% endif %}"
    class="btn btn-primary"
    role="button"
  >
    <i class="mdi mdi-plus-thick" aria-hidden="true"></i> {{ label }}
  </a>
{% endif %}
```

See `netbox_aci_plugin/object_actions.py` for the `AddChildObject` class
and `add_child_action()` factory, and [Views - Parent-specific children
view](views.md#parent-specific-children-view) for how the actions tuple
is wired in the concrete children view.

### Inline card-header "Add" buttons

For inline reduced tables on a detail page (not behind a `ViewTab`),
the "Add" button is placed directly in the card header using
Bootstrap's `card-actions` pattern:

<!-- markdownlint-disable MD013 -->

```django
<h2 class="card-header">
  {% trans "Subnets" %}
  {% if perms.netbox_aci_plugin.add_acibridgedomainsubnet %}
    {% url 'plugins:netbox_aci_plugin:acibridgedomainsubnet_add' as add_url %}
    <div class="card-actions">
      <a
        href="{{ add_url }}?aci_bridge_domain={{ object.pk }}&aci_vrf={{ object.aci_vrf.pk }}&nb_vrf={{ object.aci_vrf.nb_vrf.pk }}&nb_tenant={{ object.nb_tenant.pk }}&return_url={{ object.get_absolute_url }}"
        class="btn btn-ghost-primary btn-sm"
      >
        <i class="mdi mdi-plus-thick" aria-hidden="true"></i>
        {% trans "Add a Subnet" %}
      </a>
    </div>
  {% endif %}
</h2>
```

<!-- markdownlint-enable MD013 -->

Rules:

- Gate the button on the matching `add_<child>` permission.
- Pre-fill the parent FK and any cascading-dropdown seed fields via URL
  query parameters so the child form initializes correctly.
- Set `return_url` to the parent's detail page
  (`object.get_absolute_url`) so the user lands back there after
  creating the child.

## Secondary-side parent-scope injection

When a child relation tab appears on the non-primary parent's detail
page (e.g. `ACIBridgeDomainL3OutBinding` listed from the L3Out side),
the "Add" button must inject the non-primary parent's scope fields so
the child form's cascading dropdowns prefill correctly. This injection
happens entirely in the view layer via `url_params` lambdas on
`add_child_action()` - no separate template is involved. (See [Forms -
Single-mental-model relation forms](forms.md#single-mental-model-relation-forms)
for why the form itself only models one parent side.)

Example from `views/tenant/l3outs.py`:

```python
actions = (
    add_child_action(
        "netbox_aci_plugin.ACIBridgeDomainL3OutBinding",
        _("Attach a Bridge Domain"),
        url_params={
            "aci_fabric": lambda ctx: ctx["object"].aci_tenant.aci_fabric_id,
            "aci_tenant": lambda ctx: ctx["object"].aci_tenant_id,
            "aci_vrf": lambda ctx: ctx["object"].aci_vrf_id,
            "aci_l3out": lambda ctx: ctx["object"].pk,
        },
    ),
) + ACIBridgeDomainL3OutBindingChildrenView.actions
```

`aci_fabric`, `aci_tenant`, `aci_vrf`, and `aci_l3out` are all injected
as lambdas that read from the current parent context (`ctx["object"]` is
the L3Out instance), so the child form's dropdowns cascade from the
correct scope without needing multi-key `initial_params` on the form
side.
