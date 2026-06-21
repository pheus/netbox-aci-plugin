# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns

from ...models.access_policies.vlan_pools import ACIVLANPool, ACIVLANPoolRange


class ACIVLANPoolTable(NetBoxTable):
    """NetBox table for the ACI VLAN Pool model."""

    name = tables.Column(
        verbose_name=_("ACI VLAN Pool"),
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
    allocation_mode = columns.ChoiceFieldColumn()
    nb_vlan_group = tables.Column(
        linkify=True,
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
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIVLANPool
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "allocation_mode",
            "nb_vlan_group",
            "nb_tenant",
            "owner",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "allocation_mode",
            "nb_vlan_group",
            "nb_tenant",
            "tags",
        )


class ACIVLANPoolRangeTable(NetBoxTable):
    """NetBox table for the ACI VLAN Pool Range model."""

    aci_vlan_pool = tables.Column(
        verbose_name=_("ACI VLAN Pool"),
        linkify=True,
    )
    aci_fabric = tables.Column(
        verbose_name=_("ACI Fabric"),
        accessor="aci_vlan_pool__aci_fabric",
        linkify=True,
    )
    vlan_id_from = tables.Column(
        verbose_name=_("VLAN ID (from)"),
        linkify=True,
    )
    vlan_id_to = tables.Column(
        verbose_name=_("VLAN ID (to)"),
    )
    allocation_mode = columns.ChoiceFieldColumn()
    role = columns.ChoiceFieldColumn()
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIVLANPoolRange
        fields: tuple = (
            "pk",
            "id",
            "aci_vlan_pool",
            "aci_fabric",
            "vlan_id_from",
            "vlan_id_to",
            "allocation_mode",
            "role",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "aci_vlan_pool",
            "aci_fabric",
            "vlan_id_from",
            "vlan_id_to",
            "allocation_mode",
            "role",
        )
