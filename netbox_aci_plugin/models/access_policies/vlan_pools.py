# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Models for ACI access-policy VLAN Pools."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel
from utilities.data import ranges_to_string

from ...choices import (
    VLANAllocationModeChoices,
    VLANPoolRangeAllocationModeChoices,
    VLANPoolRangeRoleChoices,
)
from ...constants import VLAN_VID_MAX, VLAN_VID_MIN
from ..base import ACIFabricBaseModel

if TYPE_CHECKING:
    from django.db.backends.postgresql.psycopg_any import NumericRange

    from ..fabric.fabrics import ACIFabric


class ACIVLANPool(ACIFabricBaseModel):
    """ACI VLAN Pool (fvnsVlanInstP) scoped to a fabric.

    Groups VLAN encapsulation ranges with an allocation mode, optionally
    backed by a NetBox VLAN group.
    """

    aci_fabric = models.ForeignKey(
        to="netbox_aci_plugin.ACIFabric",
        on_delete=models.PROTECT,
        related_name="aci_vlan_pools",
        verbose_name=_("ACI Fabric"),
    )
    allocation_mode = models.CharField(
        verbose_name=_("allocation mode"),
        max_length=7,
        choices=VLANAllocationModeChoices,
        default=VLANAllocationModeChoices.MODE_STATIC,
        help_text=_(
            "Dynamic pools let the APIC assign VLANs automatically (typically "
            "for VMM domains). Static pools use manually defined ranges."
        ),
    )
    nb_vlan_group = models.OneToOneField(
        to="ipam.VLANGroup",
        on_delete=models.SET_NULL,
        related_name="aci_vlan_pool",
        verbose_name=_("NetBox VLAN group"),
        blank=True,
        null=True,
    )

    clone_fields: tuple = ACIFabricBaseModel.clone_fields + (
        "aci_fabric",
        "allocation_mode",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIFabric",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_fabric", "name"),
                name="%(app_label)s_%(class)s_unique_name_per_aci_fabric",
            ),
        ]
        default_related_name: str = "aci_vlan_pools"
        ordering: tuple = ("aci_fabric", "name")
        verbose_name: str = _("ACI VLAN Pool")

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        errors = {}

        # Validate the assigned NetBox VLAN group covers all existing
        # ACIVLANPoolRange instances of the ACIVLANPool
        if self.nb_vlan_group_id and self.pk:
            vid_ranges = self.nb_vlan_group.vid_ranges
            offending = [
                pool_range
                for pool_range in self.aci_vlan_pool_ranges.all()
                if not pool_range.is_within_vlan_group_ranges(vid_ranges)
            ]
            if offending:
                errors.setdefault("nb_vlan_group", []).append(
                    _(
                        "The assigned NetBox VLAN group's ranges ({ranges}) "
                        "do not cover all existing ACI VLAN Pool ranges: {offending}."
                    ).format(
                        ranges=ranges_to_string(vid_ranges),
                        offending=", ".join(str(r) for r in offending),
                    )
                )

        if errors:
            raise ValidationError(errors)

    @property
    def parent_object(self) -> ACIFabric:
        """Return the parent object of the instance."""
        return self.aci_fabric

    def get_allocation_mode_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return VLANAllocationModeChoices.colors.get(self.allocation_mode)

    def covers_vid(self, vid: int) -> bool:
        """Return whether the VLAN ID is within one of the pool's ranges."""
        return self.aci_vlan_pool_ranges.filter(
            vlan_id_from__lte=vid, vlan_id_to__gte=vid
        ).exists()


