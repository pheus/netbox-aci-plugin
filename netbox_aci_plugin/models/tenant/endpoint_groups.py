# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.models import MACAddress
from django.apps import apps
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from ipam.models import IPAddress, Prefix

from ...choices import (
    QualityOfServiceClassChoices,
    USegAttributeMatchOperatorChoices,
    USegAttributeTypeChoices,
)
from ...constants import USEG_NETWORK_ATTRIBUTES_MODELS
from ...validators import ACIPolicyNameValidator
from ..base import ACIBaseModel
from ..mixins import UniqueGenericForeignKeyMixin
from .app_profiles import ACIAppProfile
from .bridge_domains import ACIBridgeDomain
from .tenants import ACITenant
from .vrfs import ACIVRF

#
# ACI Endpoint Group Base
#


class ACIEndpointGroupBaseModel(ACIBaseModel):
    """NetBox abstract model for ACI Endpoint Group (EPG)."""

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
            "Custom quality of service (QoS) policy name associate with the EPG."
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

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        # Validate the assigned ACIBrideDomain belongs to either the same
        # ACITenant as the ACIAppProfile or to the special ACITenant 'common'
        if (
            self.aci_bridge_domain.aci_tenant != self.aci_app_profile.aci_tenant
            and self.aci_bridge_domain.aci_tenant.name != "common"
        ):
            raise ValidationError(
                _(
                    "An assigned ACIBridgeDomain must belong to the "
                    "same ACITenant as the ACIAppProfile or to the "
                    "ACITenant 'common'."
                )
            )

    def save(self, *args, **kwargs) -> None:
        """Save the current instance to the database."""
        # Ensure the assigned ACIBrideDomain belongs to either the same
        # ACITenant as the ACIAppProfile or to the special ACITenant 'common'
        if (
            self.aci_bridge_domain.aci_tenant != self.aci_app_profile.aci_tenant
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
    """NetBox model for ACI Endpoint Group (EPG)."""

    proxy_arp_enabled = models.BooleanField(
        verbose_name=_("proxy ARP enabled"),
        default=False,
        help_text=_("Whether proxy ARP is enabled for the EPG. Default is disabled."),
    )

    # Generic relations
    aci_contract_relations = GenericRelation(
        to="netbox_aci_plugin.ACIContractRelation",
        content_type_field="aci_object_type",
        object_id_field="aci_object_id",
        related_query_name="aci_endpoint_group",
    )
    aci_esg_endpoint_group_selectors = GenericRelation(
        to="netbox_aci_plugin.ACIEsgEndpointGroupSelector",
        content_type_field="aci_epg_object_type",
        object_id_field="aci_epg_object_id",
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
        ordering: tuple = ("aci_app_profile", "name")
        verbose_name: str = _("ACI Endpoint Group")


#
# ACI uSeg Endpoint Group
#


class ACIUSegEndpointGroup(ACIEndpointGroupBaseModel):
    """NetBox model for ACI uSeg Endpoint Groups (uSegEPG)."""

    match_operator = models.CharField(
        verbose_name=_("match uSeg attributes"),
        max_length=3,
        default=USegAttributeMatchOperatorChoices.MATCH_ANY,
        choices=USegAttributeMatchOperatorChoices,
        help_text=_("Operator to match the related uSeg attributes. Default is 'any'."),
    )

    # Generic relations
    aci_contract_relations = GenericRelation(
        to="netbox_aci_plugin.ACIContractRelation",
        content_type_field="aci_object_type",
        object_id_field="aci_object_id",
        related_query_name="aci_useg_endpoint_group",
    )
    aci_esg_endpoint_group_selectors = GenericRelation(
        to="netbox_aci_plugin.ACIEsgEndpointGroupSelector",
        content_type_field="aci_epg_object_type",
        object_id_field="aci_epg_object_id",
        related_query_name="aci_useg_endpoint_group",
    )

    clone_fields: tuple = ACIEndpointGroupBaseModel.clone_fields + ("match_operator",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_app_profile", "name"),
                name="%(app_label)s_%(class)s_unique_name_per_aci_app_profile",
            ),
        ]
        default_related_name: str = "aci_useg_endpoint_groups"
        ordering: tuple = ("aci_app_profile", "name")
        verbose_name: str = _("ACI uSeg Endpoint Group")

    def get_match_operator_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return USegAttributeMatchOperatorChoices.colors.get(self.match_operator)


#
# Base classes for uSeg Attribute models
#


class ACIUSegAttributeBaseModel(ACIBaseModel):
    """Base model for ACI uSeg Attribute."""

    aci_useg_endpoint_group = models.ForeignKey(
        to=ACIUSegEndpointGroup,
        on_delete=models.CASCADE,
        verbose_name=_("ACI uSeg Endpoint Group"),
    )
    type = models.CharField(
        verbose_name=_("uSeg attribute type"),
        max_length=3,
        default=USegAttributeTypeChoices.TYPE_MAC,
        editable=False,
        choices=USegAttributeTypeChoices,
        help_text=_("Type of the uSeg attribute. Default is 'mac'."),
    )

    clone_fields: tuple = ACIBaseModel.clone_fields + ("aci_useg_endpoint_group",)
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIUSegEndpointGroup",)

    class Meta:
        abstract: bool = True
        ordering: tuple = (
            "name",
            "aci_useg_endpoint_group",
            "type",
        )

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return f"{self.name} ({self.aci_useg_endpoint_group.name})"

    @property
    def parent_object(self) -> ACIBaseModel:
        """Return the parent object of the instance."""
        return self.aci_useg_endpoint_group

    @property
    def aci_tenant(self) -> ACITenant:
        """Return the ACITenant instance of related ACIUSegEndpointGroup."""
        return self.aci_useg_endpoint_group.aci_tenant

    @property
    def aci_app_profile(self) -> ACIAppProfile:
        """Return the ACIAppProfile of the related ACIUSegEndpointGroup."""
        return self.aci_useg_endpoint_group.aci_app_profile

    def get_type_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return USegAttributeTypeChoices.colors.get(self.type)


#
# ACI uSeg Network Attribute
#


class ACIUSegNetworkAttribute(ACIUSegAttributeBaseModel, UniqueGenericForeignKeyMixin):
    """NetBox model for ACI uSeg Network Attribute."""

    attr_object_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to=USEG_NETWORK_ATTRIBUTES_MODELS,
        verbose_name=_("attribute object type"),
        blank=True,
        null=True,
    )
    attr_object_id = models.PositiveBigIntegerField(
        verbose_name=_("attribute object ID"),
        blank=True,
        null=True,
    )
    attr_object = GenericForeignKey(
        ct_field="attr_object_type",
        fk_field="attr_object_id",
    )
    use_epg_subnet = models.BooleanField(
        verbose_name=_("use EPG subnet"),
        default=False,
        help_text=_(
            "Whether the EPG subnet is applied as uSeg attribute. Default is disabled."
        ),
    )

    # Cached related objects by association name for faster access
    _ip_address = models.ForeignKey(
        to="ipam.IPAddress",
        on_delete=models.CASCADE,
        related_name="_aci_useg_network_attributes",
        verbose_name=_("IP Address"),
        blank=True,
        null=True,
    )
    _mac_address = models.ForeignKey(
        to="dcim.MACAddress",
        on_delete=models.CASCADE,
        related_name="_aci_useg_network_attributes",
        verbose_name=_("MAC Address"),
        blank=True,
        null=True,
    )
    _prefix = models.ForeignKey(
        to="ipam.Prefix",
        on_delete=models.CASCADE,
        related_name="_aci_useg_network_attributes",
        verbose_name=_("Prefix"),
        blank=True,
        null=True,
    )

    clone_fields: tuple = ACIUSegAttributeBaseModel.clone_fields + (
        "attr_object_type",
        "attr_object_id",
        "use_epg_subnet",
    )

    # Unique GenericForeignKey validation
    generic_fk_field = "attr_object"
    generic_unique_fields = ("aci_useg_endpoint_group",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=(
                    "name",
                    "aci_useg_endpoint_group",
                ),
                name=("%(app_label)s_%(class)s_unique_name_per_useg_endpoint_group"),
            ),
            models.UniqueConstraint(
                fields=(
                    "aci_useg_endpoint_group",
                    "attr_object_type",
                    "attr_object_id",
                ),
                name=(
                    "%(app_label)s_%(class)s_unique_attr_object_per_useg_endpoint_group"
                ),
            ),
            models.UniqueConstraint(
                fields=(
                    "aci_useg_endpoint_group",
                    "use_epg_subnet",
                ),
                name=(
                    "%(app_label)s_%(class)s_unique_use_epg_subnet_"
                    "per_useg_endpoint_group"
                ),
                condition=models.Q(use_epg_subnet=True),
                violation_error_message=_(
                    "ACI uSeg Endpoint Group with a 'use EPG Subnet' "
                    "attribute already exists."
                ),
            ),
        ]
        default_related_name: str = "aci_useg_network_attributes"
        indexes: tuple = (models.Index(fields=("attr_object_type", "attr_object_id")),)
        ordering: tuple = (
            "name",
            "aci_useg_endpoint_group",
            "_ip_address",
            "_mac_address",
            "_prefix",
        )
        verbose_name: str = _("ACI uSeg Network Attribute")

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        # Validate Attribute object assignment before validation of any other
        # fields
        if self.attr_object_type and not (self.attr_object or self.attr_object_id):
            attr_model_class = self.attr_object_type.model_class()
            raise ValidationError(
                {
                    "attr_object": _(
                        "The {attr_object} field is required, if an Attribute "
                        "Object Type is selected.".format(
                            attr_object=attr_model_class._meta.verbose_name
                        )
                    )
                }
            )

        super().clean()

        # Ensure that when 'use_epg_subnet' is True, neither 'attr_object_type'
        # nor 'attr_object_id' is set
        if self.use_epg_subnet:
            if self.attr_object_type:
                raise ValidationError(
                    _("Cannot set attr_object_type with 'use_epg_subnet = True'.")
                )
            if self.attr_object_id:
                raise ValidationError(
                    _("Cannot set attr_object_id with 'use_epg_subnet = True'.")
                )

        # Perform the mixin's unique constraint validation
        self._validate_generic_uniqueness()

    def save(self, *args, **kwargs) -> None:
        """Save the current instance to the database."""
        # Cache the related objects for faster access
        self.cache_related_objects()

        # Set attribute type
        self.set_attribute_type()

        super().save(*args, **kwargs)

    def cache_related_objects(self) -> None:
        """Cache the related objects for faster access."""
        self._ip_address = self._mac_address = self._prefix = None
        if self.attr_object_type:
            attr_object_type = self.attr_object_type.model_class()
            if attr_object_type == apps.get_model("ipam", "IPAddress"):
                self._ip_address = self.attr_object
            elif attr_object_type == apps.get_model("dcim", "MACAddress"):
                self._mac_address = self.attr_object
            elif attr_object_type == apps.get_model("ipam", "Prefix"):
                self._prefix = self.attr_object

    cache_related_objects.alters_data = True

    def set_attribute_type(self) -> None:
        """Set the 'type' field based on the attribute type."""
        if self.use_epg_subnet or self._ip_address or self._prefix:
            self.type = USegAttributeTypeChoices.TYPE_IP
        elif self._mac_address:
            self.type = USegAttributeTypeChoices.TYPE_MAC

    set_attribute_type.alters_data = True


#
# Generic Relations: ACIUSegNetworkAttribute
#

GenericRelation(
    to=ACIUSegNetworkAttribute,
    content_type_field="attr_object_type",
    object_id_field="attr_object_id",
    related_query_name="ip_address",
).contribute_to_class(IPAddress, name="aci_useg_network_attributes")

GenericRelation(
    to=ACIUSegNetworkAttribute,
    content_type_field="attr_object_type",
    object_id_field="attr_object_id",
    related_query_name="mac_address",
).contribute_to_class(MACAddress, name="aci_useg_network_attributes")

GenericRelation(
    to=ACIUSegNetworkAttribute,
    content_type_field="attr_object_type",
    object_id_field="attr_object_id",
    related_query_name="prefix",
).contribute_to_class(Prefix, name="aci_useg_network_attributes")
