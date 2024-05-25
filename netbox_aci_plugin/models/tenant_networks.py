# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.fields import MACAddressField
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxLengthValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel

from ..choices import (
    BDMultiDestinationFloodingChoices,
    BDUnknownMulticastChoices,
    BDUnknownUnicastChoices,
    VRFPCEnforcementDirectionChoices,
    VRFPCEnforcementPreferenceChoices,
)
from ..models.tenants import ACITenant
from ..validators import ACIPolicyDescriptionValidator, ACIPolicyNameValidator


class ACIVRF(NetBoxModel):
    """NetBox model for ACI VRF."""

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
    aci_tenant = models.ForeignKey(
        to=ACITenant,
        on_delete=models.PROTECT,
        related_name="aci_vrfs",
        verbose_name=_("ACI Tenant"),
    )
    nb_tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("NetBox tenant"),
        blank=True,
        null=True,
    )
    nb_vrf = models.ForeignKey(
        to="ipam.VRF",
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("NetBox VRF"),
        blank=True,
        null=True,
    )
    bd_enforcement_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Bridge Domain enforcement enabled"),
        help_text=_(
            "Allow EP to ping only gateways within associated bridge domain. "
            "Default is disabled."
        ),
    )
    dns_labels = ArrayField(
        base_field=models.CharField(
            max_length=64,
            validators=[
                MaxLengthValidator(64),
                ACIPolicyNameValidator,
            ],
        ),
        verbose_name=_("DNS labels"),
        blank=True,
        null=True,
        help_text=_("Enter labels separated by comma"),
    )
    ip_data_plane_learning_enabled = models.BooleanField(
        verbose_name=_("IP data plane learning enabled"),
        default=True,
        help_text=_(
            "Whether IP data plane learning is enabled for VRF. "
            "Default is enabled."
        ),
    )
    pc_enforcement_direction = models.CharField(
        verbose_name=_("policy control enforcement direction"),
        max_length=8,
        default=VRFPCEnforcementDirectionChoices.DIR_INGRESS,
        choices=VRFPCEnforcementDirectionChoices,
        help_text=_(
            "Controls policy enforcement direction for VRF. "
            "Default is 'ingress'."
        ),
    )
    pc_enforcement_preference = models.CharField(
        verbose_name=_("policy control enforcement preference"),
        max_length=10,
        default=VRFPCEnforcementPreferenceChoices.PREF_ENFORCED,
        choices=VRFPCEnforcementPreferenceChoices,
        help_text=_(
            "Controls policy enforcement preference for VRF. "
            "Default is 'enforced'."
        ),
    )
    pim_ipv4_enabled = models.BooleanField(
        verbose_name=_("PIM (multicast) IPv4 enabled"),
        default=False,
        help_text=_(
            "Multicast routing enabled for the VRF. Default is disabled."
        ),
    )
    pim_ipv6_enabled = models.BooleanField(
        verbose_name=_("PIM (multicast) IPv6 enabled"),
        default=False,
        help_text=_(
            "Multicast routing enabled for the VRF. Default is disabled."
        ),
    )
    preferred_group_enabled = models.BooleanField(
        verbose_name=_("preferred group enabled"),
        default=False,
        help_text=_(
            "Whether preferred group feature is enabled for the VRF. "
            "Default is disabled."
        ),
    )
    comments = models.TextField(
        verbose_name=_("comments"),
        blank=True,
    )

    clone_fields: tuple = (
        "description",
        "aci_tenant",
        "nb_tenant",
        "nb_vrf",
        "bd_enforcement_enabled",
        "dns_labels",
        "ip_data_plane_learning_enabled",
        "pc_enforcement_direction",
        "pc_enforcement_preference",
        "pim_ipv4_enabled",
        "pim_ipv6_enabled",
        "preferred_group_enabled",
    )
    prerequisite_models: tuple = ("netbox_aci_plugin.ACITenant",)

    class Meta:
        ordering: tuple = ("aci_tenant", "name")
        unique_together: tuple = ("aci_tenant", "name")
        verbose_name: str = _("ACI VRF")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return self.name

    def get_absolute_url(self) -> str:
        """Return the absolute URL of the instance."""
        return reverse("plugins:netbox_aci_plugin:acivrf", args=[self.pk])

    def get_pc_enforcement_direction_color(self):
        """Return the associated color of choice from the ChoiceSet."""
        return VRFPCEnforcementDirectionChoices.colors.get(
            self.pc_enforcement_direction
        )

    def get_pc_enforcement_preference_color(self):
        """Return the associated color of choice from the ChoiceSet."""
        return VRFPCEnforcementPreferenceChoices.colors.get(
            self.pc_enforcement_preference
        )


