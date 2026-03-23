# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ...constants import ACI_NAME_MAX_LEN
from ...validators import ACIPolicyNameRequiredValidator
from ..base import ACIFabricBaseModel

if TYPE_CHECKING:
    from ..fabric.fabrics import ACIFabric


class ACIDomainBaseModel(ACIFabricBaseModel):
    """Base model for ACI Access Policy Domains."""

    aci_fabric = models.ForeignKey(
        to="netbox_aci_plugin.ACIFabric",
        on_delete=models.PROTECT,
        related_name="%(class)ss",
        verbose_name=_("ACI Fabric"),
    )
    security_domains = ArrayField(
        base_field=models.CharField(
            max_length=ACI_NAME_MAX_LEN,
            validators=[ACIPolicyNameRequiredValidator],
        ),
        verbose_name=_("security domains"),
        blank=True,
        default=list,
        help_text=_("Optional list of ACI security domain names."),
    )

    clone_fields: tuple = ACIFabricBaseModel.clone_fields + (
        "aci_fabric",
        "security_domains",
    )

    class Meta:
        abstract: bool = True

    @property
    def parent_object(self) -> ACIFabric:
        """Return the parent object of the instance."""
        return self.aci_fabric


class ACIRoutedDomain(ACIDomainBaseModel):
    """NetBox model for ACI Routed Domains."""

    aci_fabric = models.ForeignKey(
        to="netbox_aci_plugin.ACIFabric",
        on_delete=models.PROTECT,
        related_name="aci_routed_domains",
        verbose_name=_("ACI Fabric"),
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIFabric",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_fabric", "name"),
                name="%(app_label)s_%(class)s_unique_name_per_aci_fabric",
            ),
        ]
        ordering: tuple = ("aci_fabric", "name")
        verbose_name: str = _("ACI Routed Domain")

    def clean(self) -> None:
        """Validate unique security domain entries."""
        super().clean()
        errors = {}
        if self.security_domains:
            seen = set()
            duplicates = set()
            for domain in self.security_domains:
                if domain in seen:
                    duplicates.add(domain)
                seen.add(domain)
            if duplicates:
                errors["security_domains"] = [
                    _("Duplicate security domain(s): {duplicates}").format(
                        duplicates=", ".join(sorted(duplicates))
                    )
                ]
        if errors:
            raise ValidationError(errors)
