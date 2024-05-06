# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from ..models.tenants import ACITenant


class ACITenantTable(NetBoxTable):
    """NetBox table for ACI Tenant model."""

    name = tables.Column(linkify=True, verbose_name="ACI Tenant")
    alias = tables.Column(linkify=True)
    description = tables.Column()
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACITenant
        fields: tuple = (
            "pk",
            "id",
            "name",
            "alias",
            "description",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "alias",
            "description",
            "tags",
        )
