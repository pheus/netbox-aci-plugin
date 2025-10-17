import django.core.validators
import django.db.models.deletion
import netbox.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0011_fabric"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACIPod",
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
                ("scope_id", models.PositiveBigIntegerField(blank=True, null=True)),
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
                    "pod_id",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(255),
                        ]
                    ),
                ),
                (
                    "_location",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dcim.location",
                    ),
                ),
                (
                    "_region",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dcim.region",
                    ),
                ),
                (
                    "_site",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dcim.site",
                    ),
                ),
                (
                    "_site_group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dcim.sitegroup",
                    ),
                ),
                (
                    "aci_fabric",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_pods",
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
                    "scope_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem", to="extras.Tag"
                    ),
                ),
                (
                    "tep_pool",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aci_pods",
                        to="ipam.prefix",
                    ),
                ),
            ],
            options={
                "verbose_name": "ACI Pod",
                "ordering": ("aci_fabric", "pod_id"),
                "constraints": [
                    models.UniqueConstraint(
                        fields=("aci_fabric", "pod_id"),
                        name="netbox_aci_plugin_acipod_unique_pod_per_aci_fabric",
                    ),
                    models.UniqueConstraint(
                        fields=("aci_fabric", "name"),
                        name="netbox_aci_plugin_acipod_unique_pod_name_per_aci_fabric",
                    ),
                ],
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
    ]
