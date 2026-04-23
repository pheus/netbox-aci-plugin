# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ipam.fields import IPNetworkField

from ...choices import QualityOfServiceClassChoices, QualityOfServiceDSCPChoices
from ...constants import ACI_NAME_MAX_LEN
from ...validators import ACIPolicyNameOptionalValidator
from ..base import ACITenantBaseModel

if TYPE_CHECKING:
    from core.models import ObjectChange

    from .tenants import ACITenant
    from .vrfs import ACIVRF


class ACIL3Out(ACITenantBaseModel):
    """NetBox model for ACI L3Out."""

    aci_tenant = models.ForeignKey(
        to="netbox_aci_plugin.ACITenant",
        on_delete=models.PROTECT,
        related_name="aci_l3outs",
        verbose_name=_("ACI Tenant"),
    )
    aci_vrf = models.ForeignKey(
        to="netbox_aci_plugin.ACIVRF",
        on_delete=models.PROTECT,
        related_name="aci_l3outs",
        verbose_name=_("ACI VRF"),
    )
    aci_routed_domain = models.ForeignKey(
        to="netbox_aci_plugin.ACIRoutedDomain",
        on_delete=models.PROTECT,
        related_name="aci_l3outs",
        verbose_name=_("ACI Routed Domain"),
    )
    bfd_policy_name = models.CharField(
        verbose_name=_("BFD policy name"),
        max_length=ACI_NAME_MAX_LEN,
        blank=True,
        validators=[ACIPolicyNameOptionalValidator],
    )
    bgp_enabled = models.BooleanField(
        verbose_name=_("BGP enabled"),
        default=False,
        help_text=_("Whether BGP is enabled for this L3Out. Default is disabled."),
    )
    custom_qos_policy_name = models.CharField(
        verbose_name=_("custom QoS policy name"),
        max_length=ACI_NAME_MAX_LEN,
        blank=True,
        validators=[ACIPolicyNameOptionalValidator],
    )
    egress_data_plane_policing_policy_name = models.CharField(
        verbose_name=_("egress data plane policing policy name"),
        max_length=ACI_NAME_MAX_LEN,
        blank=True,
        validators=[ACIPolicyNameOptionalValidator],
    )
    eigrp_enabled = models.BooleanField(
        verbose_name=_("EIGRP enabled"),
        default=False,
        help_text=_("Whether EIGRP is enabled for this L3Out. Default is disabled."),
    )
    eigrp_interface_policy_name = models.CharField(
        verbose_name=_("EIGRP interface policy name"),
        max_length=ACI_NAME_MAX_LEN,
        blank=True,
        validators=[ACIPolicyNameOptionalValidator],
    )
    export_route_control_enforcement_enabled = models.BooleanField(
        verbose_name=_("export route control enforcement enabled"),
        default=True,
        help_text=_(
            "Enables export route control enforcement for the L3Out. "
            "Default is enabled."
        ),
    )
    igmp_interface_policy_name = models.CharField(
        verbose_name=_("IGMP interface policy name"),
        max_length=ACI_NAME_MAX_LEN,
        blank=True,
        validators=[ACIPolicyNameOptionalValidator],
    )
    import_route_control_enforcement_enabled = models.BooleanField(
        verbose_name=_("import route control enforcement enabled"),
        default=False,
        help_text=_(
            "Enables import route control enforcement for the L3Out. "
            "Default is disabled."
        ),
    )
    ingress_data_plane_policing_policy_name = models.CharField(
        verbose_name=_("ingress data plane policing policy name"),
        max_length=ACI_NAME_MAX_LEN,
        blank=True,
        validators=[ACIPolicyNameOptionalValidator],
    )
    interleak_route_map_name = models.CharField(
        verbose_name=_("interleak route map name"),
        max_length=ACI_NAME_MAX_LEN,
        blank=True,
        validators=[ACIPolicyNameOptionalValidator],
    )
    l3_multicast_ipv4_enabled = models.BooleanField(
        verbose_name=_("L3 multicast IPv4 enabled"),
        default=False,
        help_text=_(
            "Whether IPv4 Layer 3 multicast is enabled for this L3Out. "
            "Default is disabled."
        ),
    )
    l3_multicast_ipv6_enabled = models.BooleanField(
        verbose_name=_("L3 multicast IPv6 enabled"),
        default=False,
        help_text=_(
            "Whether IPv6 Layer 3 multicast is enabled for this L3Out. "
            "Default is disabled."
        ),
    )
    # Plugin-side marker; APIC derives Multi-Pod from bgpExtP on infra L3Outs.
    multipod_enabled = models.BooleanField(
        verbose_name=_("Multi-Pod enabled"),
        default=False,
        help_text=_(
            "Designates this infra Tenant L3Out as used for ACI Multi-Pod. "
            "Default is disabled."
        ),
    )
    ospf_enabled = models.BooleanField(
        verbose_name=_("OSPF enabled"),
        default=False,
        help_text=_("Whether OSPF is enabled for this L3Out. Default is disabled."),
    )
    ospf_external_policy_name = models.CharField(
        verbose_name=_("OSPF external policy name"),
        max_length=ACI_NAME_MAX_LEN,
        blank=True,
        validators=[ACIPolicyNameOptionalValidator],
    )
    pim_policy_name = models.CharField(
        verbose_name=_("PIM policy name"),
        max_length=ACI_NAME_MAX_LEN,
        blank=True,
        validators=[ACIPolicyNameOptionalValidator],
    )
    target_dscp = models.CharField(
        verbose_name=_("target DSCP"),
        max_length=11,
        default=QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED,
        choices=QualityOfServiceDSCPChoices,
        help_text=_(
            "Rewrites the DSCP value of incoming traffic to the selected value. "
            "Default is 'unspecified'."
        ),
    )

    clone_fields: tuple = ACITenantBaseModel.clone_fields + (
        "aci_tenant",
        "aci_vrf",
        "aci_routed_domain",
        "bfd_policy_name",
        "bgp_enabled",
        "custom_qos_policy_name",
        "egress_data_plane_policing_policy_name",
        "eigrp_enabled",
        "eigrp_interface_policy_name",
        "export_route_control_enforcement_enabled",
        "igmp_interface_policy_name",
        "import_route_control_enforcement_enabled",
        "ingress_data_plane_policing_policy_name",
        "interleak_route_map_name",
        "l3_multicast_ipv4_enabled",
        "l3_multicast_ipv6_enabled",
        "multipod_enabled",
        "ospf_enabled",
        "ospf_external_policy_name",
        "pim_policy_name",
        "target_dscp",
    )
    prerequisite_models: tuple = (
        "netbox_aci_plugin.ACIRoutedDomain",
        "netbox_aci_plugin.ACITenant",
        "netbox_aci_plugin.ACIVRF",
    )

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_tenant", "name"),
                name="%(app_label)s_%(class)s_unique_per_aci_tenant",
            ),
        ]
        ordering: tuple = ("aci_tenant", "name")
        verbose_name: str = _("ACI L3Out")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        if self.aci_tenant.name == "common":
            return f"{self.name} ({self.aci_tenant.name})"
        return self.name

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()
        errors = {}

        if self.aci_vrf_id and self.aci_tenant_id:
            # Ensure that the assigned ACI VRF is part of the same
            # ACI Fabric as the ACI L3Out.
            if self.aci_vrf.aci_tenant.aci_fabric != self.aci_tenant.aci_fabric:
                errors.setdefault("aci_vrf", []).append(
                    _(
                        "The assigned ACI VRF must belong to the same "
                        "ACI Fabric as the ACI L3Out."
                    )
                )

            # Ensure that the assigned ACI VRF is part of the same
            # ACI Tenant as the ACI L3Out, or the ACI Tenant 'common'.
            if (
                self.aci_vrf.aci_tenant != self.aci_tenant
                and self.aci_vrf.aci_tenant.name != "common"
            ):
                errors.setdefault("aci_vrf", []).append(
                    _(
                        "The assigned ACI VRF must belong to the same "
                        "ACI Tenant as the ACI L3Out, or to the "
                        "ACI Tenant 'common'."
                    )
                )

        # Ensure that the assigned ACI Routed Domain is part of the same
        # ACI Fabric as the ACI L3Out.
        if (
            self.aci_routed_domain_id
            and self.aci_tenant_id
            and self.aci_routed_domain.aci_fabric != self.aci_tenant.aci_fabric
        ):
            errors.setdefault("aci_routed_domain", []).append(
                _(
                    "The assigned ACI Routed Domain must belong to the same "
                    "ACI Fabric as the ACI L3Out."
                )
            )

        # Ensure that Multi-Pod is only enabled for L3Outs in the
        # ACI Tenant 'infra'.
        if (
            self.multipod_enabled
            and self.aci_tenant_id
            and self.aci_tenant.name != "infra"
        ):
            errors.setdefault("multipod_enabled", []).append(
                _("Multi-Pod can only be enabled for L3Outs in the 'infra' ACI Tenant.")
            )

        # Ensure that EIGRP is not combined with BGP or OSPF on the same
        # ACI L3Out.
        if self.eigrp_enabled and (self.bgp_enabled or self.ospf_enabled):
            errors.setdefault("eigrp_enabled", []).append(
                _(
                    "EIGRP cannot be enabled together with BGP or OSPF "
                    "on the same ACI L3Out."
                )
            )

        # Ensure that import route control enforcement is only enabled
        # for BGP or OSPF L3Outs.
        if self.import_route_control_enforcement_enabled and not (
            self.bgp_enabled or self.ospf_enabled
        ):
            errors.setdefault("import_route_control_enforcement_enabled", []).append(
                _(
                    "Import route control enforcement requires BGP or OSPF "
                    "to be enabled for the ACI L3Out."
                )
            )

        # Ensure that an OSPF external policy is only assigned when OSPF
        # is enabled.
        if self.ospf_external_policy_name and not self.ospf_enabled:
            errors.setdefault("ospf_external_policy_name", []).append(
                _(
                    "An OSPF external policy can only be assigned when "
                    "OSPF is enabled for the ACI L3Out."
                )
            )

        # Ensure that an EIGRP interface policy is only assigned when EIGRP
        # is enabled.
        if self.eigrp_interface_policy_name and not self.eigrp_enabled:
            errors.setdefault("eigrp_interface_policy_name", []).append(
                _(
                    "An EIGRP interface policy can only be assigned when "
                    "EIGRP is enabled for the ACI L3Out."
                )
            )

        # Ensure that a PIM policy is only assigned when L3 multicast is
        # enabled.
        if self.pim_policy_name and not (
            self.l3_multicast_ipv4_enabled or self.l3_multicast_ipv6_enabled
        ):
            errors.setdefault("pim_policy_name", []).append(
                _(
                    "A PIM policy can only be assigned when L3 multicast "
                    "IPv4 or IPv6 is enabled for the ACI L3Out."
                )
            )

        # Ensure that an IGMP interface policy is only assigned when L3
        # multicast IPv4 is enabled.
        if self.igmp_interface_policy_name and not self.l3_multicast_ipv4_enabled:
            errors.setdefault("igmp_interface_policy_name", []).append(
                _(
                    "An IGMP interface policy can only be assigned when "
                    "L3 multicast IPv4 is enabled for the ACI L3Out."
                )
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        """Save the current instance to the database."""
        if self.aci_vrf_id and self.aci_tenant_id:
            if self.aci_vrf.aci_tenant.aci_fabric != self.aci_tenant.aci_fabric:
                raise ValidationError(
                    _(
                        "The assigned ACI VRF must belong to the same "
                        "ACI Fabric as the ACI L3Out."
                    )
                )
            if (
                self.aci_vrf.aci_tenant != self.aci_tenant
                and self.aci_vrf.aci_tenant.name != "common"
            ):
                raise ValidationError(
                    _(
                        "The assigned ACI VRF must belong to the same "
                        "ACI Tenant as the ACI L3Out, or to the "
                        "ACI Tenant 'common'."
                    )
                )
        if (
            self.aci_routed_domain_id
            and self.aci_tenant_id
            and self.aci_routed_domain.aci_fabric != self.aci_tenant.aci_fabric
        ):
            raise ValidationError(
                _(
                    "The assigned ACI Routed Domain must belong to the same "
                    "ACI Fabric as the ACI L3Out."
                )
            )
        if (
            self.multipod_enabled
            and self.aci_tenant_id
            and self.aci_tenant.name != "infra"
        ):
            raise ValidationError(
                _(
                    "The ACI L3Out must belong to the ACI Tenant 'infra' "
                    "when multipod is enabled."
                )
            )

        super().save(*args, **kwargs)

    @property
    def parent_object(self) -> ACITenantBaseModel:
        """Return the parent object of the instance."""
        return self.aci_tenant

    def get_target_dscp_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return QualityOfServiceDSCPChoices.colors.get(self.target_dscp)


class ACIExternalEndpointGroup(ACITenantBaseModel):
    """NetBox model for ACI External Endpoint Group."""

    aci_l3out = models.ForeignKey(
        to="netbox_aci_plugin.ACIL3Out",
        on_delete=models.CASCADE,
        related_name="aci_external_endpoint_groups",
        verbose_name=_("ACI L3Out"),
    )
    qos_class = models.CharField(
        verbose_name=_("QoS class"),
        max_length=11,
        default=QualityOfServiceClassChoices.CLASS_UNSPECIFIED,
        choices=QualityOfServiceClassChoices,
        help_text=_(
            "Specifies the priority handling for traffic sourced by the "
            "External EPG. Default is 'unspecified'."
        ),
    )
    preferred_group_member_enabled = models.BooleanField(
        verbose_name=_("preferred group member enabled"),
        default=False,
        help_text=_(
            "Whether this External EPG is a member of the preferred group. "
            "Default is disabled."
        ),
    )
    target_dscp = models.CharField(
        verbose_name=_("target DSCP"),
        max_length=11,
        default=QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED,
        choices=QualityOfServiceDSCPChoices,
        help_text=_(
            "Rewrites the DSCP value of incoming traffic to the selected value. "
            "Default is 'unspecified'."
        ),
    )

    # Generic relations
    aci_contract_relations = GenericRelation(
        to="netbox_aci_plugin.ACIContractRelation",
        content_type_field="aci_object_type",
        object_id_field="aci_object_id",
        related_query_name="aci_external_endpoint_group",
    )

    clone_fields: tuple = ACITenantBaseModel.clone_fields + (
        "aci_l3out",
        "qos_class",
        "preferred_group_member_enabled",
        "target_dscp",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIL3Out",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_l3out", "name"),
                name="%(app_label)s_%(class)s_unique_per_l3out",
            ),
        ]
        ordering: tuple = ("aci_l3out", "name")
        verbose_name: str = _("ACI External Endpoint Group")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        if self.aci_l3out.aci_tenant.name == "common":
            return f"{self.name} ({self.aci_l3out.name}, common)"
        return f"{self.name} ({self.aci_l3out.name})"

    def to_objectchange(self, action) -> ObjectChange:
        """Return an ObjectChange for the change made to an instance."""
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.aci_l3out
        return objectchange

    @property
    def aci_tenant(self) -> ACITenant:
        """Return the ACITenant instance of related ACIL3Out."""
        return self.aci_l3out.aci_tenant

    @property
    def aci_vrf(self) -> ACIVRF:
        """Return the ACIVRF instance of related ACIL3Out."""
        return self.aci_l3out.aci_vrf

    @property
    def parent_object(self) -> ACITenantBaseModel:
        """Return the parent object of the instance."""
        return self.aci_l3out

    def get_qos_class_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return QualityOfServiceClassChoices.colors.get(self.qos_class)

    def get_target_dscp_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return QualityOfServiceDSCPChoices.colors.get(self.target_dscp)


