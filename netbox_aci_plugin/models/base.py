# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel

from ..constants import ACI_DESC_MAX_LEN, ACI_NAME_MAX_LEN
from ..validators import (
    ACIPolicyDescriptionValidator,
    ACIPolicyNameOptionalValidator,
    ACIPolicyNameRequiredValidator,
)


class ACIBaseModel(NetBoxModel):
    """NetBox abstract model for ACI classes."""

    name = models.CharField(
        verbose_name=_("name"),
        max_length=ACI_NAME_MAX_LEN,
        validators=[ACIPolicyNameRequiredValidator],
    )
    name_alias = models.CharField(
        verbose_name=_("name alias"),
        max_length=ACI_NAME_MAX_LEN,
        blank=True,
        validators=[ACIPolicyNameOptionalValidator],
    )
    description = models.CharField(
        verbose_name=_("description"),
        max_length=ACI_DESC_MAX_LEN,
        blank=True,
        validators=[ACIPolicyDescriptionValidator],
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
        raise NotImplementedError
