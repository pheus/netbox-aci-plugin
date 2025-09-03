# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel

from ...choices import (
    ContractRelationRoleChoices,
    ContractScopeChoices,
    ContractSubjectFilterActionChoices,
    ContractSubjectFilterApplyDirectionChoices,
    ContractSubjectFilterPriorityChoices,
    QualityOfServiceClassChoices,
    QualityOfServiceDSCPChoices,
)
from ...constants import CONTRACT_RELATION_OBJECT_TYPES
from ...validators import ACIPolicyNameValidator
from ..base import ACIBaseModel
from ..mixins import UniqueGenericForeignKeyMixin
from .contract_filters import ACIContractFilter
from .endpoint_groups import ACIEndpointGroup, ACIUSegEndpointGroup
from .endpoint_security_groups import ACIEndpointSecurityGroup
from .tenants import ACITenant


class ACIContract(ACIBaseModel):
    """NetBox model for ACI Contract."""

    aci_tenant = models.ForeignKey(
        to=ACITenant,
        on_delete=models.PROTECT,
        related_name="aci_contracts",
        verbose_name=_("ACI Tenant"),
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

    clone_fields: tuple = ACIBaseModel.clone_fields + (
        "aci_tenant",
        "qos_class",
        "scope",
        "target_dscp",
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
        verbose_name: str = _("ACI Contract")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        if self.aci_tenant.name == "common":
            return f"{self.name} ({self.aci_tenant.name})"
        return self.name

    @property
    def parent_object(self) -> ACIBaseModel:
        """Return the parent object of the instance."""
        return self.aci_tenant

    def get_qos_class_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return QualityOfServiceClassChoices.colors.get(self.qos_class)

    def get_scope_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return ContractScopeChoices.colors.get(self.scope)


class ACIContractRelation(NetBoxModel, UniqueGenericForeignKeyMixin):
    """NetBox model for ACI Contract Relation to ACI objects."""

    aci_contract = models.ForeignKey(
        to=ACIContract,
        on_delete=models.CASCADE,
        related_name="aci_contract_relations",
        verbose_name=_("ACI Contract"),
    )
    aci_object_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to=CONTRACT_RELATION_OBJECT_TYPES,
        verbose_name=_("ACI object type"),
        blank=True,
        null=True,
    )
    aci_object_id = models.PositiveBigIntegerField(
        verbose_name=_("ACI object ID"),
        blank=True,
        null=True,
    )
    aci_object = GenericForeignKey(
        ct_field="aci_object_type",
        fk_field="aci_object_id",
    )
    role = models.CharField(
        verbose_name=_("role"),
        max_length=4,
        choices=ContractRelationRoleChoices,
        default=ContractRelationRoleChoices.ROLE_PROVIDER,
        help_text=_(
            "Specifies the role of the ACI Contract for the given "
            "ACI object as either a provider or a consumer. "
            "Default is 'provider'."
        ),
    )
    comments = models.TextField(
        verbose_name=_("comments"),
        blank=True,
    )

    # Cached related objects by association name for faster access
    _aci_endpoint_group = models.ForeignKey(
        to="netbox_aci_plugin.ACIEndpointGroup",
        on_delete=models.CASCADE,
        related_name="_aci_contract_relations",
        verbose_name=_("ACI Endpoint Group"),
        blank=True,
        null=True,
    )
    _aci_endpoint_security_group = models.ForeignKey(
        to="netbox_aci_plugin.ACIEndpointSecurityGroup",
        on_delete=models.CASCADE,
        related_name="_aci_contract_relations",
        verbose_name=_("ACI Endpoint Security Group"),
        blank=True,
        null=True,
    )
    _aci_useg_endpoint_group = models.ForeignKey(
        to="netbox_aci_plugin.ACIUSegEndpointGroup",
        on_delete=models.CASCADE,
        related_name="_aci_contract_relations",
        verbose_name=_("ACI uSeg Endpoint Group"),
        blank=True,
        null=True,
    )
    _aci_vrf = models.ForeignKey(
        to="netbox_aci_plugin.ACIVRF",
        on_delete=models.CASCADE,
        related_name="_aci_contract_relations",
        verbose_name=_("ACI VRF"),
        blank=True,
        null=True,
    )

    clone_fields: tuple = (
        "aci_contract",
        "aci_object_type",
        "aci_object_id",
        "role",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIContract",)

    # Unique GenericForeignKey validation
    generic_fk_field = "aci_object"
    generic_unique_fields = (
        "aci_contract",
        "role",
    )

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=(
                    "aci_contract",
                    "aci_object_type",
                    "aci_object_id",
                    "role",
                ),
                name="%(app_label)s_%(class)s_unique_per_aci_contract_role",
            ),
        ]
        indexes: tuple = (models.Index(fields=("aci_object_type", "aci_object_id")),)
        ordering: tuple = (
            "aci_contract",
            "_aci_endpoint_group",
            "_aci_vrf",
            "role",
        )
        verbose_name: str = _("ACI Contract Relation")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return f"{self.aci_contract.name} - {self.role} - {self.aci_object}"

    @property
    def aci_contract_tenant(self) -> ACITenant:
        """Return the ACITenant instance of related ACIContract."""
        return self.aci_contract.aci_tenant

    @property
    def aci_object_tenant(self) -> ACITenant:
        """Return the ACITenant instance of the related ACI object."""
        return self.aci_object.aci_tenant

    @property
    def parent_object(self) -> ACIBaseModel:
        """Return the parent object of the instance."""
        return self.aci_contract

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        # Validate ACI object assignment before validation of any other fields
        if self.aci_object_type and not (self.aci_object or self.aci_object_id):
            aci_model_class = self.aci_object_type.model_class()
            raise ValidationError(
                {
                    "aci_object": _(
                        "The {aci_object} field is required, if an ACI Object "
                        "Type is selected.".format(
                            aci_object=aci_model_class._meta.verbose_name
                        )
                    )
                }
            )

        super().clean()

        # Validate the assigned ACI Contract and ACI Object shares the same
        # ACI Tenant
        if self.aci_contract.aci_tenant != self.aci_object.aci_tenant:
            aci_model_class = self.aci_object_type.model_class()
            raise ValidationError(
                {
                    "aci_object": _(
                        "An assigned {aci_object} must belong to the same "
                        "ACI Tenant as the ACI Contract.".format(
                            aci_object=aci_model_class._meta.verbose_name
                        )
                    )
                }
            )

        # Perform the mixin's unique constraint validation
        self._validate_generic_uniqueness()

        # Validate that the ACI Contract has no conflicting ACI Object types
        # assigned.
        # (e.g., ACI Endpoint Group and ACI Endpoint Security Group)
        self._validate_aci_object_conflict()

    def _validate_aci_object_conflict(self) -> None:
        """Validate that this does not conflict with an existing ACI Object."""
        endpoint_group_ct = ContentType.objects.get_for_model(ACIEndpointGroup)
        useg_endpoint_group_ct = ContentType.objects.get_for_model(ACIUSegEndpointGroup)
        endpoint_security_group_ct = ContentType.objects.get_for_model(
            ACIEndpointSecurityGroup
        )

        # Determine which ContentTypes conflict with the current
        # ACI Object Type
        if self.aci_object_type == endpoint_security_group_ct:
            conflict_cts = [endpoint_group_ct, useg_endpoint_group_ct]
        elif self.aci_object_type in [
            endpoint_group_ct,
            useg_endpoint_group_ct,
        ]:
            conflict_cts = [endpoint_security_group_ct]
        else:
            return  # No conflicts, so exit early

        # Check whether there is an existing ContractRelation for the same
        # ACI Contract with a conflicting ACI Object Type.
        conflict_relations = ACIContractRelation.objects.filter(
            aci_contract=self.aci_contract,
            aci_object_type__in=conflict_cts,
        )
        # If updating an existing instance, exclude the current record.
        if self.pk:
            conflict_relations = conflict_relations.exclude(pk=self.pk)

        if conflict_relations.exists():
            raise ValidationError(
                _(
                    "Invalid Contract Relation: ACI Endpoint Security Groups "
                    "cannot be associated together with ACI Endpoint Groups "
                    "or ACI uSeg Endpoint Groups for the same ACI Contract."
                )
            )

    def save(self, *args, **kwargs) -> None:
        """Save the current instance to the database."""
        # Cache the related objects for faster access
        self.cache_related_objects()

        super().save(*args, **kwargs)

    def cache_related_objects(self) -> None:
        """Cache the related objects for faster access."""
        self._aci_endpoint_group = self._aci_vrf = None
        if self.aci_object_type:
            aci_object_type = self.aci_object_type.model_class()
            if aci_object_type == apps.get_model(
                "netbox_aci_plugin", "ACIEndpointGroup"
            ):
                self._aci_endpoint_group = self.aci_object
            elif aci_object_type == apps.get_model(
                "netbox_aci_plugin", "ACIEndpointSecurityGroup"
            ):
                self._aci_endpoint_security_group = self.aci_object
            elif aci_object_type == apps.get_model(
                "netbox_aci_plugin", "ACIUSegEndpointGroup"
            ):
                self._aci_useg_endpoint_group = self.aci_object
            elif aci_object_type == apps.get_model("netbox_aci_plugin", "ACIVRF"):
                self._aci_vrf = self.aci_object

    cache_related_objects.alters_data = True

    def get_role_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return ContractRelationRoleChoices.colors.get(self.role)


