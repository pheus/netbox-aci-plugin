# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns

from ..models.tenant_contracts import ACIContract


class ACIContractTable(NetBoxTable):
    """NetBox table for the ACI Contract model."""

    name = tables.Column(
        verbose_name=_("Contract"),
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
    qos_class = columns.ChoiceFieldColumn(
        verbose_name=_("QoS class"),
    )
    scope = columns.ChoiceFieldColumn(
        verbose_name=_("Scope"),
    )
    target_dscp = columns.ChoiceFieldColumn(
        verbose_name=_("Target DSCP"),
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIContract
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "aci_tenant",
            "nb_tenant",
            "description",
            "qos_class",
            "scope",
            "target_dscp",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "nb_tenant",
            "description",
            "scope",
            "tags",
        )
