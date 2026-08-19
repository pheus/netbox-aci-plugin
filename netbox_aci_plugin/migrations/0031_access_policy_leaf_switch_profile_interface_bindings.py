import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import netbox.models.deletion
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0030_access_policy_leaf_interface_profiles"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACILeafSwitchProfileInterfaceBinding",
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
                    "aci_leaf_interface_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_leaf_switch_profile_bindings",
                        to="netbox_aci_plugin.acileafinterfaceprofile",
                    ),
                ),
                (
                    "aci_leaf_switch_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_leaf_interface_profile_bindings",
                        to="netbox_aci_plugin.acileafswitchprofile",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem", to="extras.Tag"
                    ),
                ),
            ],
            options={
                "verbose_name": "ACI Leaf Switch Profile Interface Binding",
                "ordering": ("aci_leaf_switch_profile", "aci_leaf_interface_profile"),
                "default_related_name": "aci_leaf_switch_profile_interface_bindings",
                "constraints": [
                    models.UniqueConstraint(
                        fields=(
                            "aci_leaf_switch_profile",
                            "aci_leaf_interface_profile",
                        ),
                        name="netbox_aci_plugin_acileafswitchprofileinterfacebinding_unique_binding",
                    )
                ],
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
    ]
