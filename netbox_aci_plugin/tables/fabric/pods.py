# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns

from ...models.fabric.pods import ACIPod


class ACIPodTable(NetBoxTable):
    """NetBox table for the ACI Pod model."""

    name = tables.Column(
        verbose_name=_("ACI Pod"),
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
    pod_id = tables.Column(
        verbose_name=_("Pod ID"),
        linkify=True,
    )
    tep_pool = tables.Column(
        verbose_name=_("TEP Pool"),
        linkify=True,
    )
    scope_type = columns.ContentTypeColumn(
        verbose_name=_("Scope Type"),
    )
    scope = tables.Column(
        verbose_name=_("Scope"),
        linkify=True,
        orderable=False,
    )
    nb_tenant = tables.Column(
        linkify=True,
    )
    owner_group = tables.Column(
        accessor="owner__group",
        linkify=True,
        verbose_name=_("Owner Group"),
    )
    owner = tables.Column(
        linkify=True,
        verbose_name=_("Owner"),
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIPod
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "pod_id",
            "tep_pool",
            "scope_type",
            "scope",
            "nb_tenant",
            "owner",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "pod_id",
            "description",
            "scope",
            "nb_tenant",
            "tags",
        )
