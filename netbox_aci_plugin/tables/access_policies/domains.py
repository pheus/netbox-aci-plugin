# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns

from ...models.access_policies.domains import ACIPhysicalDomain, ACIRoutedDomain


class ACIRoutedDomainTable(NetBoxTable):
    """NetBox table for the ACI Routed Domain model."""

    name = tables.Column(
        verbose_name=_("ACI Routed Domain"),
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
    aci_vlan_pool = tables.Column(
        verbose_name=_("VLAN Pool"),
        linkify=True,
    )
    security_domains = columns.ArrayColumn(
        verbose_name=_("Security Domains"),
        orderable=False,
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
        model = ACIRoutedDomain
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_vlan_pool",
            "security_domains",
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
            "aci_vlan_pool",
            "security_domains",
            "nb_tenant",
            "tags",
        )


class ACIPhysicalDomainTable(NetBoxTable):
    """NetBox table for the ACI Physical Domain model."""

    name = tables.Column(
        verbose_name=_("ACI Physical Domain"),
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
    aci_vlan_pool = tables.Column(
        verbose_name=_("VLAN Pool"),
        linkify=True,
    )
    security_domains = columns.ArrayColumn(
        verbose_name=_("Security Domains"),
        orderable=False,
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
        model = ACIPhysicalDomain
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_vlan_pool",
            "security_domains",
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
            "aci_vlan_pool",
            "security_domains",
            "nb_tenant",
            "tags",
        )
