# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the fabric ACI Pod model."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = ("ACIPodPanel",)


class ACIPodPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Pod detail view."""

    title = _("ACI Pod")

    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    pod_id = attrs.NumericAttr("pod_id", label=_("Pod ID"))
    tep_pool = attrs.RelatedObjectAttr("tep_pool", linkify=True, label=_("TEP Pool"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )
    scope = attrs.GenericForeignKeyAttr("scope", linkify=True, label=_("Scope"))
