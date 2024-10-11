# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns

from ..models.tenant_contract_filters import ACIContractFilter


class ACIContractFilterTable(NetBoxTable):
    """NetBox table for ACI Contract Filter model."""

    name = tables.Column(
        verbose_name=_("Contract Filter"),
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
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIContractFilter
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "aci_tenant",
            "nb_tenant",
            "description",
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
