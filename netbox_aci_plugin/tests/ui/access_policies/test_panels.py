# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for the access-policies domain's declarative UI panels.

Complements tests/views/access_policies/, which pins the two
permission-scoped ContextTablePanel cards through full HTTP round
trips. These tests assert on the declared structure (accessor, label,
attr type) and on get_value()'s resolved data, never on rendered
markup, for the rows a plain attr-table row would not exercise
meaningfully: the collapsed AAEP domain GFK, the LAG type derived
property, the security domains array, and the four new *_count
properties added for this port.
"""

from __future__ import annotations

from netbox.ui import attrs

from ....choices import LeafInterfacePolicyGroupTypeChoices, VLANAllocationModeChoices
from ....models.access_policies.aaep import (
    ACIAAEPDomainBinding,
    ACIAttachableAccessEntityProfile,
)
from ....models.access_policies.domains import ACIPhysicalDomain
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ....models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
    ACILeafInterfaceSelector,
)
from ....models.access_policies.leaf_switch_profiles import (
    ACILeafSelector,
    ACILeafSwitchProfile,
)
from ....models.access_policies.vlan_pools import ACIVLANPool
from ....models.fabric.fabrics import ACIFabric
from ....ui.panels.access_policies.aaep import ACIAAEPDomainBindingPanel
from ....ui.panels.access_policies.domains import ACIPhysicalDomainPanel
from ....ui.panels.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroupPanel,
)
from ....ui.panels.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfilePanel,
    ACILeafInterfaceSelectorPanel,
)
from ....ui.panels.access_policies.leaf_switch_profiles import (
    ACILeafSelectorPanel,
    ACILeafSwitchProfilePanel,
)
from ..base import ACIBaseUITestCase


class ACIAAEPDomainBindingPanelTestCase(ACIBaseUITestCase):
    """Unit tests for the collapsed ACI Domain Object GFK row."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIAAEPDomainBindingPanel tests."""
        aci_fabric = ACIFabric.objects.create(
            name="ACIUIAAEPBindingFabric", fabric_id=1, infra_vlan_vid=100
        )
        aci_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACIUIAAEPBindingAAEP", aci_fabric=aci_fabric
        )
        aci_vlan_pool = ACIVLANPool.objects.create(
            name="ACIUIAAEPBindingVLANPool",
            aci_fabric=aci_fabric,
            allocation_mode=VLANAllocationModeChoices.MODE_STATIC,
        )
        cls.aci_physical_domain = ACIPhysicalDomain.objects.create(
            name="ACIUIAAEPBindingPhysicalDomain",
            aci_fabric=aci_fabric,
            aci_vlan_pool=aci_vlan_pool,
        )
        cls.aci_binding = ACIAAEPDomainBinding.objects.create(
            aci_aaep=aci_aaep, aci_domain_object=cls.aci_physical_domain
        )

    def test_aci_domain_object_attr_is_a_linkified_gfk(self) -> None:
        """aci_domain_object is a linkified GenericForeignKeyAttr."""
        attr = ACIAAEPDomainBindingPanel._attrs["aci_domain_object"]
        self.assertIsInstance(attr, attrs.GenericForeignKeyAttr)
        self.assertEqual(attr.accessor, "aci_domain_object")
        self.assertTrue(attr.linkify)

    def test_aci_domain_object_get_value_resolves_the_linked_object(self) -> None:
        """The GFK row resolves to the bound Physical Domain."""
        attr = ACIAAEPDomainBindingPanel._attrs["aci_domain_object"]
        self.assertEqual(attr.get_value(self.aci_binding), self.aci_physical_domain)


class ACILeafInterfacePolicyGroupPanelLagTypeTestCase(ACIBaseUITestCase):
    """Unit tests for the LAG Type derived-property row.

    lag_type is a plain TextAttr, not a ChoiceAttr: it reads a
    computed property with no get_lag_type_display()/_color() pair,
    unlike the adjacent group_type badge row.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafInterfacePolicyGroupPanel tests."""
        aci_fabric = ACIFabric.objects.create(
            name="ACIUILAGTypeFabric", fabric_id=1, infra_vlan_vid=100
        )
        cls.access_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACIUILAGTypeAccess",
            aci_fabric=aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        cls.pc_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACIUILAGTypePC",
            aci_fabric=aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_PC,
        )
        cls.vpc_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACIUILAGTypeVPC",
            aci_fabric=aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_VPC,
        )

    def test_lag_type_attr_is_a_text_attr(self) -> None:
        """lag_type is a TextAttr on the lag_type property."""
        attr = ACILeafInterfacePolicyGroupPanel._attrs["lag_type"]
        self.assertIsInstance(attr, attrs.TextAttr)
        self.assertEqual(attr.accessor, "lag_type")

    def test_lag_type_get_value_is_none_for_access(self) -> None:
        """An access group's LAG Type row resolves to None."""
        attr = ACILeafInterfacePolicyGroupPanel._attrs["lag_type"]
        self.assertIsNone(attr.get_value(self.access_group))

    def test_lag_type_get_value_for_port_channel(self) -> None:
        """A port channel group's LAG Type row resolves to 'link'."""
        attr = ACILeafInterfacePolicyGroupPanel._attrs["lag_type"]
        self.assertEqual(attr.get_value(self.pc_group), "link")

    def test_lag_type_get_value_for_virtual_port_channel(self) -> None:
        """A virtual port channel group's LAG Type row resolves to 'node'."""
        attr = ACILeafInterfacePolicyGroupPanel._attrs["lag_type"]
        self.assertEqual(attr.get_value(self.vpc_group), "node")


