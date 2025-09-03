import django.core.validators
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models
from netbox.plugins.utils import get_plugin_config

from netbox_aci_plugin import ACIConfig


def create_default_aci_tenants(apps, schema_editor) -> None:
    """Creates default ACI tenants if they do not already exist."""
    if get_plugin_config(ACIConfig.name, "create_default_aci_tenants", True):
        db_alias = schema_editor.connection.alias
        # The ACITenant model cannot be imported directly as it may be a newer
        # version than this migration expects.
        aci_tenant = apps.get_model(ACIConfig.name, "ACITenant")
        default_aci_tenants = ["common", "infra", "mgmt"]
        for default_aci_tenant in default_aci_tenants:
            if (
                not aci_tenant.objects.using(db_alias)
                .filter(name=default_aci_tenant)
                .exists()
            ):
                aci_tenant.objects.using(db_alias).create(name=default_aci_tenant)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("extras", "0115_convert_dashboard_widgets"),
        ("tenancy", "0015_contactassignment_rename_content_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACITenant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, null=True),
                ),
                (
                    "last_updated",
                    models.DateTimeField(auto_now=True, null=True),
                ),
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
                            django.core.validators.MaxLengthValidator(64),
                            django.core.validators.RegexValidator(
                                code="invalid",
                                message="Only alphanumeric characters, hyphens, periods and underscores are allowed.",
                                regex="^[a-zA-Z0-9_.:-]{1,64}$",
                            ),
                        ],
                    ),
                ),
                (
                    "name_alias",
                    models.CharField(
                        blank=True,
                        max_length=64,
                        validators=[
                            django.core.validators.MaxLengthValidator(64),
                            django.core.validators.RegexValidator(
                                code="invalid",
                                message="Only alphanumeric characters, hyphens, periods and underscores are allowed.",
                                regex="^[a-zA-Z0-9_.:-]{1,64}$",
                            ),
                        ],
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True,
                        max_length=128,
                        validators=[
                            django.core.validators.MaxLengthValidator(128),
                            django.core.validators.RegexValidator(
                                code="invalid",
                                message="Only alphanumeric characters and !#$%%()*,-./:;@ _{|}~?&+ are allowed.",
                                regex="^[a-zA-Z0-9\\\\!#$%()*,-./:;@ _{|}~?&+]{1,128}$",
                            ),
                        ],
                    ),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "nb_tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aci_tenants",
                        to="tenancy.tenant",
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
                "verbose_name": "ACI Tenant",
                "ordering": ("name",),
            },
        ),
        migrations.AddConstraint(
            model_name="acitenant",
            constraint=models.UniqueConstraint(
                fields=("name",), name="unique_aci_tenant_name"
            ),
        ),
        migrations.RunPython(create_default_aci_tenants),
    ]
