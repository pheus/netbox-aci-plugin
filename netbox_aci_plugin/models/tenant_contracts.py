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
            "Provider within the fabric. "
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
            "Rewrites the DSCP value of the incoming traffic to the specified "
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


class ACIContractSubject(NetBoxModel):
    """NetBox model for ACI Contract Subject."""

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
    aci_contract = models.ForeignKey(
        to=ACIContract,
        on_delete=models.CASCADE,
        related_name="aci_contract_subjects",
        verbose_name=_("ACI Contract"),
    )
    nb_tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        related_name="aci_contract_subjects",
        verbose_name=_("NetBox tenant"),
        blank=True,
        null=True,
    )
    apply_both_directions_enabled = models.BooleanField(
        verbose_name=_("apply both directions enabled"),
        default=True,
        help_text=_(
            "Enables filters defined in the subject to be applied in both "
            "directions. Default is enabled."
        ),
    )
    qos_class = models.CharField(
        verbose_name=_("QoS class"),
        max_length=11,
        default=QualityOfServiceClassChoices.CLASS_UNSPECIFIED,
        choices=QualityOfServiceClassChoices,
        help_text=_(
            "Specifies the priority handling for traffic between Consumer and "
            "Provider within the fabric. "
            "Default is 'unspecified'."
        ),
    )
    qos_class_cons_to_prov = models.CharField(
        verbose_name=_("QoS class (consumer to provider)"),
        max_length=11,
        default=QualityOfServiceClassChoices.CLASS_UNSPECIFIED,
        choices=QualityOfServiceClassChoices,
        help_text=_(
            "Specifies the priority handling for traffic from Consumer to "
            "Provider within the fabric. "
            "Default is 'unspecified'."
        ),
    )
    qos_class_prov_to_cons = models.CharField(
        verbose_name=_("QoS class (provider to consumer)"),
        max_length=11,
        default=QualityOfServiceClassChoices.CLASS_UNSPECIFIED,
        choices=QualityOfServiceClassChoices,
        help_text=_(
            "Specifies the priority handling for traffic from Provider to "
            "Consumer within the fabric. "
            "Default is 'unspecified'."
        ),
    )
    reverse_filter_ports_enabled = models.BooleanField(
        verbose_name=_("reverse filter ports enabled"),
        default=True,
        help_text=_(
            "Reverse source and destination ports to allow return traffic. "
            "Default is enabled."
        ),
    )
    service_graph_name = models.CharField(
        verbose_name=_("Service Graph name"),
        max_length=64,
        blank=True,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
        help_text=_(
            "Specifies the name of the Service Graph associated with the "
            "contract subject."
        ),
    )
    service_graph_name_cons_to_prov = models.CharField(
        verbose_name=_("Service Graph name (consumer to provider)"),
        max_length=64,
        blank=True,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
        help_text=_(
            "Specifies the name of the Service Graph associated with the "
            "contract subject for traffic from Consumer to Provider."
        ),
    )
    service_graph_name_prov_to_cons = models.CharField(
        verbose_name=_("Service Graph name (provider to consumer)"),
        max_length=64,
        blank=True,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
        help_text=_(
            "Specifies the name of the Service Graph associated with the "
            "contract subject for traffic from Provider to Consumer."
        ),
    )
    target_dscp = models.CharField(
        verbose_name=_("target DSCP"),
        max_length=11,
        default=QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED,
        choices=QualityOfServiceDSCPChoices,
        help_text=_(
            "Rewrites the DSCP value of the incoming traffic to the specified "
            "value. Default is 'unspecified'."
        ),
    )
    target_dscp_cons_to_prov = models.CharField(
        verbose_name=_("target DSCP (consumer to provider)"),
        max_length=11,
        default=QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED,
        choices=QualityOfServiceDSCPChoices,
        help_text=_(
            "Rewrites the DSCP value of the incoming traffic to the specified "
            "value for traffic from Consumer to Provider. "
            "Default is 'unspecified'."
        ),
    )
    target_dscp_prov_to_cons = models.CharField(
        verbose_name=_("target DSCP (provider to consumer)"),
        max_length=11,
        default=QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED,
        choices=QualityOfServiceDSCPChoices,
        help_text=_(
            "Rewrites the DSCP value of the incoming traffic to the specified "
            "value for traffic from Provider to Consumer. "
            "Default is 'unspecified'."
        ),
    )
    comments = models.TextField(
        verbose_name=_("comments"),
        blank=True,
    )

    clone_fields: tuple = (
        "description",
        "aci_contract",
        "nb_tenant",
        "apply_both_directions_enabled",
        "qos_class",
        "qos_class_cons_to_prov",
        "qos_class_prov_to_cons",
        "reverse_filter_ports_enabled",
        "service_graph_name",
        "service_graph_name_cons_to_prov",
        "service_graph_name_prov_to_cons",
        "target_dscp",
        "target_dscp_cons_to_prov",
        "target_dscp_prov_to_cons",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIContract",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_contract", "name"),
                name="unique_aci_contract_subject_name_per_aci_contract",
            ),
        ]
        ordering: tuple = ("aci_contract", "name")
        verbose_name: str = _("ACI Contract Subject")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        if self.aci_tenant.name == "common":
            return f"{self.name} ({self.aci_tenant.name})"
        else:
            return self.name

    @property
    def aci_tenant(self) -> ACITenant:
        """Return the ACITenant instance of related ACIContract."""
        return self.aci_contract.aci_tenant

    def get_absolute_url(self) -> str:
        """Return the absolute URL of the instance."""
        return reverse(
            "plugins:netbox_aci_plugin:acicontractsubject",
            args=[self.pk],
        )

    def get_qos_class_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return QualityOfServiceClassChoices.colors.get(self.qos_class)

    def get_qos_class_cons_to_prov_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return QualityOfServiceClassChoices.colors.get(
            self.qos_class_cons_to_prov
        )

    def get_qos_class_prov_to_cons_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return QualityOfServiceClassChoices.colors.get(
            self.qos_class_prov_to_cons
        )
