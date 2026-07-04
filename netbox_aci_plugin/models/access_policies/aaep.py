# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Models for ACI Attachable Access Entity Profiles and domain bindings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel

from ...constants import AAEP_DOMAIN_OBJECT_TYPES
from ..base import ACIFabricBaseModel
from ..mixins import UniqueGenericForeignKeyMixin

if TYPE_CHECKING:
    from core.models import ObjectChange

    from ..fabric.fabrics import ACIFabric


class ACIAttachableAccessEntityProfile(ACIFabricBaseModel):
    """ACI Attachable Access Entity Profile (infraAttEntityP).

    Ties interface policy groups to access domains (physical or
    routed), and optionally enables the infrastructure VLAN on
    associated ports. Parented by an ACIFabric and associated
    with physical and routed domains via domain bindings.
    """

    aci_fabric = models.ForeignKey(
        to="netbox_aci_plugin.ACIFabric",
        on_delete=models.PROTECT,
        related_name="aci_aaeps",
        verbose_name=_("ACI Fabric"),
    )
    infra_vlan = models.BooleanField(
        verbose_name=_("Infrastructure VLAN"),
        default=False,
        help_text=_(
            "Enable the infrastructure VLAN on ports associated with this AAEP."
        ),
    )

    clone_fields: tuple = ACIFabricBaseModel.clone_fields + (
        "aci_fabric",
        "infra_vlan",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIFabric",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_fabric", "name"),
                name="%(app_label)s_%(class)s_unique_name_per_aci_fabric",
            ),
        ]
        default_related_name: str = "aci_aaeps"
        ordering: tuple = ("aci_fabric", "name")
        verbose_name: str = _("ACI Attachable Access Entity Profile")

    @property
    def parent_object(self) -> ACIFabric:
        """Return the parent object of the instance."""
        return self.aci_fabric


class ACIAAEPDomainBinding(NetBoxModel, UniqueGenericForeignKeyMixin):
    """Attachment of an ACI domain to an AAEP.

    Links an ACIAttachableAccessEntityProfile to a physical or routed
    domain through a generic foreign key, mirrored into a cached
    foreign key for efficient querying.

    Notes:
        The referenced domain must belong to the AAEP's ACI Fabric.
    """

    aci_aaep = models.ForeignKey(
        to="netbox_aci_plugin.ACIAttachableAccessEntityProfile",
        on_delete=models.CASCADE,
        related_name="aci_aaep_domain_bindings",
        verbose_name=_("ACI AAEP"),
    )
    aci_domain_object_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to=AAEP_DOMAIN_OBJECT_TYPES,
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
    comments = models.TextField(
        verbose_name=_("comments"),
        blank=True,
    )

    # Cached related objects by association name for faster access
    _aci_physical_domain = models.ForeignKey(
        to="netbox_aci_plugin.ACIPhysicalDomain",
        on_delete=models.CASCADE,
        related_name="_aci_aaep_domain_bindings",
        verbose_name=_("ACI Physical Domain"),
        blank=True,
        null=True,
    )
    _aci_routed_domain = models.ForeignKey(
        to="netbox_aci_plugin.ACIRoutedDomain",
        on_delete=models.CASCADE,
        related_name="_aci_aaep_domain_bindings",
        verbose_name=_("ACI Routed Domain"),
        blank=True,
        null=True,
    )

    clone_fields: tuple = ("aci_aaep", "aci_domain_object_type")
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIAttachableAccessEntityProfile",)

    # Unique GenericForeignKey validation
    generic_fk_field = "aci_domain_object"
    generic_unique_fields = ("aci_aaep",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=(
                    "aci_aaep",
                    "aci_domain_object_type",
                    "aci_domain_object_id",
                ),
                name="%(app_label)s_%(class)s_unique_aci_domain_object_per_aaep",
            ),
        ]
        default_related_name: str = "aci_aaep_domain_bindings"
        indexes: tuple = (
            models.Index(fields=("aci_domain_object_type", "aci_domain_object_id")),
        )
        ordering: tuple = ("aci_aaep", "_aci_physical_domain", "_aci_routed_domain")
        verbose_name: str = _("ACI AAEP Domain Binding")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return f"{self.aci_aaep.name} - {self.aci_domain_object}"

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
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

        # Validate the domain object belongs to the AAEP's ACIFabric
        if (
            self.aci_aaep_id
            and self.aci_domain_object_id
            and self.aci_aaep.aci_fabric_id != self.aci_domain_object.aci_fabric_id
        ):
            aci_model_class = self.aci_domain_object_type.model_class()
            errors.setdefault("aci_domain_object", []).append(
                _(
                    "The assigned {aci_domain_object} must belong to the "
                    "same ACI Fabric as the ACI AAEP."
                ).format(aci_domain_object=aci_model_class._meta.verbose_name)
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
        self._aci_physical_domain = self._aci_routed_domain = None
        if self.aci_domain_object_type:
            aci_domain_object_type = self.aci_domain_object_type.model_class()
            if aci_domain_object_type == apps.get_model(
                "netbox_aci_plugin", "ACIPhysicalDomain"
            ):
                self._aci_physical_domain = self.aci_domain_object
            elif aci_domain_object_type == apps.get_model(
                "netbox_aci_plugin", "ACIRoutedDomain"
            ):
                self._aci_routed_domain = self.aci_domain_object

    cache_related_objects.alters_data = True

    def to_objectchange(self, action) -> ObjectChange:
        """Return an ObjectChange for the change made to an instance."""
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.aci_aaep
        return objectchange

    @property
    def parent_object(self) -> ACIAttachableAccessEntityProfile:
        """Return the parent object of the instance."""
        return self.aci_aaep
