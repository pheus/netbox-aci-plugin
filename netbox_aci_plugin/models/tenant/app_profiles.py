# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..base import ACIBaseModel
from .tenants import ACITenant


class ACIAppProfile(ACIBaseModel):
    """NetBox model for ACI Application Profile."""

    aci_tenant = models.ForeignKey(
        to=ACITenant,
        on_delete=models.PROTECT,
        related_name="aci_app_profiles",
        verbose_name=_("ACI Tenant"),
    )

    clone_fields: tuple = ACIBaseModel.clone_fields + ("aci_tenant",)
    prerequisite_models: tuple = ("netbox_aci_plugin.ACITenant",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_tenant", "name"),
                name="%(app_label)s_%(class)s_unique_per_aci_tenant",
            ),
        ]
        ordering: tuple = ("aci_tenant", "name")
        verbose_name: str = _("ACI Application Profile")

    @property
    def parent_object(self) -> ACIBaseModel:
        """Return the parent object of the instance."""
        return self.aci_tenant
