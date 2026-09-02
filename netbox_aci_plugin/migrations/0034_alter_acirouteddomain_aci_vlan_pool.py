import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0033_owner_no_reverse_accessor"),
    ]

    operations = [
        migrations.AlterField(
            model_name="acirouteddomain",
            name="aci_vlan_pool",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="aci_routed_domains",
                to="netbox_aci_plugin.acivlanpool",
            ),
        ),
    ]
