import django.contrib.postgres.fields
import django.core.validators
import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import netbox.models.deletion
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0015_remove_acifabric_unique_fabric_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACIRoutedDomain",
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
                    "name",
                    models.CharField(
                        max_length=64,
                        validators=[
                            django.core.validators.RegexValidator(
                                code="invalid",
                                message="Only alphanumeric characters, periods, underscores, colons and hyphens are allowed.",
                                regex="^[A-Za-z0-9_.:-]+$",
                            )
                        ],
                    ),
                ),
                (
                    "name_alias",
                    models.CharField(
                        blank=True,
                        max_length=64,
                        validators=[
                            django.core.validators.RegexValidator(
                                code="invalid",
                                message="Only alphanumeric characters, periods, underscores, colons and hyphens are allowed.",
                                regex="^[A-Za-z0-9_.:-]*$",
                            )
                        ],
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
                    "security_domains",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            max_length=64,
                            validators=[
                                django.core.validators.RegexValidator(
                                    code="invalid",
                                    message="Only alphanumeric characters, periods, underscores, colons and hyphens are allowed.",
                                    regex="^[A-Za-z0-9_.:-]+$",
                                )
                            ],
                        ),
                        blank=True,
                        default=list,
                        size=None,
                    ),
                ),
                (
                    "aci_fabric",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_routed_domains",
                        to="netbox_aci_plugin.acifabric",
                    ),
                ),
                (
                    "nb_tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)ss",
                        to="tenancy.tenant",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="users.owner",
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
                "verbose_name": "ACI Routed Domain",
                "ordering": ("aci_fabric", "name"),
                "constraints": [
                    models.UniqueConstraint(
                        fields=("aci_fabric", "name"),
                        name="netbox_aci_plugin_acirouteddomain_unique_name_per_aci_fabric",
                    )
                ],
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
    ]
