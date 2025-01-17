# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns

from ..models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup


class ACIAppProfileTable(NetBoxTable):
    """NetBox table for the ACI Application Profile model."""

    name = tables.Column(
        verbose_name=_("Application Profile"),
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
        model = ACIAppProfile
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


class ACIEndpointGroupTable(NetBoxTable):
    """NetBox table for the ACI Endpoint Group model."""

    name = tables.Column(
        verbose_name=_("Endpoint Group"),
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
    aci_bridge_domain = tables.Column(
        linkify=True,
    )
    nb_tenant = tables.Column(
        linkify=True,
    )
    qos_class = columns.ChoiceFieldColumn(
        verbose_name=_("QoS class"),
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIEndpointGroup
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "aci_tenant",
            "aci_app_profile",
            "aci_bridge_domain",
            "nb_tenant",
            "description",
            "admin_shutdown",
            "custom_qos_policy_name",
            "flood_in_encap_enabled",
            "intra_epg_isolation_enabled",
            "qos_class",
            "preferred_group_member_enabled",
            "proxy_arp_enabled",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_app_profile",
            "aci_bridge_domain",
            "nb_tenant",
            "description",
            "tags",
        )
