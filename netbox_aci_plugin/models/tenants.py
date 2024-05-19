# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.validators import MaxLengthValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
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
        verbose_name=_("name"),
    )
    alias = models.CharField(
        max_length=64,
        blank=True,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
        verbose_name=_("alias"),
    )
    description = models.CharField(
        max_length=128,
        blank=True,
        validators=[
            MaxLengthValidator(128),
            ACIPolicyDescriptionValidator,
        ],
        verbose_name=_("description"),
    )
    nb_tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="+",
        blank=True,
        null=True,
        verbose_name=_("NetBox tenant"),
    )
    comments = models.TextField(
        blank=True,
        verbose_name=_("comments"),
    )

    clone_fields: tuple = (
        "description",
        "nb_tenant",
    )

    class Meta:
        ordering: tuple = ("name",)
        verbose_name: str = _("ACI Tenant")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return self.name

    def get_absolute_url(self) -> str:
        """Return the absolute URL of the instance."""
        return reverse("plugins:netbox_aci_plugin:acitenant", args=[self.pk])
