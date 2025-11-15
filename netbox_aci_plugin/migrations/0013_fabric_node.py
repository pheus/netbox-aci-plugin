import django.core.validators
import django.db.models.deletion
import netbox.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models

import netbox_aci_plugin.models.mixins


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0012_fabric_pod"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACINode",
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
                    "node_id",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(4000),
                        ]
                    ),
                ),
                (
                    "node_object_id",
                    models.PositiveBigIntegerField(blank=True, null=True),
                ),
                ("role", models.CharField(default="leaf", max_length=6)),
                ("node_type", models.CharField(default="unknown", max_length=16)),
                (
                    "_device",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="_aci_nodes",
                        to="dcim.device",
                    ),
                ),
                (
                    "_virtual_machine",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="_aci_nodes",
                        to="virtualization.virtualmachine",
                    ),
                ),
                (
                    "aci_pod",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_nodes",
                        to="netbox_aci_plugin.acipod",
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
                    "node_object_type",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to=models.Q(
                            models.Q(
                                models.Q(("app_label", "dcim"), ("model", "device")),
                                models.Q(
                                    ("app_label", "virtualization"),
                                    ("model", "virtualmachine"),
                                ),
                                _connector="OR",
                            )
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
                    "tep_ip_address",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aci_nodes",
                        to="ipam.ipaddress",
                    ),
                ),
            ],
            options={
                "verbose_name": "ACI Node",
                "ordering": ("aci_pod", "node_id"),
                "constraints": [
                    models.UniqueConstraint(
                        fields=("aci_pod", "node_id"),
                        name="netbox_aci_plugin_acinode_unique_nodeid_per_pod",
                    ),
                    models.UniqueConstraint(
                        fields=("aci_pod", "name"),
                        name="netbox_aci_plugin_acinode_unique_nodename_per_pod",
                    ),
                    models.UniqueConstraint(
                        fields=("node_object_id", "node_object_type"),
                        name="netbox_aci_plugin_acinode_unique_node_object",
                        violation_error_message="ACI Node must be unique per ACI Fabric.",
                    ),
                ],
            },
            bases=(
                netbox.models.deletion.DeleteMixin,
                models.Model,
                netbox_aci_plugin.models.mixins.UniqueGenericForeignKeyMixin,
            ),
        ),
    ]
