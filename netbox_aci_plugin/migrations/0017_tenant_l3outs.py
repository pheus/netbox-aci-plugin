import django.core.validators
import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import ipam.fields
import netbox.models.deletion
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0016_access_policy_routed_domain"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACIL3Out",
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
                    "bfd_policy_name",
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
                ("bgp_enabled", models.BooleanField(default=False)),
                (
                    "custom_qos_policy_name",
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
                    "egress_data_plane_policing_policy_name",
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
                ("eigrp_enabled", models.BooleanField(default=False)),
                (
                    "eigrp_interface_policy_name",
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
                    "export_route_control_enforcement_enabled",
                    models.BooleanField(default=True),
                ),
                (
                    "igmp_interface_policy_name",
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
                    "import_route_control_enforcement_enabled",
                    models.BooleanField(default=False),
                ),
                (
                    "ingress_data_plane_policing_policy_name",
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
                    "interleak_route_map_name",
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
                ("l3_multicast_ipv4_enabled", models.BooleanField(default=False)),
                ("l3_multicast_ipv6_enabled", models.BooleanField(default=False)),
                ("multipod_enabled", models.BooleanField(default=False)),
                ("ospf_enabled", models.BooleanField(default=False)),
                (
                    "ospf_external_policy_name",
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
                    "pim_policy_name",
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
                ("target_dscp", models.CharField(default="unspecified", max_length=11)),
                (
                    "aci_routed_domain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_l3outs",
                        to="netbox_aci_plugin.acirouteddomain",
                    ),
                ),
                (
                    "aci_tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_l3outs",
                        to="netbox_aci_plugin.acitenant",
                    ),
                ),
                (
                    "aci_vrf",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_l3outs",
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
                "verbose_name": "ACI L3Out",
                "ordering": ("aci_tenant", "name"),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.CreateModel(
            name="ACIExternalEndpointGroup",
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
                ("qos_class", models.CharField(default="unspecified", max_length=11)),
                ("preferred_group_member_enabled", models.BooleanField(default=False)),
                ("target_dscp", models.CharField(default="unspecified", max_length=11)),
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
                (
                    "aci_l3out",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_external_endpoint_groups",
                        to="netbox_aci_plugin.acil3out",
                    ),
                ),
            ],
            options={
                "verbose_name": "ACI External Endpoint Group",
                "ordering": ("aci_l3out", "name"),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.CreateModel(
            name="ACIExternalSubnet",
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
                    "matched_prefix",
                    ipam.fields.IPNetworkField(db_index=True),
                ),
                ("import_route_control_enabled", models.BooleanField(default=False)),
                ("export_route_control_enabled", models.BooleanField(default=False)),
                ("shared_route_control_enabled", models.BooleanField(default=False)),
                ("import_security_enabled", models.BooleanField(default=True)),
                ("shared_security_enabled", models.BooleanField(default=False)),
                (
                    "aggregate_import_route_control_enabled",
                    models.BooleanField(default=False),
                ),
                (
                    "aggregate_export_route_control_enabled",
                    models.BooleanField(default=False),
                ),
                (
                    "aggregate_shared_route_control_enabled",
                    models.BooleanField(default=False),
                ),
                ("bgp_route_summarization_enabled", models.BooleanField(default=False)),
                (
                    "bgp_route_summarization_policy_name",
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
                    "ospf_route_summarization_enabled",
                    models.BooleanField(default=False),
                ),
                (
                    "ospf_route_summarization_policy_name",
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
                    "eigrp_route_summarization_enabled",
                    models.BooleanField(default=False),
                ),
                (
                    "aci_external_endpoint_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_external_subnets",
                        to="netbox_aci_plugin.aciexternalendpointgroup",
                    ),
                ),
                (
                    "nb_prefix",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_external_subnets",
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
                "verbose_name": "ACI External Subnet",
                "ordering": ("aci_external_endpoint_group", "matched_prefix", "name"),
                "constraints": [
                    models.UniqueConstraint(
                        fields=("aci_external_endpoint_group", "name"),
                        name="netbox_aci_plugin_aciexternalsubnet_unique_per_ext_epg",
                    ),
                    models.UniqueConstraint(
                        fields=("aci_external_endpoint_group", "matched_prefix"),
                        name="netbox_aci_plugin_aciexternalsubnet_unique_matched_prefix_ext_epg",
                    ),
                ],
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.AddConstraint(
            model_name="acil3out",
            constraint=models.UniqueConstraint(
                fields=("aci_tenant", "name"),
                name="netbox_aci_plugin_acil3out_unique_per_aci_tenant",
            ),
        ),
        migrations.AddConstraint(
            model_name="aciexternalendpointgroup",
            constraint=models.UniqueConstraint(
                fields=("aci_l3out", "name"),
                name="netbox_aci_plugin_aciexternalendpointgroup_unique_per_l3out",
            ),
        ),
        migrations.AlterModelOptions(
            name="acicontractrelation",
            options={
                "ordering": (
                    "aci_contract",
                    "_aci_endpoint_group",
                    "_aci_external_endpoint_group",
                    "_aci_vrf",
                    "role",
                )
            },
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
                        (
                            "aciendpointgroup",
                            "aciendpointsecuritygroup",
                            "aciexternalendpointgroup",
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
        migrations.AddField(
            model_name="acicontractrelation",
            name="_aci_external_endpoint_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="_aci_contract_relations",
                to="netbox_aci_plugin.aciexternalendpointgroup",
            ),
        ),
    ]
