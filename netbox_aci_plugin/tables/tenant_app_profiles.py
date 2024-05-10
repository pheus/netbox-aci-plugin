# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns

from ..models.tenant_app_profiles import ACIAppProfile


class ACIAppProfileTable(NetBoxTable):
    """NetBox table for ACI Application Profile model."""

    name = tables.Column(
        linkify=True, verbose_name=_("ACI Application Profile")
    )
    alias = tables.Column(linkify=True)
    description = tables.Column()
    aci_tenant = tables.Column(linkify=True)
    nb_tenant = tables.Column(linkify=True)
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIAppProfile
        fields: tuple = (
            "pk",
            "id",
            "name",
            "alias",
            "aci_tenant",
            "nb_tenant",
            "description",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "alias",
            "aci_tenant",
            "nb_tenant",
            "description",
            "tags",
        )
