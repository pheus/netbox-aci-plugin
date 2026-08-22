# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns

from ...models.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlock,
    ACILeafSelector,
    ACILeafSwitchProfile,
    ACILeafSwitchProfileInterfaceBinding,
)


class ACILeafSwitchProfileTable(NetBoxTable):
    """NetBox table for the ACI Leaf Switch Profile model."""

    name = tables.Column(
        verbose_name=_("Leaf Switch Profile"),
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
        model = ACILeafSwitchProfile
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
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
            "nb_tenant",
            "tags",
        )


class ACILeafSelectorTable(NetBoxTable):
    """NetBox table for the ACI Leaf Selector model."""

    name = tables.Column(
        verbose_name=_("Leaf Selector"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    aci_fabric = tables.Column(
        verbose_name=_("Fabric"),
        accessor="aci_leaf_switch_profile__aci_fabric",
        linkify=True,
    )
    aci_leaf_switch_profile = tables.Column(
        verbose_name=_("Leaf Switch Profile"),
        linkify=True,
    )
    aci_leaf_node_block_count = tables.Column(
        verbose_name=_("Node Blocks"),
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
        model = ACILeafSelector
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_leaf_switch_profile",
            "aci_leaf_node_block_count",
            "nb_tenant",
            "owner",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_leaf_switch_profile",
            "aci_leaf_node_block_count",
            "nb_tenant",
            "tags",
        )


class ACILeafNodeBlockTable(NetBoxTable):
    """NetBox table for the ACI Leaf Node Block model."""

    name = tables.Column(
        verbose_name=_("Node Block"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    aci_fabric = tables.Column(
        verbose_name=_("Fabric"),
        accessor="aci_leaf_selector__aci_leaf_switch_profile__aci_fabric",
        linkify=True,
    )
    aci_leaf_switch_profile = tables.Column(
        verbose_name=_("Leaf Switch Profile"),
        accessor="aci_leaf_selector__aci_leaf_switch_profile",
        linkify=True,
    )
    aci_leaf_selector = tables.Column(
        verbose_name=_("Leaf Selector"),
        linkify=True,
    )
    node_id_from = tables.Column(
        verbose_name=_("Node ID (from)"),
    )
    node_id_to = tables.Column(
        verbose_name=_("Node ID (to)"),
    )
    aci_node_count = tables.Column(
        verbose_name=_("Nodes"),
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
        model = ACILeafNodeBlock
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_leaf_switch_profile",
            "aci_leaf_selector",
            "node_id_from",
            "node_id_to",
            "aci_node_count",
            "nb_tenant",
            "owner",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_leaf_selector",
            "node_id_from",
            "node_id_to",
            "aci_node_count",
            "nb_tenant",
            "tags",
        )


class ACILeafSwitchProfileInterfaceBindingTable(NetBoxTable):
    """Table for ACILeafSwitchProfileInterfaceBinding model."""

    aci_fabric = tables.Column(
        verbose_name=_("Fabric"),
        accessor="aci_leaf_switch_profile__aci_fabric",
        linkify=True,
    )
    aci_leaf_switch_profile = tables.Column(
        verbose_name=_("Leaf Switch Profile"),
        linkify=True,
    )
    aci_leaf_interface_profile = tables.Column(
        verbose_name=_("Leaf Interface Profile"),
        linkify=True,
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACILeafSwitchProfileInterfaceBinding
        fields: tuple = (
            "pk",
            "id",
            "aci_fabric",
            "aci_leaf_switch_profile",
            "aci_leaf_interface_profile",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "aci_fabric",
            "aci_leaf_switch_profile",
            "aci_leaf_interface_profile",
        )
