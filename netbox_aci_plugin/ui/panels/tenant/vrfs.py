# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the tenant ACI VRF model."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = (
    "ACIVRFAdditionalSettingsPanel",
    "ACIVRFEndpointLearningPanel",
    "ACIVRFMulticastPanel",
    "ACIVRFPanel",
    "ACIVRFPolicyControlPanel",
)


class ACIVRFPanel(panels.ObjectAttributesPanel):
    """Identity attribute panel for the ACI VRF detail view."""

    title = _("ACI VRF")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )
    nb_vrf = attrs.RelatedObjectAttr("nb_vrf", linkify=True, label=_("NetBox VRF"))


class ACIVRFPolicyControlPanel(panels.ObjectAttributesPanel):
    """Policy control attribute panel for the ACI VRF detail view."""

    title = _("Policy Control Settings")

    pc_enforcement_direction = attrs.ChoiceAttr(
        "pc_enforcement_direction",
        label=_("Policy Control Enforcement Direction"),
    )
    pc_enforcement_preference = attrs.ChoiceAttr(
        "pc_enforcement_preference",
        label=_("Policy Control Enforcement Preference"),
    )
    bd_enforcement_enabled = attrs.BooleanAttr(
        "bd_enforcement_enabled", label=_("Bridge Domain Enforcement")
    )
    preferred_group_enabled = attrs.BooleanAttr(
        "preferred_group_enabled", label=_("Preferred Group")
    )


class ACIVRFEndpointLearningPanel(panels.ObjectAttributesPanel):
    """Endpoint learning attribute panel for the ACI VRF detail view."""

    title = _("Endpoint Learning Settings")

    ip_data_plane_learning_enabled = attrs.BooleanAttr(
        "ip_data_plane_learning_enabled", label=_("IP Data Plane Learning")
    )


class ACIVRFMulticastPanel(panels.ObjectAttributesPanel):
    """Multicast attribute panel for the ACI VRF detail view."""

    title = _("Multicast Settings")

    pim_ipv4_enabled = attrs.BooleanAttr(
        "pim_ipv4_enabled", label=_("PIM (Multicast) IPv4")
    )
    pim_ipv6_enabled = attrs.BooleanAttr(
        "pim_ipv6_enabled", label=_("PIM (Multicast) IPv6")
    )


class ACIVRFAdditionalSettingsPanel(panels.ObjectAttributesPanel):
    """Additional settings attribute panel for the ACI VRF detail view."""

    title = _("Additional Settings")

    dns_labels = attrs.ArrayAttr("dns_labels", label=_("DNS Labels"))
