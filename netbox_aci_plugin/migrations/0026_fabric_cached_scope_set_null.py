import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0025_epg_aaep_binding"),
        ("dcim", "0225_gfk_indexes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="acifabric",
            name="_region",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="dcim.region",
            ),
        ),
        migrations.AlterField(
            model_name="acifabric",
            name="_site_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="dcim.sitegroup",
            ),
        ),
        migrations.AlterField(
            model_name="acipod",
            name="_region",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="dcim.region",
            ),
        ),
        migrations.AlterField(
            model_name="acipod",
            name="_site_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="dcim.sitegroup",
            ),
        ),
    ]
