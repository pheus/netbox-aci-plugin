# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import ACIBaseModel


class ACITenant(ACIBaseModel):
    """NetBox model for ACI Tenant."""

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("name",),
                name="unique_aci_tenant_name",
            ),
        ]
        ordering: tuple = ("name",)
        verbose_name: str = _("ACI Tenant")