class ACIPhysicalDomainPanelSecurityDomainsTestCase(ACIBaseUITestCase):
    """Unit tests for the Security Domains array row.

    Shared verbatim with ACIRoutedDomainPanel, which the panel-order
    test already pins as its own declared attribute.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIPhysicalDomainPanel tests."""
        aci_fabric = ACIFabric.objects.create(
            name="ACIUISecurityDomainsFabric", fabric_id=1, infra_vlan_vid=100
        )
        aci_vlan_pool = ACIVLANPool.objects.create(
            name="ACIUISecurityDomainsVLANPool",
            aci_fabric=aci_fabric,
            allocation_mode=VLANAllocationModeChoices.MODE_STATIC,
        )
        cls.aci_domain_bare = ACIPhysicalDomain.objects.create(
            name="ACIUISecurityDomainsBare",
            aci_fabric=aci_fabric,
            aci_vlan_pool=aci_vlan_pool,
        )
        cls.aci_domain_scoped = ACIPhysicalDomain.objects.create(
            name="ACIUISecurityDomainsScoped",
            aci_fabric=aci_fabric,
            aci_vlan_pool=aci_vlan_pool,
            security_domains=["sd-one", "sd-two"],
        )

    def test_security_domains_attr_is_an_array_attr(self) -> None:
        """security_domains is an ArrayAttr on the model field."""
        attr = ACIPhysicalDomainPanel._attrs["security_domains"]
        self.assertIsInstance(attr, attrs.ArrayAttr)
        self.assertEqual(attr.accessor, "security_domains")

    def test_security_domains_get_value_is_none_for_empty_list(self) -> None:
        """An empty security_domains list resolves to None."""
        attr = ACIPhysicalDomainPanel._attrs["security_domains"]
        self.assertIsNone(attr.get_value(self.aci_domain_bare))

    def test_security_domains_get_value_joins_the_names(self) -> None:
        """A populated security_domains list joins as 'a, b'."""
        attr = ACIPhysicalDomainPanel._attrs["security_domains"]
        self.assertEqual(attr.get_value(self.aci_domain_scoped), "sd-one, sd-two")


class AccessPoliciesCountAttrTestCase(ACIBaseUITestCase):
    """Unit tests for the four new *_count NumericAttr rows.

    Each property's own zero/nonzero matrix is pinned at the model
    layer (tests/models/access_policies/); these confirm the panel row
    is wired to the right accessor and surfaces its value.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the *_count attr rows."""
        aci_fabric = ACIFabric.objects.create(
            name="ACIUICountAttrFabric", fabric_id=1, infra_vlan_vid=100
        )
        cls.aci_leaf_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACIUICountAttrInterfaceProfile", aci_fabric=aci_fabric
        )
        cls.aci_leaf_interface_selector = ACILeafInterfaceSelector.objects.create(
            name="ACIUICountAttrInterfaceSelector",
            aci_leaf_interface_profile=cls.aci_leaf_interface_profile,
        )
        cls.aci_leaf_switch_profile = ACILeafSwitchProfile.objects.create(
            name="ACIUICountAttrSwitchProfile", aci_fabric=aci_fabric
        )
        cls.aci_leaf_selector = ACILeafSelector.objects.create(
            name="ACIUICountAttrSelector",
            aci_leaf_switch_profile=cls.aci_leaf_switch_profile,
        )
        ACILeafInterfaceSelector.objects.create(
            name="ACIUICountAttrInterfaceSelector2",
            aci_leaf_interface_profile=cls.aci_leaf_interface_profile,
        )
        ACILeafSelector.objects.create(
            name="ACIUICountAttrSelector2",
            aci_leaf_switch_profile=cls.aci_leaf_switch_profile,
        )

    def test_leaf_interface_profile_selector_count_attr(self) -> None:
        """ACILeafInterfaceProfilePanel counts its Selectors."""
        attr = ACILeafInterfaceProfilePanel._attrs["selector_count"]
        self.assertIsInstance(attr, attrs.NumericAttr)
        self.assertEqual(attr.accessor, "selector_count")
        self.assertEqual(attr.get_value(self.aci_leaf_interface_profile), 2)

    def test_leaf_switch_profile_selector_count_attr(self) -> None:
        """ACILeafSwitchProfilePanel counts its Selectors."""
        attr = ACILeafSwitchProfilePanel._attrs["selector_count"]
        self.assertIsInstance(attr, attrs.NumericAttr)
        self.assertEqual(attr.accessor, "selector_count")
        self.assertEqual(attr.get_value(self.aci_leaf_switch_profile), 2)

    def test_leaf_interface_selector_port_block_count_attr(self) -> None:
        """ACILeafInterfaceSelectorPanel counts its Port Blocks."""
        attr = ACILeafInterfaceSelectorPanel._attrs["port_block_count"]
        self.assertIsInstance(attr, attrs.NumericAttr)
        self.assertEqual(attr.accessor, "port_block_count")
        self.assertEqual(attr.get_value(self.aci_leaf_interface_selector), 0)

    def test_leaf_selector_node_block_count_attr(self) -> None:
        """ACILeafSelectorPanel counts its Node Blocks."""
        attr = ACILeafSelectorPanel._attrs["node_block_count"]
        self.assertIsInstance(attr, attrs.NumericAttr)
        self.assertEqual(attr.accessor, "node_block_count")
        self.assertEqual(attr.get_value(self.aci_leaf_selector), 0)
