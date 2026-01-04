# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns

from ...models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
    ACIUSegNetworkAttribute,
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
    aci_fabric = tables.Column(
        verbose_name=_("ACI Fabric"),
        accessor="aci_app_profile__aci_tenant__aci_fabric",
        linkify=True,
    )
    aci_tenant = tables.Column(
        verbose_name=_("ACI Tenant"),
        accessor="aci_app_profile__aci_tenant",
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
        model = ACIEndpointGroup
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "aci_app_profile",
            "aci_bridge_domain",
            "nb_tenant",
            "admin_shutdown",
            "custom_qos_policy_name",
            "flood_in_encap_enabled",
            "intra_epg_isolation_enabled",
            "qos_class",
            "preferred_group_member_enabled",
            "proxy_arp_enabled",
            "owner",
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


class ACIUSegEndpointGroupTable(NetBoxTable):
    """NetBox table for the ACI uSeg Endpoint Group model."""

    name = tables.Column(
        verbose_name=_("uSeg EPG"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    aci_fabric = tables.Column(
        verbose_name=_("ACI Fabric"),
        accessor="aci_app_profile__aci_tenant__aci_fabric",
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
        model = ACIUSegEndpointGroup
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "aci_app_profile",
            "aci_bridge_domain",
            "nb_tenant",
            "admin_shutdown",
            "custom_qos_policy_name",
            "flood_in_encap_enabled",
            "intra_epg_isolation_enabled",
            "qos_class",
            "preferred_group_member_enabled",
            "owner",
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


class ACIUSegNetworkAttributeTable(NetBoxTable):
    """NetBox table for the ACI uSeg Network Attribute model."""

    name = tables.Column(
        verbose_name=_("Network Attribute"),
        linkify=True,
    )
    name_alias = tables.Column(
        verbose_name=_("Alias"),
        linkify=True,
    )
    aci_fabric = tables.Column(
        verbose_name=_("ACI Fabric"),
        accessor="aci_useg_endpoint_group__aci_app_profile__aci_tenant__aci_fabric",
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
    aci_useg_endpoint_group = tables.Column(
        verbose_name=_("uSeg EPG"),
        linkify=True,
    )
    attr_object_type = columns.ContentTypeColumn(
        verbose_name=_("Attribute Type"),
    )
    attr_object = tables.Column(
        verbose_name=_("Attribute"),
        orderable=False,
        linkify=True,
    )
    nb_tenant = tables.Column(
        linkify=True,
    )
    type = columns.ChoiceFieldColumn(
        verbose_name=_("Type"),
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
        model = ACIUSegNetworkAttribute
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_tenant",
            "aci_app_profile",
            "aci_useg_endpoint_group",
            "attr_object_type",
            "attr_object",
            "nb_tenant",
            "type",
            "use_epg_subnet",
            "owner",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_useg_endpoint_group",
            "type",
            "attr_object_type",
            "attr_object",
            "description",
            "use_epg_subnet",
            "tags",
        )
