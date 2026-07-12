import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import netbox.models.deletion
import netbox_aci_plugin.models.mixins
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_aci_plugin", "0023_access_policy_aaep"),
    ]

    operations = [
        migrations.CreateModel(
            name="ACIEndpointGroupDomainBinding",
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
                    "aci_epg_object_id",
                    models.PositiveBigIntegerField(blank=True, null=True),
                ),
                (
                    "aci_domain_object_id",
                    models.PositiveBigIntegerField(blank=True, null=True),
                ),
                (
                    "deployment_immediacy",
                    models.CharField(default="lazy", max_length=9),
                ),
                (
                    "resolution_immediacy",
                    models.CharField(default="lazy", max_length=13),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "_aci_endpoint_group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="_aci_endpoint_group_domain_bindings",
                        to="netbox_aci_plugin.aciendpointgroup",
                    ),
                ),
                (
                    "_aci_physical_domain",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="_aci_endpoint_group_domain_bindings",
                        to="netbox_aci_plugin.aciphysicaldomain",
                    ),
                ),
                (
                    "_aci_useg_endpoint_group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="_aci_endpoint_group_domain_bindings",
                        to="netbox_aci_plugin.aciusegendpointgroup",
                    ),
                ),
                (
                    "aci_domain_object_type",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to=models.Q(
                            ("app_label", "netbox_aci_plugin"),
                            ("model__in", ("aciphysicaldomain",)),
                        ),
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "aci_epg_object_type",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to=models.Q(
                            ("app_label", "netbox_aci_plugin"),
                            (
                                "model__in",
                                ("aciendpointgroup", "aciusegendpointgroup"),
                            ),
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
                "verbose_name": "ACI Endpoint Group Domain Binding",
                "ordering": (
                    "_aci_endpoint_group",
                    "_aci_useg_endpoint_group",
                    "_aci_physical_domain",
                ),
                "default_related_name": "aci_endpoint_group_domain_bindings",
                "indexes": [
                    models.Index(
                        fields=["aci_epg_object_type", "aci_epg_object_id"],
                        name="netbox_aci__aci_epg_7b531c_idx",
                    ),
                    models.Index(
                        fields=["aci_domain_object_type", "aci_domain_object_id"],
                        name="netbox_aci__aci_dom_8afab1_idx",
                    ),
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=(
                            "aci_epg_object_type",
                            "aci_epg_object_id",
                            "aci_domain_object_type",
                            "aci_domain_object_id",
                        ),
                        name="netbox_aci_plugin_aciendpointgroupdomainbinding_unique_aci_domain_object_per_epg",
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
