# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns

from ...models.fabric.vpc_protection_groups import ACIVPCProtectionGroup


class ACIVPCProtectionGroupTable(NetBoxTable):
    """NetBox table for the ACI VPC Protection Group model."""

    name = tables.Column(
        verbose_name=_("VPC Protection Group"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    aci_fabric = tables.Column(
        verbose_name=_("Fabric"),
        linkify=True,
    )
    logical_pair_id = tables.Column(
        verbose_name=_("Logical Pair ID"),
    )
    aci_node_a = tables.Column(
        verbose_name=_("Node A"),
        linkify=True,
    )
    aci_node_b = tables.Column(
        verbose_name=_("Node B"),
        linkify=True,
    )
    nb_tenant = tables.Column(
        linkify=True,
    )
    owner_group = tables.Column(
        verbose_name=_("Owner Group"),
        accessor="owner__group",
        linkify=True,
    )
    owner = tables.Column(
        linkify=True,
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIVPCProtectionGroup
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "logical_pair_id",
            "aci_node_a",
            "aci_node_b",
            "nb_tenant",
            "owner",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_fabric",
            "description",
            "logical_pair_id",
            "aci_node_a",
            "aci_node_b",
            "nb_tenant",
            "tags",
        )
