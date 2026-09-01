# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for the tenant domain's declarative UI panels.

Covers only the non-obvious attrs: the GenericForeignKeyAttr rows that
collapse a retired template's separate type-and-value row pair into
one row, the dual-GFK Endpoint Group Domain Binding card, the ESG EPG
Selector's TemplatedAttr (which core does not test at all, since it
has no precedent for a dynamic row label), and the Contract Filter
Entry's tcp_rules_display property surfaced through a TextAttr.
"""

from __future__ import annotations

from ipam.models import IPAddress
from netbox.ui import attrs

from ....choices import ContractFilterTCPRulesChoices, VLANAllocationModeChoices
from ....models.access_policies.domains import ACIPhysicalDomain
from ....models.access_policies.vlan_pools import ACIVLANPool
from ....models.fabric.fabrics import ACIFabric
from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.bridge_domains import ACIBridgeDomain
from ....models.tenant.contract_filters import ACIContractFilter, ACIContractFilterEntry
from ....models.tenant.contracts import ACIContract, ACIContractRelation
from ....models.tenant.endpoint_group_bindings import ACIEndpointGroupDomainBinding
from ....models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
    ACIUSegNetworkAttribute,
)
from ....models.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroup,
    ACIEsgEndpointGroupSelector,
    ACIEsgEndpointSelector,
)
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF
from ....ui.panels.tenant.contract_filters import ACIContractFilterEntryTCPPanel
from ....ui.panels.tenant.contracts import ACIContractRelationPanel
from ....ui.panels.tenant.endpoint_group_bindings import (
    ACIEndpointGroupDomainBindingPanel,
)
from ....ui.panels.tenant.endpoint_groups import ACIUSegNetworkAttributeAssignmentPanel
from ....ui.panels.tenant.endpoint_security_groups import (
    ACIEsgEndpointGroupSelectorAssignmentPanel,
    ACIEsgEndpointSelectorAssignmentPanel,
)
from ..base import ACIBaseUITestCase


class ACIContractRelationPanelTestCase(ACIBaseUITestCase):
    """Unit tests for the ACI Object GFK row on ACIContractRelationPanel."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractRelationPanel tests."""
        aci_fabric = ACIFabric.objects.create(
            name="ACIUIContractRelationFabric", fabric_id=1, infra_vlan_vid=100
        )
        aci_tenant = ACITenant.objects.create(
            name="ACIUIContractRelationTenant", aci_fabric=aci_fabric
        )
        aci_app_profile = ACIAppProfile.objects.create(
            name="ACIUIContractRelationAppProfile", aci_tenant=aci_tenant
        )
        aci_vrf = ACIVRF.objects.create(
            name="ACIUIContractRelationVRF", aci_tenant=aci_tenant
        )
        aci_bd = ACIBridgeDomain.objects.create(
            name="ACIUIContractRelationBD", aci_tenant=aci_tenant, aci_vrf=aci_vrf
        )
        cls.aci_epg = ACIEndpointGroup.objects.create(
            name="ACIUIContractRelationEPG",
            aci_app_profile=aci_app_profile,
            aci_bridge_domain=aci_bd,
        )
        aci_contract = ACIContract.objects.create(
            name="ACIUIContractRelationContract", aci_tenant=aci_tenant
        )
        cls.aci_contract_relation = ACIContractRelation.objects.create(
            aci_contract=aci_contract, aci_object=cls.aci_epg
        )

    def test_aci_object_attr_is_a_linkified_gfk(self) -> None:
        """aci_object is a linkified GenericForeignKeyAttr."""
        attr = ACIContractRelationPanel._attrs["aci_object"]
        self.assertIsInstance(attr, attrs.GenericForeignKeyAttr)
        self.assertEqual(attr.accessor, "aci_object")
        self.assertTrue(attr.linkify)

    def test_aci_object_get_value_resolves_the_linked_object(self) -> None:
        """The ACI Object row resolves to the linked EPG."""
        attr = ACIContractRelationPanel._attrs["aci_object"]
        self.assertEqual(attr.get_value(self.aci_contract_relation), self.aci_epg)