class ACIVLANPoolRange(NetBoxModel):
    """ACI VLAN Pool encapsulation range (fvnsEncapBlk).

    A contiguous VLAN ID block within an ACIVLANPool.
    """

    aci_vlan_pool = models.ForeignKey(
        to="netbox_aci_plugin.ACIVLANPool",
        on_delete=models.CASCADE,
        related_name="aci_vlan_pool_ranges",
        verbose_name=_("ACI VLAN Pool"),
    )
    vlan_id_from = models.PositiveSmallIntegerField(
        verbose_name=_("VLAN ID (from)"),
        validators=[
            MinValueValidator(VLAN_VID_MIN),
            MaxValueValidator(VLAN_VID_MAX),
        ],
    )
    vlan_id_to = models.PositiveSmallIntegerField(
        verbose_name=_("VLAN ID (to)"),
        validators=[
            MinValueValidator(VLAN_VID_MIN),
            MaxValueValidator(VLAN_VID_MAX),
        ],
    )
    allocation_mode = models.CharField(
        verbose_name=_("allocation mode"),
        max_length=7,
        choices=VLANPoolRangeAllocationModeChoices,
        default=VLANPoolRangeAllocationModeChoices.MODE_INHERIT,
        help_text=_(
            "Overrides the pool allocation mode for this block. 'inherit' uses "
            "the pool setting."
        ),
    )
    role = models.CharField(
        verbose_name=_("role"),
        max_length=8,
        choices=VLANPoolRangeRoleChoices,
        default=VLANPoolRangeRoleChoices.ROLE_EXTERNAL,
    )
    comments = models.TextField(
        verbose_name=_("comments"),
        blank=True,
    )

    clone_fields: tuple = (
        "aci_vlan_pool",
        "allocation_mode",
        "role",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIVLANPool",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_vlan_pool", "vlan_id_from", "vlan_id_to"),
                name="%(app_label)s_%(class)s_unique_range_per_pool",
            ),
        ]
        default_related_name: str = "aci_vlan_pool_ranges"
        ordering: tuple = ("aci_vlan_pool", "vlan_id_from")
        verbose_name: str = _("ACI VLAN Pool Range")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return f"{self.vlan_id_from}-{self.vlan_id_to}"

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()
        errors = {}
        if (
            self.vlan_id_from is not None
            and self.vlan_id_to is not None
            and self.vlan_id_from > self.vlan_id_to
        ):
            errors.setdefault("vlan_id_to", []).append(
                _("The starting VLAN ID must not be greater than the ending VLAN ID.")
            )
        if (
            not errors
            and self.aci_vlan_pool_id
            and self.vlan_id_from is not None
            and self.vlan_id_to is not None
        ):
            overlap = (
                ACIVLANPoolRange.objects.filter(
                    aci_vlan_pool_id=self.aci_vlan_pool_id,
                    vlan_id_from__lte=self.vlan_id_to,
                    vlan_id_to__gte=self.vlan_id_from,
                )
                .exclude(pk=self.pk)
                .exists()
            )
            if overlap:
                errors.setdefault("vlan_id_from", []).append(
                    _(
                        "This VLAN range overlaps an existing range in "
                        "the ACI VLAN Pool."
                    )
                )
            if not errors:
                group = self.aci_vlan_pool.nb_vlan_group
                if group is not None and not self.is_within_vlan_group_ranges(
                    group.vid_ranges
                ):
                    # Key the error to whichever endpoint falls outside the
                    # group's ranges.
                    field = (
                        "vlan_id_from"
                        if any(self.vlan_id_to in r for r in group.vid_ranges)
                        else "vlan_id_to"
                    )
                    errors.setdefault(field, []).append(
                        _(
                            "This VLAN range is not fully within the assigned "
                            "NetBox VLAN group's ranges ({ranges})."
                        ).format(ranges=ranges_to_string(group.vid_ranges))
                    )
        if errors:
            raise ValidationError(errors)

    def to_objectchange(self, action):
        """Return an ObjectChange for the change made to an instance."""
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.aci_vlan_pool
        return objectchange

    @property
    def parent_object(self) -> ACIVLANPool:
        """Return the parent object of the instance."""
        return self.aci_vlan_pool

    def get_allocation_mode_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return VLANPoolRangeAllocationModeChoices.colors.get(self.allocation_mode)

    def get_role_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return VLANPoolRangeRoleChoices.colors.get(self.role)

    def is_within_vlan_group_ranges(self, vid_ranges: list[NumericRange]) -> bool:
        """Return True if this range is within the given VLAN group ranges."""
        return all(
            any(vid in vid_range for vid_range in vid_ranges)
            for vid in range(self.vlan_id_from, self.vlan_id_to + 1)
        )
