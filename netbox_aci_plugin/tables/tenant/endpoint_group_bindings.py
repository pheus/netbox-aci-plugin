# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns

from ...models.tenant.endpoint_group_bindings import ACIEndpointGroupDomainBinding


class ACIEndpointGroupDomainBindingTable(NetBoxTable):
    """NetBox table for the ACI Endpoint Group Domain Binding model."""

    aci_fabric = tables.Column(
        verbose_name=_("ACI Fabric"),
        accessor="aci_epg_object__aci_fabric",
        orderable=False,
        linkify=True,
    )
    aci_epg_object_type = columns.ContentTypeColumn(
        verbose_name=_("EPG Type"),
    )
    aci_epg_object = tables.Column(
        verbose_name=_("Endpoint Group"),
        orderable=False,
        linkify=True,
    )
    aci_domain_object_type = columns.ContentTypeColumn(
        verbose_name=_("Domain Type"),
    )
    aci_domain_object = tables.Column(
        verbose_name=_("Domain"),
        orderable=False,
        linkify=True,
    )
    deployment_immediacy = columns.ChoiceFieldColumn()
    resolution_immediacy = columns.ChoiceFieldColumn()
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIEndpointGroupDomainBinding
        fields: tuple = (
            "pk",
            "id",
            "aci_fabric",
            "aci_epg_object_type",
            "aci_epg_object",
            "aci_domain_object_type",
            "aci_domain_object",
            "deployment_immediacy",
            "resolution_immediacy",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "aci_epg_object_type",
            "aci_epg_object",
            "aci_domain_object_type",
            "aci_domain_object",
            "deployment_immediacy",
            "resolution_immediacy",
            "tags",
        )
