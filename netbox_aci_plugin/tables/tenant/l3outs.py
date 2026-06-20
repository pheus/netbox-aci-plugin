# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tables for tenant L3Out models."""

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns

from ...models.tenant.l3outs import (
    ACIExternalEndpointGroup,
    ACIExternalSubnet,
    ACIL3Out,
)


class ACIL3OutTable(NetBoxTable):
    """Table for ACIL3Out model."""

    name = tables.Column(linkify=True)
    name_alias = tables.Column(verbose_name=_("Alias"), linkify=True)
    aci_fabric = tables.Column(
        verbose_name=_("ACI Fabric"),
        accessor="aci_tenant__aci_fabric",
        linkify=True,
    )
    aci_tenant = tables.Column(verbose_name=_("ACI Tenant"), linkify=True)
    aci_vrf = tables.Column(verbose_name=_("ACI VRF"), linkify=True)
    aci_routed_domain = tables.Column(verbose_name=_("ACI Routed Domain"), linkify=True)
    nb_tenant = tables.Column(verbose_name=_("NetBox Tenant"), linkify=True)
    target_dscp = columns.ChoiceFieldColumn()
    import_route_control_enforcement_enabled = columns.BooleanColumn(
        verbose_name=_("Import RC enforce"),
    )
    export_route_control_enforcement_enabled = columns.BooleanColumn(
        verbose_name=_("Export RC enforce"),
    )
    bgp_enabled = columns.BooleanColumn(verbose_name=_("BGP"))
    ospf_enabled = columns.BooleanColumn(verbose_name=_("OSPF"))
    eigrp_enabled = columns.BooleanColumn(verbose_name=_("EIGRP"))
    l3_multicast_ipv4_enabled = columns.BooleanColumn(
        verbose_name=_("L3 multicast IPv4"),
    )
    l3_multicast_ipv6_enabled = columns.BooleanColumn(
        verbose_name=_("L3 multicast IPv6"),
    )
    multipod_enabled = columns.BooleanColumn(verbose_name=_("Multipod"))
    owner_group = tables.Column(
        accessor="owner__group",
        linkify=True,
        verbose_name=_("Owner Group"),
    )
    owner = tables.Column(
        linkify=True,
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIL3Out
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_tenant",
            "aci_vrf",
            "aci_routed_domain",
            "target_dscp",
            "import_route_control_enforcement_enabled",
            "export_route_control_enforcement_enabled",
            "bgp_enabled",
            "ospf_enabled",
            "eigrp_enabled",
            "l3_multicast_ipv4_enabled",
            "l3_multicast_ipv6_enabled",
            "multipod_enabled",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_fabric",
            "aci_tenant",
            "aci_vrf",
            "aci_routed_domain",
            "export_route_control_enforcement_enabled",
            "bgp_enabled",
            "ospf_enabled",
        )


class ACIExternalEndpointGroupTable(NetBoxTable):
    """Table for ACIExternalEndpointGroup model."""

    name = tables.Column(linkify=True)
    name_alias = tables.Column(verbose_name=_("Alias"), linkify=True)
    aci_fabric = tables.Column(
        verbose_name=_("ACI Fabric"),
        accessor="aci_l3out__aci_tenant__aci_fabric",
        linkify=True,
    )
    aci_tenant = tables.Column(
        verbose_name=_("ACI Tenant"),
        accessor="aci_l3out__aci_tenant",
        linkify=True,
    )
    aci_vrf = tables.Column(
        verbose_name=_("ACI VRF"),
        accessor="aci_l3out__aci_vrf",
        linkify=True,
    )
    aci_l3out = tables.Column(verbose_name=_("ACI L3Out"), linkify=True)
    nb_tenant = tables.Column(verbose_name=_("NetBox Tenant"), linkify=True)
    preferred_group_member_enabled = columns.BooleanColumn(
        verbose_name=_("Preferred member"),
    )
    qos_class = columns.ChoiceFieldColumn()
    target_dscp = columns.ChoiceFieldColumn()
    owner_group = tables.Column(
        accessor="owner__group",
        linkify=True,
        verbose_name=_("Owner Group"),
    )
    owner = tables.Column(
        linkify=True,
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIExternalEndpointGroup
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_tenant",
            "aci_vrf",
            "aci_l3out",
            "preferred_group_member_enabled",
            "qos_class",
            "target_dscp",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_fabric",
            "aci_tenant",
            "aci_vrf",
            "aci_l3out",
            "preferred_group_member_enabled",
            "qos_class",
        )


