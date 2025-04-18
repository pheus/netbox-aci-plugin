# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.apps import apps
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ...constants import ESG_ENDPOINT_GROUP_SELECTORS_MODELS
from ..base import ACIBaseModel
from ..mixins import UniqueGenericForeignKeyMixin
from .app_profiles import ACIAppProfile
from .tenants import ACITenant
from .vrfs import ACIVRF

#
# ACI Endpoint Security Group
#


class ACIEndpointSecurityGroup(ACIBaseModel):
    """NetBox model for ACI Endpoint Security Group (ESG)."""

    aci_app_profile = models.ForeignKey(
        to=ACIAppProfile,
        on_delete=models.PROTECT,
        verbose_name=_("ACI Application Profile"),
    )
    aci_vrf = models.ForeignKey(
        to=ACIVRF,
        on_delete=models.PROTECT,
        verbose_name=_("ACI VRf"),
    )
    admin_shutdown = models.BooleanField(
        verbose_name=_("Admin state shutdown"),
        default=False,
        help_text=_(
            "Whether the ESG is in shutdown mode removing all policy "
            "configuration from all switches. Default is disabled."
        ),
    )
    intra_esg_isolation_enabled = models.BooleanField(
        verbose_name=_("Intra-ESG isolation enabled"),
        default=False,
        help_text=_(
            "Prevents communication between endpoints in an ESG when "
            "enabled. Default is disabled."
        ),
    )
    preferred_group_member_enabled = models.BooleanField(
        verbose_name=_("Preferred Group member enabled"),
        default=False,
        help_text=_(
            "Whether this ESG is a member of the preferred group and allows "
            "communication without contracts. Default is disabled."
        ),
    )

    clone_fields: tuple = ACIBaseModel.clone_fields + (
        "aci_app_profile",
        "aci_vrf",
        "admin_shutdown",
        "intra_esg_isolation_enabled",
        "preferred_group_member_enabled",
    )
    prerequisite_models: tuple = (
        "netbox_aci_plugin.ACIAppProfile",
        "netbox_aci_plugin.ACIVRF",
    )

    # Generic relations
    aci_contract_relations = GenericRelation(
        to="netbox_aci_plugin.ACIContractRelation",
        content_type_field="aci_object_type",
        object_id_field="aci_object_id",
        related_query_name="aci_endpoint_security_group",
    )

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_app_profile", "name"),
                name="%(app_label)s_%(class)s_unique_name_per_aci_app_profile",
            ),
        ]
        default_related_name: str = "aci_endpoint_security_groups"
        ordering: tuple = ("aci_app_profile", "name")
        verbose_name: str = _("ACI Endpoint Security Group")

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        # Validate the assigned ACIVRF belongs to either the same ACITenant as
        # the ACIAppProfile or to the special ACITenant 'common'
        if (
            self.aci_vrf.aci_tenant != self.aci_app_profile.aci_tenant
            and self.aci_vrf.aci_tenant.name != "common"
        ):
            raise ValidationError(
                _(
                    "Assigned ACIVRF have to belong to the same ACITenant as "
                    "the ACIAppProfile or to the special ACITenant 'common'."
                )
            )

    def save(self, *args, **kwargs) -> None:
        """Saves the current instance to the database."""
        # Ensure the assigned ACIVRF belongs to either the same ACITenant as
        # the ACIAppProfile or to the special ACITenant 'common'
        if (
            self.aci_vrf.aci_tenant != self.aci_app_profile.aci_tenant
            and self.aci_vrf.aci_tenant.name != "common"
        ):
            raise ValidationError(
                _(
                    "Assigned ACIVRF have to belong to the same ACITenant as "
                    "the ACIAppProfile or to the special ACITenant 'common'."
                )
            )

        super().save(*args, **kwargs)

    @property
    def aci_tenant(self) -> ACITenant:
        """Return the ACITenant instance of the related ACIAppProfile."""
        return self.aci_app_profile.aci_tenant

    @property
    def parent_object(self) -> ACIBaseModel:
        """Return the parent object of the instance."""
        return self.aci_app_profile