class ACIBridgeDomain(NetBoxModel):
    """NetBox model for ACI Bridge Domain."""

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
    aci_vrf = models.ForeignKey(
        to=ACIVRF,
        on_delete=models.PROTECT,
        related_name="aci_bridge_domains",
        verbose_name=_("ACI VRF"),
    )
    nb_tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("NetBox tenant"),
        blank=True,
        null=True,
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
            "IP learning is limited to the Bridge Domain's subnets. "
            "Default is enabled."
        ),
    )
    mac_address = MACAddressField(
        verbose_name=_("MAC address"),
        blank=True,
        null=True,
        default="00:22:BD:F8:19:FF",
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
            "Multicast routing enabled for the Bridge Domain. "
            "Default is disabled."
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
        verbose_name=_("PIM destination filter"),
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
            "Multicast routing enabled for the Bridge Domain. "
            "Default is disabled."
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
            "Defines the IPv4 unknown multicast forwarding method. "
            "Default is 'flood'."
        ),
    )
    unknown_ipv6_multicast = models.CharField(
        verbose_name=_("unknown IPv6 multicast"),
        max_length=9,
        default=BDUnknownMulticastChoices.UNKNOWN_MULTI_FLOOD,
        choices=BDUnknownMulticastChoices,
        help_text=_(
            "Defines the IPv6 unknown multicast forwarding method. "
            "Default is 'flood'."
        ),
    )
    unknown_unicast = models.CharField(
        verbose_name=_("unknown unicast"),
        max_length=5,
        default=BDUnknownUnicastChoices.UNKNOWN_UNI_PROXY,
        choices=BDUnknownUnicastChoices,
        help_text=_(
            "Defines the layer 2 unknown unicast forwarding method. "
            "Default is 'proxy'."
        ),
    )
    virtual_mac_address = MACAddressField(
        verbose_name=_("virtual MAC address"),
        blank=True,
        null=True,
    )
    comments = models.TextField(
        verbose_name=_("comments"),
        blank=True,
    )

    clone_fields: tuple = (
        "description",
        "aci_vrf",
        "nb_tenant",
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
    prerequisite_models: tuple = ("netbox_aci_plugin.ACIVRF",)

    class Meta:
        ordering: tuple = ("aci_vrf", "name")
        unique_together: tuple = ("aci_vrf", "name")
        verbose_name: str = _("ACI Bridge Domain")

    def __str__(self) -> str:
        """Return string representation of the instance."""
        return self.name

    @property
    def aci_tenant(self) -> ACITenant:
        """Return the ACITenant instance of related ACIVRF."""
        return self.aci_vrf.aci_tenant

    def get_absolute_url(self) -> str:
        """Return the absolute URL of the instance."""
        return reverse(
            "plugins:netbox_aci_plugin:acibridgedomain", args=[self.pk]
        )

    def get_multi_destination_flooding_color(self):
        """Return the associated color of choice from the ChoiceSet."""
        return BDMultiDestinationFloodingChoices.colors.get(
            self.multi_destination_flooding
        )

    def get_unknown_ipv4_multicast_color(self):
        """Return the associated color of choice from the ChoiceSet."""
        return BDUnknownMulticastChoices.colors.get(
            self.unknown_ipv4_multicast
        )

    def get_unknown_ipv6_multicast_color(self):
        """Return the associated color of choice from the ChoiceSet."""
        return BDUnknownMulticastChoices.colors.get(
            self.unknown_ipv6_multicast
        )

    def get_unknown_unicast_color(self):
        """Return the associated color of choice from the ChoiceSet."""
        return BDUnknownUnicastChoices.colors.get(self.unknown_unicast)
