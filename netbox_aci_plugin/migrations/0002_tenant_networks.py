import dcim.fields
import django.contrib.postgres.fields
import django.core.validators
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenancy", "0015_contactassignment_rename_content_type"),
        ("ipam", "0069_gfk_indexes"),
        ("extras", "0115_convert_dashboard_widgets"),
        ("netbox_aci_plugin", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACIVRF",
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
                                message=(
                                    "Only alphanumeric characters, hyphens, periods and underscores are allowed."
                                ),
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
                                message=(
                                    "Only alphanumeric characters, hyphens, periods and underscores are allowed."
                                ),
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
                                message=(
                                    "Only alphanumeric characters and !#$%%()*,-./:;@ _{|}~?&+ are allowed."
                                ),
                                regex="^[a-zA-Z0-9\\\\!#$%()*,-./:;@ _{|}~?&+]{1,128}$",
                            ),
                        ],
                    ),
                ),
                ("bd_enforcement_enabled", models.BooleanField(default=False)),
                (
                    "dns_labels",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            max_length=64,
                            validators=[
                                django.core.validators.MaxLengthValidator(64),
                                django.core.validators.RegexValidator(
                                    code="invalid",
                                    message=(
                                        "Only alphanumeric characters, hyphens, periods and underscores are allowed."
                                    ),
                                    regex="^[a-zA-Z0-9_.:-]{1,64}$",
                                ),
                            ],
                        ),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "ip_data_plane_learning_enabled",
                    models.BooleanField(default=True),
                ),
                (
                    "pc_enforcement_direction",
                    models.CharField(default="ingress", max_length=8),
                ),
                (
                    "pc_enforcement_preference",
                    models.CharField(default="enforced", max_length=10),
                ),
                ("pim_ipv4_enabled", models.BooleanField(default=False)),
                ("pim_ipv6_enabled", models.BooleanField(default=False)),
                (
                    "preferred_group_enabled",
                    models.BooleanField(default=False),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "aci_tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_vrfs",
                        to="netbox_aci_plugin.acitenant",
                    ),
                ),
                (
                    "nb_tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aci_vrfs",
                        to="tenancy.tenant",
                    ),
                ),
                (
                    "nb_vrf",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aci_vrfs",
                        to="ipam.vrf",
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
                "verbose_name": "ACI VRF",
                "ordering": ("aci_tenant", "name"),
            },
        ),
        migrations.AddConstraint(
            model_name="acivrf",
            constraint=models.UniqueConstraint(
                fields=("aci_tenant", "name"),
                name="unique_aci_vrf_name_per_aci_tenant",
            ),
        ),
        migrations.CreateModel(
            name="ACIBridgeDomain",
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
                                message=(
                                    "Only alphanumeric characters, hyphens, periods and underscores are allowed."
                                ),
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
                                message=(
                                    "Only alphanumeric characters, hyphens, periods and underscores are allowed."
                                ),
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
                                message=(
                                    "Only alphanumeric characters and !#$%%()*,-./:;@ _{|}~?&+ are allowed."
                                ),
                                regex="^[a-zA-Z0-9\\\\!#$%()*,-./:;@ _{|}~?&+]{1,128}$",
                            ),
                        ],
                    ),
                ),
                (
                    "advertise_host_routes_enabled",
                    models.BooleanField(default=False),
                ),
                ("arp_flooding_enabled", models.BooleanField(default=False)),
                (
                    "clear_remote_mac_enabled",
                    models.BooleanField(default=False),
                ),
                (
                    "dhcp_labels",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            max_length=64,
                            validators=[
                                django.core.validators.MaxLengthValidator(64),
                                django.core.validators.RegexValidator(
                                    code="invalid",
                                    message=(
                                        "Only alphanumeric characters, hyphens, periods and underscores are allowed."
                                    ),
                                    regex="^[a-zA-Z0-9_.:-]{1,64}$",
                                ),
                            ],
                        ),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "ep_move_detection_enabled",
                    models.BooleanField(default=False),
                ),
                (
                    "igmp_interface_policy_name",
                    models.CharField(
                        blank=True,
                        max_length=64,
                        validators=[
                            django.core.validators.MaxLengthValidator(64),
                            django.core.validators.RegexValidator(
                                code="invalid",
                                message=(
                                    "Only alphanumeric characters, hyphens, periods and underscores are allowed."
                                ),
                                regex="^[a-zA-Z0-9_.:-]{1,64}$",
                            ),
                        ],
                    ),
                ),
                (
                    "igmp_snooping_policy_name",
                    models.CharField(
                        blank=True,
                        max_length=64,
                        validators=[
                            django.core.validators.MaxLengthValidator(64),
                            django.core.validators.RegexValidator(
                                code="invalid",
                                message=(
                                    "Only alphanumeric characters, hyphens, periods and underscores are allowed."
                                ),
                                regex="^[a-zA-Z0-9_.:-]{1,64}$",
                            ),
                        ],
                    ),
                ),
                (
                    "ip_data_plane_learning_enabled",
                    models.BooleanField(default=True),
                ),
                ("limit_ip_learn_enabled", models.BooleanField(default=True)),
                (
                    "mac_address",
                    dcim.fields.MACAddressField(
                        blank=True, default="00:22:BD:F8:19:FF", null=True
                    ),
                ),
                (
                    "multi_destination_flooding",
                    models.CharField(default="bd-flood", max_length=11),
                ),
                ("pim_ipv4_enabled", models.BooleanField(default=False)),
                (
                    "pim_ipv4_destination_filter",
                    models.CharField(
                        blank=True,
                        max_length=64,
                        validators=[
                            django.core.validators.MaxLengthValidator(64),
                            django.core.validators.RegexValidator(
                                code="invalid",
                                message=(
                                    "Only alphanumeric characters, hyphens, periods and underscores are allowed."
                                ),
                                regex="^[a-zA-Z0-9_.:-]{1,64}$",
                            ),
                        ],
                    ),
                ),
                (
                    "pim_ipv4_source_filter",
                    models.CharField(
                        blank=True,
                        max_length=64,
                        validators=[
                            django.core.validators.MaxLengthValidator(64),
                            django.core.validators.RegexValidator(
                                code="invalid",
                                message=(
                                    "Only alphanumeric characters, hyphens, periods and underscores are allowed."
                                ),
                                regex="^[a-zA-Z0-9_.:-]{1,64}$",
                            ),
                        ],
                    ),
                ),
                ("pim_ipv6_enabled", models.BooleanField(default=False)),
                ("unicast_routing_enabled", models.BooleanField(default=True)),
                (
                    "unknown_ipv4_multicast",
                    models.CharField(default="flood", max_length=9),
                ),
                (
                    "unknown_ipv6_multicast",
                    models.CharField(default="flood", max_length=9),
                ),
                (
                    "unknown_unicast",
                    models.CharField(default="proxy", max_length=5),
                ),
                (
                    "virtual_mac_address",
                    dcim.fields.MACAddressField(blank=True, null=True),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "aci_tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_bridge_domains",
                        to="netbox_aci_plugin.acitenant",
                    ),
                ),
                (
                    "aci_vrf",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aci_bridge_domains",
                        to="netbox_aci_plugin.acivrf",
                    ),
                ),
                (
                    "nb_tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aci_bridge_domains",
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
                "verbose_name": "ACI Bridge Domain",
                "ordering": ("aci_tenant", "aci_vrf", "name"),
            },
        ),
        migrations.AddConstraint(
            model_name="acibridgedomain",
            constraint=models.UniqueConstraint(
                fields=("aci_tenant", "name"),
                name="unique_aci_bridge_domain_name_per_aci_tenant",
            ),
        ),
        migrations.CreateModel(
            name="ACIBridgeDomainSubnet",
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
                                message=(
                                    "Only alphanumeric characters, hyphens, periods and underscores are allowed."
                                ),
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
                                message=(
                                    "Only alphanumeric characters, hyphens, periods and underscores are allowed."
                                ),
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
                                message=(
                                    "Only alphanumeric characters and !#$%%()*,-./:;@ _{|}~?&+ are allowed."
                                ),
                                regex="^[a-zA-Z0-9\\\\!#$%()*,-./:;@ _{|}~?&+]{1,128}$",
                            ),
                        ],
                    ),
                ),
                (
                    "advertised_externally_enabled",
                    models.BooleanField(default=False),
                ),
                ("igmp_querier_enabled", models.BooleanField(default=False)),
                (
                    "ip_data_plane_learning_enabled",
                    models.BooleanField(default=True),
                ),
                ("no_default_gateway", models.BooleanField(default=False)),
                ("nd_ra_enabled", models.BooleanField(default=True)),
                (
                    "nd_ra_prefix_policy_name",
                    models.CharField(
                        blank=True,
                        max_length=64,
                        validators=[
                            django.core.validators.MaxLengthValidator(64),
                            django.core.validators.RegexValidator(
                                code="invalid",
                                message=(
                                    "Only alphanumeric characters, hyphens, periods and underscores are allowed."
                                ),
                                regex="^[a-zA-Z0-9_.:-]{1,64}$",
                            ),
                        ],
                    ),
                ),
                (
                    "preferred_ip_address_enabled",
                    models.BooleanField(default=False),
                ),
                ("shared_enabled", models.BooleanField(default=False)),
                ("virtual_ip_enabled", models.BooleanField(default=False)),
                ("comments", models.TextField(blank=True)),
                (
                    "aci_bridge_domain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_bridge_domain_subnets",
                        to="netbox_aci_plugin.acibridgedomain",
                    ),
                ),
                (
                    "gateway_ip_address",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_bridge_domain_subnet",
                        to="ipam.ipaddress",
                    ),
                ),
                (
                    "nb_tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="aci_bridge_domain_subnets",
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
                "verbose_name": "ACI Bridge Domain Subnet",
                "ordering": ("aci_bridge_domain", "name"),
            },
        ),
        migrations.AddConstraint(
            model_name="acibridgedomainsubnet",
            constraint=models.UniqueConstraint(
                fields=("aci_bridge_domain", "name"),
                name="unique_aci_bd_subnet_name_per_aci_bridge_domain",
            ),
        ),
        migrations.AddConstraint(
            model_name="acibridgedomainsubnet",
            constraint=models.UniqueConstraint(
                fields=("aci_bridge_domain", "gateway_ip_address"),
                name="unique_aci_bd_subnet_gateway_ip_per_aci_bridge_domain",
            ),
        ),
        migrations.AddConstraint(
            model_name="acibridgedomainsubnet",
            constraint=models.UniqueConstraint(
                condition=models.Q(("preferred_ip_address_enabled", True)),
                fields=("aci_bridge_domain",),
                name="unique_aci_bd_subnet_preferred_ip_per_bridge_domain",
                violation_error_message=(
                    "ACI Bridge Domain with a preferred (primary) gateway IP address already exists."
                ),
            ),
        ),
    ]
