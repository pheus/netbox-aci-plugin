# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel

from ..validators import ACIPolicyDescriptionValidator, ACIPolicyNameValidator


class ACIBaseModel(NetBoxModel):
    """NetBox abstract model for ACI classes."""

    name = models.CharField(
        verbose_name=_("name"),
        max_length=64,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
    )
    name_alias = models.CharField(
        verbose_name=_("name alias"),
        max_length=64,
        blank=True,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
    )
    description = models.CharField(
        verbose_name=_("description"),
        max_length=128,
        blank=True,
        validators=[
            MaxLengthValidator(128),
            ACIPolicyDescriptionValidator,
        ],
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
        "nb_tenant",
    )

    class Meta:
        abstract: bool = True
        ordering: tuple = ("name",)

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return self.name

    @property
    def parent_object(self) -> NetBoxModel | None:
        """Return the parent object of the instance."""
        return NotImplemented