class ACIEndpointGroupDomainBindingPanelTestCase(ACIBaseUITestCase):
    """Unit tests for the dual-GFK ACIEndpointGroupDomainBindingPanel."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEndpointGroupDomainBindingPanel tests."""
        aci_fabric = ACIFabric.objects.create(
            name="ACIUIDomainBindingFabric", fabric_id=1, infra_vlan_vid=100
        )
        aci_tenant = ACITenant.objects.create(
            name="ACIUIDomainBindingTenant", aci_fabric=aci_fabric
        )
        aci_app_profile = ACIAppProfile.objects.create(
            name="ACIUIDomainBindingAppProfile", aci_tenant=aci_tenant
        )
        aci_vrf = ACIVRF.objects.create(
            name="ACIUIDomainBindingVRF", aci_tenant=aci_tenant
        )
        aci_bd = ACIBridgeDomain.objects.create(
            name="ACIUIDomainBindingBD", aci_tenant=aci_tenant, aci_vrf=aci_vrf
        )
        cls.aci_epg = ACIEndpointGroup.objects.create(
            name="ACIUIDomainBindingEPG",
            aci_app_profile=aci_app_profile,
            aci_bridge_domain=aci_bd,
        )
        aci_vlan_pool = ACIVLANPool.objects.create(
            name="ACIUIDomainBindingVLANPool",
            aci_fabric=aci_fabric,
            allocation_mode=VLANAllocationModeChoices.MODE_STATIC,
        )
        cls.aci_physical_domain = ACIPhysicalDomain.objects.create(
            name="ACIUIDomainBindingPhysicalDomain",
            aci_fabric=aci_fabric,
            aci_vlan_pool=aci_vlan_pool,
        )
        cls.aci_binding = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg, aci_domain_object=cls.aci_physical_domain
        )

    def test_aci_epg_object_attr_is_a_linkified_gfk(self) -> None:
        """aci_epg_object is a linkified GenericForeignKeyAttr."""
        attr = ACIEndpointGroupDomainBindingPanel._attrs["aci_epg_object"]
        self.assertIsInstance(attr, attrs.GenericForeignKeyAttr)
        self.assertEqual(attr.accessor, "aci_epg_object")
        self.assertTrue(attr.linkify)

    def test_aci_domain_object_attr_is_a_linkified_gfk(self) -> None:
        """aci_domain_object is a linkified GenericForeignKeyAttr."""
        attr = ACIEndpointGroupDomainBindingPanel._attrs["aci_domain_object"]
        self.assertIsInstance(attr, attrs.GenericForeignKeyAttr)
        self.assertEqual(attr.accessor, "aci_domain_object")
        self.assertTrue(attr.linkify)

    def test_both_gfk_rows_resolve_their_own_side(self) -> None:
        """Each GFK row resolves its own side, not the other's."""
        epg_attr = ACIEndpointGroupDomainBindingPanel._attrs["aci_epg_object"]
        domain_attr = ACIEndpointGroupDomainBindingPanel._attrs["aci_domain_object"]
        self.assertEqual(epg_attr.get_value(self.aci_binding), self.aci_epg)
        self.assertEqual(
            domain_attr.get_value(self.aci_binding), self.aci_physical_domain
        )


