import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import netbox.models.deletion
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0017_tenant_l3outs"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACIBridgeDomainL3OutBinding",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=utilities.json.CustomFieldJSONEncoder,
                    ),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "aci_bridge_domain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_l3out_bindings",
                        to="netbox_aci_plugin.acibridgedomain",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem", to="extras.Tag"
                    ),
                ),
                (
                    "aci_l3out",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_bridge_domain_bindings",
                        to="netbox_aci_plugin.acil3out",
                    ),
                ),
            ],
            options={
                "verbose_name": "ACI Bridge Domain L3Out Binding",
                "ordering": ("aci_bridge_domain", "aci_l3out"),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.AddConstraint(
            model_name="acibridgedomainl3outbinding",
            constraint=models.UniqueConstraint(
                fields=("aci_bridge_domain", "aci_l3out"),
                name="netbox_aci_plugin_acibridgedomainl3outbinding_unique_binding",
            ),
        ),
    ]
