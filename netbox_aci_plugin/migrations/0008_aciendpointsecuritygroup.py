import django.core.validators
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0007_tenant_useg_endpoint_group"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACIEndpointSecurityGroup",
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
                ("admin_shutdown", models.BooleanField(default=False)),
                (
                    "intra_esg_isolation_enabled",
                    models.BooleanField(default=False),
                ),
                (
                    "preferred_group_member_enabled",
                    models.BooleanField(default=False),
                ),
                (
                    "aci_app_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="netbox_aci_plugin.aciappprofile",
                    ),
                ),
                (
                    "aci_vrf",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="netbox_aci_plugin.acivrf",
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
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem", to="extras.Tag"
                    ),
                ),
            ],
            options={
                "verbose_name": "ACI Endpoint Security Group",
                "ordering": ("aci_app_profile", "name"),
                "default_related_name": "aci_endpoint_security_groups",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("aci_app_profile", "name"),
                        name="netbox_aci_plugin_aciendpointsecuritygroup_unique_name_per_aci_app_profile",
                    )
                ],
            },
        ),
    ]
