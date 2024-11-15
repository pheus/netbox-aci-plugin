# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.validators import MaxLengthValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel

from ..choices import (
    ContractScopeChoices,
    QualityOfServiceClassChoices,
    QualityOfServiceDSCPChoices,
)
from ..models.tenants import ACITenant
from ..validators import ACIPolicyDescriptionValidator, ACIPolicyNameValidator


class ACIContract(NetBoxModel):
    """NetBox model for ACI Contract."""

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
        related_name="aci_contracts",
        verbose_name=_("ACI Tenant"),
    )
    nb_tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        related_name="aci_contracts",
        verbose_name=_("NetBox tenant"),
        blank=True,
        null=True,
    )
    qos_class = models.CharField(
        verbose_name=_("QoS class"),
        max_length=11,
        default=QualityOfServiceClassChoices.CLASS_UNSPECIFIED,
        choices=QualityOfServiceClassChoices,
        help_text=_(
            "Specifies the priority handling for traffic between Consumer and "
            "Provider within the fabric."
            "Default is 'unspecified'."
        ),
    )
    scope = models.CharField(
        verbose_name=_("scope"),
        max_length=19,
        default=ContractScopeChoices.SCOPE_VRF,
        choices=ContractScopeChoices,
        help_text=_(
            "Scope defines the extent within which the contract is "
            "applicable. Default is 'vrf'."
        ),
    )
    target_dscp = models.CharField(
        verbose_name=_("target DSCP"),
        max_length=11,
        default=QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED,
        choices=QualityOfServiceDSCPChoices,
        help_text=_(
            "Rewrites the DSCP value of the incoming traffic to the specified"
            "value. Default is 'unspecified'."
        ),
    )
    comments = models.TextField(
        verbose_name=_("comments"),
        blank=True,
    )

    clone_fields: tuple = (
        "description",
        "aci_tenant",
        "nb_tenant",
        "qos_class",
        "scope",
        "target_dscp",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACITenant",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_tenant", "name"),
                name="unique_aci_contract_name_per_aci_tenant",
            ),
        ]
        ordering: tuple = ("aci_tenant", "name")
        verbose_name: str = _("ACI Contract")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        if self.aci_tenant.name == "common":
            return f"{self.name} ({self.aci_tenant.name})"
        else:
            return self.name

    def get_absolute_url(self) -> str:
        """Return the absolute URL of the instance."""
        return reverse("plugins:netbox_aci_plugin:acicontract", args=[self.pk])

    def get_qos_class_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return QualityOfServiceClassChoices.colors.get(self.qos_class)

    def get_scope_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return ContractScopeChoices.colors.get(self.scope)
