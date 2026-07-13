import django.core.validators
import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import netbox.models.deletion
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0024_epg_domain_binding"),
        ("ipam", "0086_gfk_indexes"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACIEndpointGroupAAEPBinding",
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
                    "encap_vlan_id",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(4094),
                        ],
                    ),
                ),
                (
                    "primary_encap_vlan_id",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(4094),
                        ],
                    ),
                ),
                ("mode", models.CharField(default="regular", max_length=8)),
                (
                    "deployment_immediacy",
                    models.CharField(default="lazy", max_length=9),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "aci_aaep",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_endpoint_group_bindings",
                        to="netbox_aci_plugin.aciattachableaccessentityprofile",
                    ),
                ),
                (
                    "aci_endpoint_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aci_aaep_bindings",
                        to="netbox_aci_plugin.aciendpointgroup",
                    ),
                ),
                (
                    "nb_vlan",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)ss",
                        to="ipam.vlan",
                    ),
                ),
                (
                    "primary_nb_vlan",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="ipam.vlan",
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
                "verbose_name": "ACI Endpoint Group AAEP Binding",
                "ordering": ("aci_endpoint_group", "aci_aaep"),
                "default_related_name": "aci_endpoint_group_aaep_bindings",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("aci_endpoint_group", "aci_aaep"),
                        name="netbox_aci_plugin_aciendpointgroupaaepbinding_unique_binding",
                    )
                ],
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
    ]