class ACIExternalEndpointGroupReducedTable(NetBoxTable):
    """Reduced table for ACIExternalEndpointGroup model."""

    name = tables.Column(linkify=True)
    preferred_group_member_enabled = columns.BooleanColumn(
        verbose_name=_("Preferred member"),
    )
    qos_class = columns.ChoiceFieldColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIExternalEndpointGroup
        fields: tuple = (
            "pk",
            "id",
            "name",
            "preferred_group_member_enabled",
            "qos_class",
        )
        default_columns: tuple = ("name", "preferred_group_member_enabled", "qos_class")


class ACIExternalSubnetTable(NetBoxTable):
    """Table for ACIExternalSubnet model."""

    name = tables.Column(linkify=True)
    name_alias = tables.Column(verbose_name=_("Alias"), linkify=True)
    aci_fabric = tables.Column(
        verbose_name=_("ACI Fabric"),
        accessor="aci_external_endpoint_group__aci_l3out__aci_tenant__aci_fabric",
        linkify=True,
    )
    aci_tenant = tables.Column(
        verbose_name=_("ACI Tenant"),
        accessor="aci_external_endpoint_group__aci_l3out__aci_tenant",
        linkify=True,
    )
    aci_l3out = tables.Column(
        verbose_name=_("ACI L3Out"),
        accessor="aci_external_endpoint_group__aci_l3out",
        linkify=True,
    )
    aci_external_endpoint_group = tables.Column(
        verbose_name=_("ACI External EPG"),
        linkify=True,
    )
    matched_prefix = tables.Column(linkify=True)
    nb_prefix = tables.Column(linkify=True)
    import_route_control_enabled = columns.BooleanColumn(verbose_name=_("Import RC"))
    export_route_control_enabled = columns.BooleanColumn(verbose_name=_("Export RC"))
    shared_route_control_enabled = columns.BooleanColumn(verbose_name=_("Shared RC"))
    import_security_enabled = columns.BooleanColumn(verbose_name=_("Import security"))
    shared_security_enabled = columns.BooleanColumn(verbose_name=_("Shared security"))
    aggregate_import_route_control_enabled = columns.BooleanColumn(
        verbose_name=_("Agg. import RC"),
    )
    aggregate_export_route_control_enabled = columns.BooleanColumn(
        verbose_name=_("Agg. export RC"),
    )
    aggregate_shared_route_control_enabled = columns.BooleanColumn(
        verbose_name=_("Agg. shared RC"),
    )
    bgp_route_summarization_enabled = columns.BooleanColumn(
        verbose_name=_("BGP summary"),
    )
    ospf_route_summarization_enabled = columns.BooleanColumn(
        verbose_name=_("OSPF summary"),
    )
    eigrp_route_summarization_enabled = columns.BooleanColumn(
        verbose_name=_("EIGRP summary"),
    )
    owner_group = tables.Column(
        accessor="owner__group",
        linkify=True,
        verbose_name=_("Owner Group"),
    )
    owner = tables.Column(
        linkify=True,
    )
    tags = columns.TagColumn()
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = ACIExternalSubnet
        fields: tuple = (
            "pk",
            "id",
            "name",
            "name_alias",
            "description",
            "aci_fabric",
            "aci_tenant",
            "aci_l3out",
            "aci_external_endpoint_group",
            "matched_prefix",
            "nb_prefix",
            "import_route_control_enabled",
            "export_route_control_enabled",
            "shared_route_control_enabled",
            "import_security_enabled",
            "shared_security_enabled",
            "nb_tenant",
            "owner",
            "comments",
            "tags",
        )
        default_columns: tuple = (
            "name",
            "name_alias",
            "aci_fabric",
            "aci_tenant",
            "aci_l3out",
            "aci_external_endpoint_group",
            "matched_prefix",
            "export_route_control_enabled",
            "shared_security_enabled",
        )


class ACIExternalSubnetReducedTable(NetBoxTable):
    """Reduced table for ACIExternalSubnet model."""

    name = tables.Column(linkify=True)
    matched_prefix = tables.Column(linkify=True)
    import_route_control_enabled = columns.BooleanColumn(verbose_name=_("Import RC"))
    export_route_control_enabled = columns.BooleanColumn(verbose_name=_("Export RC"))
    shared_security_enabled = columns.BooleanColumn(verbose_name=_("Shared security"))

    class Meta(NetBoxTable.Meta):
        model = ACIExternalSubnet
        fields: tuple = (
            "pk",
            "id",
            "name",
            "matched_prefix",
            "import_route_control_enabled",
            "export_route_control_enabled",
            "shared_security_enabled",
        )
        default_columns: tuple = (
            "matched_prefix",
            "import_route_control_enabled",
            "export_route_control_enabled",
            "shared_security_enabled",
        )
