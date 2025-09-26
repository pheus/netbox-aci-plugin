import django.core.validators
import django.db.models.deletion
import netbox.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models
from netbox.plugins.utils import get_plugin_config

from netbox_aci_plugin import ACIConfig


def create_default_aci_fabric(apps, schema_editor) -> None:
    """Creates default ACI Fabric."""
    db_alias = schema_editor.connection.alias
    ACIFabric = apps.get_model(ACIConfig.name, "ACIFabric")
    ACITenant = apps.get_model(ACIConfig.name, "ACITenant")

    if (
        get_plugin_config(ACIConfig.name, "create_default_aci_fabric", True)
        or get_plugin_config(ACIConfig.name, "create_default_aci_tenants", True)
        or ACITenant.objects.using(db_alias).exists()
    ):
        ACIFabric.objects.using(db_alias).create(
            name="Fabric1", fabric_id=1, infra_vlan_vid=3900
        )


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0010_alter_aci_model_validators"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACIFabric",
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
                (
                    "fabric_id",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(128),
                        ]
                    ),
                ),
                (
                    "infra_vlan_vid",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(4094),
                        ]
                    ),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "infra_vlan",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aci_fabrics",
                        to="ipam.vlan",
                    ),
                ),
                (
                    "gipo_pool",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aci_fabrics",
                        to="ipam.prefix",
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
            ],
            options={
                "verbose_name": "ACI Fabric",
                "ordering": ("name",),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.AddConstraint(
            model_name="acifabric",
            constraint=models.UniqueConstraint(
                fields=("name",), name="netbox_aci_plugin_acifabric_unique_name"
            ),
        ),
        migrations.AddConstraint(
            model_name="acifabric",
            constraint=models.UniqueConstraint(
                fields=("fabric_id",),
                name="netbox_aci_plugin_acifabric_unique_fabric_id",
            ),
        ),
        migrations.RunPython(create_default_aci_fabric, migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name="acitenant",
            name="netbox_aci_plugin_acitenant_unique_name",
        ),
        migrations.AddField(
            model_name="acitenant",
            name="aci_fabric",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="aci_tenants",
                to="netbox_aci_plugin.acifabric",
            ),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name="acitenant",
            options={"ordering": ("aci_fabric", "name")},
        ),
        migrations.AddConstraint(
            model_name="acitenant",
            constraint=models.UniqueConstraint(
                fields=("aci_fabric", "name"),
                name="netbox_aci_plugin_acitenant_unique_name_per_aci_fabric",
            ),
        ),
        migrations.AlterModelOptions(
            name="acibridgedomain",
            options={"ordering": ("aci_tenant", "name")},
        ),
    ]