#
# Base classes for Endpoint Security Group (ESG) Selector models
#


class ACIEsgSelectorBaseModel(ACIBaseModel):
    """Base model for ACI Endpoint Security Group (ESG) Selector."""

    aci_endpoint_security_group = models.ForeignKey(
        to=ACIEndpointSecurityGroup,
        on_delete=models.CASCADE,
        verbose_name=_("ACI Endpoint Security Group"),
    )

    clone_fields: tuple = ACIBaseModel.clone_fields + (
        "aci_endpoint_security_group",
    )
    prerequisite_models: tuple = (
        "netbox_aci_plugin.ACIEndpointSecurityGroup",
    )

    class Meta:
        abstract: bool = True
        ordering: tuple = (
            "name",
            "aci_endpoint_security_group",
            "type",
        )

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return f"{self.name} ({self.aci_endpoint_security_group.name})"

    @property
    def parent_object(self) -> ACIBaseModel:
        """Return the parent object of the instance."""
        return self.aci_endpoint_security_group

    @property
    def aci_tenant(self) -> ACITenant:
        """Return the ACITenant instance of the related ESG."""
        return self.aci_endpoint_security_group.aci_tenant

    @property
    def aci_app_profile(self) -> ACIAppProfile:
        """Return the ACIAppProfile instance of the related ESG."""
        return self.aci_endpoint_security_group.aci_app_profile


#
# ACI Endpoint Security Group (ESG) Selector for Endpoint Groups (EPG)
#


