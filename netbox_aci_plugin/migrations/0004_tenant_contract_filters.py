import django.contrib.postgres.fields
import django.core.validators
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models
from netbox.plugins.utils import get_plugin_config

import netbox_aci_plugin.models.tenant.contract_filters
import netbox_aci_plugin.validators
from netbox_aci_plugin import ACIConfig


def create_default_aci_contract_filters(apps, schema_editor) -> None:
    """Creates default ACI Contract Filters if they do not already exist."""
    if get_plugin_config(ACIConfig.name, "create_default_aci_contract_filters", True):
        db_alias = schema_editor.connection.alias
        # The model cannot be imported directly as it may be a newer
        # version than this migration expects.
        aci_tenant = apps.get_model(ACIConfig.name, "ACITenant")
        aci_contract_filter = apps.get_model(ACIConfig.name, "ACIContractFilter")
        aci_contract_filter_entry = apps.get_model(
            ACIConfig.name, "ACIContractFilterEntry"
        )
        # Ensure ACI Tenant "common" exists
        if not aci_tenant.objects.using(db_alias).filter(name="common").exists():
            aci_tenant.objects.using(db_alias).create(name="common")
        aci_common_tenant = aci_tenant.objects.using(db_alias).get(name="common")

        # Define default contract filters and their entries
        default_aci_filters = [
            {
                "name": "default",
                "aci_filter_entry": {
                    "name": "default",
                },
            },
            {
                "name": "arp",
                "aci_filter_entry": {
                    "name": "arp",
                    "ether_type": "arp",
                },
            },
            {
                "name": "est",
                "aci_filter_entry": {
                    "name": "est",
                    "ether_type": "ip",
                    "ip_protocol": "tcp",
                    "tcp_rules": ["est"],
                },
            },
            {
                "name": "icmp",
                "aci_filter_entry": {
                    "name": "icmp",
                    "ether_type": "ip",
                    "ip_protocol": "icmp",
                },
            },
        ]

        # Create filters and entries if they do not already exist
        for default_aci_filter in default_aci_filters:
            if not aci_contract_filter.objects.filter(
                name=default_aci_filter["name"]
            ).exists():
                created_filter = aci_contract_filter.objects.create(
                    name=default_aci_filter["name"],
                    aci_tenant=aci_common_tenant,
                )
                aci_contract_filter_entry.objects.create(
                    aci_contract_filter=created_filter,
                    **default_aci_filter["aci_filter_entry"],
                )


class Migration(migrations.Migration):
    dependencies = [
        ("extras", "0121_customfield_related_object_filter"),
        ("tenancy", "0015_contactassignment_rename_content_type"),
        ("netbox_aci_plugin", "0003_tenant_app_profiles"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACIContractFilter",
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
                        related_name="aci_contract_filters",
                        to="netbox_aci_plugin.acitenant",
                    ),
                ),
                (
                    "nb_tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aci_contract_filters",
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
                "verbose_name": "ACI Contract Filter",
                "ordering": ("aci_tenant", "name"),
            },
        ),
        migrations.CreateModel(
            name="ACIContractFilterEntry",
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
                    "arp_opc",
                    models.CharField(default="unspecified", max_length=11),
                ),
                (
                    "destination_from_port",
                    models.CharField(
                        default="unspecified",
                        max_length=11,
                        validators=[
                            netbox_aci_plugin.validators.validate_contract_filter_port
                        ],
                    ),
                ),
                (
                    "destination_to_port",
                    models.CharField(
                        default="unspecified",
                        max_length=11,
                        validators=[
                            netbox_aci_plugin.validators.validate_contract_filter_port
                        ],
                    ),
                ),
                (
                    "ether_type",
                    models.CharField(default="unspecified", max_length=12),
                ),
                (
                    "icmp_v4_type",
                    models.CharField(default="unspecified", max_length=13),
                ),
                (
                    "icmp_v6_type",
                    models.CharField(default="unspecified", max_length=13),
                ),
                (
                    "ip_protocol",
                    models.CharField(
                        default="unspecified",
                        max_length=11,
                        validators=[
                            netbox_aci_plugin.validators.validate_contract_filter_ip_protocol
                        ],
                    ),
                ),
                (
                    "match_dscp",
                    models.CharField(default="unspecified", max_length=11),
                ),
                (
                    "match_only_fragments_enabled",
                    models.BooleanField(default=False),
                ),
                (
                    "source_from_port",
                    models.CharField(
                        default="unspecified",
                        max_length=11,
                        validators=[
                            netbox_aci_plugin.validators.validate_contract_filter_port
                        ],
                    ),
                ),
                (
                    "source_to_port",
                    models.CharField(
                        default="unspecified",
                        max_length=11,
                        validators=[
                            netbox_aci_plugin.validators.validate_contract_filter_port
                        ],
                    ),
                ),
                ("stateful_enabled", models.BooleanField(default=False)),
                (
                    "tcp_rules",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=11),
                        blank=True,
                        default=netbox_aci_plugin.models.tenant.contract_filters.default_contract_filter_entry_tcp_rules,
                        size=None,
                        validators=[
                            netbox_aci_plugin.validators.validate_contract_filter_tcp_rules
                        ],
                    ),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "aci_contract_filter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_contract_filter_entries",
                        to="netbox_aci_plugin.acicontractfilter",
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
                "verbose_name": "ACI Contract Filter Entry",
                "verbose_name_plural": "ACI Contract Filter Entries",
                "ordering": ("aci_contract_filter", "name"),
            },
        ),
        migrations.AddConstraint(
            model_name="acicontractfilter",
            constraint=models.UniqueConstraint(
                fields=("aci_tenant", "name"),
                name="unique_aci_contract_filter_name_per_aci_tenant",
            ),
        ),
        migrations.AddConstraint(
            model_name="acicontractfilterentry",
            constraint=models.UniqueConstraint(
                fields=("aci_contract_filter", "name"),
                name="unique_aci_filter_entry_name_per_aci_contract_filter",
            ),
        ),
        migrations.RunPython(create_default_aci_contract_filters),
    ]
