from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0014_owner"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="acifabric",
            name="netbox_aci_plugin_acifabric_unique_fabric_id",
        ),
    ]
