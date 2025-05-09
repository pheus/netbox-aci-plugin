import django.core.validators
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models

import netbox_aci_plugin.models.mixins


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0007_tenant_useg_endpoint_group"),
    ]

    operations = [
        migrations.AlterField(
            model_name="acicontractrelation",
            name="aci_object_type",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to=models.Q(
                    ("app_label", "netbox_aci_plugin"),
                    (
                        "model__in",
                        (
                            "aciendpointgroup",
                            "aciendpointsecuritygroup",
                            "aciusegendpointgroup",
                            "acivrf",
                        ),
                    ),
                ),
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="contenttypes.contenttype",
            ),
        ),
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
            },
        ),
        migrations.AddField(
            model_name="acicontractrelation",
            name="_aci_endpoint_security_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="_aci_contract_relations",
                to="netbox_aci_plugin.aciendpointsecuritygroup",
            ),
        ),
        migrations.CreateModel(
            name="ACIEsgEndpointGroupSelector",
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
                    "aci_epg_object_id",
                    models.PositiveBigIntegerField(blank=True, null=True),
                ),
                (
                    "_aci_endpoint_group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="_aci_esg_endpoint_group_selectors",
                        to="netbox_aci_plugin.aciendpointgroup",
                    ),
                ),
                (
                    "_aci_useg_endpoint_group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="_aci_esg_endpoint_group_selectors",
                        to="netbox_aci_plugin.aciusegendpointgroup",
                    ),
                ),
                (
                    "aci_endpoint_security_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="netbox_aci_plugin.aciendpointsecuritygroup",
                    ),
                ),
                (
                    "aci_epg_object_type",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to=models.Q(
                            models.Q(
                                ("app_label", "netbox_aci_plugin"),
                                (
                                    "model__in",
                                    (
                                        "aciendpointgroup",
                                        "aciusegendpointgroup",
                                    ),
                                ),
                            )
                        ),
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="contenttypes.contenttype",
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
                "verbose_name": "ACI ESG Endpoint Group Selector",
                "ordering": (
                    "name",
                    "aci_endpoint_security_group",
                    "_aci_endpoint_group",
                    "_aci_useg_endpoint_group",
                ),
                "default_related_name": "aci_esg_endpoint_group_selectors",
            },
            bases=(
                models.Model,
                netbox_aci_plugin.models.mixins.UniqueGenericForeignKeyMixin,
            ),
        ),
        migrations.CreateModel(
            name="ACIEsgEndpointSelector",
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
                    "ep_object_id",
                    models.PositiveBigIntegerField(blank=True, null=True),
                ),
                (
                    "_ip_address",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="_aci_esg_endpoint_selectors",
                        to="ipam.ipaddress",
                    ),
                ),
                (
                    "_prefix",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="_aci_esg_endpoint_selectors",
                        to="ipam.prefix",
                    ),
                ),
                (
                    "aci_endpoint_security_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="netbox_aci_plugin.aciendpointsecuritygroup",
                    ),
                ),
                (
                    "ep_object_type",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to=models.Q(
                            models.Q(
                                ("app_label", "ipam"),
                                ("model__in", ("prefix", "ipaddress")),
                            )
                        ),
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="contenttypes.contenttype",
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
                "verbose_name": "ACI ESG Endpoint Selector",
                "ordering": (
                    "name",
                    "aci_endpoint_security_group",
                    "_ip_address",
                    "_prefix",
                ),
                "default_related_name": "aci_esg_endpoint_selectors",
            },
            bases=(
                models.Model,
                netbox_aci_plugin.models.mixins.UniqueGenericForeignKeyMixin,
            ),
        ),
        migrations.AddConstraint(
            model_name="aciendpointsecuritygroup",
            constraint=models.UniqueConstraint(
                fields=("aci_app_profile", "name"),
                name="netbox_aci_plugin_aciendpointsecuritygroup_unique_name_per_aci_app_profile",
            ),
        ),
        migrations.AddIndex(
            model_name="aciesgendpointgroupselector",
            index=models.Index(
                fields=["aci_epg_object_type", "aci_epg_object_id"],
                name="netbox_aci__aci_epg_44bc03_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="aciesgendpointgroupselector",
            constraint=models.UniqueConstraint(
                fields=("name", "aci_endpoint_security_group"),
                name="netbox_aci_plugin_aciesgendpointgroupselector_unique_name_per_endpoint_security_group",
            ),
        ),
        migrations.AddConstraint(
            model_name="aciesgendpointgroupselector",
            constraint=models.UniqueConstraint(
                fields=(
                    "aci_endpoint_security_group",
                    "aci_epg_object_type",
                    "aci_epg_object_id",
                ),
                name="netbox_aci_plugin_aciesgendpointgroupselector_unique_aci_epg_object_per_endpoint_security_group",
            ),
        ),
        migrations.AddIndex(
            model_name="aciesgendpointselector",
            index=models.Index(
                fields=["ep_object_type", "ep_object_id"],
                name="netbox_aci__ep_obje_85224b_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="aciesgendpointselector",
            constraint=models.UniqueConstraint(
                fields=("name", "aci_endpoint_security_group"),
                name="netbox_aci_plugin_aciesgendpointselector_unique_name_per_endpoint_security_group",
            ),
        ),
        migrations.AddConstraint(
            model_name="aciesgendpointselector",
            constraint=models.UniqueConstraint(
                fields=(
                    "aci_endpoint_security_group",
                    "ep_object_type",
                    "ep_object_id",
                ),
                name="netbox_aci_plugin_aciesgendpointselector_unique_ep_object_per_endpoint_security_group",
            ),
        ),
    ]
