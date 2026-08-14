# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns

from ...models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
    ACILeafInterfaceSelector,
    ACILeafPortBlock,
)


class ACILeafInterfaceProfileTable(NetBoxTable):
    """NetBox table for the ACI Leaf Interface Profile model."""

    name = tables.Column(
        verbose_name=_("Leaf Interface Profile"),
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
        model = ACILeafInterfaceProfile
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


class ACILeafInterfaceSelectorTable(NetBoxTable):
    """NetBox table for the ACI Leaf Interface Selector model."""

    name = tables.Column(
        verbose_name=_("Leaf Interface Selector"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    aci_fabric = tables.Column(
        verbose_name=_("Fabric"),
        accessor="aci_leaf_interface_profile__aci_fabric",
        linkify=True,
    )
    aci_leaf_interface_profile = tables.Column(
        verbose_name=_("Leaf Interface Profile"),
        linkify=True,
    )
    aci_leaf_interface_policy_group = tables.Column(
        verbose_name=_("Leaf Interface Policy Group"),
        linkify=True,
    )
    aci_leaf_port_block_count = tables.Column(
        verbose_name=_("Port Blocks"),
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
        model = ACILeafInterfaceSelector
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_leaf_interface_profile",
            "aci_leaf_interface_policy_group",
            "aci_leaf_port_block_count",
            "nb_tenant",
            "owner",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_leaf_interface_profile",
            "aci_leaf_interface_policy_group",
            "aci_leaf_port_block_count",
            "nb_tenant",
            "tags",
        )


class ACILeafPortBlockTable(NetBoxTable):
    """NetBox table for the ACI Leaf Port Block model."""

    name = tables.Column(
        verbose_name=_("Port Block"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    aci_fabric = tables.Column(
        verbose_name=_("Fabric"),
        accessor="aci_leaf_interface_selector__aci_leaf_interface_profile__aci_fabric",
        linkify=True,
    )
    aci_leaf_interface_profile = tables.Column(
        verbose_name=_("Leaf Interface Profile"),
        accessor="aci_leaf_interface_selector__aci_leaf_interface_profile",
        linkify=True,
    )
    aci_leaf_interface_selector = tables.Column(
        verbose_name=_("Leaf Interface Selector"),
        linkify=True,
    )
    module_from = tables.Column(
        verbose_name=_("Module (from)"),
    )
    module_to = tables.Column(
        verbose_name=_("Module (to)"),
    )
    port_from = tables.Column(
        verbose_name=_("Port (from)"),
    )
    port_to = tables.Column(
        verbose_name=_("Port (to)"),
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
        model = ACILeafPortBlock
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_leaf_interface_profile",
            "aci_leaf_interface_selector",
            "module_from",
            "module_to",
            "port_from",
            "port_to",
            "nb_tenant",
            "owner",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "description",
            "aci_leaf_interface_selector",
            "module_from",
            "module_to",
            "port_from",
            "port_to",
            "nb_tenant",
            "tags",
        )
