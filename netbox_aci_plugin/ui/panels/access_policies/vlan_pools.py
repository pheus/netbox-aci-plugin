# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the ACI VLAN Pool models."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = (
    "ACIVLANPoolPanel",
    "ACIVLANPoolRangePanel",
)


class ACIVLANPoolPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI VLAN Pool detail view."""

    title = _("ACI VLAN Pool")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    allocation_mode = attrs.ChoiceAttr("allocation_mode", label=_("Allocation Mode"))
    nb_vlan_group = attrs.RelatedObjectAttr(
        "nb_vlan_group", linkify=True, label=_("NetBox VLAN Group")
    )
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACIVLANPoolRangePanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI VLAN Pool Range detail view."""

    title = _("ACI VLAN Pool Range")
    aci_vlan_pool = attrs.RelatedObjectAttr(
        "aci_vlan_pool", linkify=True, label=_("ACI VLAN Pool")
    )
    vlan_id_from = attrs.NumericAttr("vlan_id_from", label=_("VLAN ID (from)"))
    vlan_id_to = attrs.NumericAttr("vlan_id_to", label=_("VLAN ID (to)"))
    allocation_mode = attrs.ChoiceAttr("allocation_mode", label=_("Allocation Mode"))
    role = attrs.ChoiceAttr("role", label=_("Role"))
