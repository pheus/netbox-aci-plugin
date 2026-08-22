import django.core.validators
import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import netbox.models.deletion
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        (
            "netbox_aci_plugin",
            "0031_access_policy_leaf_switch_profile_interface_bindings",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="ACILeafInterfaceOverride",
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
                (
                    "description",
                    models.CharField(
                        blank=True,
                        max_length=128,
                        validators=[
                            django.core.validators.RegexValidator(
                                code="invalid",
                                message="Only alphanumeric characters and !#$%%()*,-./:;@ _{|}~?&+ are allowed.",
                                regex="^[A-Za-z0-9!#$%()*,-./:;@ _{|}~?&+]*$",
                            )
                        ],
                    ),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "aci_leaf_interface_policy_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_leaf_interface_overrides",
                        to="netbox_aci_plugin.acileafinterfacepolicygroup",
                    ),
                ),
                (
                    "aci_node_interface",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_leaf_interface_override",
                        to="netbox_aci_plugin.acinodeinterface",
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
                "verbose_name": "ACI Leaf Interface Override",
                "ordering": ("aci_node_interface",),
                "default_related_name": "aci_leaf_interface_overrides",
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
    ]
