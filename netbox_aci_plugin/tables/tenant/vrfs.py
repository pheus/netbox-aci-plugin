# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns

from ...models.tenant.vrfs import ACIVRF


class ACIVRFTable(NetBoxTable):
    """NetBox table for the ACI VRF model."""

    name = tables.Column(
        verbose_name=_("ACI VRF"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    aci_tenant = tables.Column(
        linkify=True,
    )
    nb_tenant = tables.Column(
        linkify=True,
    )
    nb_vrf = tables.Column(
        linkify=True,
    )
    bd_enforcement_enabled = columns.BooleanColumn(verbose_name=_("BD enforcement"))
    dns_labels = columns.ArrayColumn()
    ip_data_plane_learning_enabled = columns.BooleanColumn(
        verbose_name=_("DP learning"),
    )
    pc_enforcement_direction = columns.ChoiceFieldColumn(
        verbose_name=_("Enforcement direction"),
    )
    pc_enforcement_preference = columns.ChoiceFieldColumn(
        verbose_name=_("Enforcement preference"),
    )
    pim_ipv4_enabled = columns.BooleanColumn(
        verbose_name=_("PIM IPv4"),
    )
    pim_ipv6_enabled = columns.BooleanColumn(
        verbose_name=_("PIM IPv6"),
    )
    preferred_group_enabled = columns.BooleanColumn(
        verbose_name=_("Preferred group"),
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIVRF
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "aci_tenant",
            "nb_tenant",
            "nb_vrf",
            "description",
            "bd_enforcement_enabled",
            "dns_labels",
            "ip_data_plane_learning_enabled",
            "pc_enforcement_direction",
            "pc_enforcement_preference",
            "pim_ipv4_enabled",
            "pim_ipv6_enabled",
            "preferred_group_enabled",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "nb_tenant",
            "description",
            "tags",
        )
