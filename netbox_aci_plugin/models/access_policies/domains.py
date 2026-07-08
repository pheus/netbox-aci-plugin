# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Models for ACI access-policy domains."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericRelation
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
    """Abstract base for ACI access-policy domains.

    Binds a domain to an ACIFabric and carries the optional list of
    ACI security domain names.
    """

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
    aci_vlan_pool = models.ForeignKey(
        to="netbox_aci_plugin.ACIVLANPool",
        on_delete=models.SET_NULL,
        related_name="%(class)ss",
        verbose_name=_("ACI VLAN Pool"),
        blank=True,
        null=True,
    )

    clone_fields: tuple = ACIFabricBaseModel.clone_fields + (
        "aci_fabric",
        "security_domains",
        "aci_vlan_pool",
    )

    class Meta:
        abstract: bool = True

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
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
                errors.setdefault("security_domains", []).append(
                    _("Duplicate security domain(s): {duplicates}").format(
                        duplicates=", ".join(sorted(duplicates))
                    )
                )
        if (
            self.aci_vlan_pool_id
            and self.aci_fabric_id
            and self.aci_vlan_pool.aci_fabric_id != self.aci_fabric_id
        ):
            errors.setdefault("aci_vlan_pool", []).append(
                _("The assigned VLAN pool must belong to the domain's ACI Fabric.")
            )
        if errors:
            raise ValidationError(errors)

    @property
    def parent_object(self) -> ACIFabric:
        """Return the parent object of the instance."""
        return self.aci_fabric


class ACIRoutedDomain(ACIDomainBaseModel):
    """Routed (L3) domain tying L3Outs to fabric access policy.

    Parented by an ACIFabric and referenced by L3Outs to provide
    their routed connectivity profile.

    Notes:
        Security domain names must be unique within the domain.
    """

    aci_fabric = models.ForeignKey(
        to="netbox_aci_plugin.ACIFabric",
        on_delete=models.PROTECT,
        related_name="aci_routed_domains",
        verbose_name=_("ACI Fabric"),
    )

    # Generic relations
    aci_aaep_domain_bindings = GenericRelation(
        to="netbox_aci_plugin.ACIAAEPDomainBinding",
        content_type_field="aci_domain_object_type",
        object_id_field="aci_domain_object_id",
        related_query_name="aci_routed_domain",
    )

    prerequisite_models: tuple = ("netbox_aci_plugin.ACIFabric",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_fabric", "name"),
                name="%(app_label)s_%(class)s_unique_name_per_aci_fabric",
            ),
        ]
        default_related_name: str = "aci_routed_domains"
        ordering: tuple = ("aci_fabric", "name")
        verbose_name: str = _("ACI Routed Domain")


class ACIPhysicalDomain(ACIDomainBaseModel):
    """Physical domain tying EPGs to fabric access policy.

    Parented by an ACIFabric and referenced by EPG domain bindings to
    provide bare-metal and hypervisor connectivity.

    Notes:
        Security domain names must be unique within the domain.
    """

    aci_fabric = models.ForeignKey(
        to="netbox_aci_plugin.ACIFabric",
        on_delete=models.PROTECT,
        related_name="aci_physical_domains",
        verbose_name=_("ACI Fabric"),
    )
    aci_vlan_pool = models.ForeignKey(
        to="netbox_aci_plugin.ACIVLANPool",
        on_delete=models.PROTECT,
        related_name="aci_physical_domains",
        verbose_name=_("ACI VLAN Pool"),
    )

    # Generic relations
    aci_aaep_domain_bindings = GenericRelation(
        to="netbox_aci_plugin.ACIAAEPDomainBinding",
        content_type_field="aci_domain_object_type",
        object_id_field="aci_domain_object_id",
        related_query_name="aci_physical_domain",
    )
    aci_endpoint_group_domain_bindings = GenericRelation(
        to="netbox_aci_plugin.ACIEndpointGroupDomainBinding",
        content_type_field="aci_domain_object_type",
        object_id_field="aci_domain_object_id",
        related_query_name="aci_physical_domain",
    )

    prerequisite_models: tuple = ("netbox_aci_plugin.ACIFabric",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_fabric", "name"),
                name="%(app_label)s_%(class)s_unique_name_per_aci_fabric",
            ),
        ]
        default_related_name: str = "aci_physical_domains"
        ordering: tuple = ("aci_fabric", "name")
        verbose_name: str = _("ACI Physical Domain")
