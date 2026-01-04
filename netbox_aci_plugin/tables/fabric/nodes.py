# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns

from ...models.fabric.nodes import ACINode


class ACINodeTable(NetBoxTable):
    """NetBox table for the ACI Node model."""

    name = tables.Column(
        verbose_name=_("ACI Node"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    aci_fabric = tables.Column(
        accessor="aci_pod__aci_fabric",
        verbose_name=_("Fabric"),
        linkify=True,
    )
    aci_pod = tables.Column(
        verbose_name=_("Pod"),
        linkify=True,
    )
    pod_id = tables.Column(
        accessor="aci_pod__pod_id",
        verbose_name=_("Pod ID"),
        linkify=True,
    )
    node_id = tables.Column(
        verbose_name=_("Node ID"),
        linkify=True,
    )
    node_object_type = columns.ContentTypeColumn(
        verbose_name=_("Object Type"),
    )
    node_object = tables.Column(
        verbose_name=_("Object"),
        orderable=False,
        linkify=True,
    )
    role = columns.ChoiceFieldColumn(
        verbose_name=_("Role"),
    )
    node_type = columns.ChoiceFieldColumn(
        verbose_name=_("Type"),
    )
    tep_ip_address = tables.Column(
        verbose_name=_("TEP IP"),
        linkify=True,
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
        model = ACINode
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "pod_id",
            "node_id",
            "node_object_type",
            "node_object",
            "role",
            "node_type",
            "tep_ip_address",
            "nb_tenant",
            "owner",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "aci_pod",
            "node_id",
            "node_object",
            "role",
            "description",
            "nb_tenant",
            "tags",
        )
