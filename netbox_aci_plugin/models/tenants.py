# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.validators import MaxLengthValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from ..validators import ACIPolicyDescriptionValidator, ACIPolicyNameValidator


class ACITenant(NetBoxModel):
    """NetBox model for ACI Tenant."""

    name = models.CharField(
        max_length=64,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
    )
    alias = models.CharField(
        max_length=64, blank=True, validators=[ACIPolicyNameValidator]
    )
    description = models.CharField(
        max_length=128, blank=True, validators=[ACIPolicyDescriptionValidator]
    )
    comments = models.TextField(blank=True)

    class Meta:
        ordering: tuple = ("name",)
        verbose_name: str = "ACI Tenant"

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return self.name

    def get_absolute_url(self) -> str:
        """Return the absolute URL of the instance."""
        return reverse("plugins:netbox_aci_plugin:acitenant", args=[self.pk])
