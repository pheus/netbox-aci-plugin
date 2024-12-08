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
    ContractSubjectFilterActionChoices,
    ContractSubjectFilterApplyDirectionChoices,
    ContractSubjectFilterPriorityChoices,
    QualityOfServiceClassChoices,
    QualityOfServiceDSCPChoices,
)
from ..models.tenant_contract_filters import ACIContractFilter
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
            "applicable. Default is 'context'."
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


class ACIContractSubjectFilter(NetBoxModel):
    """NetBox model for ACI Contract Subject Filter Attachment."""

    aci_contract_filter = models.ForeignKey(
        to=ACIContractFilter,
        on_delete=models.CASCADE,
        related_name="aci_contract_subject_filters",
        verbose_name=_("ACI Contract Filter"),
    )
    aci_contract_subject = models.ForeignKey(
        to=ACIContractSubject,
        on_delete=models.CASCADE,
        related_name="aci_contract_subject_filters",
        verbose_name=_("ACI Contract Subject"),
    )
    action = models.CharField(
        verbose_name=_("action"),
        max_length=6,
        default=ContractSubjectFilterActionChoices.ACTION_PERMIT,
        choices=ContractSubjectFilterActionChoices,
        help_text=_(
            "Defines the action to be taken on the traffic matched by the "
            "filter. Choose 'permit' to allow the traffic, or 'deny' to block "
            "it. Default is 'permit'."
        ),
    )
    apply_direction = models.CharField(
        verbose_name=_("apply direction"),
        max_length=4,
        default=ContractSubjectFilterApplyDirectionChoices.DIR_BOTH,
        choices=ContractSubjectFilterApplyDirectionChoices,
        help_text=_(
            "Specifies the direction to apply the filter: 'both' directions, "
            "'ctp' (consumer to provider), or 'ptc' (provider to consumer). "
            "Default is 'both'."
        ),
    )
    log_enabled = models.BooleanField(
        verbose_name=_("logging enabled"),
        default=False,
        help_text=_(
            "Enables logging for the matched traffic. Default is disabled."
        ),
    )
    policy_compression_enabled = models.BooleanField(
        verbose_name=_("policy compression enabled"),
        default=False,
        help_text=_(
            "Enable policy-based compression for filtering traffic. "
            "This reduces the number of rules in the TCAM. "
            "Default is disabled."
        ),
    )
    priority = models.CharField(
        verbose_name=_("(deny) priority"),
        max_length=7,
        default=ContractSubjectFilterPriorityChoices.CLASS_DEFAULT,
        choices=ContractSubjectFilterPriorityChoices,
        help_text=_(
            "Specifies the priority of the deny action for matched traffic. "
            "Only relevant when 'deny' is selected as the action. "
            "Default is 'default'."
        ),
    )
    comments = models.TextField(
        verbose_name=_("comments"),
        blank=True,
    )

    clone_fields: tuple = (
        "aci_contract_subject",
        "action",
        "apply_direction",
        "log_enabled",
        "policy_compression_enabled",
        "priority",
    )
    prerequisite_models: tuple = (
        "netbox_aci_plugin.ACIContractSubject",
        "netbox_aci_plugin.ACIContractFilter",
    )

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_contract_subject", "aci_contract_filter"),
                name="unique_aci_contract_filter_per_aci_contract_subject",
            ),
        ]
        ordering: tuple = ("aci_contract_subject", "aci_contract_filter")
        verbose_name: str = _("ACI Contract Subject Filter")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return (
            f"{self.aci_contract_subject.name}-"
            f"{self.aci_contract_filter.name}"
        )

    @property
    def aci_contract(self) -> ACIContract:
        """Return the ACIContract instance of related ACIContractSubject."""
        return self.aci_contract_subject.aci_contract

    @property
    def aci_contract_filter_tenant(self) -> ACITenant:
        """Return the ACITenant instance of related ACIContractFilter."""
        return self.aci_contract_filter.aci_tenant

    @property
    def aci_contract_subject_tenant(self) -> ACITenant:
        """Return the ACITenant instance of related ACIContractSubject."""
        return self.aci_contract_subject.aci_tenant

    def get_absolute_url(self) -> str:
        """Return the absolute URL of the instance."""
        return reverse(
            "plugins:netbox_aci_plugin:acicontractsubjectfilter",
            args=[self.pk],
        )

    def get_action_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return ContractSubjectFilterActionChoices.colors.get(self.action)

    def get_apply_direction_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return ContractSubjectFilterApplyDirectionChoices.colors.get(
            self.apply_direction
        )

    def get_priority_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return ContractSubjectFilterPriorityChoices.colors.get(self.priority)
