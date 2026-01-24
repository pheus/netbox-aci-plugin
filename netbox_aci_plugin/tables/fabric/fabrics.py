# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns

from ...models.fabric.fabrics import ACIFabric


class ACIFabricTable(NetBoxTable):
    """NetBox table for the ACI Fabric model."""

    name = tables.Column(
        verbose_name=_("ACI Fabric"),
        linkify=True,
    )
    fabric_id = tables.Column(
        verbose_name=_("Fabric ID"),
        linkify=True,
    )
    infra_vlan_vid = tables.Column(
        verbose_name=_("Infra VID"),
    )
    infra_vlan = tables.Column(
        verbose_name=_("Infra VLAN"),
        linkify=True,
    )
    gipo_pool = tables.Column(
        verbose_name=_("GIPo Pool"),
        linkify=True,
    )
    scope_type = columns.ContentTypeColumn(
        verbose_name=_("Scope Type"),
    )
    scope = tables.Column(
        verbose_name=_("Scope"),
        linkify=True,
        orderable=False,
    )
    nb_tenant = tables.Column(
        linkify=True,
    )
    owner_group = tables.Column(
        accessor="owner__group",
        linkify=True,
        verbose_name=_("Owner Group"),
    )
    owner = tables.Column(
        linkify=True,
        verbose_name=_("Owner"),
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIFabric
        fields: tuple = (
            "pk",
            "id",
            "name",
            "description",
            "fabric_id",
            "infra_vlan_vid",
            "infra_vlan",
            "gipo_pool",
            "scope_type",
            "scope",
            "nb_tenant",
            "owner",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "fabric_id",
            "description",
            "scope",
            "nb_tenant",
            "tags",
        )
