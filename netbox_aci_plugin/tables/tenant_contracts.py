# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns

from ..models.tenant_contracts import ACIContract, ACIContractSubject


class ACIContractTable(NetBoxTable):
    """NetBox table for the ACI Contract model."""

    name = tables.Column(
        verbose_name=_("Contract"),
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
    qos_class = columns.ChoiceFieldColumn(
        verbose_name=_("QoS class"),
    )
    scope = columns.ChoiceFieldColumn(
        verbose_name=_("Scope"),
    )
    target_dscp = columns.ChoiceFieldColumn(
        verbose_name=_("Target DSCP"),
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIContract
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "aci_tenant",
            "nb_tenant",
            "description",
            "qos_class",
            "scope",
            "target_dscp",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "nb_tenant",
            "description",
            "scope",
            "tags",
        )


class ACIContractSubjectTable(NetBoxTable):
    """NetBox table for the ACI Contract Subject model."""

    name = tables.Column(
        verbose_name=_("Subject"),
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
    aci_contract = tables.Column(
        verbose_name=_("Contract"),
        linkify=True,
    )
    nb_tenant = tables.Column(
        linkify=True,
    )
    apply_both_directions_enabled = columns.BooleanColumn(
        verbose_name=_("Apply both directions"),
    )
    qos_class = columns.ChoiceFieldColumn(
        verbose_name=_("QoS class"),
    )
    qos_class_cons_to_prov = columns.ChoiceFieldColumn(
        verbose_name=_("QoS class (cons->prov)"),
    )
    qos_class_prov_to_cons = columns.ChoiceFieldColumn(
        verbose_name=_("QoS class (prov->cons)"),
    )
    reverse_filter_ports_enabled = columns.BooleanColumn(
        verbose_name=_("Reverse filter ports"),
    )
    service_graph_name = tables.Column(
        verbose_name=_("Service Graph name"),
    )
    service_graph_name_cons_to_prov = tables.Column(
        verbose_name=_("Service Graph name (cons->prov)"),
    )
    service_graph_name_prov_to_cons = tables.Column(
        verbose_name=_("Service Graph name (prov->cons)"),
    )
    target_dscp = columns.ChoiceFieldColumn(
        verbose_name=_("Target DSCP"),
    )
    target_dscp_cons_to_prov = columns.ChoiceFieldColumn(
        verbose_name=_("Target DSCP (cons->prov)"),
    )
    target_dscp_prov_to_cons = columns.ChoiceFieldColumn(
        verbose_name=_("Target DSCP (prov->cons)"),
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIContractSubject
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "aci_tenant",
            "aci_contract",
            "nb_tenant",
            "description",
            "apply_both_directions_enabled",
            "qos_class",
            "qos_class_cons_to_prov",
            "qos_class_prov_to_cons",
            "reverse_filter_ports_enabled",
            "service_graph_name",
            "service_graph_name_cons_to_prov",
            "service_graph_name_prov_to_cons",
            "target_dscp",
            "target_dscp_cons_to_prov",
            "target_dscp_prov_to_cons",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_tenant",
            "aci_contract",
            "apply_both_directions_enabled",
            "reverse_filter_ports_enabled",
            "service_graph_name",
            "qos_class",
            "target_dscp",
            "description",
            "tags",
        )


class ACIContractSubjectReducedTable(NetBoxTable):
    """Reduced NetBox table for the ACI Contract Subject model."""

    name = tables.Column(
        verbose_name=_("Subject"),
        linkify=True,
    )
    apply_both_directions_enabled = columns.BooleanColumn(
        verbose_name=_("Apply both directions"),
    )

    class Meta(NetBoxTable.Meta):
        model = ACIContractSubject
        fields: tuple = (
            "pk",
            "id",
            "name",
            "apply_both_directions_enabled",
        )
        default_columns: tuple = (
            "name",
            "apply_both_directions_enabled",
        )
