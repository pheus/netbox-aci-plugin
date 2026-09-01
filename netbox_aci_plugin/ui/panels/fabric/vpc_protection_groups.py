# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the fabric ACI VPC Protection Group model."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = ("ACIVPCProtectionGroupPanel",)


class ACIVPCProtectionGroupPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI VPC Protection Group detail view."""

    title = _("ACI VPC Protection Group")

    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    logical_pair_id = attrs.NumericAttr("logical_pair_id", label=_("Logical Pair ID"))
    aci_node_a = attrs.RelatedObjectAttr(
        "aci_node_a", linkify=True, label=_("ACI Node A")
    )
    aci_node_b = attrs.RelatedObjectAttr(
        "aci_node_b", linkify=True, label=_("ACI Node B")
    )
    aci_pod = attrs.RelatedObjectAttr("aci_pod", linkify=True, label=_("ACI Pod"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )
