# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from dcim.models.mixins import CachedScopeMixin
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ...constants import POD_ID_MAX, POD_ID_MIN
from ..base import ACIFabricBaseModel

if TYPE_CHECKING:
    from ..fabric.fabrics import ACIFabric


class ACIPod(CachedScopeMixin, ACIFabricBaseModel):
    """NetBox model for ACI Pod."""

    aci_fabric = models.ForeignKey(
        to="netbox_aci_plugin.ACIFabric",
        on_delete=models.PROTECT,
        related_name="aci_pods",
        verbose_name=_("ACI Fabric"),
    )
    pod_id = models.PositiveSmallIntegerField(
        verbose_name=_("Pod ID"),
        validators=[
            MinValueValidator(POD_ID_MIN),
            MaxValueValidator(POD_ID_MAX),
        ],
    )
    tep_pool = models.ForeignKey(
        to="ipam.Prefix",
        on_delete=models.SET_NULL,
        related_name="aci_pods",
        verbose_name=_("TEP Pool"),
        blank=True,
        null=True,
        help_text=_(
            "The internal TEP pool used to assign Tunnel Endpoint (TEP) "
            "addresses to leaf and spine nodes within the pod."
        ),
    )

    clone_fields: tuple = ACIFabricBaseModel.clone_fields + (
        "aci_fabric",
        "scope_type",
        "scope_id",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIFabric",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_fabric", "pod_id"),
                name="%(app_label)s_%(class)s_unique_pod_per_aci_fabric",
            ),
            models.UniqueConstraint(
                fields=("aci_fabric", "name"),
                name="%(app_label)s_%(class)s_unique_pod_name_per_aci_fabric",
            ),
        ]
        ordering: tuple = ("aci_fabric", "pod_id")
        verbose_name: str = _("ACI Pod")

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        errors = {}

        # Ensure tep_pool is an IPv4 unicast prefix with a prefix
        # length of /0–/21 (inclusive).
        if self.tep_pool and (
            self.tep_pool.prefix.version != 4
            or self.tep_pool.prefix.prefixlen > 21
            or self.tep_pool.prefix.is_multicast()
        ):
            errors.setdefault("tep_pool", []).append(
                _("TEP Pool must be an IPv4 unicast prefix no more specific than /21.")
            )

        if errors:
            raise ValidationError(errors)

    @property
    def parent_object(self) -> ACIFabric:
        """Return the parent object of the instance."""
        return self.aci_fabric
