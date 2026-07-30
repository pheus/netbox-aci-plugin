# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns

from ...models.fabric.node_interfaces import ACINodeInterface


class ACINodeInterfaceTable(NetBoxTable):
    """NetBox table for the ACI Node Interface model."""

    aci_fabric = tables.Column(
        verbose_name=_("Fabric"),
        accessor="aci_node___aci_fabric",
        linkify=True,
    )
    aci_pod = tables.Column(
        verbose_name=_("Pod"),
        accessor="aci_node__aci_pod",
        linkify=True,
    )
    aci_node = tables.Column(
        verbose_name=_("Node"),
        linkify=True,
    )
    nb_interface = tables.Column(
        verbose_name=_("Interface"),
        linkify=True,
    )
    sub_port = tables.Column(
        # 0 means none (the APIC sentinel), which django-tables2's
        # default empty_values does not include
        empty_values=(0,),
    )
    interface_token = tables.Column(
        verbose_name=_("Interface Token"),
        linkify=True,
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
        model = ACINodeInterface
        fields: tuple = (
            "pk",
            "id",
            "interface_token",
            "description",
            "aci_fabric",
            "aci_pod",
            "aci_node",
            "nb_interface",
            "module",
            "port",
            "sub_port",
            "nb_tenant",
            "owner",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "interface_token",
            "description",
            "aci_fabric",
            "aci_pod",
            "aci_node",
            "nb_interface",
            "module",
            "port",
            "sub_port",
            "nb_tenant",
            "tags",
        )
