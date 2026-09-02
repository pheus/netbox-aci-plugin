import django.core.validators
import django.db.models.deletion
import taggit.managers
from django.db import migrations, models
from django.db.models.functions import Greatest, Least

import netbox.models.deletion
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0027_acinode_fabric_scope_stage"),
        ("dcim", "0225_gfk_indexes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="acinode",
            name="_aci_fabric",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="netbox_aci_plugin.acifabric",
            ),
        ),
        migrations.AddConstraint(
            model_name="acinode",
            constraint=models.UniqueConstraint(
                fields=("_aci_fabric", "node_id"),
                name="netbox_aci_plugin_acinode_uniq_nodeid_per_fabric",
                violation_error_message="ACI Node IDs must be unique per ACI Fabric.",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="acinode",
            name="netbox_aci_plugin_acinode_unique_nodeid_per_pod",
        ),
        migrations.CreateModel(
            name="ACINodeInterface",
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
                    "module",
                    models.PositiveSmallIntegerField(
                        default=1,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(255),
                        ],
                    ),
                ),
                (
                    "port",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(127),
                        ]
                    ),
                ),
                (
                    "sub_port",
                    models.PositiveSmallIntegerField(
                        default=0,
                        validators=[django.core.validators.MaxValueValidator(64)],
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
                    "aci_node",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_node_interfaces",
                        to="netbox_aci_plugin.acinode",
                    ),
                ),
                (
                    "nb_interface",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aci_node_interface",
                        to="dcim.interface",
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
                        related_name="+",
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
                "verbose_name": "ACI Node Interface",
                "ordering": ("aci_node", "module", "port", "sub_port"),
                "default_related_name": "aci_node_interfaces",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("aci_node", "module", "port", "sub_port"),
                        name="netbox_aci_plugin_acinodeinterface_uniq_coords",
                        violation_error_message=(
                            "A Node Interface with these coordinates already "
                            "exists on the ACI Node."
                        ),
                    ),
                ],
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.CreateModel(
            name="ACILeafInterfacePolicyGroup",
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
                ("group_type", models.CharField(max_length=16)),
                (
                    "aci_aaep",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_leaf_interface_policy_groups",
                        to="netbox_aci_plugin.aciattachableaccessentityprofile",
                    ),
                ),
                (
                    "aci_fabric",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_leaf_interface_policy_groups",
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
                        related_name="+",
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
                "verbose_name": "ACI Leaf Interface Policy Group",
                "ordering": ("aci_fabric", "name"),
                "default_related_name": "aci_leaf_interface_policy_groups",
                "constraints": [
                    models.UniqueConstraint(
                        condition=models.Q(group_type="access"),
                        fields=("aci_fabric", "name"),
                        name="netbox_aci_plugin_acileafinterfacepolicygroup_uniq_access_name",
                        violation_error_message=(
                            "An Access Interface Policy Group with this "
                            "name already exists in the ACI Fabric."
                        ),
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(group_type__in=("pc", "vpc")),
                        fields=("aci_fabric", "name"),
                        name="netbox_aci_plugin_acileafinterfacepolicygroup_uniq_bundle_name",
                        violation_error_message=(
                            "A Port Channel or Virtual Port Channel "
                            "Interface Policy Group with this name "
                            "already exists in the ACI Fabric."
                        ),
                    ),
                ],
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.CreateModel(
            name="ACIVPCProtectionGroup",
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
                    "logical_pair_id",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(1000),
                        ]
                    ),
                ),
                (
                    "aci_fabric",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_vpc_protection_groups",
                        to="netbox_aci_plugin.acifabric",
                    ),
                ),
                (
                    "aci_node_a",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="netbox_aci_plugin.acinode",
                    ),
                ),
                (
                    "aci_node_b",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="netbox_aci_plugin.acinode",
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
                        related_name="+",
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
                "verbose_name": "ACI VPC Protection Group",
                "ordering": ("aci_fabric", "logical_pair_id"),
                "default_related_name": "aci_vpc_protection_groups",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("aci_fabric", "name"),
                        name="netbox_aci_plugin_acivpcprotectiongroup_uniq_name",
                        violation_error_message=(
                            "A VPC Protection Group with this name already "
                            "exists in the ACI Fabric."
                        ),
                    ),
                    models.UniqueConstraint(
                        fields=("aci_fabric", "logical_pair_id"),
                        name="netbox_aci_plugin_acivpcprotectiongroup_uniq_pair_id",
                        violation_error_message=(
                            "A VPC Protection Group with this logical pair "
                            "ID already exists in the ACI Fabric."
                        ),
                    ),
                    models.UniqueConstraint(
                        Least("aci_node_a", "aci_node_b"),
                        Greatest("aci_node_a", "aci_node_b"),
                        name="netbox_aci_plugin_acivpcprotectiongroup_uniq_pair",
                        violation_error_message=(
                            "This pair of ACI Nodes is already assigned to "
                            "another VPC Protection Group."
                        ),
                    ),
                    models.CheckConstraint(
                        condition=~models.Q(aci_node_a=models.F("aci_node_b")),
                        name="netbox_aci_plugin_acivpcprotectiongroup_distinct_nodes",
                    ),
                ],
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
    ]