class ACIContractSubject(ACIBaseModel):
    """NetBox model for ACI Contract Subject."""

    aci_contract = models.ForeignKey(
        to=ACIContract,
        on_delete=models.CASCADE,
        related_name="aci_contract_subjects",
        verbose_name=_("ACI Contract"),
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

    clone_fields: tuple = ACIBaseModel.clone_fields + (
        "aci_contract",
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
                name="%(app_label)s_%(class)s_unique_per_aci_contract",
            ),
        ]
        ordering: tuple = ("aci_contract", "name")
        verbose_name: str = _("ACI Contract Subject")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        if self.aci_tenant.name == "common":
            return f"{self.name} ({self.aci_tenant.name})"
        return self.name

    @property
    def aci_tenant(self) -> ACITenant:
        """Return the ACITenant instance of related ACIContract."""
        return self.aci_contract.aci_tenant

    @property
    def parent_object(self) -> ACIBaseModel:
        """Return the parent object of the instance."""
        return self.aci_contract

    def get_qos_class_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return QualityOfServiceClassChoices.colors.get(self.qos_class)

    def get_qos_class_cons_to_prov_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return QualityOfServiceClassChoices.colors.get(self.qos_class_cons_to_prov)

    def get_qos_class_prov_to_cons_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return QualityOfServiceClassChoices.colors.get(self.qos_class_prov_to_cons)


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
        help_text=_("Enables logging for the matched traffic. Default is disabled."),
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
                name="%(app_label)s_%(class)s_unique_per_aci_contract_subject",
            ),
        ]
        ordering: tuple = ("aci_contract_subject", "aci_contract_filter")
        verbose_name: str = _("ACI Contract Subject Filter")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return f"{self.aci_contract_subject.name}-{self.aci_contract_filter.name}"

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

    @property
    def parent_object(self) -> ACIBaseModel:
        """Return the parent object of the instance."""
        return self.aci_contract_subject

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
