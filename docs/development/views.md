# Views

Views live under `netbox_aci_plugin/views/<domain>/<model>.py`. Every
view subclasses one of NetBox's `generic.*` view classes and registers
itself via the `@register_model_view` decorator (so URLs auto-resolve
via `get_model_urls()`, see [URL routing](#url-routing) below).

## Standard view-set per primary model

Each primary model ships five views:

- **Detail:** `@register_model_view(<Model>)`, class `<Model>View`,
  base `generic.ObjectView`.
- **List:** `@register_model_view(<Model>, "list", path="",
  detail=False)`, class `<Model>ListView`, base
  `generic.ObjectListView`.
- **Add/edit:** `@register_model_view(<Model>, "add", detail=False)`
  and `@register_model_view(<Model>, "edit")`, class
  `<Model>EditView`, base `generic.ObjectEditView`.
- **Delete:** `@register_model_view(<Model>, "delete")`, class
  `<Model>DeleteView`, base `generic.ObjectDeleteView`.
- **Bulk import:** `@register_model_view(<Model>, "bulk_import",
  path="import", detail=False)`, class `<Model>BulkImportView`, base
  `generic.BulkImportView`.

...plus bulk edit (`path="edit"`) / bulk delete (`path="delete"`) views
for primary models, and one children view per `ViewTab` the detail page
exposes.

### Class ordering within a view file

Within each model's view group, declare view classes in this order:

1. Base `ChildrenView` (the unfiltered tab definition)
2. `<Model>View` (detail)
3. `<Model>ListView` (list)
4. `<Model>EditView` (edit)
5. `<Model>DeleteView` (delete)
6. Concrete (parent-specific) `ChildrenView` subclasses
7. `<Model>BulkImportView`
8. `<Model>BulkEditView`
9. `<Model>BulkDeleteView`

Base ChildrenViews come first because concrete ChildrenViews and
parent-specific views subclass them. Bulk views come last.

## Class attribute order

Declare class-level attributes on views in this order:

- `ObjectView` (detail): `queryset`.
- `ObjectListView` (list): `queryset`, `filterset`,
  `filterset_form`, `table`.
- `ObjectEditView` (edit): `queryset`, `form`.
- `ObjectDeleteView` (delete): `queryset`.
- `BulkImportView`: `queryset`, `model_form`.
- `BulkEditView`: `queryset`, `filterset`, `table`, `form`.
- `BulkDeleteView`: `queryset`, `filterset`, `table`.
- `ObjectChildrenView` (children): `child_model`, `filterset`,
  `tab`, `table`.

`queryset` is always first. For list views the order is
`queryset, filterset, filterset_form, table`: filterset before table
because the filterset narrows the queryset before the table renders it.

## QuerySet optimization

Every view declares its `queryset` explicitly with `select_related`
for FK fields displayed on the page and `prefetch_related("tags")`
for the tags M2M:

```python
queryset = ACIBridgeDomain.objects.select_related(
    "aci_tenant",
    "aci_vrf",
    "nb_tenant",
    "owner",
).prefetch_related(
    "tags",
)
```

Reuse the same chain across the list / detail / edit / delete views
of the same model. Copy/paste rather than deduplicating via a queryset
helper unless it materially helps. Different views may select
different sets (the list view tends to be narrower than the detail
view).

## Detail-view extra context

For an object detail page that should render related-object panels
inline (a child reduced table, a related-objects card from
`GetRelatedModelsMixin`), implement `get_extra_context()`:

```python
@register_model_view(ACIBridgeDomain)
class ACIBridgeDomainView(generic.ObjectView):
    queryset = ACIBridgeDomain.objects.select_related(...).prefetch_related("tags")

    def get_extra_context(self, request, instance) -> dict:
        """Return related Bridge Domain Subnets as extra context."""
        subnets_table = ACIBridgeDomainSubnetReducedTable(
            instance.aci_bridge_domain_subnets.all()
        )
        subnets_table.configure(request=request)
        return {"subnets_table": subnets_table}
```

The template reads `subnets_table` directly:

```django
<div class="table-responsive">
  {% render_table subnets_table %}
</div>
```

Use a `*ReducedTable` (see [Tables - Reduced
tables](tables.md#reduced-tables)); the parent FK column is redundant
when you're on the parent's detail page.

### `GetRelatedModelsMixin` for cross-cutting counts

For a "related objects" panel that aggregates counts across many
linked models (used on Tenant, Fabric, and Pod views), mix in
`utilities.views.GetRelatedModelsMixin` and return the result from
`get_related_models()`:

```python
from utilities.views import GetRelatedModelsMixin

@register_model_view(ACITenant)
class ACITenantView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = ACITenant.objects.select_related(...).prefetch_related("tags")

    def get_extra_context(self, request, instance) -> dict:
        """Return related models as extra context."""
        extra_related_models: tuple[tuple[QuerySet, str], ...] = (
            (
                ACIEndpointGroup.objects.restrict(request.user, "view").filter(
                    aci_app_profile__aci_tenant=instance
                ),
                "aci_tenant_id",
            ),
            ...
        )
        return {
            "related_models": self.get_related_models(
                request, instance, extra=extra_related_models,
            )
        }
```

The mixin auto-discovers direct FK references to the instance; pass
`extra=` for indirect relationships (via grandparent traversal).
Templates render the result via `inc/panels/related_objects.html`
(see [Templates - Required panel
includes](templates.md#required-panel-includes)).

## Children views (tabs)

For each child relationship that should appear as a tab on the parent
detail page, declare:

1. A **base children view** in the child's file, defining the tab and
   table.
2. A **parent-specific children view** in the parent's file, filtered
   by the parent FK with the parent column hidden.

### Base children view

```python
class ACIBridgeDomainSubnetChildrenView(generic.ObjectChildrenView):
    """Base children view for attaching a tab of ACI Bridge Domain Subnet."""

    child_model = ACIBridgeDomainSubnet
    filterset = ACIBridgeDomainSubnetFilterSet
    tab = ViewTab(
        label=_("BD Subnets"),
        badge=lambda obj: obj.aci_bridge_domain_subnets.count(),
        permission="netbox_aci_plugin.view_acibridgedomainsubnet",
        weight=1000,
    )
    table = ACIBridgeDomainSubnetTable

    def get_children(self, request, parent):
        """Return all objects of ACIBridgeDomainSubnet."""
        return (
            ACIBridgeDomainSubnet.objects.restrict(request.user, "view")
            .select_related(
                "aci_bridge_domain",
                "gateway_ip_address",
                "nb_tenant",
                "owner",
            )
            .prefetch_related("tags")
        )
```

Rules:

- `child_model`, `filterset`, `tab`, `table` are all required.
- `tab.badge` is a `lambda obj:` that returns the count via the
  parent's reverse-FK accessor (`obj.<related_name>.count()`).
- `tab.weight` orders tabs left-to-right; default 1000. Bump by 100
  to tie-break a sibling tab declared in the same file (e.g.
  `contracts.py`'s "Subjects" tab at 1000 and "Relations" tab at
  1100, which share the ACI Contract detail page). When several
  files contribute child tabs to the same parent (e.g. Fabric's
  Routed Domains / VLAN Pools / Physical Domains tabs), pre-allocate
  100-spaced slots (2000, 2100, 2200, ...) instead of reusing 1000.
- `get_children()` returns the **unfiltered** queryset of the child
  model with the standard `select_related` + `prefetch_related`
  chain. The parent-specific subclass narrows it.

### Parent-specific children view

```python
@register_model_view(ACIBridgeDomain, "bridgedomainsubnets", path="subnets")
class ACIBridgeDomainBridgeDomainSubnetView(ACIBridgeDomainSubnetChildrenView):
    """Children view of ACI Bridge Domain Subnet of ACI Bridge Domain."""

    queryset = ACIBridgeDomain.objects.all()
    actions = (
        add_child_action(
            "netbox_aci_plugin.ACIBridgeDomainSubnet",
            _("Add a BD Subnet"),
            url_params={
                "aci_tenant": lambda ctx: ctx["object"].aci_tenant_id,
                "aci_vrf": lambda ctx: ctx["object"].aci_vrf_id,
                "aci_bridge_domain": lambda ctx: ctx["object"].pk,
                "nb_vrf": lambda ctx: ctx["object"].aci_vrf.nb_vrf_id,
                "nb_tenant": lambda ctx: ctx["object"].nb_tenant_id,
            },
        ),
    ) + ACIBridgeDomainSubnetChildrenView.actions

    def get_children(self, request, parent):
        """Return all children objects to the current parent object."""
        return super().get_children(request, parent).filter(aci_bridge_domain=parent.pk)

    def get_table(self, *args, **kwargs):
        """Return table with ACIBridgeDomain column hidden."""
        table = super().get_table(*args, **kwargs)
        table.columns.hide("aci_bridge_domain")
        return table
```

Import `add_child_action` from `netbox_aci_plugin.object_actions`.

Rules:

- `queryset` is the **parent** model's queryset (NetBox routes the
  detail-page URL through the parent).
- `actions` extends the base class's `actions` tuple by prepending one
  `add_child_action(...)` call per "Add" button the tab needs. Append
  `+ <BaseChildrenView>.actions` to preserve any buttons the base class
  defines.
- `add_child_action(model, label, url_params)` builds a reusable
  `AddChildObject` subclass (see `netbox_aci_plugin/object_actions.py`).
  Pass the dotted `"app.ModelName"` label, a translated button label,
  and a `url_params` dict. Each dict value is a callable receiving the
  template context; `ctx["object"]` is the parent instance.
- `get_children()` calls `super()` then `.filter(<parent_fk>=parent.pk)`.
- `get_table()` hides the column corresponding to the parent FK,
  redundant when listing children of that specific parent.

## URL routing

### URL naming

URL names follow `<modellower>_<action>`: all lowercase, no separators
inside the model name:

| URL name                | Purpose     |
|-------------------------|-------------|
| `acitenant_list`        | list view   |
| `acitenant`             | detail view |
| `acitenant_add`         | create      |
| `acitenant_edit`        | edit        |
| `acitenant_delete`      | delete      |
| `acitenant_bulk_import` | bulk import |

### Plugin URL structure

`urls.py` registers one `path(...)` pair per primary model (non-detail
and detail), using `get_model_urls()`:

```python
from django.urls import include, path
from utilities.urls import get_model_urls

urlpatterns: tuple = (
    # ACI Fabric
    path(
        "fabrics/",
        include(get_model_urls("netbox_aci_plugin", "acifabric", detail=False)),
    ),
    path(
        "fabrics/<int:pk>/",
        include(get_model_urls("netbox_aci_plugin", "acifabric")),
    ),
    # ACI Pod
    path("pods/", include(get_model_urls("netbox_aci_plugin", "acipod", detail=False))),
    path("pods/<int:pk>/", include(get_model_urls("netbox_aci_plugin", "acipod"))),
    # ...
)
```

Each pair is preceded by a `# ACI <Verbose Model>` section comment.

### Flat vs nested model URLs

Whether a model gets a flat top-level URL or nests under its parent
comes down to one question: is browsing and filtering every instance of
the model, across all of its parents, useful to operators?

When it is, the model gets a flat path (`<plural-kebab-noun>/`) plus a
navigation entry, even for a conceptual child such as Bridge Domain
Subnet (`bridge-domain-subnets/`) or Contract Filter Entry
(`contract-filter-entries/`). The sidebar highlights the menu entry
whose URL is a prefix of the current page, so a flat path keeps the
model's own entry highlighted instead of the parent's.

When it is not, the model nests one level under its parent and has no
navigation entry. Two cases qualify. First, a Relation/Binding
association with no identity of its own, a pure join extending
`NetBoxModel` directly (see
[Models - Class hierarchy](models.md#class-hierarchy)), such as
`ACIContractRelation`, `ACIContractSubjectFilter`, or a Binding model
like `ACIBridgeDomainL3OutBinding`. Second, a model that is only
meaningful inside one specific parent, so a list spanning parents would
have no use. Carrying its own `name` field does not by itself make a
model flat:

```python
# ACI Bridge Domain L3Out Binding (parent_object = aci_bridge_domain)
path(
    "bridge-domains/l3out-bindings/",
    include(get_model_urls(
        "netbox_aci_plugin", "acibridgedomainl3outbinding", detail=False
    )),
),
path(
    "bridge-domains/l3out-bindings/<int:pk>/",
    include(get_model_urls("netbox_aci_plugin", "acibridgedomainl3outbinding")),
),
```

When the child slug would be ambiguous on its own (a BD has multiple
binding types), include enough context to disambiguate
(`l3out-bindings/`, not just `bindings/`).

!!! note "Named models can still nest"
    `ACIUSegNetworkAttribute`, `ACIEsgEndpointGroupSelector`, and
    `ACIEsgEndpointSelector` carry their own `name` but nest under their
    parent slug (`useg-endpoint-groups/network-attributes/`,
    `endpoint-security-groups/epg-selectors/`,
    `endpoint-security-groups/ep-selectors/`) because each is only
    meaningful within its parent: there is no use in listing every uSeg
    attribute or ESG selector across the fabric. They nest by the rule
    above, not as an exception to it.

!!! note "Nesting may cross domain folders"
    The parent slug is chosen by the model's `parent_object`, not by the
    child's own layer folder, so a nested path can span two domains.
    `ACILeafInterfaceOverride` lives in `access_policies/` but its parent
    `ACINodeInterface` lives in `fabric/`, giving
    `node-interfaces/leaf-interface-overrides/`. That is correct: the
    route describes where the object hangs in the object graph, and
    `urls.py` is a flat list of paths, so nothing about the folder layout
    constrains it. Do not flatten a nav-less child just to keep its route
    inside its own domain.

!!! note "Borderline: browse-all vs. parent-only"
    `ACIExternalSubnet` is the judgment case. It is only meaningful
    within its L3Out, which argues for nesting, yet operators may want a
    single list of all external subnets to filter across L3Outs, which
    argues for a flat path (its current treatment). Decide per model on
    that browse and filter utility.

!!! note "API URLs stay flat"
    REST API consumers expect unambiguous resource paths. Use flat
    compound names in `api/urls.py` (`bridge-domain-l3out-bindings`)
    regardless of UI nesting. See [REST API - Router
    paths](rest-api.md#router-paths).

### Children-tab URL registration

Child views register via `@register_model_view(<parent>, <action>,
path="<slug>")`:

- `<action>` is the internal action name: kebab-free, all lowercase,
  unique per parent (`bridgedomainsubnets`, `endpointgroups`,
  `l3outs`).
- `path=` is the URL slug appended to the parent's detail path
  (`subnets/`, `endpoint-groups/`, `l3outs/`).

```python
@register_model_view(ACIBridgeDomain, "bridgedomainsubnets", path="subnets")
@register_model_view(ACIBridgeDomain, "endpointgroups", path="endpoint-groups")
```

Keep `<action>` and `path` related (action `bridgedomainsubnets` maps
to path `subnets/`) but not identical: the action name uniqueness lives
in NetBox's model-view registry, while the slug uniqueness lives in
the URL space.
