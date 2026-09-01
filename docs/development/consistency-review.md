# Consistency Review

Use this checklist when reviewing the plugin for naming, ordering,
coverage, and documentation drift. It works well as a self-review before
opening a pull request. Gather findings first, then decide whether each
one needs a code fix, a doc update, or a follow-up issue.

## Review batches

Run the review in small batches so each pass has a clear scope.

1. Inventory concrete models and layer coverage.
2. Check class names and file placement.
3. Check model field and member order.
4. Check form, table, filterset, view, API, GraphQL, search, and test
   class-attribute order.
5. Check field naming and field order across layers.
6. Check method names and method order.
7. Identify base-class or mixin opportunities.
8. Check test coverage by layer.
9. Check for missing or stale guidance in the development docs.
10. Check whether any code-level rules are undocumented and should be
    captured in `docs/development/`.

## Commands

Run from the plugin root unless noted otherwise. Activate the
NetBox/plugin virtualenv first so `ruff`, `python`, and `mkdocs`
resolve from that environment:

```bash
rg --files netbox_aci_plugin docs pyproject.toml ruff.toml
pattern="class .*\\(|fieldsets|queryset|filterset|table"
pattern="$pattern|serializer_class|filterset_class"
rg -n "$pattern" netbox_aci_plugin
ruff format --check netbox_aci_plugin
ruff check netbox_aci_plugin
```

Run plugin tests from the NetBox `netbox/` directory with the same
virtualenv active:

```bash
cd "$NETBOX_ROOT/netbox"
python manage.py test netbox_aci_plugin --keepdb
```

Drop `--keepdb` when model fields, migrations, or schema changed.

## Layer matrix

For every concrete model, verify the matching layer objects exist:

- **Model:** `<Model>`.
- **Table:** `<Model>Table`, plus reduced tables where detail views need
  child panels.
- **FilterSet:** `<Model>FilterSet`.
- **Forms:** `<Model>EditForm`, `<Model>BulkEditForm`,
  `<Model>FilterForm`, and `<Model>ImportForm`.
- **UI panels:** `<Model>Panel`, declared
  on the detail view's `layout`, plus a `Breadcrumb` per ancestor level.
- **Views:** detail, list, edit, delete, bulk import, and bulk
  edit/delete where applicable.
- **URLs:** UI routes via `get_model_urls()` and an API router route.
- **Serializer:** `<Model>Serializer`.
- **API viewset:** `<Model>ListViewSet`.
- **GraphQL:** `<Model>Type` and `<Model>Filter`.
- **Search:** `<Model>Index`.
- **Tests:** model, form, and API tests; filterset, view, table, and
  GraphQL tests where adopted.
- **Docs:** feature docs and development docs when a change introduces
  a new convention.

## Finding categories

Use these categories to classify review notes:

- **Bug:** behavior that can fail at runtime or produce wrong data.
- **Inconsistency:** code that works but violates a documented or
  dominant local pattern.
- **Missing Test:** expected coverage is absent or incomplete.
- **Docs Gap:** rules are missing, stale, ambiguous, or contradicted by
  code.
- **Optimization:** query, rendering, or maintenance improvement without
  immediate bug impact.
- **Base Class Candidate:** repeated logic that may deserve a documented
  helper or mixin.
- **Deferred:** valid work intentionally outside the current scope.
- **False Positive:** reviewed item that should not be changed under the
  current project decisions.
- **Superseded:** finding already resolved by later work.

## Attribute-order checklist

Use the layer docs for the detailed rules. This section gives
only the cross-layer quick check.

- **Models:** fields, managers, `Meta`, `__str__()`, `clean_fields()`,
  `clean()`, `save()`, `delete()`, `get_absolute_url()`,
  `to_objectchange()`, properties, then custom methods.
- **Forms:** field declarations, `fieldsets`, `Meta` / `model`, then
  helper methods. The exact form-type order lives in
  [Forms](forms.md#field-declaration-order).
- **UI panels:** `title` / `actions` class attributes before declared
  attribute fields. Every panel subclasses `ObjectAttributesPanel`
  directly, never a shared base, because the metaclass walks base
  classes first and gives no way to reorder inherited rows.
- **FilterSets:** `id`, `name` / `slug`, parent FK name/ID pairs,
  feature filters, `Meta`, then `search()`.
- **Tables:** identity columns, parent/scope columns, feature columns,
  tenancy/ownership, tags/comments, `Meta`, then render helpers.
- **Views:** follow
  [Views - Class attribute order](views.md#class-attribute-order).
- **Serializers:** `url`, nested/related serializer fields, custom
  fields, `Meta`, then validators.
- **API viewsets:** `queryset`, `serializer_class`, `filterset_class`.
- **GraphQL filters:** parent/scope fields, IDs immediately after
  related object fields, then feature fields in model order.
- **GraphQL types:** type fields and exclusions in model order;
  relation refs near the related model field.
- **Search indexes:** `model`, `fields`, `display_attrs`.
- **Tests:** class attributes before fixtures; `setUpTestData()` before
  individual tests.

When the codebase lacks a documented rule for a layer, record a `Docs
Gap` instead of forcing a subjective code change.

## Reporting

Capture findings somewhere durable, such as a tracking issue or the
description of the pull request that addresses them. For each finding,
include:

- finding ID
- category and severity
- file and line reference
- concise finding
- recommended action
- status after recheck (`Confirmed`, `Deferred`, `False Positive`,
  `Superseded`)

When reporting verification, include the exact command, working
directory, pass/fail result, and relevant output.
