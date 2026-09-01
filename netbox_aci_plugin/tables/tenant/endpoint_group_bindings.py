# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns

from ...models.tenant.endpoint_group_bindings import (
    ACIEndpointGroupAAEPBinding,
    ACIEndpointGroupDomainBinding,
)


class ACIEndpointGroupDomainBindingTable(NetBoxTable):
    """NetBox table for the ACI Endpoint Group Domain Binding model."""

    aci_fabric = tables.Column(
        verbose_name=_("Fabric"),
        accessor="aci_epg_object__aci_fabric",
        orderable=False,
        linkify=True,
    )
    aci_epg_object_type = columns.ContentTypeColumn(
        verbose_name=_("EPG Type"),
    )
    aci_epg_object = tables.Column(
        verbose_name=_("EPG"),
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


class ACIEndpointGroupAAEPBindingTable(NetBoxTable):
    """NetBox table for the ACI Endpoint Group AAEP Binding model."""

    aci_endpoint_group = tables.Column(
        verbose_name=_("Endpoint Group"),
        linkify=True,
    )
    aci_aaep = tables.Column(
        verbose_name=_("AAEP"),
        linkify=True,
    )
    nb_vlan = tables.Column(
        verbose_name=_("NetBox VLAN"),
        linkify=True,
    )
    effective_encap_vlan_id = tables.Column(
        verbose_name=_("Effective Encap VLAN ID"),
        orderable=False,
    )
    primary_nb_vlan = tables.Column(
        verbose_name=_("Primary NetBox VLAN"),
        linkify=True,
    )
    effective_primary_encap_vlan_id = tables.Column(
        verbose_name=_("Effective Primary Encap VLAN ID"),
        orderable=False,
    )
    mode = columns.ChoiceFieldColumn()
    deployment_immediacy = columns.ChoiceFieldColumn()
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIEndpointGroupAAEPBinding
        fields: tuple = (
            "pk",
            "id",
            "aci_endpoint_group",
            "aci_aaep",
            "nb_vlan",
            "encap_vlan_id",
            "effective_encap_vlan_id",
            "primary_nb_vlan",
            "primary_encap_vlan_id",
            "effective_primary_encap_vlan_id",
            "mode",
            "deployment_immediacy",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "aci_endpoint_group",
            "aci_aaep",
            "nb_vlan",
            "encap_vlan_id",
            "effective_encap_vlan_id",
            "mode",
            "deployment_immediacy",
            "tags",
        )