class ACIUSegNetworkAttributeAssignmentPanelTestCase(ACIBaseUITestCase):
    """Unit tests for the attr_object GFK row on the Assignment panel."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIUSegNetworkAttributeAssignmentPanel."""
        aci_fabric = ACIFabric.objects.create(
            name="ACIUIUSegAttrFabric", fabric_id=1, infra_vlan_vid=100
        )
        aci_tenant = ACITenant.objects.create(
            name="ACIUIUSegAttrTenant", aci_fabric=aci_fabric
        )
        aci_app_profile = ACIAppProfile.objects.create(
            name="ACIUIUSegAttrAppProfile", aci_tenant=aci_tenant
        )
        aci_vrf = ACIVRF.objects.create(name="ACIUIUSegAttrVRF", aci_tenant=aci_tenant)
        aci_bd = ACIBridgeDomain.objects.create(
            name="ACIUIUSegAttrBD", aci_tenant=aci_tenant, aci_vrf=aci_vrf
        )
        aci_useg_epg = ACIUSegEndpointGroup.objects.create(
            name="ACIUIUSegAttrEPG",
            aci_app_profile=aci_app_profile,
            aci_bridge_domain=aci_bd,
        )
        cls.ip_address = IPAddress.objects.create(address="192.0.2.1/32")
        cls.aci_useg_attribute = ACIUSegNetworkAttribute.objects.create(
            name="ACIUIUSegAttrNetworkAttr",
            aci_useg_endpoint_group=aci_useg_epg,
            attr_object=cls.ip_address,
        )

    def test_attr_object_attr_is_a_linkified_gfk(self) -> None:
        """attr_object is a linkified GenericForeignKeyAttr."""
        attr = ACIUSegNetworkAttributeAssignmentPanel._attrs["attr_object"]
        self.assertIsInstance(attr, attrs.GenericForeignKeyAttr)
        self.assertEqual(attr.accessor, "attr_object")
        self.assertTrue(attr.linkify)

    def test_attr_object_get_value_resolves_the_linked_object(self) -> None:
        """The Attribute Object row resolves to the linked IP address."""
        attr = ACIUSegNetworkAttributeAssignmentPanel._attrs["attr_object"]
        self.assertEqual(attr.get_value(self.aci_useg_attribute), self.ip_address)


class ACIEsgEndpointSelectorAssignmentPanelTestCase(ACIBaseUITestCase):
    """Unit tests for the ep_object GFK row on the Endpoint Assignment card."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEsgEndpointSelectorAssignmentPanel tests."""
        aci_fabric = ACIFabric.objects.create(
            name="ACIUIEpSelectorFabric", fabric_id=1, infra_vlan_vid=100
        )
        aci_tenant = ACITenant.objects.create(
            name="ACIUIEpSelectorTenant", aci_fabric=aci_fabric
        )
        aci_app_profile = ACIAppProfile.objects.create(
            name="ACIUIEpSelectorAppProfile", aci_tenant=aci_tenant
        )
        aci_vrf = ACIVRF.objects.create(
            name="ACIUIEpSelectorVRF", aci_tenant=aci_tenant
        )
        aci_esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIUIEpSelectorESG",
            aci_app_profile=aci_app_profile,
            aci_vrf=aci_vrf,
        )
        cls.ip_address = IPAddress.objects.create(address="192.0.2.2/32")
        cls.aci_ep_selector = ACIEsgEndpointSelector.objects.create(
            name="ACIUIEpSelector",
            aci_endpoint_security_group=aci_esg,
            ep_object=cls.ip_address,
        )

    def test_ep_object_attr_is_a_linkified_gfk(self) -> None:
        """ep_object is a linkified GenericForeignKeyAttr."""
        attr = ACIEsgEndpointSelectorAssignmentPanel._attrs["ep_object"]
        self.assertIsInstance(attr, attrs.GenericForeignKeyAttr)
        self.assertEqual(attr.accessor, "ep_object")
        self.assertTrue(attr.linkify)

    def test_ep_object_get_value_resolves_the_linked_object(self) -> None:
        """The Endpoint Object row resolves to the linked IP address."""
        attr = ACIEsgEndpointSelectorAssignmentPanel._attrs["ep_object"]
        self.assertEqual(attr.get_value(self.aci_ep_selector), self.ip_address)


