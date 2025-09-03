# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import NetBoxTable, columns

from ...models.tenant.app_profiles import ACIAppProfile
from ...models.tenant.contracts import (
    ACIContract,
    ACIContractRelation,
    ACIContractSubject,
    ACIContractSubjectFilter,
)


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


class ACIContractRelationTable(NetBoxTable):
    """NetBox table for the ACI Contract Relation model."""

    aci_contract_tenant = tables.Column(
        verbose_name=_("ACI Tenant (Contract)"),
        linkify=True,
    )
    aci_contract = tables.Column(
        verbose_name=_("Contract"),
        linkify=True,
    )
    aci_object_tenant = tables.Column(
        verbose_name=_("ACI Tenant (Object)"),
        linkify=True,
    )
    aci_object_type = columns.ContentTypeColumn(
        verbose_name=_("Object Type"),
    )
    aci_object = tables.Column(
        verbose_name=_("Object"),
        orderable=False,
        linkify=True,
    )
    role = columns.ChoiceFieldColumn(
        verbose_name=_("Role"),
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIContractRelation
        fields: tuple = (
            "pk",
            "id",
            "aci_contract",
            "aci_contract_tenant",
            "aci_object_type",
            "aci_object",
            "aci_object_tenant",
            "role",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "aci_contract",
            "aci_contract_tenant",
            "aci_object_type",
            "aci_object",
            "role",
            "tags",
        )

    def render_aci_object(self, record) -> str | None:
        """Render the ACI object name."""
        if isinstance(record.aci_object.parent_object, ACIAppProfile):
            return f"{record.aci_object.aci_app_profile} | {record.aci_object.name}"
        return record.aci_object.name


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


class ACIContractSubjectFilterTable(NetBoxTable):
    """NetBox table for the ACI Contract Subject Filter model."""

    aci_contract = tables.Column(
        verbose_name=_("Contract"),
        linkify=True,
    )
    aci_contract_filter_tenant = tables.Column(
        verbose_name=_("ACI Tenant (Filter)"),
        linkify=True,
    )
    aci_contract_filter = tables.Column(
        verbose_name=_("Filter"),
        linkify=True,
    )
    aci_contract_subject_tenant = tables.Column(
        verbose_name=_("ACI Tenant (Subject)"),
        linkify=True,
    )
    aci_contract_subject = tables.Column(
        verbose_name=_("Subject"),
        linkify=True,
    )
    action = columns.ChoiceFieldColumn(
        verbose_name=_("Action"),
    )
    apply_direction = columns.ChoiceFieldColumn(
        verbose_name=_("Apply direction"),
    )
    log_enabled = columns.BooleanColumn(
        verbose_name=_("Logging"),
    )
    policy_compression_enabled = columns.BooleanColumn(
        verbose_name=_("Compression"),
    )
    priority = columns.ChoiceFieldColumn(
        verbose_name=_("Priority"),
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIContractSubjectFilter
        fields: tuple = (
            "pk",
            "id",
            "aci_contract_filter_tenant",
            "aci_contract_filter",
            "aci_contract_subject_tenant",
            "aci_contract",
            "aci_contract_subject",
            "action",
            "apply_direction",
            "log_enabled",
            "policy_compression_enabled",
            "priority",
            "tags",
            "comments",
        )
        default_columns: tuple = (
            "aci_contract_subject",
            "aci_contract_subject_tenant",
            "aci_contract",
            "aci_contract_filter",
            "action",
            "log_enabled",
            "policy_compression_enabled",
            "tags",
        )


class ACIContractSubjectFilterReducedTable(NetBoxTable):
    """Reduced NetBox table for the ACI Contract Subject Filter model."""

    aci_contract_filter_tenant = tables.Column(
        verbose_name=_("ACI Tenant (Filter)"),
        linkify=True,
    )
    aci_contract_filter = tables.Column(
        verbose_name=_("Filter"),
        linkify=True,
    )
    action = columns.ChoiceFieldColumn(
        verbose_name=_("Action"),
    )

    class Meta(NetBoxTable.Meta):
        model = ACIContractSubjectFilter
        fields: tuple = (
            "pk",
            "id",
            "aci_contract_filter_tenant",
            "aci_contract_filter",
            "action",
        )
        default_columns: tuple = (
            "aci_contract_filter",
            "action",
        )
