# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..base import ACIBaseModel
from .app_profiles import ACIAppProfile
from .tenants import ACITenant
from .vrfs import ACIVRF

#
# ACI Endpoint Security Group
#


class ACIEndpointSecurityGroup(ACIBaseModel):
    """NetBox model for ACI Endpoint Security Group (ESG)."""

    aci_app_profile = models.ForeignKey(
        to=ACIAppProfile,
        on_delete=models.PROTECT,
        verbose_name=_("ACI Application Profile"),
    )
    aci_vrf = models.ForeignKey(
        to=ACIVRF,
        on_delete=models.PROTECT,
        verbose_name=_("ACI VRf"),
    )
    admin_shutdown = models.BooleanField(
        verbose_name=_("Admin state shutdown"),
        default=False,
        help_text=_(
            "Whether the ESG is in shutdown mode removing all policy "
            "configuration from all switches. Default is disabled."
        ),
    )
    intra_esg_isolation_enabled = models.BooleanField(
        verbose_name=_("Intra-ESG isolation enabled"),
        default=False,
        help_text=_(
            "Prevents communication between endpoints in an ESG when "
            "enabled. Default is disabled."
        ),
    )
    preferred_group_member_enabled = models.BooleanField(
        verbose_name=_("Preferred Group member enabled"),
        default=False,
        help_text=_(
            "Whether this ESG is a member of the preferred group and allows "
            "communication without contracts. Default is disabled."
        ),
    )

    clone_fields: tuple = ACIBaseModel.clone_fields + (
        "aci_app_profile",
        "aci_vrf",
        "admin_shutdown",
        "intra_esg_isolation_enabled",
        "preferred_group_member_enabled",
    )
    prerequisite_models: tuple = (
        "netbox_aci_plugin.ACIAppProfile",
        "netbox_aci_plugin.ACIVRF",
    )

    # Generic relations
    aci_contract_relations = GenericRelation(
        to="netbox_aci_plugin.ACIContractRelation",
        content_type_field="aci_object_type",
        object_id_field="aci_object_id",
        related_query_name="aci_endpoint_security_group",
    )

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_app_profile", "name"),
                name="%(app_label)s_%(class)s_unique_name_per_aci_app_profile",
            ),
        ]
        default_related_name: str = "aci_endpoint_security_groups"
        ordering: tuple = ("aci_app_profile", "name")
        verbose_name: str = _("ACI Endpoint Security Group")

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        # Validate the assigned ACIVRF belongs to either the same ACITenant as
        # the ACIAppProfile or to the special ACITenant 'common'
        if (
            self.aci_vrf.aci_tenant != self.aci_app_profile.aci_tenant
            and self.aci_vrf.aci_tenant.name != "common"
        ):
            raise ValidationError(
                _(
                    "Assigned ACIVRF have to belong to the same ACITenant as "
                    "the ACIAppProfile or to the special ACITenant 'common'."
                )
            )

    def save(self, *args, **kwargs) -> None:
        """Saves the current instance to the database."""
        # Ensure the assigned ACIVRF belongs to either the same ACITenant as
        # the ACIAppProfile or to the special ACITenant 'common'
        if (
            self.aci_vrf.aci_tenant != self.aci_app_profile.aci_tenant
            and self.aci_vrf.aci_tenant.name != "common"
        ):
            raise ValidationError(
                _(
                    "Assigned ACIVRF have to belong to the same ACITenant as "
                    "the ACIAppProfile or to the special ACITenant 'common'."
                )
            )

        super().save(*args, **kwargs)

    @property
    def aci_tenant(self) -> ACITenant:
        """Return the ACITenant instance of the related ACIAppProfile."""
        return self.aci_app_profile.aci_tenant

    @property
    def parent_object(self) -> ACIBaseModel:
        """Return the parent object of the instance."""
        return self.aci_app_profile
