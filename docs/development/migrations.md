# Migrations

Migration files live in `netbox_aci_plugin/migrations/`. The plugin
mixes Django-generated schema migrations with hand-authored data
migrations for seed content.

## Filename pattern

`NNNN_<short_description>.py` where the description names the **grouped
feature**, not individual model names. The grouping makes the migration
list legible at a glance:

Examples:

- `0001_initial.py`: initial schema and seed tenants.
- `0011_fabric.py`: ACIFabric model and default fabric.
- `0012_fabric_pod.py`: ACIPod model.
- `0014_owner.py`: `owner` FK rollout across many models.
- `0017_tenant_l3outs.py`: L3Out, ExternalEndpointGroup, and
  ExternalSubnet.
- `0018_bridge_domain_l3out_binding.py`: binding relation.

Prefer one descriptive name over a long string of model names. If a
single migration touches many models because they share a feature
(e.g. `owner`), name it after the feature.

## Data migration idempotency

Every seed-data `RunPython` operation must be **idempotent**: running
the same migration twice on the same database must produce the same
result. Use this two-part contract:

1. Gate on the plugin config flag via `get_plugin_config(...)`.
2. Guard each create with `.filter(...).exists()`.

```python
from netbox.plugins.utils import get_plugin_config
from netbox_aci_plugin import ACIConfig


def create_default_aci_tenants(apps, schema_editor) -> None:
    """Creates default ACI tenants if they do not already exist."""
    if get_plugin_config(ACIConfig.name, "create_default_aci_tenants", True):
        db_alias = schema_editor.connection.alias
        aci_tenant = apps.get_model(ACIConfig.name, "ACITenant")
        default_aci_tenants = ["common", "infra", "mgmt"]
        for default_aci_tenant in default_aci_tenants:
            if (
                not aci_tenant.objects.using(db_alias)
                .filter(name=default_aci_tenant)
                .exists()
            ):
                aci_tenant.objects.using(db_alias).create(name=default_aci_tenant)
```

!!! warning "Always use `apps.get_model()` inside `RunPython`"
    Importing the concrete model class freezes it to its current
    definition. If the model evolves later, an old migration that
    imports the class breaks. `apps.get_model("netbox_aci_plugin",
    "ACITenant")` returns the historical model as it existed at the
    migration's place in history.

### Reverse handler

Data migrations that add seed rows pass `migrations.RunPython.noop` as
the reverse: the seed rows are owned by the user once created, and
auto-deleting them on rollback is unsafe:

```python
migrations.RunPython(create_default_aci_fabric, migrations.RunPython.noop),
```

When the reverse genuinely cannot be expressed (e.g. ambiguous undo),
omit it and document the reason in a comment.

## Owner rollout pattern

`0014_owner.py` is the reference shape for adding one field across many
models in a single migration. Use this pattern when introducing
cross-cutting fields like `owner`, `status`, or future mixin fields:

```python
class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0013_fabric_node"),
        ("users", "0015_owner"),
    ]

    operations = [
        migrations.AddField(
            model_name="aciappprofile",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="users.owner",
            ),
        ),
        migrations.AddField(
            model_name="acibridgedomain",
            name="owner",
            field=models.ForeignKey(...),
        ),
        # ... one AddField per model
    ]
```

Rules:

- Each model gets its own `AddField` op; don't try to share the field
  definition object across ops. Django's autodetector emits them
  separately and the migration is more readable that way.
- Field options are uniform: `blank=True`, `null=True`,
  `on_delete=PROTECT`. Optional ownership should never block deletion
  upstream.
- One dependency entry per app whose model the FK targets (here,
  `users`).

## `UniqueConstraint.name` template

Every `UniqueConstraint` declared in a model uses the
`%(app_label)s_%(class)s_...` name template (see [Models -
UniqueConstraint
naming](models.md#uniqueconstraint-naming-template)) so the constraint
name remains stable when models are renamed and inherits cleanly into
subclasses. Migrations referencing constraints by name (e.g.
`RemoveConstraint` ops) must use the rendered name, e.g.
`netbox_aci_plugin_acitenant_unique_name`.

## Schema migrations

Prefer auto-generated migrations from `python manage.py makemigrations
netbox_aci_plugin`. Hand-edit only for:

- Adjusting `dependencies` after a manual rebase.
- Adding a `RunPython` op alongside the schema change.
- Renaming an op for clarity (rare).

Don't hand-edit the field-definition argument list; let Django emit it.
If a difference between the model and the generated migration surprises
you, the model is probably what needs adjusting, not the migration.
