import django.core.validators
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenancy", "0015_contactassignment_rename_content_type"),
        ("extras", "0115_convert_dashboard_widgets"),
        ("netbox_aci_plugin", "0002_tenant_networks"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACIAppProfile",
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
                    "aci_tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_app_profiles",
                        to="netbox_aci_plugin.acitenant",
                    ),
                ),
                (
                    "nb_tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aci_app_profiles",
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
                "verbose_name": "ACI Application Profile",
                "ordering": ("aci_tenant", "name"),
            },
        ),
        migrations.AddConstraint(
            model_name="aciappprofile",
            constraint=models.UniqueConstraint(
                fields=("aci_tenant", "name"),
                name="unique_aci_app_profile_name_per_aci_tenant",
            ),
        ),
        migrations.CreateModel(
            name="ACIEndpointGroup",
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
                ("admin_shutdown", models.BooleanField(default=False)),
                (
                    "custom_qos_policy_name",
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
                ("flood_in_encap_enabled", models.BooleanField(default=False)),
                (
                    "intra_epg_isolation_enabled",
                    models.BooleanField(default=False),
                ),
                (
                    "qos_class",
                    models.CharField(default="unspecified", max_length=11),
                ),
                (
                    "preferred_group_member_enabled",
                    models.BooleanField(default=False),
                ),
                ("proxy_arp_enabled", models.BooleanField(default=False)),
                ("comments", models.TextField(blank=True)),
                (
                    "aci_app_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_endpoint_groups",
                        to="netbox_aci_plugin.aciappprofile",
                    ),
                ),
                (
                    "aci_bridge_domain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_endpoint_groups",
                        to="netbox_aci_plugin.acibridgedomain",
                    ),
                ),
                (
                    "nb_tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aci_endpoint_groups",
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
                "verbose_name": "ACI Endpoint Group",
                "ordering": ("aci_app_profile", "name"),
            },
        ),
        migrations.AddConstraint(
            model_name="aciendpointgroup",
            constraint=models.UniqueConstraint(
                fields=("aci_app_profile", "name"),
                name="unique_endpoint_group_name_per_aci_app_profile",
            ),
        ),
    ]