class ACIExternalSubnet(ACITenantBaseModel):
    """NetBox model for ACI External Subnet."""

    aci_external_endpoint_group = models.ForeignKey(
        to="netbox_aci_plugin.ACIExternalEndpointGroup",
        on_delete=models.CASCADE,
        related_name="aci_external_subnets",
        verbose_name=_("ACI External Endpoint Group"),
    )
    matched_prefix = IPNetworkField(
        verbose_name=_("matched prefix"),
        db_index=True,
        help_text=_(
            "IPv4 or IPv6 prefix matched by this external subnet. "
            "Populated by sync_matched_prefix() from the linked NetBox "
            "prefix when one is selected; otherwise required directly."
        ),
    )
    nb_prefix = models.ForeignKey(
        to="ipam.Prefix",
        on_delete=models.PROTECT,
        related_name="aci_external_subnets",
        verbose_name=_("NetBox prefix"),
        blank=True,
        null=True,
        help_text=_(
            "Optional NetBox prefix used as the matched prefix for this "
            "external subnet."
        ),
    )
    import_route_control_enabled = models.BooleanField(
        verbose_name=_("import route control enabled"),
        default=False,
        help_text=_(
            "Classifies this external subnet for import route control. "
            "Default is disabled."
        ),
    )
    export_route_control_enabled = models.BooleanField(
        verbose_name=_("export route control enabled"),
        default=False,
        help_text=_(
            "Classifies this external subnet for export route control. "
            "Default is disabled."
        ),
    )
    shared_route_control_enabled = models.BooleanField(
        verbose_name=_("shared route control enabled"),
        default=False,
        help_text=_(
            "Classifies this external subnet for shared route control. "
            "Default is disabled."
        ),
    )
    import_security_enabled = models.BooleanField(
        verbose_name=_("import security enabled"),
        default=True,
        help_text=_(
            "Classifies this external subnet for security import. Default is enabled."
        ),
    )
    shared_security_enabled = models.BooleanField(
        verbose_name=_("shared security enabled"),
        default=False,
        help_text=_(
            "Classifies this external subnet for shared security import. "
            "Default is disabled."
        ),
    )
    aggregate_import_route_control_enabled = models.BooleanField(
        verbose_name=_("aggregate import route control enabled"),
        default=False,
        help_text=_(
            "Aggregates import route control prefixes for this external subnet. "
            "Default is disabled."
        ),
    )
    aggregate_export_route_control_enabled = models.BooleanField(
        verbose_name=_("aggregate export route control enabled"),
        default=False,
        help_text=_(
            "Aggregates export route control prefixes for this external subnet. "
            "Default is disabled."
        ),
    )
    aggregate_shared_route_control_enabled = models.BooleanField(
        verbose_name=_("aggregate shared route control enabled"),
        default=False,
        help_text=_(
            "Aggregates shared route control prefixes for this external subnet. "
            "Default is disabled."
        ),
    )
    bgp_route_summarization_enabled = models.BooleanField(
        verbose_name=_("BGP route summarization enabled"),
        default=False,
        help_text=_(
            "Whether BGP route summarization is enabled for this external subnet. "
            "Default is disabled."
        ),
    )
    bgp_route_summarization_policy_name = models.CharField(
        verbose_name=_("BGP route summarization policy name"),
        max_length=ACI_NAME_MAX_LEN,
        blank=True,
        validators=[ACIPolicyNameOptionalValidator],
    )
    ospf_route_summarization_enabled = models.BooleanField(
        verbose_name=_("OSPF route summarization enabled"),
        default=False,
        help_text=_(
            "Whether OSPF route summarization is enabled for this external subnet. "
            "Default is disabled."
        ),
    )
    ospf_route_summarization_policy_name = models.CharField(
        verbose_name=_("OSPF route summarization policy name"),
        max_length=ACI_NAME_MAX_LEN,
        blank=True,
        validators=[ACIPolicyNameOptionalValidator],
    )
    eigrp_route_summarization_enabled = models.BooleanField(
        verbose_name=_("EIGRP route summarization enabled"),
        default=False,
        help_text=_(
            "Whether EIGRP route summarization is enabled for this external subnet. "
            "Default is disabled."
        ),
    )
    clone_fields: tuple = ACITenantBaseModel.clone_fields + (
        "aci_external_endpoint_group",
        "matched_prefix",
        "nb_prefix",
        "import_route_control_enabled",
        "export_route_control_enabled",
        "shared_route_control_enabled",
        "import_security_enabled",
        "shared_security_enabled",
        "aggregate_import_route_control_enabled",
        "aggregate_export_route_control_enabled",
        "aggregate_shared_route_control_enabled",
        "bgp_route_summarization_enabled",
        "bgp_route_summarization_policy_name",
        "ospf_route_summarization_enabled",
        "ospf_route_summarization_policy_name",
        "eigrp_route_summarization_enabled",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIExternalEndpointGroup",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_external_endpoint_group", "name"),
                name="%(app_label)s_%(class)s_unique_per_ext_epg",
            ),
            models.UniqueConstraint(
                fields=("aci_external_endpoint_group", "matched_prefix"),
                name="%(app_label)s_%(class)s_unique_matched_prefix_ext_epg",
            ),
        ]
        ordering: tuple = ("aci_external_endpoint_group", "matched_prefix", "name")
        verbose_name: str = _("ACI External Subnet")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return f"{self.matched_prefix} ({self.aci_external_endpoint_group.name})"

    def clean_fields(self, exclude=None) -> None:
        """Sync matched prefix before Django required-field validation."""
        self.sync_matched_prefix()
        super().clean_fields(exclude=exclude)

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        errors = {}

        if self.matched_prefix is None:
            errors.setdefault("matched_prefix", []).append(
                _("A matched prefix is required.")
            )
            raise ValidationError(errors)

        # Ensure that the selected NetBox Prefix belongs to the same NetBox
        # VRF as the NetBox VRF mapped to the parent ACI VRF.
        if (
            self.nb_prefix_id
            and self.aci_external_endpoint_group_id
            and self.nb_prefix.vrf_id != self.aci_vrf.nb_vrf_id
        ):
            errors.setdefault("nb_prefix", []).append(
                _(
                    "The selected prefix must belong to the same NetBox VRF "
                    "as the ACI VRF mapped to this L3Out."
                )
            )

        if self.aci_external_endpoint_group_id:
            aci_l3out = self.aci_l3out

            # Import Route Control Subnet is only meaningful when Import Route
            # Control Enforcement is enabled on the parent L3Out. In APIC this
            # is an L3Out-level option and is supported for BGP and OSPF, but
            # not for EIGRP.
            if (
                self.import_route_control_enabled
                and not aci_l3out.import_route_control_enforcement_enabled
            ):
                errors.setdefault("import_route_control_enabled", []).append(
                    _(
                        "Import route control can only be enabled when import "
                        "route control enforcement is enabled on the parent "
                        "ACI L3Out."
                    )
                )

            if (
                self.import_route_control_enabled
                and aci_l3out.eigrp_enabled
                and not (aci_l3out.bgp_enabled or aci_l3out.ospf_enabled)
            ):
                errors.setdefault("import_route_control_enabled", []).append(
                    _(
                        "Import route control is supported for BGP and OSPF "
                        "L3Outs, but not for EIGRP-only L3Outs."
                    )
                )

            # Aggregate Import and Aggregate Export are refinements of their
            # matching route-control scopes. They must not be enabled without
            # the corresponding base route-control flag.
            if (
                self.aggregate_import_route_control_enabled
                and not self.import_route_control_enabled
            ):
                errors.setdefault(
                    "aggregate_import_route_control_enabled",
                    [],
                ).append(
                    _(
                        "Aggregate import route control requires import route "
                        "control to be enabled."
                    )
                )

            if (
                self.aggregate_export_route_control_enabled
                and not self.export_route_control_enabled
            ):
                errors.setdefault(
                    "aggregate_export_route_control_enabled",
                    [],
                ).append(
                    _(
                        "Aggregate export route control requires export route "
                        "control to be enabled."
                    )
                )

            if (
                self.aggregate_shared_route_control_enabled
                and not self.shared_route_control_enabled
            ):
                errors.setdefault(
                    "aggregate_shared_route_control_enabled",
                    [],
                ).append(
                    _(
                        "Aggregate shared route control requires shared route "
                        "control to be enabled."
                    )
                )

            # ACI supports Aggregate Import and Aggregate Export only for the
            # default-route subnet. Treat both IPv4 0.0.0.0/0 and IPv6 ::/0 as
            # default routes by checking prefix length 0.
            if (
                self.aggregate_import_route_control_enabled
                and not self._is_default_route()
            ):
                errors.setdefault(
                    "aggregate_import_route_control_enabled",
                    [],
                ).append(
                    _(
                        "Aggregate import route control can only be enabled "
                        "for a default-route prefix."
                    )
                )

            if (
                self.aggregate_export_route_control_enabled
                and not self._is_default_route()
            ):
                errors.setdefault(
                    "aggregate_export_route_control_enabled",
                    [],
                ).append(
                    _(
                        "Aggregate export route control can only be enabled "
                        "for a default-route prefix."
                    )
                )

            # Shared Security Import leaks the prefix-to-pcTag mapping for
            # shared L3Out contracts. ACI requires the subnet to be classified
            # as an External Subnet for the External EPG first; otherwise
            # the original VRF does not know which External EPG the prefix
            # belongs to.
            if self.shared_security_enabled and not self.import_security_enabled:
                errors.setdefault("shared_security_enabled", []).append(
                    _(
                        "Shared security can only be enabled when import "
                        "security is enabled."
                    )
                )

            # Shared Security Import is normally configured together
            # with Shared Route Control, but it may also be more
            # granular than the Shared Route Control prefix. It must
            # not be less granular.
            if (
                self.shared_security_enabled
                and not self._has_shared_route_control_covering_prefix()
            ):
                errors.setdefault("shared_security_enabled", []).append(
                    _(
                        "Shared security requires shared route control on the "
                        "same subnet, or on a less-specific subnet in the same "
                        "ACI External Endpoint Group."
                    )
                )

            route_summarization_fields = (
                "bgp_route_summarization_enabled",
                "ospf_route_summarization_enabled",
                "eigrp_route_summarization_enabled",
            )
            enabled_route_summarizations = [
                field for field in route_summarization_fields if getattr(self, field)
            ]

            # l3extSubnet has a single l3extRsSubnetToRtSumm relation. Net as
            # Code also resolves the target policy with BGP > OSPF > EIGRP
            # precedence if multiple booleans are true. Reject that ambiguity
            # in NetBox instead of silently ignoring later selections.
            if len(enabled_route_summarizations) > 1:
                for field in enabled_route_summarizations:
                    errors.setdefault(field, []).append(
                        _(
                            "Only one route summarization type can be enabled "
                            "on the same ACI External Subnet."
                        )
                    )

            if enabled_route_summarizations:
                # Route summarization under an External EPG is used to
                # advertise a summarized prefix toward L3Out peers.
                # APIC's GUI workflow enables this through Export Route
                # Control Subnet.
                if not self.export_route_control_enabled:
                    errors.setdefault("export_route_control_enabled", []).append(
                        _(
                            "Export route control must be enabled when route "
                            "summarization is enabled."
                        )
                    )

                # Cisco's GUI procedure for External EPG route
                # summarization also marks the subnet as External
                # Subnet for the External EPG. Keep this as a hard
                # validation so the summarized prefix remains tied to
                # the External EPG for policy classification.
                if not self.import_security_enabled:
                    errors.setdefault("import_security_enabled", []).append(
                        _(
                            "Import security must be enabled when route "
                            "summarization is enabled."
                        )
                    )

            if self.bgp_route_summarization_enabled and not aci_l3out.bgp_enabled:
                errors.setdefault("bgp_route_summarization_enabled", []).append(
                    _(
                        "BGP route summarization can only be enabled when BGP "
                        "is enabled on the parent ACI L3Out."
                    )
                )

            if self.ospf_route_summarization_enabled and not aci_l3out.ospf_enabled:
                errors.setdefault("ospf_route_summarization_enabled", []).append(
                    _(
                        "OSPF route summarization can only be enabled when "
                        "OSPF is enabled on the parent ACI L3Out."
                    )
                )

            if self.eigrp_route_summarization_enabled and not aci_l3out.eigrp_enabled:
                errors.setdefault("eigrp_route_summarization_enabled", []).append(
                    _(
                        "EIGRP route summarization can only be enabled when "
                        "EIGRP is enabled on the parent ACI L3Out."
                    )
                )

            # Policy name fields should not be populated when the
            # matching route summarization type is disabled.
            if (
                self.bgp_route_summarization_policy_name
                and not self.bgp_route_summarization_enabled
            ):
                errors.setdefault(
                    "bgp_route_summarization_policy_name",
                    [],
                ).append(
                    _(
                        "A BGP route summarization policy can only be assigned "
                        "when BGP route summarization is enabled."
                    )
                )

            if (
                self.ospf_route_summarization_policy_name
                and not self.ospf_route_summarization_enabled
            ):
                errors.setdefault(
                    "ospf_route_summarization_policy_name",
                    [],
                ).append(
                    _(
                        "An OSPF route summarization policy can only be assigned "
                        "when OSPF route summarization is enabled."
                    )
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        """Sync matched prefix before saving."""
        self.sync_matched_prefix()

        update_fields = kwargs.get("update_fields")
        if self.nb_prefix_id and update_fields is not None:
            kwargs["update_fields"] = set(update_fields) | {"matched_prefix"}

        super().save(*args, **kwargs)

    def to_objectchange(self, action) -> ObjectChange:
        """Return an ObjectChange for the change made to an instance."""
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.aci_external_endpoint_group
        return objectchange

    @property
    def aci_l3out(self) -> ACIL3Out:
        """Return the ACIL3Out instance of related External EPG."""
        return self.aci_external_endpoint_group.aci_l3out

    @property
    def aci_tenant(self) -> ACITenant:
        """Return the ACITenant instance of related External EPG."""
        return self.aci_external_endpoint_group.aci_tenant

    @property
    def aci_vrf(self) -> ACIVRF:
        """Return the ACIVRF instance of related External EPG."""
        return self.aci_external_endpoint_group.aci_vrf

    @property
    def parent_object(self) -> ACITenantBaseModel:
        """Return the parent object of the instance."""
        return self.aci_external_endpoint_group

    @property
    def prefix_source(self) -> str:
        """Return the prefix source of the instance."""
        return "netbox" if self.nb_prefix_id else "direct"

    def sync_matched_prefix(self) -> None:
        """Sync the matched prefix from the NetBox Prefix model."""
        if self.nb_prefix_id:
            self.matched_prefix = self.nb_prefix.prefix

    sync_matched_prefix.alters_data = True

    @staticmethod
    def _prefix_contains(parent_prefix, child_prefix) -> bool:
        """Return True if parent_prefix contains child_prefix."""
        return (
            parent_prefix.version == child_prefix.version
            and parent_prefix.first <= child_prefix.first
            and parent_prefix.last >= child_prefix.last
        )

    def _is_default_route(self) -> bool:
        """Return True if the matched prefix is a default route."""
        return bool(self.matched_prefix and self.matched_prefix.prefixlen == 0)

    def _has_shared_route_control_covering_prefix(self) -> bool:
        """Return True if Shared Route Control covers this subnet.

        ACI allows Shared Security Import to be more granular than
        Shared Route Control. For example, 10.0.0.0/8 can be marked
        for Shared Route Control, while 10.1.0.0/16 and 10.2.0.0/16
        are marked for Shared Security Import.

        Shared Security Import must not be less granular than the corresponding
        Shared Route Control prefix.
        """
        if not self.matched_prefix or not self.aci_external_endpoint_group_id:
            return False

        if self.shared_route_control_enabled:
            return True

        shared_route_control_subnets = type(self).objects.filter(
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            shared_route_control_enabled=True,
        )

        if self.pk:
            shared_route_control_subnets = shared_route_control_subnets.exclude(
                pk=self.pk,
            )

        for subnet in shared_route_control_subnets:
            if self._prefix_contains(subnet.matched_prefix, self.matched_prefix):
                return True

        return False
