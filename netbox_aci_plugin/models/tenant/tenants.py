# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel

from ..base import ACITenantBaseModel


class ACITenant(ACITenantBaseModel):
    """NetBox model for ACI Tenant."""

    aci_fabric = models.ForeignKey(
        to="netbox_aci_plugin.ACIFabric",
        on_delete=models.PROTECT,
        related_name="aci_tenants",
        verbose_name=_("ACI Tenant"),
    )

    clone_fields: tuple = ACITenantBaseModel.clone_fields + ("aci_fabric",)
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIFabric",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_fabric", "name"),
                name="%(app_label)s_%(class)s_unique_name_per_aci_fabric",
            ),
        ]
        ordering: tuple = ("aci_fabric", "name")
        verbose_name: str = _("ACI Tenant")

    @property
    def parent_object(self) -> NetBoxModel:
        """Return the parent object of the instance."""
        return self.aci_fabric
