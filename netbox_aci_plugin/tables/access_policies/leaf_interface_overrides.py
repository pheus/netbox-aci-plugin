# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns

from ...models.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverride,
)


class ACILeafInterfaceOverrideTable(NetBoxTable):
    """Table for ACILeafInterfaceOverride model."""

    aci_fabric = tables.Column(
        verbose_name=_("Fabric"),
        accessor="aci_node_interface__aci_node___aci_fabric",
        linkify=True,
    )
    aci_pod = tables.Column(
        verbose_name=_("Pod"),
        accessor="aci_node_interface__aci_node__aci_pod",
        linkify=True,
    )
    aci_node = tables.Column(
        verbose_name=_("Node"),
        accessor="aci_node_interface__aci_node",
        linkify=True,
    )
    aci_node_interface = tables.Column(
        verbose_name=_("Node Interface"),
        linkify=True,
    )
    aci_leaf_interface_policy_group = tables.Column(
        verbose_name=_("Leaf Interface Policy Group"),
        linkify=True,
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACILeafInterfaceOverride
        fields: tuple = (
            "pk",
            "id",
            "aci_fabric",
            "aci_pod",
            "aci_node",
            "aci_node_interface",
            "aci_leaf_interface_policy_group",
            "description",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "aci_fabric",
            "aci_node",
            "aci_node_interface",
            "aci_leaf_interface_policy_group",
            "description",
        )
