# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ...choices import QualityOfServiceClassChoices
from ...validators import ACIPolicyNameValidator
from ..base import ACIBaseModel
from .app_profiles import ACIAppProfile
from .bridge_domains import ACIBridgeDomain
from .tenants import ACITenant
from .vrfs import ACIVRF

#
# ACI Endpoint Group Base
#


class ACIEndpointGroupBaseModel(ACIBaseModel):
    """NetBox abstract model for ACI Endpoint Groups (EPG)."""

    aci_app_profile = models.ForeignKey(
        to=ACIAppProfile,
        on_delete=models.PROTECT,
        verbose_name=_("ACI Application Profile"),
    )
    aci_bridge_domain = models.ForeignKey(
        to=ACIBridgeDomain,
        on_delete=models.PROTECT,
        verbose_name=_("ACI Bridge Domain"),
    )
    admin_shutdown = models.BooleanField(
        verbose_name=_("admin state shutdown"),
        default=False,
        help_text=_(
            "Whether the EPG is in shutdown mode removing all policy "
            "configuration from all switches. Default is disabled."
        ),
    )
    custom_qos_policy_name = models.CharField(
        verbose_name=_("custom QoS policy name"),
        max_length=64,
        blank=True,
        help_text=_(
            "Custom quality of service (QoS) policy name associate with the "
            "EPG."
        ),
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
    )
    flood_in_encap_enabled = models.BooleanField(
        verbose_name=_("flood in encapsulation enabled"),
        default=False,
        help_text=_(
            "Limits the flooding traffic to the encapsulation of the "
            "EPG. Default is disabled."
        ),
    )
    intra_epg_isolation_enabled = models.BooleanField(
        verbose_name=_("intra-EPG isolation enabled"),
        default=False,
        help_text=_(
            "Prevents communication between endpoints in an EPG when "
            "enabled. Default is disabled."
        ),
    )
    qos_class = models.CharField(
        verbose_name=_("QoS class"),
        max_length=11,
        default=QualityOfServiceClassChoices.CLASS_UNSPECIFIED,
        choices=QualityOfServiceClassChoices,
        help_text=_(
            "Assignment of the ACI Quality-of-Service level for "
            "traffic sourced in the EPG. Default is 'unspecified'."
        ),
    )
    preferred_group_member_enabled = models.BooleanField(
        verbose_name=_("preferred group member enabled"),
        default=False,
        help_text=_(
            "Whether this EPG is a member of the preferred group and allows "
            "communication without contracts. Default is disabled."
        ),
    )

    clone_fields: tuple = ACIBaseModel.clone_fields + (
        "aci_app_profile",
        "aci_bridge_domain",
        "admin_shutdown",
        "custom_qos_policy_name",
        "flood_in_encap_enabled",
        "intra_epg_isolation_enabled",
        "qos_class",
        "preferred_group_member_enabled",
    )
    prerequisite_models: tuple = (
        "netbox_aci_plugin.ACIAppProfile",
        "netbox_aci_plugin.ACIBridgeDomain",
    )

    class Meta:
        abstract: bool = True
        ordering: tuple = ("aci_app_profile", "name")

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        # Validate the assigned ACIBrideDomain belongs to either the same
        # ACITenant as the ACIAppProfile or to the special ACITenant 'common'
        if (
            self.aci_bridge_domain.aci_tenant
            != self.aci_app_profile.aci_tenant
            and self.aci_bridge_domain.aci_tenant.name != "common"
        ):
            raise ValidationError(
                _(
                    "Assigned ACIBridgeDomain have to belong to the same "
                    "ACITenant as the ACIAppProfile or to the special "
                    "ACITenant 'common'."
                )
            )

    def save(self, *args, **kwargs) -> None:
        """Saves the current instance to the database."""
        # Ensure the assigned ACIBrideDomain belongs to either the same
        # ACITenant as the ACIAppProfile or to the special ACITenant 'common'
        if (
            self.aci_bridge_domain.aci_tenant
            != self.aci_app_profile.aci_tenant
            and self.aci_bridge_domain.aci_tenant.name != "common"
        ):
            raise ValidationError(
                _(
                    "Assigned ACIBridgeDomain have to belong to the same "
                    "ACITenant as the ACIAppProfile or to the special "
                    "ACITenant 'common'."
                )
            )

        super().save(*args, **kwargs)

    @property
    def aci_tenant(self) -> ACITenant:
        """Return the ACITenant instance of the related ACIAppProfile."""
        return self.aci_app_profile.aci_tenant

    @property
    def aci_vrf(self) -> ACIVRF:
        """Return the ACIVRF instance of the related ACIBridgeDomain."""
        return self.aci_bridge_domain.aci_vrf

    @property
    def parent_object(self) -> ACIBaseModel:
        """Return the parent object of the instance."""
        return self.aci_app_profile

    def get_qos_class_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return QualityOfServiceClassChoices.colors.get(self.qos_class)


#
# ACI Endpoint Group
#


class ACIEndpointGroup(ACIEndpointGroupBaseModel):
    """NetBox model for ACI Endpoint Groups (EPG)."""

    proxy_arp_enabled = models.BooleanField(
        verbose_name=_("proxy ARP enabled"),
        default=False,
        help_text=_(
            "Whether proxy ARP is enabled for the EPG. Default is disabled."
        ),
    )

    # Generic relations
    aci_contract_relations = GenericRelation(
        to="netbox_aci_plugin.ACIContractRelation",
        content_type_field="aci_object_type",
        object_id_field="aci_object_id",
        related_query_name="aci_endpoint_group",
    )

    clone_fields: tuple = ACIEndpointGroupBaseModel.clone_fields + (
        "proxy_arp_enabled",
    )

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_app_profile", "name"),
                name="%(app_label)s_%(class)s_unique_name_per_aci_app_profile",
            ),
        ]
        default_related_name: str = "aci_endpoint_groups"
        verbose_name: str = _("ACI Endpoint Group")
