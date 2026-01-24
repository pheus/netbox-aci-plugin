# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from dcim.models.mixins import CachedScopeMixin
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel
from netbox.models.mixins import OwnerMixin

from ...constants import (
    ACI_DESC_MAX_LEN,
    ACI_NAME_MAX_LEN,
    FABRIC_ID_MAX,
    FABRIC_ID_MIN,
    VLAN_VID_MAX,
    VLAN_VID_MIN,
)
from ...validators import ACIPolicyDescriptionValidator, ACIPolicyNameRequiredValidator


class ACIFabric(CachedScopeMixin, OwnerMixin, NetBoxModel):
    """NetBox model for ACI Fabric."""

    name = models.CharField(
        verbose_name=_("name"),
        max_length=ACI_NAME_MAX_LEN,
        validators=[ACIPolicyNameRequiredValidator],
    )
    description = models.CharField(
        verbose_name=_("description"),
        max_length=ACI_DESC_MAX_LEN,
        blank=True,
        validators=[ACIPolicyDescriptionValidator],
    )
    fabric_id = models.PositiveSmallIntegerField(
        verbose_name=_("Fabric ID"),
        help_text=_("ACI Fabric ID (1–128). Used by GOLF Auto‑RT if enabled."),
        validators=[
            MinValueValidator(FABRIC_ID_MIN),
            MaxValueValidator(FABRIC_ID_MAX),
        ],
    )
    infra_vlan_vid = models.PositiveSmallIntegerField(
        verbose_name=_("Infrastructure VLAN ID"),
        help_text=_("Fabric-wide Infrastructure VLAN (1–4094)."),
        validators=[
            MinValueValidator(VLAN_VID_MIN),
            MaxValueValidator(VLAN_VID_MAX),
        ],
    )
    infra_vlan = models.ForeignKey(
        to="ipam.VLAN",
        on_delete=models.SET_NULL,
        related_name="aci_fabrics",
        verbose_name=_("Infrastructure VLAN"),
        blank=True,
        null=True,
        help_text=_("Optional: reference a NetBox VLAN that documents the same ID."),
    )
    gipo_pool = models.ForeignKey(
        "ipam.Prefix",
        on_delete=models.SET_NULL,
        related_name="aci_fabrics",
        verbose_name=_("GIPo pool"),
        blank=True,
        null=True,
        help_text=_("Fabric-wide multicast pool (GIPo), e.g. 225.0.0.0/15"),
    )
    nb_tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        related_name="%(class)ss",
        verbose_name=_("NetBox tenant"),
        blank=True,
        null=True,
    )
    comments = models.TextField(
        verbose_name=_("comments"),
        blank=True,
    )

    clone_fields: tuple = (
        "description",
        "infra_vlan_vid",
        "infra_vlan",
        "gipo_pool",
        "scope_type",
        "scope_id",
        "nb_tenant",
    )

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("name",),
                name="%(app_label)s_%(class)s_unique_name",
            ),
            models.UniqueConstraint(
                fields=("fabric_id",),
                name="%(app_label)s_%(class)s_unique_fabric_id",
            ),
        ]
        ordering: tuple = ("name",)
        verbose_name: str = _("ACI Fabric")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return self.name

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        errors = {}

        # Ensure VLAN object VID matches infra_vlan_vid
        if (
            self.infra_vlan
            and self.infra_vlan_vid
            and self.infra_vlan.vid != self.infra_vlan_vid
        ):
            errors.setdefault("infra_vlan", []).append(
                _("NetBox referenced VLAN VID must match the Infrastructure VLAN VID.")
            )

        # Ensure gipo_pool is IPv4 multicast prefix
        if self.gipo_pool and (
            self.gipo_pool.prefix.version != 4
            or not self.gipo_pool.prefix.is_multicast()
        ):
            errors.setdefault("gipo_pool", []).append(
                _("GIPo must be IPv4 multicast prefix.")
            )

        if errors:
            raise ValidationError(errors)

    @property
    def aci_fabric(self) -> ACIFabric:
        """Return self as the ACIFabric instance."""
        return self

    @property
    def parent_object(self) -> NetBoxModel | None:
        """Return the parent object of the instance."""
        return None
