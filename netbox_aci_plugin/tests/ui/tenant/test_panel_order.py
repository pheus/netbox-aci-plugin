# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Row-order tests for the tenant domain's declarative UI panels.

Each panel renders its attributes in declaration order, so these pin
the order the retired detail templates authored. Panels declare every
attribute inline rather than inheriting a shared tail, because
ObjectAttributesPanelMeta always places inherited attributes before
locally declared ones and offers no way to reorder them.
"""

from __future__ import annotations

from django.test import SimpleTestCase

from netbox.ui.panels import ObjectAttributesPanel

from ....ui.panels.tenant.app_profiles import ACIAppProfilePanel
from ....ui.panels.tenant.bridge_domains import (
    ACIBridgeDomainAdditionalSettingsPanel,
    ACIBridgeDomainEndpointLearningPanel,
    ACIBridgeDomainForwardingMethodPanel,
    ACIBridgeDomainL3OutBindingPanel,
    ACIBridgeDomainMulticastPanel,
    ACIBridgeDomainPanel,
    ACIBridgeDomainRoutingPanel,
    ACIBridgeDomainSubnetControlPanel,
    ACIBridgeDomainSubnetEndpointLearningPanel,
    ACIBridgeDomainSubnetIPv6Panel,
    ACIBridgeDomainSubnetPanel,
    ACIBridgeDomainSubnetScopePanel,
)
from ....ui.panels.tenant.contract_filters import (
    ACIContractFilterEntryARPPanel,
    ACIContractFilterEntryEthernetPanel,
    ACIContractFilterEntryICMPPanel,
    ACIContractFilterEntryIPProtocolPanel,
    ACIContractFilterEntryPanel,
    ACIContractFilterEntryPortRangePanel,
    ACIContractFilterEntryTCPPanel,
    ACIContractFilterPanel,
)
from ....ui.panels.tenant.contracts import (
    ACIContractPanel,
    ACIContractPriorityPanel,
    ACIContractRelationPanel,
    ACIContractScopePanel,
    ACIContractSubjectDirectionPanel,
    ACIContractSubjectFilterDirectionPanel,
    ACIContractSubjectFilterDirectivesPanel,
    ACIContractSubjectFilterPanel,
    ACIContractSubjectFilterPriorityPanel,
    ACIContractSubjectPanel,
    ACIContractSubjectPriorityPanel,
    ACIContractSubjectServiceGraphPanel,
)
from ....ui.panels.tenant.endpoint_group_bindings import (
    ACIEndpointGroupAAEPBindingPanel,
    ACIEndpointGroupDomainBindingPanel,
)
from ....ui.panels.tenant.endpoint_groups import (
    ACIEndpointGroupForwardingPanel,
    ACIEndpointGroupPanel,
    ACIEndpointGroupPolicyEnforcementPanel,
    ACIEndpointGroupQoSPanel,
    ACIUSegEndpointGroupForwardingPanel,
    ACIUSegEndpointGroupPanel,
    ACIUSegEndpointGroupPolicyEnforcementPanel,
    ACIUSegEndpointGroupQoSPanel,
    ACIUSegNetworkAttributeAssignmentPanel,
    ACIUSegNetworkAttributeEPGSubnetPanel,
    ACIUSegNetworkAttributePanel,
)
from ....ui.panels.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroupPanel,
    ACIEndpointSecurityGroupPolicyEnforcementPanel,
    ACIEsgEndpointGroupSelectorAssignmentPanel,
    ACIEsgEndpointGroupSelectorPanel,
    ACIEsgEndpointSelectorAssignmentPanel,
    ACIEsgEndpointSelectorPanel,
)
from ....ui.panels.tenant.l3outs import (
    ACIExternalEndpointGroupPanel,
    ACIExternalEndpointGroupPolicyPanel,
    ACIExternalSubnetPanel,
    ACIExternalSubnetRouteSummarizationPanel,
    ACIExternalSubnetScopePanel,
    ACIL3OutPanel,
    ACIL3OutPolicyPanel,
    ACIL3OutPolicyReferencesPanel,
    ACIL3OutProtocolsPanel,
)
from ....ui.panels.tenant.tenants import ACITenantPanel
from ....ui.panels.tenant.vrfs import (
    ACIVRFAdditionalSettingsPanel,
    ACIVRFEndpointLearningPanel,
    ACIVRFMulticastPanel,
    ACIVRFPanel,
    ACIVRFPolicyControlPanel,
)
from ..base import layout_panels, layout_views

# Attribute name and accessor, in the order the retired detail template
# rendered each row. The accessor is pinned because a copy-paste slip can
# point a row at a neighbouring field without changing the row order.
EXPECTED_ORDER = {
    ACITenantPanel: [
        ("aci_fabric", "aci_fabric"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIVRFPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
        ("nb_vrf", "nb_vrf"),
    ],
    ACIVRFPolicyControlPanel: [
        ("pc_enforcement_direction", "pc_enforcement_direction"),
        ("pc_enforcement_preference", "pc_enforcement_preference"),
        ("bd_enforcement_enabled", "bd_enforcement_enabled"),
        ("preferred_group_enabled", "preferred_group_enabled"),
    ],
    ACIVRFEndpointLearningPanel: [
        ("ip_data_plane_learning_enabled", "ip_data_plane_learning_enabled"),
    ],
    ACIVRFMulticastPanel: [
        ("pim_ipv4_enabled", "pim_ipv4_enabled"),
        ("pim_ipv6_enabled", "pim_ipv6_enabled"),
    ],
    ACIVRFAdditionalSettingsPanel: [
        ("dns_labels", "dns_labels"),
    ],
    ACIAppProfilePanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIBridgeDomainPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("aci_vrf", "aci_vrf"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIBridgeDomainRoutingPanel: [
        ("unicast_routing_enabled", "unicast_routing_enabled"),
        ("advertise_host_routes_enabled", "advertise_host_routes_enabled"),
        ("ep_move_detection_enabled", "ep_move_detection_enabled"),
        ("mac_address", "mac_address"),
        ("virtual_mac_address", "virtual_mac_address"),
    ],
    ACIBridgeDomainForwardingMethodPanel: [
        ("arp_flooding_enabled", "arp_flooding_enabled"),
        ("unknown_unicast", "unknown_unicast"),
        ("unknown_ipv4_multicast", "unknown_ipv4_multicast"),
        ("unknown_ipv6_multicast", "unknown_ipv6_multicast"),
        ("multi_destination_flooding", "multi_destination_flooding"),
    ],
    ACIBridgeDomainEndpointLearningPanel: [
        ("ip_data_plane_learning_enabled", "ip_data_plane_learning_enabled"),
        ("limit_ip_learn_enabled", "limit_ip_learn_enabled"),
        ("clear_remote_mac_enabled", "clear_remote_mac_enabled"),
    ],
    ACIBridgeDomainMulticastPanel: [
        ("pim_ipv4_enabled", "pim_ipv4_enabled"),
        ("pim_ipv6_enabled", "pim_ipv6_enabled"),
        ("igmp_interface_policy_name", "igmp_interface_policy_name"),
        ("igmp_snooping_policy_name", "igmp_snooping_policy_name"),
        ("pim_ipv4_source_filter", "pim_ipv4_source_filter"),
        ("pim_ipv4_destination_filter", "pim_ipv4_destination_filter"),
    ],
    ACIBridgeDomainAdditionalSettingsPanel: [
        ("dhcp_labels", "dhcp_labels"),
    ],
    ACIBridgeDomainSubnetPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("aci_vrf", "aci_vrf"),
        ("aci_bridge_domain", "aci_bridge_domain"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
        ("preferred_ip_address_enabled", "preferred_ip_address_enabled"),
        ("virtual_ip_enabled", "virtual_ip_enabled"),
    ],
    ACIBridgeDomainSubnetScopePanel: [
        ("advertised_externally_enabled", "advertised_externally_enabled"),
        ("shared_enabled", "shared_enabled"),
    ],
    ACIBridgeDomainSubnetControlPanel: [
        ("igmp_querier_enabled", "igmp_querier_enabled"),
        ("no_default_gateway", "no_default_gateway"),
    ],
    ACIBridgeDomainSubnetEndpointLearningPanel: [
        ("ip_data_plane_learning_enabled", "ip_data_plane_learning_enabled"),
    ],
    ACIBridgeDomainSubnetIPv6Panel: [
        ("nd_ra_enabled", "nd_ra_enabled"),
        ("nd_ra_prefix_policy_name", "nd_ra_prefix_policy_name"),
    ],
    ACIBridgeDomainL3OutBindingPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("aci_vrf", "aci_vrf"),
        ("aci_bridge_domain", "aci_bridge_domain"),
        ("aci_l3out", "aci_l3out"),
    ],
    ACIContractPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIContractScopePanel: [
        ("scope", "scope"),
    ],
    ACIContractPriorityPanel: [
        ("qos_class", "qos_class"),
        ("target_dscp", "target_dscp"),
    ],
    ACIContractRelationPanel: [
        ("aci_fabric", "aci_contract.aci_fabric"),
        ("aci_tenant", "aci_contract.aci_tenant"),
        ("aci_contract", "aci_contract"),
        ("aci_object", "aci_object"),
        ("role", "role"),
    ],
    ACIContractSubjectPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("aci_contract", "aci_contract"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIContractSubjectDirectionPanel: [
        ("apply_both_directions_enabled", "apply_both_directions_enabled"),
        ("reverse_filter_ports_enabled", "reverse_filter_ports_enabled"),
    ],
    ACIContractSubjectServiceGraphPanel: [
        ("service_graph_name", "service_graph_name"),
        ("service_graph_name_cons_to_prov", "service_graph_name_cons_to_prov"),
        ("service_graph_name_prov_to_cons", "service_graph_name_prov_to_cons"),
    ],
    ACIContractSubjectPriorityPanel: [
        ("qos_class", "qos_class"),
        ("qos_class_cons_to_prov", "qos_class_cons_to_prov"),
        ("qos_class_prov_to_cons", "qos_class_prov_to_cons"),
        ("target_dscp", "target_dscp"),
        ("target_dscp_cons_to_prov", "target_dscp_cons_to_prov"),
        ("target_dscp_prov_to_cons", "target_dscp_prov_to_cons"),
    ],
    ACIContractSubjectFilterPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("aci_contract", "aci_contract"),
        ("aci_contract_subject", "aci_contract_subject"),
        ("aci_contract_filter", "aci_contract_filter"),
        ("action", "action"),
    ],
    ACIContractSubjectFilterDirectionPanel: [
        ("apply_direction", "apply_direction"),
    ],
    ACIContractSubjectFilterDirectivesPanel: [
        ("log_enabled", "log_enabled"),
        ("policy_compression_enabled", "policy_compression_enabled"),
    ],
    ACIContractSubjectFilterPriorityPanel: [
        ("priority", "priority"),
    ],
    ACIContractFilterPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIContractFilterEntryPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("aci_contract_filter", "aci_contract_filter"),
        ("name_alias", "name_alias"),
        ("description", "description"),
    ],
    ACIContractFilterEntryEthernetPanel: [
        ("ether_type", "ether_type"),
    ],
    ACIContractFilterEntryARPPanel: [
        ("arp_opc", "arp_opc"),
    ],
    ACIContractFilterEntryIPProtocolPanel: [
        ("ip_protocol", "ip_protocol"),
        ("match_dscp", "match_dscp"),
        ("match_only_fragments_enabled", "match_only_fragments_enabled"),
    ],
    ACIContractFilterEntryICMPPanel: [
        ("icmp_v4_type", "icmp_v4_type"),
        ("icmp_v6_type", "icmp_v6_type"),
    ],
    ACIContractFilterEntryPortRangePanel: [
        ("source_from_port", "source_from_port"),
        ("source_to_port", "source_to_port"),
        ("destination_from_port", "destination_from_port"),
        ("destination_to_port", "destination_to_port"),
    ],
    ACIContractFilterEntryTCPPanel: [
        ("stateful_enabled", "stateful_enabled"),
        ("tcp_rules", "tcp_rules_display"),
    ],
    ACIEndpointGroupPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("aci_app_profile", "aci_app_profile"),
        ("aci_vrf", "aci_vrf"),
        ("aci_bridge_domain", "aci_bridge_domain"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIEndpointGroupPolicyEnforcementPanel: [
        ("preferred_group_member_enabled", "preferred_group_member_enabled"),
        ("intra_epg_isolation_enabled", "intra_epg_isolation_enabled"),
    ],
    ACIEndpointGroupForwardingPanel: [
        ("flood_in_encap_enabled", "flood_in_encap_enabled"),
        ("proxy_arp_enabled", "proxy_arp_enabled"),
    ],
    ACIEndpointGroupQoSPanel: [
        ("qos_class", "qos_class"),
        ("custom_qos_policy_name", "custom_qos_policy_name"),
    ],
    ACIUSegEndpointGroupPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("aci_app_profile", "aci_app_profile"),
        ("aci_vrf", "aci_vrf"),
        ("aci_bridge_domain", "aci_bridge_domain"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIUSegEndpointGroupPolicyEnforcementPanel: [
        ("preferred_group_member_enabled", "preferred_group_member_enabled"),
        ("intra_epg_isolation_enabled", "intra_epg_isolation_enabled"),
    ],
    ACIUSegEndpointGroupForwardingPanel: [
        ("flood_in_encap_enabled", "flood_in_encap_enabled"),
    ],
    ACIUSegEndpointGroupQoSPanel: [
        ("qos_class", "qos_class"),
        ("custom_qos_policy_name", "custom_qos_policy_name"),
    ],
    ACIUSegNetworkAttributePanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("aci_app_profile", "aci_app_profile"),
        ("aci_useg_endpoint_group", "aci_useg_endpoint_group"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("type", "type"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIUSegNetworkAttributeEPGSubnetPanel: [
        ("use_epg_subnet", "use_epg_subnet"),
    ],
    ACIUSegNetworkAttributeAssignmentPanel: [
        ("attr_object", "attr_object"),
    ],
    ACIEndpointGroupDomainBindingPanel: [
        ("aci_epg_object", "aci_epg_object"),
        ("aci_domain_object", "aci_domain_object"),
        ("deployment_immediacy", "deployment_immediacy"),
        ("resolution_immediacy", "resolution_immediacy"),
    ],
    ACIEndpointGroupAAEPBindingPanel: [
        ("aci_endpoint_group", "aci_endpoint_group"),
        ("aci_aaep", "aci_aaep"),
        ("mode", "mode"),
        ("deployment_immediacy", "deployment_immediacy"),
        ("nb_vlan", "nb_vlan"),
        ("encap_vlan_id", "encap_vlan_id"),
        ("effective_encap_vlan_id", "effective_encap_vlan_id"),
        ("primary_nb_vlan", "primary_nb_vlan"),
        ("primary_encap_vlan_id", "primary_encap_vlan_id"),
        ("effective_primary_encap_vlan_id", "effective_primary_encap_vlan_id"),
    ],
    ACIEndpointSecurityGroupPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("aci_app_profile", "aci_app_profile"),
        ("aci_vrf", "aci_vrf"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIEndpointSecurityGroupPolicyEnforcementPanel: [
        ("preferred_group_member_enabled", "preferred_group_member_enabled"),
        ("intra_esg_isolation_enabled", "intra_esg_isolation_enabled"),
    ],
    ACIEsgEndpointGroupSelectorPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("aci_app_profile", "aci_app_profile"),
        ("aci_endpoint_security_group", "aci_endpoint_security_group"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIEsgEndpointGroupSelectorAssignmentPanel: [
        ("aci_tenant", "aci_epg_object.aci_tenant"),
        ("aci_app_profile", "aci_epg_object.aci_app_profile"),
        ("aci_epg_object", "aci_epg_object"),
    ],
    ACIEsgEndpointSelectorPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("aci_app_profile", "aci_app_profile"),
        ("aci_endpoint_security_group", "aci_endpoint_security_group"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIEsgEndpointSelectorAssignmentPanel: [
        ("ep_object", "ep_object"),
    ],
    ACIL3OutPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("aci_vrf", "aci_vrf"),
        ("aci_routed_domain", "aci_routed_domain"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIL3OutPolicyPanel: [
        ("target_dscp", "target_dscp"),
        (
            "import_route_control_enforcement_enabled",
            "import_route_control_enforcement_enabled",
        ),
        (
            "export_route_control_enforcement_enabled",
            "export_route_control_enforcement_enabled",
        ),
    ],
    ACIL3OutProtocolsPanel: [
        ("bgp_enabled", "bgp_enabled"),
        ("ospf_enabled", "ospf_enabled"),
        ("eigrp_enabled", "eigrp_enabled"),
        ("l3_multicast_ipv4_enabled", "l3_multicast_ipv4_enabled"),
        ("l3_multicast_ipv6_enabled", "l3_multicast_ipv6_enabled"),
    ],
    ACIL3OutPolicyReferencesPanel: [
        ("custom_qos_policy_name", "custom_qos_policy_name"),
        ("bfd_policy_name", "bfd_policy_name"),
        ("pim_policy_name", "pim_policy_name"),
        ("igmp_interface_policy_name", "igmp_interface_policy_name"),
        ("ospf_external_policy_name", "ospf_external_policy_name"),
        ("eigrp_interface_policy_name", "eigrp_interface_policy_name"),
        ("interleak_route_map_name", "interleak_route_map_name"),
        (
            "ingress_data_plane_policing_policy_name",
            "ingress_data_plane_policing_policy_name",
        ),
        (
            "egress_data_plane_policing_policy_name",
            "egress_data_plane_policing_policy_name",
        ),
    ],
    ACIExternalEndpointGroupPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("aci_vrf", "aci_vrf"),
        ("aci_l3out", "aci_l3out"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIExternalEndpointGroupPolicyPanel: [
        ("preferred_group_member_enabled", "preferred_group_member_enabled"),
        ("target_dscp", "target_dscp"),
        ("qos_class", "qos_class"),
    ],
    ACIExternalSubnetPanel: [
        ("aci_fabric", "aci_fabric"),
        ("aci_tenant", "aci_tenant"),
        ("aci_l3out", "aci_l3out"),
        ("aci_external_endpoint_group", "aci_external_endpoint_group"),
        ("matched_prefix", "matched_prefix"),
        ("nb_prefix", "nb_prefix"),
        ("name_alias", "name_alias"),
        ("description", "description"),
        ("nb_tenant", "nb_tenant"),
    ],
    ACIExternalSubnetScopePanel: [
        ("import_route_control_enabled", "import_route_control_enabled"),
        ("export_route_control_enabled", "export_route_control_enabled"),
        ("shared_route_control_enabled", "shared_route_control_enabled"),
        ("import_security_enabled", "import_security_enabled"),
        ("shared_security_enabled", "shared_security_enabled"),
        (
            "aggregate_import_route_control_enabled",
            "aggregate_import_route_control_enabled",
        ),
        (
            "aggregate_export_route_control_enabled",
            "aggregate_export_route_control_enabled",
        ),
        (
            "aggregate_shared_route_control_enabled",
            "aggregate_shared_route_control_enabled",
        ),
    ],
    ACIExternalSubnetRouteSummarizationPanel: [
        ("bgp_route_summarization_enabled", "bgp_route_summarization_enabled"),
        ("bgp_route_summarization_policy_name", "bgp_route_summarization_policy_name"),
        ("ospf_route_summarization_enabled", "ospf_route_summarization_enabled"),
        (
            "ospf_route_summarization_policy_name",
            "ospf_route_summarization_policy_name",
        ),
        ("eigrp_route_summarization_enabled", "eigrp_route_summarization_enabled"),
    ],
}


class TenantPanelAttributeOrderTestCase(SimpleTestCase):
    """Pin the attribute order of every tenant domain panel."""

    def test_panels_declare_attributes_in_the_authored_order(self) -> None:
        """Each panel keeps the row order of the template it replaced."""
        for panel_class, expected in EXPECTED_ORDER.items():
            with self.subTest(panel=panel_class.__name__):
                pairs = [
                    (name, attr.accessor) for name, attr in panel_class._attrs.items()
                ]
                self.assertEqual(pairs, expected)

    def test_every_declared_panel_is_pinned(self) -> None:
        """A panel added to a layout without a pin fails here."""
        declared = {
            type(panel)
            for view_class in layout_views("netbox_aci_plugin.views.tenant")
            for panel in layout_panels(view_class)
            if isinstance(panel, ObjectAttributesPanel)
        }
        self.assertCountEqual(EXPECTED_ORDER.keys(), declared)
