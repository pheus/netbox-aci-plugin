# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel
from netbox.models.mixins import OwnerMixin

from ..constants import ACI_DESC_MAX_LEN, ACI_NAME_MAX_LEN
from ..validators import (
    ACIPolicyDescriptionValidator,
    ACIPolicyNameOptionalValidator,
    ACIPolicyNameRequiredValidator,
)

if TYPE_CHECKING:
    from .fabric.fabrics import ACIFabric
    from .tenant.tenants import ACITenant


class ACIBaseModel(OwnerMixin, NetBoxModel):
    """Base model for ACI policies."""

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
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement 'parent_object'"
        )


class ACIFabricBaseModel(ACIBaseModel):
    """Base model for ACI Fabric-level policies."""

    class Meta:
        abstract = True

    @property
    def aci_fabric(self) -> ACIFabric:
        """
        Return the ACIFabric instance.

        Subclasses must implement this property or have an 'aci_fabric' field.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement 'aci_fabric'"
        )


class ACITenantBaseModel(ACIBaseModel):
    """Base model for ACI Tenant-level policies."""

    class Meta:
        abstract = True

    @property
    def aci_tenant(self) -> ACITenant:
        """
        Return the ACITenant instance.

        Subclasses must implement this property or have an 'aci_tenant' field.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement 'aci_tenant'"
        )

    @property
    def aci_fabric(self) -> ACIFabric:
        """Return the ACIFabric instance of the related ACITenant."""
        return self.aci_tenant.aci_fabric
