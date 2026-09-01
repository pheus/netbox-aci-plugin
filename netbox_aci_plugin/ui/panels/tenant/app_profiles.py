# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the tenant ACI Application Profile model."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = ("ACIAppProfilePanel",)


class ACIAppProfilePanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Application Profile detail view."""

    title = _("ACI Application Profile")
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
