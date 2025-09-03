# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ...choices import (
    VRFPCEnforcementDirectionChoices,
    VRFPCEnforcementPreferenceChoices,
)
from ...validators import ACIPolicyNameValidator
from ..base import ACIBaseModel
from .tenants import ACITenant


class ACIVRF(ACIBaseModel):
    """NetBox model for ACI VRF."""

    aci_tenant = models.ForeignKey(
        to=ACITenant,
        on_delete=models.PROTECT,
        related_name="aci_vrfs",
        verbose_name=_("ACI Tenant"),
    )
    nb_vrf = models.ForeignKey(
        to="ipam.VRF",
        on_delete=models.SET_NULL,
        related_name="aci_vrfs",
        verbose_name=_("NetBox VRF"),
        blank=True,
        null=True,
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
        verbose_name=_("DNS labels"),
        blank=True,
        null=True,
        help_text=_("Enter labels separated by comma"),
    )
    ip_data_plane_learning_enabled = models.BooleanField(
        verbose_name=_("IP data plane learning enabled"),
        default=True,
        help_text=_(
            "Whether IP data plane learning is enabled for VRF. Default is enabled."
        ),
    )
    pc_enforcement_direction = models.CharField(
        verbose_name=_("policy control enforcement direction"),
        max_length=8,
        default=VRFPCEnforcementDirectionChoices.DIR_INGRESS,
        choices=VRFPCEnforcementDirectionChoices,
        help_text=_(
            "Controls policy enforcement direction for VRF. Default is 'ingress'."
        ),
    )
    pc_enforcement_preference = models.CharField(
        verbose_name=_("policy control enforcement preference"),
        max_length=10,
        default=VRFPCEnforcementPreferenceChoices.PREF_ENFORCED,
        choices=VRFPCEnforcementPreferenceChoices,
        help_text=_(
            "Controls policy enforcement preference for VRF. Default is 'enforced'."
        ),
    )
    pim_ipv4_enabled = models.BooleanField(
        verbose_name=_("PIM (multicast) IPv4 enabled"),
        default=False,
        help_text=_("Multicast routing enabled for the VRF. Default is disabled."),
    )
    pim_ipv6_enabled = models.BooleanField(
        verbose_name=_("PIM (multicast) IPv6 enabled"),
        default=False,
        help_text=_("Multicast routing enabled for the VRF. Default is disabled."),
    )
    preferred_group_enabled = models.BooleanField(
        verbose_name=_("preferred group enabled"),
        default=False,
        help_text=_(
            "Whether preferred group feature is enabled for the VRF. "
            "Default is disabled."
        ),
    )

    # Generic relations
    aci_contract_relations = GenericRelation(
        to="netbox_aci_plugin.ACIContractRelation",
        content_type_field="aci_object_type",
        object_id_field="aci_object_id",
        related_query_name="aci_vrf",
    )

    clone_fields: tuple = ACIBaseModel.clone_fields + (
        "aci_tenant",
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
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_tenant", "name"),
                name="%(app_label)s_%(class)s_unique_per_aci_tenant",
            ),
        ]
        ordering: tuple = ("aci_tenant", "name")
        verbose_name: str = _("ACI VRF")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        if self.aci_tenant.name == "common":
            return f"{self.name} ({self.aci_tenant.name})"
        return self.name

    @property
    def parent_object(self) -> ACIBaseModel:
        """Return the parent object of the instance."""
        return self.aci_tenant

    def get_pc_enforcement_direction_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return VRFPCEnforcementDirectionChoices.colors.get(
            self.pc_enforcement_direction
        )

    def get_pc_enforcement_preference_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return VRFPCEnforcementPreferenceChoices.colors.get(
            self.pc_enforcement_preference
        )
