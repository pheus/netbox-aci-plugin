# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.fields import MACAddressField
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ...choices import (
    BDMultiDestinationFloodingChoices,
    BDUnknownMulticastChoices,
    BDUnknownUnicastChoices,
)
from ...validators import ACIPolicyNameValidator
from ..base import ACIBaseModel
from .tenants import ACITenant
from .vrfs import ACIVRF


class ACIBridgeDomain(ACIBaseModel):
    """NetBox model for ACI Bridge Domain."""

    aci_tenant = models.ForeignKey(
        to=ACITenant,
        on_delete=models.PROTECT,
        related_name="aci_bridge_domains",
        verbose_name=_("ACI Tenant"),
    )
    aci_vrf = models.ForeignKey(
        to=ACIVRF,
        on_delete=models.PROTECT,
        related_name="aci_bridge_domains",
        verbose_name=_("ACI VRF"),
    )
    advertise_host_routes_enabled = models.BooleanField(
        verbose_name=_("advertise host routes enabled"),
        default=False,
        help_text=_(
            "Advertise associated endpoints as host routes (/32 prefixes) "
            "out of the L3Outs. Default is disabled."
        ),
    )
    arp_flooding_enabled = models.BooleanField(
        verbose_name=_("ARP flooding enabled"),
        default=False,
        help_text=_(
            "Allow Address Resolution Protocol (ARP) to flood in this Bridge "
            "Domain. Default is disabled."
        ),
    )
    clear_remote_mac_enabled = models.BooleanField(
        verbose_name=_("clear remote MAC entries enabled"),
        default=False,
        help_text=_(
            "Enables deletion of MAC EP on remote leaves, when EP gets "
            "deleted from local leaf. Default is disabled."
        ),
    )
    dhcp_labels = ArrayField(
        base_field=models.CharField(
            max_length=64,
            validators=[
                MaxLengthValidator(64),
                ACIPolicyNameValidator,
            ],
        ),
        verbose_name=_("DHCP labels"),
        blank=True,
        null=True,
        help_text=_("Enter labels separated by comma"),
    )
    ep_move_detection_enabled = models.BooleanField(
        verbose_name=_("EP move detection enabled"),
        default=False,
        help_text=_(
            "Enables Gratuitous ARP (GARP) to detect endpoint move. "
            "Default is disabled."
        ),
    )
    igmp_interface_policy_name = models.CharField(
        verbose_name=_("IGMP interface policy name"),
        max_length=64,
        blank=True,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
    )
    igmp_snooping_policy_name = models.CharField(
        verbose_name=_("IGMP snooping policy name"),
        max_length=64,
        blank=True,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
    )
    ip_data_plane_learning_enabled = models.BooleanField(
        verbose_name=_("IP data plane learning enabled"),
        default=True,
        help_text=_(
            "Whether IP data plane learning is enabled for Bridge Domain. "
            "Default is enabled."
        ),
    )
    limit_ip_learn_enabled = models.BooleanField(
        verbose_name=_("limit IP learning to subnet enabled"),
        default=True,
        help_text=_(
            "IP learning is limited to the Bridge Domain's subnets. Default is enabled."
        ),
    )
    mac_address = MACAddressField(
        verbose_name=_("MAC address"),
        blank=True,
        null=True,
        default="00:22:BD:F8:19:FF",
        help_text=_(
            "MAC address of the bridge domain. Default is '00:22:BD:F8:19:FF'."
        ),
    )
    multi_destination_flooding = models.CharField(
        verbose_name=_("multi destination flooding"),
        max_length=11,
        default=BDMultiDestinationFloodingChoices.FLOOD_BD,
        choices=BDMultiDestinationFloodingChoices,
        help_text=_(
            "Forwarding method for L2 multicast, broadcast, and link layer "
            "traffic. Default is 'bd-flood'."
        ),
    )
    pim_ipv4_enabled = models.BooleanField(
        verbose_name=_("PIM (multicast) IPv4 enabled"),
        default=False,
        help_text=_(
            "Multicast routing enabled for the Bridge Domain. Default is disabled."
        ),
    )
    pim_ipv4_destination_filter = models.CharField(
        verbose_name=_("PIM destination filter"),
        max_length=64,
        blank=True,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
    )
    pim_ipv4_source_filter = models.CharField(
        verbose_name=_("PIM source filter"),
        max_length=64,
        blank=True,
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
    )
    pim_ipv6_enabled = models.BooleanField(
        verbose_name=_("PIM (multicast) IPv6 enabled"),
        default=False,
        help_text=_(
            "Multicast routing enabled for the Bridge Domain. Default is disabled."
        ),
    )
    unicast_routing_enabled = models.BooleanField(
        verbose_name=_("unicast routing enabled"),
        default=True,
        help_text=_(
            "Whether IP forwarding is enabled for this Bridge Domain. "
            "Default is enabled."
        ),
    )
    unknown_ipv4_multicast = models.CharField(
        verbose_name=_("unknown IPv4 multicast"),
        max_length=9,
        default=BDUnknownMulticastChoices.UNKNOWN_MULTI_FLOOD,
        choices=BDUnknownMulticastChoices,
        help_text=_(
            "Defines the IPv4 unknown multicast forwarding method. Default is 'flood'."
        ),
    )
    unknown_ipv6_multicast = models.CharField(
        verbose_name=_("unknown IPv6 multicast"),
        max_length=9,
        default=BDUnknownMulticastChoices.UNKNOWN_MULTI_FLOOD,
        choices=BDUnknownMulticastChoices,
        help_text=_(
            "Defines the IPv6 unknown multicast forwarding method. Default is 'flood'."
        ),
    )
    unknown_unicast = models.CharField(
        verbose_name=_("unknown unicast"),
        max_length=5,
        default=BDUnknownUnicastChoices.UNKNOWN_UNI_PROXY,
        choices=BDUnknownUnicastChoices,
        help_text=_(
            "Defines the layer 2 unknown unicast forwarding method. Default is 'proxy'."
        ),
    )
    virtual_mac_address = MACAddressField(
        verbose_name=_("virtual MAC address"),
        blank=True,
        null=True,
        help_text=_(
            "Virtual MAC address of the bridge domain, used when extended to "
            "multiple sites. Default is ''."
        ),
    )

    clone_fields: tuple = ACIBaseModel.clone_fields + (
        "aci_tenant",
        "aci_vrf",
        "advertise_host_routes_enabled",
        "arp_flooding_enabled",
        "clear_remote_mac_enabled",
        "dhcp_labels",
        "ep_move_detection_enabled",
        "igmp_interface_policy_name",
        "igmp_snooping_policy_name",
        "ip_data_plane_learning_enabled",
        "limit_ip_learn_enabled",
        "mac_address",
        "multi_destination_flooding",
        "pim_ipv4_enabled",
        "pim_ipv4_destination_filter",
        "pim_ipv4_source_filter",
        "pim_ipv6_enabled",
        "unicast_routing_enabled",
        "unknown_ipv4_multicast",
        "unknown_ipv6_multicast",
        "unknown_unicast",
        "virtual_mac_address",
    )
    prerequisite_models: tuple = (
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
        ordering: tuple = ("aci_tenant", "aci_vrf", "name")
        verbose_name: str = _("ACI Bridge Domain")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        if self.aci_tenant.name == "common":
            return f"{self.name} ({self.aci_tenant.name})"
        return self.name

    def clean(self) -> None:
        """Override the model's clean method for custom field validation."""
        super().clean()

        # Validate the assigned ACIVRF belongs to either the same ACITenant as
        # the ACIBridgeDomain or to the special ACITenant 'common'
        if (
            self.aci_vrf.aci_tenant != self.aci_tenant
            and self.aci_vrf.aci_tenant.name != "common"
        ):
            raise ValidationError(
                _(
                    "Assigned ACIVRF have to belong to the same ACITenant as "
                    "the ACIBridgeDomain or to the special ACITenant 'common'."
                )
            )

    def save(self, *args, **kwargs) -> None:
        """Save the current instance to the database."""
        # Ensure the assigned ACIVRF belongs to either the same ACITenant as
        # the ACIBridgeDomain or to the special ACITenant 'common'
        if (
            self.aci_vrf.aci_tenant != self.aci_tenant
            and self.aci_vrf.aci_tenant.name != "common"
        ):
            raise ValidationError(
                _(
                    "Assigned ACIVRF have to belong to the same ACITenant as "
                    "the ACIBridgeDomain or to the special ACITenant 'common'."
                )
            )

        super().save(*args, **kwargs)

    @property
    def parent_object(self) -> ACIBaseModel:
        """Return the parent object of the instance."""
        return self.aci_tenant

    def get_multi_destination_flooding_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return BDMultiDestinationFloodingChoices.colors.get(
            self.multi_destination_flooding
        )

    def get_unknown_ipv4_multicast_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return BDUnknownMulticastChoices.colors.get(self.unknown_ipv4_multicast)

    def get_unknown_ipv6_multicast_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return BDUnknownMulticastChoices.colors.get(self.unknown_ipv6_multicast)

    def get_unknown_unicast_color(self) -> str:
        """Return the associated color of choice from the ChoiceSet."""
        return BDUnknownUnicastChoices.colors.get(self.unknown_unicast)


class ACIBridgeDomainSubnet(ACIBaseModel):
    """NetBox model for ACI Bridge Domain Subnet."""

    aci_bridge_domain = models.ForeignKey(
        to=ACIBridgeDomain,
        on_delete=models.CASCADE,
        related_name="aci_bridge_domain_subnets",
        verbose_name=_("ACI Bridge Domain"),
    )
    gateway_ip_address = models.OneToOneField(
        to="ipam.IPAddress",
        on_delete=models.CASCADE,
        related_name="aci_bridge_domain_subnet",
        verbose_name=_("gateway IP address"),
    )
    advertised_externally_enabled = models.BooleanField(
        verbose_name=_("advertised externally enabled"),
        default=False,
        help_text=_(
            "Advertises the subnet to the outside to any associated L3Outs "
            "(public scope). Default is disabled."
        ),
    )
    igmp_querier_enabled = models.BooleanField(
        verbose_name=_("IGMP querier enabled"),
        default=False,
        help_text=_(
            "Treat the gateway IP as an IGMP querier source IP. Default is disabled."
        ),
    )
    ip_data_plane_learning_enabled = models.BooleanField(
        verbose_name=_("IP data plane learning enabled"),
        default=True,
        help_text=_(
            "Whether IP data plane learning is enabled for Bridge Domain "
            "Subnet. Default is enabled."
        ),
    )
    no_default_gateway = models.BooleanField(
        verbose_name=_("no default gateway enabled"),
        default=False,
        help_text=_(
            "Remove default gateway functionality of this gateway address. "
            "Default is disabled."
        ),
    )
    nd_ra_enabled = models.BooleanField(
        verbose_name=_("ND RA enabled"),
        default=True,
        help_text=_(
            "Enables the gateway IP as a IPv6 Neighbor Discovery Router "
            "Advertisement Prefix. Default is enabled."
        ),
    )
    nd_ra_prefix_policy_name = models.CharField(
        verbose_name=_("ND RA prefix policy name"),
        max_length=64,
        blank=True,
        help_text=_(
            "IPv6 Neighbor Discovery Prefix Policy to associate with the Subnet."
        ),
        validators=[
            MaxLengthValidator(64),
            ACIPolicyNameValidator,
        ],
    )
    preferred_ip_address_enabled = models.BooleanField(
        verbose_name=_("preferred IP address enabled"),
        default=False,
        help_text=_(
            "Make this the preferred (primary) IP gateway of the Bridge "
            "Domain. Default is disabled."
        ),
    )
    shared_enabled = models.BooleanField(
        verbose_name=_("shared enabled"),
        default=False,
        help_text=_(
            "Controls communication to the shared VRF (inter-VRF route "
            "leaking). Default is disabled."
        ),
    )
    virtual_ip_enabled = models.BooleanField(
        verbose_name=_("virtual IP enabled"),
        default=False,
        help_text=_("Treat the gateway IP as virtual IP. Default is disabled."),
    )

    clone_fields: tuple = ACIBaseModel.clone_fields + (
        "aci_bridge_domain",
        "advertised_externally_enabled",
        "igmp_querier_enabled",
        "ip_data_plane_learning_enabled",
        "no_default_gateway",
        "nd_ra_enabled",
        "nd_ra_prefix_policy_name",
        "shared_enabled",
        "virtual_ip_enabled",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIBridgeDomain",)

    class Meta:
        constraints: list[models.UniqueConstraint] = [
            models.UniqueConstraint(
                fields=("aci_bridge_domain", "name"),
                name="%(app_label)s_%(class)s_unique_per_aci_bridge_domain",
            ),
            models.UniqueConstraint(
                fields=("aci_bridge_domain", "gateway_ip_address"),
                name="%(app_label)s_%(class)s_unique_per_gateway_ip_address",
            ),
            models.UniqueConstraint(
                fields=("aci_bridge_domain",),
                name="unique_aci_bd_subnet_preferred_ip_per_bridge_domain",
                condition=models.Q(preferred_ip_address_enabled=True),
                violation_error_message=_(
                    "ACI Bridge Domain with a preferred (primary) gateway IP "
                    "address already exists."
                ),
            ),
        ]
        ordering: tuple = ("aci_bridge_domain", "name")
        verbose_name: str = _("ACI Bridge Domain Subnet")

    @property
    def aci_tenant(self) -> ACITenant:
        """Return the ACITenant instance of the related ACIBridgeDomain."""
        return self.aci_bridge_domain.aci_tenant

    @property
    def aci_vrf(self) -> ACIVRF:
        """Return the ACIVRF instance of the related ACIBridgeDomain."""
        return self.aci_bridge_domain.aci_vrf

    @property
    def parent_object(self) -> ACIBaseModel:
        """Return the parent object of the instance."""
        return self.aci_bridge_domain
