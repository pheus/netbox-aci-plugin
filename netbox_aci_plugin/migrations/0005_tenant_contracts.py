import django.core.validators
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0121_customfield_related_object_filter"),
        ("tenancy", "0015_contactassignment_rename_content_type"),
        ("netbox_aci_plugin", "0004_tenant_contract_filters"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACIContract",
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
                (
                    "qos_class",
                    models.CharField(default="unspecified", max_length=11),
                ),
                ("scope", models.CharField(default="context", max_length=19)),
                (
                    "target_dscp",
                    models.CharField(default="unspecified", max_length=11),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "aci_tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_contracts",
                        to="netbox_aci_plugin.acitenant",
                    ),
                ),
                (
                    "nb_tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aci_contracts",
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
                "verbose_name": "ACI Contract",
                "ordering": ("aci_tenant", "name"),
            },
        ),
        migrations.CreateModel(
            name="ACIContractRelation",
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
                    "aci_object_id",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("role", models.CharField(default="prov", max_length=4)),
                ("comments", models.TextField(blank=True)),
                (
                    "_aci_endpoint_group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="_aci_contract_relations",
                        to="netbox_aci_plugin.aciendpointgroup",
                    ),
                ),
                (
                    "_aci_vrf",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="_aci_contract_relations",
                        to="netbox_aci_plugin.acivrf",
                    ),
                ),
                (
                    "aci_contract",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_contract_relations",
                        to="netbox_aci_plugin.acicontract",
                    ),
                ),
                (
                    "aci_object_type",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to=models.Q(
                            ("model__in", ("aciendpointgroup", "acivrf"))
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
            ],
            options={
                "verbose_name": "ACI Contract Relation",
                "ordering": (
                    "aci_contract",
                    "_aci_endpoint_group",
                    "_aci_vrf",
                    "role",
                ),
            },
        ),
        migrations.CreateModel(
            name="ACIContractSubject",
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
                (
                    "apply_both_directions_enabled",
                    models.BooleanField(default=True),
                ),
                (
                    "qos_class",
                    models.CharField(default="unspecified", max_length=11),
                ),
                (
                    "qos_class_cons_to_prov",
                    models.CharField(default="unspecified", max_length=11),
                ),
                (
                    "qos_class_prov_to_cons",
                    models.CharField(default="unspecified", max_length=11),
                ),
                (
                    "reverse_filter_ports_enabled",
                    models.BooleanField(default=True),
                ),
                (
                    "service_graph_name",
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
                    "service_graph_name_cons_to_prov",
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
                    "service_graph_name_prov_to_cons",
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
                    "target_dscp",
                    models.CharField(default="unspecified", max_length=11),
                ),
                (
                    "target_dscp_cons_to_prov",
                    models.CharField(default="unspecified", max_length=11),
                ),
                (
                    "target_dscp_prov_to_cons",
                    models.CharField(default="unspecified", max_length=11),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "aci_contract",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_contract_subjects",
                        to="netbox_aci_plugin.acicontract",
                    ),
                ),
                (
                    "nb_tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aci_contract_subjects",
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
                "verbose_name": "ACI Contract Subject",
                "ordering": ("aci_contract", "name"),
            },
        ),
        migrations.CreateModel(
            name="ACIContractSubjectFilter",
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
                ("action", models.CharField(default="permit", max_length=6)),
                (
                    "apply_direction",
                    models.CharField(default="both", max_length=4),
                ),
                ("log_enabled", models.BooleanField(default=False)),
                (
                    "policy_compression_enabled",
                    models.BooleanField(default=False),
                ),
                (
                    "priority",
                    models.CharField(default="default", max_length=7),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "aci_contract_filter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_contract_subject_filters",
                        to="netbox_aci_plugin.acicontractfilter",
                    ),
                ),
                (
                    "aci_contract_subject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_contract_subject_filters",
                        to="netbox_aci_plugin.acicontractsubject",
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
                "verbose_name": "ACI Contract Subject Filter",
                "ordering": ("aci_contract_subject", "aci_contract_filter"),
            },
        ),
        migrations.AddConstraint(
            model_name="acicontract",
            constraint=models.UniqueConstraint(
                fields=("aci_tenant", "name"),
                name="unique_aci_contract_name_per_aci_tenant",
            ),
        ),
        migrations.AddIndex(
            model_name="acicontractrelation",
            index=models.Index(
                fields=["aci_object_type", "aci_object_id"],
                name="netbox_aci__aci_obj_1fb91d_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="acicontractrelation",
            constraint=models.UniqueConstraint(
                fields=(
                    "aci_contract",
                    "aci_object_type",
                    "aci_object_id",
                    "role",
                ),
                name="unique_aci_object_relation_role_per_aci_contract",
            ),
        ),
        migrations.AddConstraint(
            model_name="acicontractsubject",
            constraint=models.UniqueConstraint(
                fields=("aci_contract", "name"),
                name="unique_aci_contract_subject_name_per_aci_contract",
            ),
        ),
        migrations.AddConstraint(
            model_name="acicontractsubjectfilter",
            constraint=models.UniqueConstraint(
                fields=("aci_contract_subject", "aci_contract_filter"),
                name="unique_aci_contract_filter_per_aci_contract_subject",
            ),
        ),
    ]
