import django.core.validators
import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import netbox.models.deletion
import netbox_aci_plugin.models.mixins
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0022_rename_bd_subnet_preferred_ip_constraint"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACIAttachableAccessEntityProfile",
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
                ("infra_vlan", models.BooleanField(default=False)),
                (
                    "aci_fabric",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_aaeps",
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
                "verbose_name": "ACI Attachable Access Entity Profile",
                "ordering": ("aci_fabric", "name"),
                "default_related_name": "aci_aaeps",
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.CreateModel(
            name="ACIAAEPDomainBinding",
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
                    "aci_domain_object_id",
                    models.PositiveBigIntegerField(blank=True, null=True),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "_aci_physical_domain",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="_aci_aaep_domain_bindings",
                        to="netbox_aci_plugin.aciphysicaldomain",
                    ),
                ),
                (
                    "_aci_routed_domain",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="_aci_aaep_domain_bindings",
                        to="netbox_aci_plugin.acirouteddomain",
                    ),
                ),
                (
                    "aci_domain_object_type",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to=models.Q(
                            ("app_label", "netbox_aci_plugin"),
                            ("model__in", ("aciphysicaldomain", "acirouteddomain")),
                        ),
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
                    "aci_aaep",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_aaep_domain_bindings",
                        to="netbox_aci_plugin.aciattachableaccessentityprofile",
                    ),
                ),
            ],
            options={
                "verbose_name": "ACI AAEP Domain Binding",
                "ordering": ("aci_aaep", "_aci_physical_domain", "_aci_routed_domain"),
                "default_related_name": "aci_aaep_domain_bindings",
            },
            bases=(
                netbox.models.deletion.DeleteMixin,
                models.Model,
                netbox_aci_plugin.models.mixins.UniqueGenericForeignKeyMixin,
            ),
        ),
        migrations.AddConstraint(
            model_name="aciattachableaccessentityprofile",
            constraint=models.UniqueConstraint(
                fields=("aci_fabric", "name"),
                name="netbox_aci_plugin_aciattachableaccessentityprofile_unique_name_per_aci_fabric",
            ),
        ),
        migrations.AddIndex(
            model_name="aciaaepdomainbinding",
            index=models.Index(
                fields=["aci_domain_object_type", "aci_domain_object_id"],
                name="netbox_aci__aci_dom_b59ca7_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="aciaaepdomainbinding",
            constraint=models.UniqueConstraint(
                fields=("aci_aaep", "aci_domain_object_type", "aci_domain_object_id"),
                name="netbox_aci_plugin_aciaaepdomainbinding_unique_aci_domain_object_per_aaep",
            ),
        ),
    ]
