# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns

from ...models.access_policies.aaep import (
    ACIAAEPDomainBinding,
    ACIAttachableAccessEntityProfile,
)


class ACIAttachableAccessEntityProfileTable(NetBoxTable):
    """NetBox table for the ACI Attachable Access Entity Profile model."""

    name = tables.Column(
        verbose_name=_("AAEP"),
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
    nb_tenant = tables.Column(
        linkify=True,
    )
    infra_vlan = columns.BooleanColumn(verbose_name=_("Infra VLAN"))
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
        model = ACIAttachableAccessEntityProfile
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "infra_vlan",
            "nb_tenant",
            "owner",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_fabric",
            "description",
            "infra_vlan",
            "nb_tenant",
            "tags",
        )


class ACIAAEPDomainBindingTable(NetBoxTable):
    """NetBox table for the ACI AAEP Domain Binding model."""

    aci_fabric = tables.Column(
        verbose_name=_("Fabric"),
        accessor="aci_aaep__aci_fabric",
        linkify=True,
    )
    aci_aaep = tables.Column(
        verbose_name=_("AAEP"),
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
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIAAEPDomainBinding
        fields: tuple = (
            "pk",
            "id",
            "aci_fabric",
            "aci_aaep",
            "aci_domain_object_type",
            "aci_domain_object",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "aci_aaep",
            "aci_domain_object_type",
            "aci_domain_object",
            "tags",
        )
