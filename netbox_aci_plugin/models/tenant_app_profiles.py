# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.validators import MaxLengthValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel

from ..choices import EPGQualityOfServiceClassChoices
from ..models.tenant_networks import ACIVRF, ACIBridgeDomain
from ..models.tenants import ACITenant
from ..validators import ACIPolicyDescriptionValidator, ACIPolicyNameValidator


class ACIAppProfile(NetBoxModel):
    """NetBox model for ACI Application Profile."""

    name = models.CharField(
        verbose_name=_("name"),
        max_length=64,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
    )
    name_alias = models.CharField(
        verbose_name=_("name alias"),
        max_length=64,
        blank=True,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
    )
    description = models.CharField(
        verbose_name=_("description"),
        max_length=128,
        blank=True,
        validators=[
            MaxLengthValidator(128),
            ACIPolicyDescriptionValidator,
        ],
    )
    aci_tenant = models.ForeignKey(
        to=ACITenant,
        on_delete=models.PROTECT,
        related_name="aci_app_profiles",
        verbose_name=_("ACI Tenant"),
    )
    nb_tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("NetBox tenant"),
        blank=True,
        null=True,
    )
    comments = models.TextField(
        verbose_name=_("comments"),
        blank=True,
    )

    clone_fields: tuple = (
        "description",
        "aci_tenant",
        "nb_tenant",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACITenant",)

    class Meta:
        ordering: tuple = ("aci_tenant", "name")
        unique_together: tuple = ("aci_tenant", "name")
        verbose_name: str = _("ACI Application Profile")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return self.name

    def get_absolute_url(self) -> str:
        """Return the absolute URL of the instance."""
        return reverse(
            "plugins:netbox_aci_plugin:aciappprofile", args=[self.pk]
        )


class ACIEndpointGroup(NetBoxModel):
    """NetBox model for ACI Endpoint Groups (EPG)."""

    name = models.CharField(
        verbose_name=_("name"),
        max_length=64,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
    )
    name_alias = models.CharField(
        verbose_name=_("name alias"),
        max_length=64,
        blank=True,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
    )
    description = models.CharField(
        verbose_name=_("description"),
        max_length=128,
        blank=True,
        validators=[
            MaxLengthValidator(128),
            ACIPolicyDescriptionValidator,
        ],
    )
    aci_app_profile = models.ForeignKey(
        to=ACIAppProfile,
        on_delete=models.PROTECT,
        related_name="aci_endpoint_groups",
        verbose_name=_("ACI Application Profile"),
    )
    aci_bridge_domain = models.ForeignKey(
        to=ACIBridgeDomain,
        on_delete=models.PROTECT,
        related_name="aci_endpoint_groups",
        verbose_name=_("ACI Bridge Domain"),
    )
    nb_tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("NetBox tenant"),
        blank=True,
        null=True,
    )
    admin_shutdown = models.BooleanField(
        verbose_name=_("admin state shutdown"),
        default=False,
        help_text=_(
            "Wether the EPG is in shutdown mode removing all policy "
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
        default=EPGQualityOfServiceClassChoices.CLASS_UNSPECIFIED,
        choices=EPGQualityOfServiceClassChoices,
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
    proxy_arp_enabled = models.BooleanField(
        verbose_name=_("proxy ARP enabled"),
        default=False,
        help_text=_(
            "Whether proxy ARP is enabled for the EPG. Default is disabled."
        ),
    )
    comments = models.TextField(
        verbose_name=_("comments"),
        blank=True,
    )

    clone_fields: tuple = (
        "description",
        "aci_app_profile",
        "aci_bridge_domain",
        "nb_tenant",
        "admin_shutdown",
        "custom_qos_policy_name",
        "flood_in_encap_enabled",
        "intra_epg_isolation_enabled",
        "qos_class",
        "preferred_group_member_enabled",
        "proxy_arp_enabled",
    )
    prerequisite_models: tuple = (
        "netbox_aci_plugin.ACIAppProfile",
        "netbox_aci_plugin.ACIBridgeDomain",
    )

    class Meta:
        ordering: tuple = ("aci_app_profile", "name")
        unique_together: tuple = (
            "aci_app_profile",
            "name",
        )
        verbose_name: str = _("ACI Endpoint Group")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return self.name

    @property
    def aci_tenant(self) -> ACITenant:
        """Return the ACITenant instance of related ACIAppProfile."""
        return self.aci_app_profile.aci_tenant

    @property
    def aci_vrf(self) -> ACIVRF:
        """Return the ACIVRF instance of related ACIBridgeDomain."""
        return self.aci_bridge_domain.aci_vrf

    def get_absolute_url(self) -> str:
        """Return the absolute URL of the instance."""
        return reverse(
            "plugins:netbox_aci_plugin:aciendpointgroup", args=[self.pk]
        )

    def get_qos_class_color(self):
        """Return the associated color of choice from the ChoiceSet."""
        return EPGQualityOfServiceClassChoices.colors.get(self.qos_class)
