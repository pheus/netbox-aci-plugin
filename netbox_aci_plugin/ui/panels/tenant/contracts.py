# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Declarative UI panels for the tenant ACI Contract models."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels

__all__ = (
    "ACIContractPanel",
    "ACIContractPriorityPanel",
    "ACIContractRelationPanel",
    "ACIContractScopePanel",
    "ACIContractSubjectDirectionPanel",
    "ACIContractSubjectFilterDirectionPanel",
    "ACIContractSubjectFilterDirectivesPanel",
    "ACIContractSubjectFilterPanel",
    "ACIContractSubjectFilterPriorityPanel",
    "ACIContractSubjectPanel",
    "ACIContractSubjectPriorityPanel",
    "ACIContractSubjectServiceGraphPanel",
)


class ACIContractPanel(panels.ObjectAttributesPanel):
    """Identity attribute panel for the ACI Contract detail view."""

    title = _("ACI Contract")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACIContractScopePanel(panels.ObjectAttributesPanel):
    """Scope attribute panel for the ACI Contract detail view."""

    title = _("Scope")

    scope = attrs.ChoiceAttr("scope", label=_("Scope"))


class ACIContractPriorityPanel(panels.ObjectAttributesPanel):
    """Priority attribute panel for the ACI Contract detail view."""

    title = _("Priority")

    qos_class = attrs.ChoiceAttr("qos_class", label=_("QoS Class"))
    target_dscp = attrs.ChoiceAttr("target_dscp", label=_("Target DSCP"))


class ACIContractRelationPanel(panels.ObjectAttributesPanel):
    """Attribute panel for the ACI Contract Relation detail view."""

    title = _("ACI Contract Relation")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_contract.aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_contract.aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    aci_contract = attrs.RelatedObjectAttr(
        "aci_contract", linkify=True, label=_("ACI Contract")
    )
    aci_object = attrs.GenericForeignKeyAttr(
        "aci_object", linkify=True, label=_("ACI Object")
    )
    role = attrs.ChoiceAttr("role", label=_("Role"))


class ACIContractSubjectPanel(panels.ObjectAttributesPanel):
    """Identity attribute panel for the ACI Contract Subject detail view."""

    title = _("ACI Contract Subject")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    aci_contract = attrs.RelatedObjectAttr(
        "aci_contract", linkify=True, label=_("ACI Contract")
    )
    name_alias = attrs.TextAttr("name_alias", label=_("Name Alias"))
    description = attrs.TextAttr("description", label=_("Description"))
    nb_tenant = attrs.RelatedObjectAttr(
        "nb_tenant", linkify=True, grouped_by="group", label=_("NetBox Tenant")
    )


class ACIContractSubjectDirectionPanel(panels.ObjectAttributesPanel):
    """Direction attribute panel for the ACI Contract Subject detail view."""

    title = _("Direction Settings")

    apply_both_directions_enabled = attrs.BooleanAttr(
        "apply_both_directions_enabled", label=_("Apply Both Directions enabled")
    )
    reverse_filter_ports_enabled = attrs.BooleanAttr(
        "reverse_filter_ports_enabled", label=_("Reverse Filter Ports enabled")
    )


class ACIContractSubjectServiceGraphPanel(panels.ObjectAttributesPanel):
    """Service Graph panel for the ACI Contract Subject detail view."""

    title = _("Service Graph")

    service_graph_name = attrs.TextAttr(
        "service_graph_name", label=_("Service Graph Name")
    )
    service_graph_name_cons_to_prov = attrs.TextAttr(
        "service_graph_name_cons_to_prov",
        label=_("Service Graph Name (Consumer to Provider)"),
    )
    service_graph_name_prov_to_cons = attrs.TextAttr(
        "service_graph_name_prov_to_cons",
        label=_("Service Graph Name (Provider to Consumer)"),
    )


class ACIContractSubjectPriorityPanel(panels.ObjectAttributesPanel):
    """Priority attribute panel for the ACI Contract Subject detail view."""

    title = _("Priority")

    qos_class = attrs.ChoiceAttr("qos_class", label=_("QoS Class"))
    qos_class_cons_to_prov = attrs.ChoiceAttr(
        "qos_class_cons_to_prov", label=_("QoS Class (Consumer to Provider)")
    )
    qos_class_prov_to_cons = attrs.ChoiceAttr(
        "qos_class_prov_to_cons", label=_("QoS Class (Provider to Consumer)")
    )
    target_dscp = attrs.ChoiceAttr("target_dscp", label=_("Target DSCP"))
    target_dscp_cons_to_prov = attrs.ChoiceAttr(
        "target_dscp_cons_to_prov", label=_("Target DSCP (Consumer to Provider)")
    )
    target_dscp_prov_to_cons = attrs.ChoiceAttr(
        "target_dscp_prov_to_cons", label=_("Target DSCP (Provider to Consumer)")
    )


class ACIContractSubjectFilterPanel(panels.ObjectAttributesPanel):
    """Identity panel for the ACI Contract Subject Filter detail view."""

    title = _("ACI Contract Subject Filter")
    aci_fabric = attrs.RelatedObjectAttr(
        "aci_fabric", linkify=True, label=_("ACI Fabric")
    )
    aci_tenant = attrs.RelatedObjectAttr(
        "aci_tenant", linkify=True, label=_("ACI Tenant")
    )
    aci_contract = attrs.RelatedObjectAttr(
        "aci_contract", linkify=True, label=_("ACI Contract")
    )
    aci_contract_subject = attrs.RelatedObjectAttr(
        "aci_contract_subject", linkify=True, label=_("ACI Contract Subject")
    )
    aci_contract_filter = attrs.RelatedObjectAttr(
        "aci_contract_filter", linkify=True, label=_("ACI Contract Filter")
    )
    action = attrs.ChoiceAttr("action", label=_("Action"))


class ACIContractSubjectFilterDirectionPanel(panels.ObjectAttributesPanel):
    """Direction panel for the ACI Contract Subject Filter detail view."""

    title = _("Direction Settings")

    apply_direction = attrs.ChoiceAttr("apply_direction", label=_("Apply Direction"))


class ACIContractSubjectFilterDirectivesPanel(panels.ObjectAttributesPanel):
    """Directives panel for the ACI Contract Subject Filter detail view."""

    title = _("Directives Settings")

    log_enabled = attrs.BooleanAttr("log_enabled", label=_("Logging enabled"))
    policy_compression_enabled = attrs.BooleanAttr(
        "policy_compression_enabled", label=_("Policy Compression enabled")
    )


class ACIContractSubjectFilterPriorityPanel(panels.ObjectAttributesPanel):
    """Priority panel for the ACI Contract Subject Filter detail view."""

    title = _("Priority")

    priority = attrs.ChoiceAttr("priority", label=_("(Deny) Priority"))