class ACIEsgEndpointGroupSelectorAssignmentPanelTestCase(ACIBaseUITestCase):
    """Unit tests for the dynamic-label EPG row.

    The retired template used the selected object's content type name
    as the row's ``<th>``, which ObjectAttributesPanel cannot express
    since a panel's row label is fixed at attr-declaration time. The
    TemplatedAttr renders the type as a muted sub-line instead, and
    core carries no test coverage for TemplatedAttr at all.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEsgEndpointGroupSelectorAssignmentPanel."""
        aci_fabric = ACIFabric.objects.create(
            name="ACIUIEpgSelectorFabric", fabric_id=1, infra_vlan_vid=100
        )
        aci_tenant = ACITenant.objects.create(
            name="ACIUIEpgSelectorTenant", aci_fabric=aci_fabric
        )
        aci_app_profile = ACIAppProfile.objects.create(
            name="ACIUIEpgSelectorAppProfile", aci_tenant=aci_tenant
        )
        aci_vrf = ACIVRF.objects.create(
            name="ACIUIEpgSelectorVRF", aci_tenant=aci_tenant
        )
        aci_bd = ACIBridgeDomain.objects.create(
            name="ACIUIEpgSelectorBD", aci_tenant=aci_tenant, aci_vrf=aci_vrf
        )
        cls.aci_epg = ACIEndpointGroup.objects.create(
            name="ACIUIEpgSelectorEPG",
            aci_app_profile=aci_app_profile,
            aci_bridge_domain=aci_bd,
        )
        aci_esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIUIEpgSelectorESG",
            aci_app_profile=aci_app_profile,
            aci_vrf=aci_vrf,
        )
        cls.aci_epg_selector = ACIEsgEndpointGroupSelector.objects.create(
            name="ACIUIEpgSelector",
            aci_endpoint_security_group=aci_esg,
            aci_epg_object=cls.aci_epg,
        )

    def test_aci_epg_object_attr_is_templated(self) -> None:
        """aci_epg_object is a TemplatedAttr on the plugin's own partial."""
        attr = ACIEsgEndpointGroupSelectorAssignmentPanel._attrs["aci_epg_object"]
        self.assertIsInstance(attr, attrs.TemplatedAttr)
        self.assertEqual(attr.accessor, "aci_epg_object")
        self.assertEqual(
            attr.template_name,
            "netbox_aci_plugin/attrs/esg_endpoint_group_selector.html",
        )

    def test_aci_epg_object_get_value_resolves_the_linked_object(self) -> None:
        """The dynamic-label row resolves to the linked EPG."""
        attr = ACIEsgEndpointGroupSelectorAssignmentPanel._attrs["aci_epg_object"]
        self.assertEqual(attr.get_value(self.aci_epg_selector), self.aci_epg)


class ACIContractFilterEntryTCPPanelTestCase(ACIBaseUITestCase):
    """Unit tests for the tcp_rules row reading tcp_rules_display."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractFilterEntryTCPPanel tests."""
        aci_fabric = ACIFabric.objects.create(
            name="ACIUITCPPanelFabric", fabric_id=1, infra_vlan_vid=100
        )
        aci_tenant = ACITenant.objects.create(
            name="ACIUITCPPanelTenant", aci_fabric=aci_fabric
        )
        cls.aci_contract_filter = ACIContractFilter.objects.create(
            name="ACIUITCPPanelFilter", aci_tenant=aci_tenant
        )

    def test_tcp_rules_attr_reads_the_display_property(self) -> None:
        """tcp_rules is a TextAttr on the tcp_rules_display property."""
        attr = ACIContractFilterEntryTCPPanel._attrs["tcp_rules"]
        self.assertIsInstance(attr, attrs.TextAttr)
        self.assertEqual(attr.accessor, "tcp_rules_display")

    def test_tcp_rules_get_value_joins_the_choiceset_labels(self) -> None:
        """The Rules row resolves to a comma-joined string when populated."""
        entry = ACIContractFilterEntry.objects.create(
            name="ACIUITCPPanelEntryPopulated",
            aci_contract_filter=self.aci_contract_filter,
            tcp_rules=[
                ContractFilterTCPRulesChoices.TCP_SYN,
                ContractFilterTCPRulesChoices.TCP_FINISH,
            ],
        )
        attr = ACIContractFilterEntryTCPPanel._attrs["tcp_rules"]
        expected = ", ".join(str(label) for label in entry.get_tcp_rules_display())
        self.assertEqual(attr.get_value(entry), expected)
        self.assertIn(",", attr.get_value(entry))

    def test_tcp_rules_get_value_is_none_for_empty_list(self) -> None:
        """The Rules row resolves to None (the placeholder path) when empty."""
        entry = ACIContractFilterEntry.objects.create(
            name="ACIUITCPPanelEntryEmpty",
            aci_contract_filter=self.aci_contract_filter,
            tcp_rules=[],
        )
        attr = ACIContractFilterEntryTCPPanel._attrs["tcp_rules"]
        self.assertIsNone(attr.get_value(entry))
