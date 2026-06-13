# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for tenant Bridge Domain models."""

from ipam.models import IPAddress
from utilities.testing import ChangeLoggedFilterSetTests

from ....filtersets.tenant.bridge_domains import (
    ACIBridgeDomainFilterSet,
    ACIBridgeDomainL3OutBindingFilterSet,
    ACIBridgeDomainSubnetFilterSet,
)
from ....models.access_policies.domains import ACIRoutedDomain
from ....models.tenant.bridge_domains import (
    ACIBridgeDomain,
    ACIBridgeDomainL3OutBinding,
    ACIBridgeDomainSubnet,
)
from ....models.tenant.l3outs import ACIL3Out
from ...models.base import ACIBaseTestCase


class ACIBridgeDomainFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACIBridgeDomainFilterSet."""

    queryset = ACIBridgeDomain.objects.all()
    filterset = ACIBridgeDomainFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIBridgeDomainFilterSet tests."""
        super().setUpTestData()
        cls.aci_bd_2 = ACIBridgeDomain.objects.create(
            name="ACIFSTestBD2", aci_tenant=cls.aci_tenant, aci_vrf=cls.aci_vrf
        )
        cls.aci_bd_3 = ACIBridgeDomain.objects.create(
            name="ACIFSTestBD3", aci_tenant=cls.aci_tenant, aci_vrf=cls.aci_vrf
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestBD2"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_bd_2, qs)
        self.assertNotIn(self.aci_bd_3, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())


class ACIBridgeDomainSubnetFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTests
):
    """Test case for ACIBridgeDomainSubnetFilterSet."""

    queryset = ACIBridgeDomainSubnet.objects.all()
    filterset = ACIBridgeDomainSubnetFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIBridgeDomainSubnetFilterSet tests."""
        super().setUpTestData()
        cls.gateway_ip_1 = IPAddress.objects.create(address="10.30.0.1/24")
        cls.gateway_ip_2 = IPAddress.objects.create(address="10.30.0.2/24")
        cls.gateway_ip_3 = IPAddress.objects.create(address="10.30.0.3/24")
        cls.subnet_1 = ACIBridgeDomainSubnet.objects.create(
            name="ACIFSTestBDSubnet1",
            aci_bridge_domain=cls.aci_bd,
            gateway_ip_address=cls.gateway_ip_1,
        )
        cls.subnet_2 = ACIBridgeDomainSubnet.objects.create(
            name="ACIFSTestBDSubnet2",
            aci_bridge_domain=cls.aci_bd,
            gateway_ip_address=cls.gateway_ip_2,
        )
        cls.subnet_3 = ACIBridgeDomainSubnet.objects.create(
            name="ACIFSTestBDSubnet3",
            aci_bridge_domain=cls.aci_bd,
            gateway_ip_address=cls.gateway_ip_3,
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestBDSubnet1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.subnet_1, qs)
        self.assertNotIn(self.subnet_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())


class ACIBridgeDomainL3OutBindingFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTests
):
    """Test case for ACIBridgeDomainL3OutBindingFilterSet."""

    queryset = ACIBridgeDomainL3OutBinding.objects.all()
    filterset = ACIBridgeDomainL3OutBindingFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIBridgeDomainL3OutBindingFilterSet tests."""
        super().setUpTestData()
        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIFSBDRelTestRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_l3out = ACIL3Out.objects.create(
            name="ACIFSBDRelTestL3Out1",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.aci_l3out_2 = ACIL3Out.objects.create(
            name="ACIFSBDRelTestL3Out2",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.aci_l3out_3 = ACIL3Out.objects.create(
            name="ACIFSBDRelTestL3Out3",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.bd_relation = ACIBridgeDomainL3OutBinding.objects.create(
            aci_bridge_domain=cls.aci_bd, aci_l3out=cls.aci_l3out
        )
        cls.bd_relation_2 = ACIBridgeDomainL3OutBinding.objects.create(
            aci_bridge_domain=cls.aci_bd, aci_l3out=cls.aci_l3out_2
        )
        cls.bd_relation_3 = ACIBridgeDomainL3OutBinding.objects.create(
            aci_bridge_domain=cls.aci_bd, aci_l3out=cls.aci_l3out_3
        )

    def test_q(self) -> None:
        """Test search() with an L3Out name substring matches the binding."""
        params = {"q": "ACIFSBDRelTestL3Out1"}
        self.assertIn(self.bd_relation, self.filterset(params, self.queryset).qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())
