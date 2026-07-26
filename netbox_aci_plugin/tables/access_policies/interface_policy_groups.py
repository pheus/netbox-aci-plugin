# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns

from ...models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)


class ACILeafInterfacePolicyGroupTable(NetBoxTable):
    """NetBox table for the ACI Leaf Interface Policy Group model."""

    name = tables.Column(
        verbose_name=_("Leaf Interface Policy Group"),
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
    group_type = columns.ChoiceFieldColumn(
        verbose_name=_("Type"),
    )
    aci_aaep = tables.Column(
        verbose_name=_("AAEP"),
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
        model = ACILeafInterfacePolicyGroup
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "group_type",
            "aci_aaep",
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
            "group_type",
            "aci_aaep",
            "nb_tenant",
            "tags",
        )
