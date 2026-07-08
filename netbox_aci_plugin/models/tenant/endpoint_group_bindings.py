# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Models for ACI Endpoint Group domain bindings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel

from ...choices import DeploymentImmediacyChoices, ResolutionImmediacyChoices
from ...constants import (
    EPG_DOMAIN_BINDING_DOMAIN_OBJECT_TYPES,
    EPG_DOMAIN_BINDING_EPG_OBJECT_TYPES,
)
from ..mixins import UniqueGenericForeignKeyMixin

if TYPE_CHECKING:
    from core.models import ObjectChange

    from ..fabric.fabrics import ACIFabric
    from .endpoint_groups import ACIEndpointGroup, ACIUSegEndpointGroup
    from .tenants import ACITenant


class ACIEndpointGroupDomainBinding(NetBoxModel, UniqueGenericForeignKeyMixin):
    """Association of an ACI Endpoint Group with an ACI domain (fvRsDomAtt).

    Links an ACIEndpointGroup or ACIUSegEndpointGroup to an ACI domain
    through generic foreign keys, mirrored into cached foreign keys for
    efficient querying. This binding is the anchor every EPG deployment
    method references.

    Notes:
        The referenced domain must belong to the same ACI Fabric as the
        endpoint group.
    """

    aci_epg_object_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to=EPG_DOMAIN_BINDING_EPG_OBJECT_TYPES,
        verbose_name=_("ACI EPG object type"),
        blank=True,
        null=True,
    )
    aci_epg_object_id = models.PositiveBigIntegerField(
        verbose_name=_("ACI EPG object ID"),
        blank=True,
        null=True,
    )
    aci_epg_object = GenericForeignKey(
        ct_field="aci_epg_object_type",
        fk_field="aci_epg_object_id",
    )
    aci_domain_object_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to=EPG_DOMAIN_BINDING_DOMAIN_OBJECT_TYPES,
        verbose_name=_("ACI domain object type"),
        blank=True,
        null=True,
    )
    aci_domain_object_id = models.PositiveBigIntegerField(
        verbose_name=_("ACI domain object ID"),
        blank=True,
        null=True,
    )
    aci_domain_object = GenericForeignKey(
        ct_field="aci_domain_object_type",
        fk_field="aci_domain_object_id",
    )
    deployment_immediacy = models.CharField(
        verbose_name=_("deployment immediacy"),
        max_length=9,
        default=DeploymentImmediacyChoices.IMMEDIACY_LAZY,
        choices=DeploymentImmediacyChoices,
        help_text=_(
            "When the policy is pushed into the leaf hardware. Default is 'On Demand'."
        ),
    )
    resolution_immediacy = models.CharField(
        verbose_name=_("resolution immediacy"),
        max_length=13,
        default=ResolutionImmediacyChoices.IMMEDIACY_LAZY,
        choices=ResolutionImmediacyChoices,
        help_text=_(
            "When the policy is downloaded to the leaf software. Default is "
            "'On Demand'."
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
        related_name="_aci_endpoint_group_domain_bindings",
        verbose_name=_("ACI Endpoint Group"),
        blank=True,
        null=True,
    )
    _aci_useg_endpoint_group = models.ForeignKey(
        to="netbox_aci_plugin.ACIUSegEndpointGroup",
        on_delete=models.CASCADE,
        related_name="_aci_endpoint_group_domain_bindings",
        verbose_name=_("ACI uSeg Endpoint Group"),
        blank=True,
        null=True,
    )
    _aci_physical_domain = models.ForeignKey(
        to="netbox_aci_plugin.ACIPhysicalDomain",
        on_delete=models.CASCADE,
        related_name="_aci_endpoint_group_domain_bindings",
        verbose_name=_("ACI Physical Domain"),
        blank=True,
        null=True,
    )

    clone_fields: tuple = (
        "aci_epg_object_type",
        "aci_domain_object_type",
        "deployment_immediacy",
        "resolution_immediacy",
    )

    # Unique GenericForeignKey validation
    generic_fk_field = "aci_epg_object"
    generic_unique_fields = ("aci_domain_object_type", "aci_domain_object_id")

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=(
                    "aci_epg_object_type",
                    "aci_epg_object_id",
                    "aci_domain_object_type",
                    "aci_domain_object_id",
                ),
                name="%(app_label)s_%(class)s_unique_aci_domain_object_per_epg",
            ),
        ]
        default_related_name: str = "aci_endpoint_group_domain_bindings"
        indexes: tuple = (
            models.Index(fields=("aci_epg_object_type", "aci_epg_object_id")),
            models.Index(fields=("aci_domain_object_type", "aci_domain_object_id")),
        )
        ordering: tuple = (
            "_aci_endpoint_group",
            "_aci_useg_endpoint_group",
            "_aci_physical_domain",
        )
        verbose_name: str = _("ACI Endpoint Group Domain Binding")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return f"{self.aci_epg_object} - {self.aci_domain_object}"

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        # Validate EPG object assignment before validation of other fields
        if self.aci_epg_object_type_id and not (
            self.aci_epg_object or self.aci_epg_object_id
        ):
            aci_model_class = self.aci_epg_object_type.model_class()
            raise ValidationError(
                {
                    "aci_epg_object": _(
                        "The {aci_epg_object} field is required, if an ACI "
                        "EPG object type is selected."
                    ).format(aci_epg_object=aci_model_class._meta.verbose_name)
                }
            )

        # Validate domain object assignment before validation of other fields
        if self.aci_domain_object_type_id and not (
            self.aci_domain_object or self.aci_domain_object_id
        ):
            aci_model_class = self.aci_domain_object_type.model_class()
            raise ValidationError(
                {
                    "aci_domain_object": _(
                        "The {aci_domain_object} field is required, if an ACI "
                        "domain object type is selected."
                    ).format(aci_domain_object=aci_model_class._meta.verbose_name)
                }
            )

        super().clean()

        errors = {}

        # Validate the domain object belongs to the same ACI Fabric as the
        # endpoint group
        if (
            self.aci_epg_object_id
            and self.aci_domain_object_id
            and hasattr(self.aci_epg_object, "aci_fabric")
            and hasattr(self.aci_domain_object, "aci_fabric")
            and self.aci_epg_object.aci_fabric != self.aci_domain_object.aci_fabric
        ):
            aci_epg_model_class = self.aci_epg_object_type.model_class()
            aci_domain_model_class = self.aci_domain_object_type.model_class()
            errors.setdefault("aci_domain_object", []).append(
                _(
                    "The assigned {aci_domain_object} must belong to the "
                    "same ACI Fabric as the {aci_epg_object}."
                ).format(
                    aci_domain_object=aci_domain_model_class._meta.verbose_name,
                    aci_epg_object=aci_epg_model_class._meta.verbose_name,
                )
            )

        if errors:
            raise ValidationError(errors)

        # Perform the mixin's unique constraint validation
        self._validate_generic_uniqueness()

    def save(self, *args, **kwargs) -> None:
        """Save the current instance to the database."""
        # Cache the related objects for faster access
        self.cache_related_objects()

        super().save(*args, **kwargs)

    def cache_related_objects(self) -> None:
        """Cache the related objects for faster access."""
        self._aci_endpoint_group = self._aci_useg_endpoint_group = None
        self._aci_physical_domain = None
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
        if self.aci_domain_object_type:
            aci_domain_object_type = self.aci_domain_object_type.model_class()
            if aci_domain_object_type == apps.get_model(
                "netbox_aci_plugin", "ACIPhysicalDomain"
            ):
                self._aci_physical_domain = self.aci_domain_object

    cache_related_objects.alters_data = True

    def to_objectchange(self, action) -> ObjectChange:
        """Return an ObjectChange for the change made to an instance."""
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.aci_epg_object
        return objectchange

    @property
    def aci_tenant(self) -> ACITenant:
        """Return the ACITenant instance of the related ACI EPG object."""
        return self.aci_epg_object.aci_tenant

    @property
    def aci_fabric(self) -> ACIFabric:
        """Return the ACIFabric instance of the related ACI Tenant."""
        return self.aci_tenant.aci_fabric

    @property
    def parent_object(self) -> ACIEndpointGroup | ACIUSegEndpointGroup:
        """Return the parent object of the instance."""
        return self.aci_epg_object

    def get_deployment_immediacy_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return DeploymentImmediacyChoices.colors.get(self.deployment_immediacy)

    def get_resolution_immediacy_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return ResolutionImmediacyChoices.colors.get(self.resolution_immediacy)
