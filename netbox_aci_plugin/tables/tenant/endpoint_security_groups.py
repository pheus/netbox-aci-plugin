# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns

from ...models.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroup,
    ACIEsgEndpointGroupSelector,
    ACIEsgEndpointSelector,
)


class ACIEndpointSecurityGroupTable(NetBoxTable):
    """NetBox table for the ACI Endpoint Security Group model."""

    name = tables.Column(
        verbose_name=_("Endpoint Security Group"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    aci_tenant = tables.Column(
        verbose_name=_("ACI Tenant"),
        linkify=True,
    )
    aci_app_profile = tables.Column(
        linkify=True,
    )
    aci_vrf = tables.Column(
        linkify=True,
    )
    nb_tenant = tables.Column(
        linkify=True,
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIEndpointSecurityGroup
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_vrf",
            "nb_tenant",
            "description",
            "admin_shutdown",
            "intra_esg_isolation_enabled",
            "preferred_group_member_enabled",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_app_profile",
            "aci_vrf",
            "nb_tenant",
            "description",
            "tags",
        )


class ACIEsgEndpointGroupSelectorTable(NetBoxTable):
    """NetBox table for the ACI ESG Endpoint Group (EPG) Selector model."""

    name = tables.Column(
        verbose_name=_("EPG Selector"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    aci_tenant = tables.Column(
        verbose_name=_("ACI Tenant (ESG)"),
        linkify=True,
    )
    aci_app_profile = tables.Column(
        verbose_name=_("ACI App Profile (ESG)"),
        linkify=True,
    )
    aci_endpoint_security_group = tables.Column(
        verbose_name=_("ACI ESG"),
        linkify=True,
    )
    aci_epg_object_tenant = tables.Column(
        verbose_name=_("ACI Tenant (EPG)"),
        linkify=True,
    )
    aci_epg_object_app_profile = tables.Column(
        verbose_name=_("ACI App Profile (EPG)"),
        linkify=True,
    )
    aci_epg_object_type = columns.ContentTypeColumn(
        verbose_name=_("ACI EPG Type"),
    )
    aci_epg_object = tables.Column(
        verbose_name=_("ACI EPG"),
        orderable=False,
        linkify=True,
    )
    nb_tenant = tables.Column(
        linkify=True,
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIEsgEndpointGroupSelector
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_endpoint_security_group",
            "aci_epg_object_tenant",
            "aci_epg_object_app_profile",
            "aci_epg_object_type",
            "aci_epg_object",
            "nb_tenant",
            "description",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_endpoint_security_group",
            "aci_epg_object_type",
            "aci_epg_object_app_profile",
            "aci_epg_object",
            "description",
            "tags",
        )


class ACIEsgEndpointSelectorTable(NetBoxTable):
    """NetBox table for the ACI ESG Endpoint Selector model."""

    name = tables.Column(
        verbose_name=_("Endpoint Selector"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    aci_tenant = tables.Column(
        verbose_name=_("ACI Tenant"),
        linkify=True,
    )
    aci_app_profile = tables.Column(
        verbose_name=_("ACI App Profile"),
        linkify=True,
    )
    aci_endpoint_security_group = tables.Column(
        verbose_name=_("ACI ESG"),
        linkify=True,
    )
    ep_object_type = columns.ContentTypeColumn(
        verbose_name=_("Endpoint Type"),
    )
    ep_object = tables.Column(
        verbose_name=_("Endpoint"),
        orderable=False,
        linkify=True,
    )
    nb_tenant = tables.Column(
        linkify=True,
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIEsgEndpointSelector
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_endpoint_security_group",
            "ep_object_type",
            "ep_object",
            "nb_tenant",
            "description",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_endpoint_security_group",
            "ep_object_type",
            "ep_object",
            "description",
            "tags",
        )
