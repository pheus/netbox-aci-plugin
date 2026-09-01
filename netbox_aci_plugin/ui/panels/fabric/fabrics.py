# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the fabric ACI Fabric model."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = ("ACIFabricPanel",)


class ACIFabricPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Fabric detail view.

    ACIFabric has no name_alias field, unlike every other primary ACI model.
    """

    title = _("ACI Fabric")

    description = attrs.TextAttr("description", label=_("Description"))
    fabric_id = attrs.NumericAttr("fabric_id", label=_("Fabric ID"))
    infra_vlan_vid = attrs.NumericAttr(
        "infra_vlan_vid", label=_("Infrastructure VLAN ID")
    )
    infra_vlan = attrs.RelatedObjectAttr(
        "infra_vlan", linkify=True, label=_("Infrastructure VLAN")
    )
    gipo_pool = attrs.RelatedObjectAttr("gipo_pool", linkify=True, label=_("GIPo Pool"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )
    scope = attrs.GenericForeignKeyAttr("scope", linkify=True, label=_("Scope"))
