from collections import Counter

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import OuterRef, Subquery


def backfill_aci_fabric(apps, schema_editor) -> None:
    """Populate the cached ACI Fabric for every existing ACI node."""
    db_alias = schema_editor.connection.alias

    aci_node_model = apps.get_model("netbox_aci_plugin", "ACINode")
    aci_pod_model = apps.get_model("netbox_aci_plugin", "ACIPod")

    pod_fabric_id = (
        aci_pod_model.objects.using(db_alias)
        .filter(pk=OuterRef("aci_pod_id"))
        .values("aci_fabric_id")[:1]
    )

    aci_node_model.objects.using(db_alias).update(
        _aci_fabric_id=Subquery(pod_fabric_id)
    )

    if (
        aci_node_model.objects.using(db_alias)
        .filter(_aci_fabric_id__isnull=True)
        .exists()
    ):
        raise RuntimeError("Unable to derive the ACI Fabric for one or more ACI Nodes.")


def find_duplicate_node_ids(rows):
    """Return the sorted fabric and node ID pairs occurring more than once."""
    counts = Counter(tuple(row) for row in rows)
    return sorted(key for key, count in counts.items() if count > 1)


def format_duplicate_node_id_error(duplicates) -> str:
    """Render the migration failure message for duplicate node IDs."""
    pairs = ", ".join(
        f"ACI Fabric {fabric_id} Node ID {node_id}" for fabric_id, node_id in duplicates
    )
    return (
        "Cannot enforce unique ACI Node IDs per ACI Fabric. The following "
        "ACI Fabric and Node ID pairs are used by more than one ACI Node: "
        f"{pairs}. Renumber the conflicting ACI Nodes manually before "
        "upgrading."
    )


def assert_unique_node_ids_per_fabric(apps, schema_editor) -> None:
    """Fail the migration when node IDs are not unique per ACI Fabric."""
    db_alias = schema_editor.connection.alias
    aci_node_model = apps.get_model("netbox_aci_plugin", "ACINode")

    rows = aci_node_model.objects.using(db_alias).values_list(
        "_aci_fabric_id", "node_id"
    )
    duplicates = find_duplicate_node_ids(rows)
    if duplicates:
        raise RuntimeError(format_duplicate_node_id_error(duplicates))


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0026_fabric_cached_scope_set_null"),
    ]

    operations = [
        migrations.AddField(
            model_name="acinode",
            name="_aci_fabric",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="netbox_aci_plugin.acifabric",
            ),
        ),
        migrations.RunPython(backfill_aci_fabric, migrations.RunPython.noop),
        migrations.RunPython(
            assert_unique_node_ids_per_fabric, migrations.RunPython.noop
        ),
    ]
