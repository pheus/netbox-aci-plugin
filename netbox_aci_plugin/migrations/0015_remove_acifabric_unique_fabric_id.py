from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0014_owner"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="acifabric",
            name="netbox_aci_plugin_acifabric_unique_fabric_id",
        ),
        migrations.RemoveConstraint(
            model_name="acinode",
            name="netbox_aci_plugin_acinode_unique_node_object",
        ),
        migrations.AddConstraint(
            model_name="acinode",
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    ("node_object_id__isnull", False),
                    ("node_object_type__isnull", False),
                ),
                fields=("node_object_type", "node_object_id"),
                name="netbox_aci_plugin_acinode_unique_assigned_node_object",
                violation_error_message="The selected object is already assigned to another ACI Node.",
            ),
        ),
    ]
