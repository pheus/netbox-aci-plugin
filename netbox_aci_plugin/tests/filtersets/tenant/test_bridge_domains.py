# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for tenant Bridge Domain binding models."""

from ....filtersets.tenant.bridge_domains import ACIBridgeDomainL3OutBindingFilterSet
from ....models.access_policies.domains import ACIRoutedDomain
from ....models.tenant.bridge_domains import ACIBridgeDomainL3OutBinding
from ....models.tenant.l3outs import ACIL3Out
from ...models.base import ACIBaseTestCase


class ACIBridgeDomainL3OutBindingFilterSetTestCase(ACIBaseTestCase):
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
            name="ACIFSBDRelTestL3Out",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.bd_relation = ACIBridgeDomainL3OutBinding.objects.create(
            aci_bridge_domain=cls.aci_bd,
            aci_l3out=cls.aci_l3out,
        )

    def test_q(self) -> None:
        """Test search() with L3Out name substring matches relation."""
        params = {"q": "ACIFSBDRelTestL3Out"}
        self.assertIn(self.bd_relation, self.filterset(params, self.queryset).qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())
