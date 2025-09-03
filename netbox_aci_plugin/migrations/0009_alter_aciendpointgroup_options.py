from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0008_aciendpointsecuritygroup"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="aciendpointgroup",
            options={
                "default_related_name": "aci_endpoint_groups",
                "ordering": ("aci_app_profile", "name"),
            },
        ),
        migrations.AlterModelOptions(
            name="aciusegendpointgroup",
            options={
                "default_related_name": "aci_useg_endpoint_groups",
                "ordering": ("aci_app_profile", "name"),
            },
        ),
    ]