class ACIEsgEndpointGroupSelector(
    ACIEsgSelectorBaseModel, UniqueGenericForeignKeyMixin
):
    """NetBox model for ACI Endpoint Security Group (ESG) EPG Selector."""

    aci_epg_object_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to=ESG_ENDPOINT_GROUP_SELECTORS_MODELS,
        verbose_name=_("Endpoint Object Type"),
        blank=True,
        null=True,
    )
    aci_epg_object_id = models.PositiveBigIntegerField(
        verbose_name=_("Endpoint Object ID"),
        blank=True,
        null=True,
    )
    aci_epg_object = GenericForeignKey(
        ct_field="aci_epg_object_type",
        fk_field="aci_epg_object_id",
    )

    # Cached related objects by association name for faster access
    _aci_endpoint_group = models.ForeignKey(
        to="netbox_aci_plugin.ACIEndpointGroup",
        on_delete=models.CASCADE,
        related_name="_aci_esg_endpoint_group_selectors",
        verbose_name=_("ACI Endpoint Group"),
        blank=True,
        null=True,
    )
    _aci_useg_endpoint_group = models.ForeignKey(
        to="netbox_aci_plugin.ACIUSegEndpointGroup",
        on_delete=models.CASCADE,
        related_name="_aci_esg_endpoint_group_selectors",
        verbose_name=_("ACI uSeg Endpoint Group"),
        blank=True,
        null=True,
    )

    clone_fields: tuple = ACIEsgSelectorBaseModel.clone_fields + (
        "aci_epg_object_type",
    )

    # Unique GenericForeignKey validation
    generic_fk_field = "aci_epg_object"
    generic_unique_fields = ("aci_endpoint_security_group",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=(
                    "name",
                    "aci_endpoint_security_group",
                ),
                name=(
                    "%(app_label)s_%(class)s_unique_name_"
                    "per_endpoint_security_group"
                ),
            ),
            models.UniqueConstraint(
                fields=(
                    "aci_endpoint_security_group",
                    "aci_epg_object_type",
                    "aci_epg_object_id",
                ),
                name=(
                    "%(app_label)s_%(class)s_unique_aci_epg_object_"
                    "per_endpoint_security_group"
                ),
            ),
        ]
        default_related_name: str = "aci_esg_endpoint_group_selectors"
        indexes: tuple = (
            models.Index(fields=("aci_epg_object_type", "aci_epg_object_id")),
        )
        ordering: tuple = (
            "name",
            "aci_endpoint_security_group",
            "_aci_endpoint_group",
            "_aci_useg_endpoint_group",
        )
        verbose_name: str = _("ACI ESG Endpoint Group Selector")

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""

        # Validate Endpoint Group object assignment before validation of
        # any other fields
        if self.aci_epg_object_type and not self.aci_epg_object:
            aci_epg_model_class = self.aci_epg_object_type.model_class()
            raise ValidationError(
                {
                    "aci_epg_object": _(
                        "The {aci_epg_object} field is required, if an Endpoint "
                        "Object Type is selected.".format(
                            aci_epg_object=aci_epg_model_class._meta.verbose_name
                        )
                    )
                }
            )
        if self.aci_epg_object and not self.aci_epg_object_type:
            raise ValidationError(
                {
                    "aci_epg_object_type": _(
                        "An Endpoint Object Type is required, if an "
                        "Endpoint Object is provided."
                    )
                }
            )

        super().clean()

        # Validate the assigned ACI EPG Object belongs to the same
        # ACITenant as the ACIEndpointSecurityGroup
        if (
            hasattr(self.aci_epg_object, "aci_tenant")
            and self.aci_endpoint_security_group.aci_tenant
            != self.aci_epg_object.aci_tenant
        ):
            aci_model_class = self.aci_epg_object_type.model_class()
            raise ValidationError(
                {
                    "aci_epg_object": _(
                        "An assigned {aci_epg_object} must belong to the "
                        "same ACI Tenant as the "
                        "ACI Endpoint Security Group.".format(
                            aci_epg_object=aci_model_class._meta.verbose_name
                        )
                    )
                }
            )

        # Validate the assigned ACI EPG Object belongs to the same
        # ACIVRF as the ACIEndpointSecurityGroup
        if (
            hasattr(self.aci_epg_object, "aci_vrf")
            and self.aci_endpoint_security_group.aci_vrf
            != self.aci_epg_object.aci_vrf
        ):
            aci_model_class = self.aci_epg_object_type.model_class()
            raise ValidationError(
                {
                    "aci_epg_object": _(
                        "An assigned {aci_epg_object} must belong to the "
                        "same ACI VRF as the "
                        "ACI Endpoint Security Group.".format(
                            aci_epg_object=aci_model_class._meta.verbose_name
                        )
                    )
                }
            )

        # Perform the mixin's unique constraint validation
        self._validate_generic_uniqueness()

    def save(self, *args, **kwargs) -> None:
        """Saves the current instance to the database."""
        # Cache the related objects for faster access
        self.cache_related_objects()

        super().save(*args, **kwargs)

    def cache_related_objects(self) -> None:
        """Cache the related objects for faster access."""
        self._aci_endpoint_group = self._aci_useg_endpoint_group = None
        if self.aci_epg_object_type:
            aci_epg_object_type = self.aci_epg_object_type.model_class()
            if aci_epg_object_type == apps.get_model(
                "netbox_aci_plugin", "ACIEndpointGroup"
            ):
                self._aci_endpoint_group = self.aci_epg_object
            elif aci_epg_object_type == apps.get_model(
                "netbox_aci_plugin", "ACIUSegEndpointGroup"
            ):
                self._aci_useg_endpoint_group = self.aci_epg_object

    cache_related_objects.alters_data = True

    @property
    def aci_epg_object_tenant(self) -> ACITenant:
        """Return the ACITenant instance of related ACI EPG object."""
        return self.aci_epg_object.aci_app_profile.aci_tenant

    @property
    def aci_epg_object_app_profile(self) -> ACIAppProfile:
        """Return the ACIAppProfile instance of related ACI EPG object."""
        return self.aci_epg_object.aci_app_profile
