import django.core.validators
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models

import netbox_aci_plugin.models.mixins


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0006_base_model"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACIUSegEndpointGroup",
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
                (
                    "match_operator",
                    models.CharField(default="any", max_length=3),
                ),
            ],
            options={
                "verbose_name": "ACI uSeg Endpoint Group",
                "default_related_name": "aci_useg_endpoint_groups",
            },
        ),
        migrations.CreateModel(
            name="ACIUSegNetworkAttribute",
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
                    "type",
                    models.CharField(default="mac", editable=False, max_length=3),
                ),
                (
                    "attr_object_id",
                    models.PositiveBigIntegerField(blank=True, null=True),
                ),
                ("use_epg_subnet", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "ACI uSeg Network Attribute",
                "ordering": (
                    "name",
                    "aci_useg_endpoint_group",
                    "_ip_address",
                    "_mac_address",
                    "_prefix",
                ),
                "default_related_name": "aci_useg_network_attributes",
            },
            bases=(
                models.Model,
                netbox_aci_plugin.models.mixins.UniqueGenericForeignKeyMixin,
            ),
        ),
        migrations.AlterModelOptions(
            name="aciendpointgroup",
            options={"default_related_name": "aci_endpoint_groups"},
        ),
        migrations.RemoveConstraint(
            model_name="aciendpointgroup",
            name="netbox_aci_plugin_aciendpointgroup_unique_per_aci_app_profile",
        ),
        migrations.AlterField(
            model_name="acicontractrelation",
            name="aci_object_type",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to=models.Q(
                    ("app_label", "netbox_aci_plugin"),
                    (
                        "model__in",
                        ("aciendpointgroup", "aciusegendpointgroup", "acivrf"),
                    ),
                ),
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AlterField(
            model_name="aciendpointgroup",
            name="aci_app_profile",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="netbox_aci_plugin.aciappprofile",
            ),
        ),
        migrations.AlterField(
            model_name="aciendpointgroup",
            name="aci_bridge_domain",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="netbox_aci_plugin.acibridgedomain",
            ),
        ),
        migrations.AddConstraint(
            model_name="aciendpointgroup",
            constraint=models.UniqueConstraint(
                fields=("aci_app_profile", "name"),
                name="netbox_aci_plugin_aciendpointgroup_unique_name_per_aci_app_profile",
            ),
        ),
        migrations.AddField(
            model_name="aciusegendpointgroup",
            name="aci_app_profile",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="netbox_aci_plugin.aciappprofile",
            ),
        ),
        migrations.AddField(
            model_name="aciusegendpointgroup",
            name="aci_bridge_domain",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="netbox_aci_plugin.acibridgedomain",
            ),
        ),
        migrations.AddField(
            model_name="aciusegendpointgroup",
            name="nb_tenant",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)ss",
                to="tenancy.tenant",
            ),
        ),
        migrations.AddField(
            model_name="aciusegendpointgroup",
            name="tags",
            field=taggit.managers.TaggableManager(
                through="extras.TaggedItem", to="extras.Tag"
            ),
        ),
        migrations.AddField(
            model_name="acicontractrelation",
            name="_aci_useg_endpoint_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="_aci_contract_relations",
                to="netbox_aci_plugin.aciusegendpointgroup",
            ),
        ),
        migrations.AddField(
            model_name="aciusegnetworkattribute",
            name="_ip_address",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="_aci_useg_network_attributes",
                to="ipam.ipaddress",
            ),
        ),
        migrations.AddField(
            model_name="aciusegnetworkattribute",
            name="_mac_address",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="_aci_useg_network_attributes",
                to="dcim.macaddress",
            ),
        ),
        migrations.AddField(
            model_name="aciusegnetworkattribute",
            name="_prefix",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="_aci_useg_network_attributes",
                to="ipam.prefix",
            ),
        ),
        migrations.AddField(
            model_name="aciusegnetworkattribute",
            name="aci_useg_endpoint_group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="netbox_aci_plugin.aciusegendpointgroup",
            ),
        ),
        migrations.AddField(
            model_name="aciusegnetworkattribute",
            name="attr_object_type",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to=models.Q(
                    models.Q(
                        models.Q(
                            ("app_label", "ipam"),
                            ("model__in", ("prefix", "ipaddress")),
                        ),
                        models.Q(("app_label", "dcim"), ("model", "macaddress")),
                        _connector="OR",
                    )
                ),
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AddField(
            model_name="aciusegnetworkattribute",
            name="nb_tenant",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)ss",
                to="tenancy.tenant",
            ),
        ),
        migrations.AddField(
            model_name="aciusegnetworkattribute",
            name="tags",
            field=taggit.managers.TaggableManager(
                through="extras.TaggedItem", to="extras.Tag"
            ),
        ),
        migrations.AddConstraint(
            model_name="aciusegendpointgroup",
            constraint=models.UniqueConstraint(
                fields=("aci_app_profile", "name"),
                name="netbox_aci_plugin_aciusegendpointgroup_unique_name_per_aci_app_profile",
            ),
        ),
        migrations.AddIndex(
            model_name="aciusegnetworkattribute",
            index=models.Index(
                fields=["attr_object_type", "attr_object_id"],
                name="netbox_aci__attr_ob_7a22b7_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="aciusegnetworkattribute",
            constraint=models.UniqueConstraint(
                fields=("name", "aci_useg_endpoint_group"),
                name="netbox_aci_plugin_aciusegnetworkattribute_unique_name_per_useg_endpoint_group",
            ),
        ),
        migrations.AddConstraint(
            model_name="aciusegnetworkattribute",
            constraint=models.UniqueConstraint(
                fields=(
                    "aci_useg_endpoint_group",
                    "attr_object_type",
                    "attr_object_id",
                ),
                name="netbox_aci_plugin_aciusegnetworkattribute_unique_attr_object_per_useg_endpoint_group",
            ),
        ),
        migrations.AddConstraint(
            model_name="aciusegnetworkattribute",
            constraint=models.UniqueConstraint(
                condition=models.Q(("use_epg_subnet", True)),
                fields=("aci_useg_endpoint_group", "use_epg_subnet"),
                name="netbox_aci_plugin_aciusegnetworkattribute_unique_use_epg_subnet_per_useg_endpoint_group",
                violation_error_message="ACI uSeg Endpoint Group with a 'use EPG Subnet' attribute already exists.",
            ),
        ),
    ]
