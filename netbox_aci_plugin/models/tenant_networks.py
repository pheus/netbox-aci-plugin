# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxLengthValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel

from ..choices import (
    VRFPCEnforcementDirectionChoices,
    VRFPCEnforcementPreferenceChoices,
)
from ..models.tenants import ACITenant
from ..validators import ACIPolicyDescriptionValidator, ACIPolicyNameValidator


class ACIVRF(NetBoxModel):
    """NetBox model for ACI VRF."""

    name = models.CharField(
        max_length=64,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
        verbose_name=_("name"),
    )
    alias = models.CharField(
        max_length=64,
        blank=True,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
        verbose_name=_("alias"),
    )
    description = models.CharField(
        max_length=128,
        blank=True,
        validators=[
            MaxLengthValidator(128),
            ACIPolicyDescriptionValidator,
        ],
        verbose_name=_("description"),
    )
    aci_tenant = models.ForeignKey(
        to=ACITenant,
        on_delete=models.PROTECT,
        related_name="aci_vrfs",
        verbose_name=_("ACI Tenant"),
    )
    nb_tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="+",
        blank=True,
        null=True,
        verbose_name=_("NetBox tenant"),
    )
    nb_vrf = models.ForeignKey(
        to="ipam.VRF",
        on_delete=models.PROTECT,
        related_name="+",
        blank=True,
        null=True,
        verbose_name=_("NetBox VRF"),
    )
    bd_enforcement_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Bridge Domain enforcement enabled"),
        help_text=_(
            "Allow EP to ping only gateways within associated bridge domain. "
            "Default is disabled."
        ),
    )
    dns_labels = ArrayField(
        base_field=models.CharField(
            max_length=64,
            validators=[
                MaxLengthValidator(64),
                ACIPolicyNameValidator,
            ],
        ),
        blank=True,
        null=True,
        verbose_name=_("DNS labels"),
        help_text=_("Enter labels separated by comma"),
    )
    ip_data_plane_learning_enabled = models.BooleanField(
        default=True,
        verbose_name=_("IP data plane learning enabled"),
        help_text=_(
            "Whether IP data plane learning is enabled for VRF. "
            "Default is enabled."
        ),
    )
    pc_enforcement_direction = models.CharField(
        max_length=8,
        choices=VRFPCEnforcementDirectionChoices,
        default=VRFPCEnforcementDirectionChoices.DIR_INGRESS,
        verbose_name=_("policy control enforcement direction"),
        help_text=_(
            "Controls policy enforcement direction for VRF. "
            "Default is 'ingress'."
        ),
    )
    pc_enforcement_preference = models.CharField(
        max_length=10,
        choices=VRFPCEnforcementPreferenceChoices,
        default=VRFPCEnforcementPreferenceChoices.PREF_ENFORCED,
        verbose_name=_("policy control enforcement preference"),
        help_text=_(
            "Controls policy enforcement preference for VRF. "
            "Default is 'enforced'."
        ),
    )
    pim_ipv4_enabled = models.BooleanField(
        default=False,
        verbose_name=_("PIM (multicast) IPv4 enabled"),
        help_text=_(
            "Multicast routing enabled for the VRF. Default is false."
        ),
    )
    pim_ipv6_enabled = models.BooleanField(
        default=False,
        verbose_name=_("PIM (multicast) IPv6 enabled"),
        help_text=_(
            "Multicast routing enabled for the VRF. Default is false."
        ),
    )
    preferred_group_enabled = models.BooleanField(
        default=False,
        verbose_name=_("preferred group enabled"),
        help_text=_(
            "Whether preferred group feature is enabled for the VRF. "
            "Default is false."
        ),
    )
    comments = models.TextField(
        blank=True,
        verbose_name=_("comments"),
    )

    clone_fields: tuple = (
        "description",
        "aci_tenant",
        "nb_tenant",
        "nb_vrf",
        "bd_enforcement_enabled",
        "dns_labels",
        "ip_data_plane_learning_enabled",
        "pc_enforcement_direction",
        "pc_enforcement_preference",
        "pim_ipv4_enabled",
        "pim_ipv6_enabled",
        "preferred_group_enabled",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACITenant",)

    class Meta:
        ordering: tuple = ("aci_tenant", "name")
        unique_together: tuple = ("aci_tenant", "name")
        verbose_name: str = _("ACI VRF")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return self.name

    def get_absolute_url(self) -> str:
        """Return the absolute URL of the instance."""
        return reverse("plugins:netbox_aci_plugin:acivrf", args=[self.pk])

    def get_pc_enforcement_direction_color(self):
        return VRFPCEnforcementDirectionChoices.colors.get(
            self.pc_enforcement_direction
        )

    def get_pc_enforcement_preference_color(self):
        return VRFPCEnforcementPreferenceChoices.colors.get(
            self.pc_enforcement_preference
        )
