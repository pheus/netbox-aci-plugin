# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for access-policy domain models."""

from utilities.testing import ChangeLoggedFilterSetTests

from ....filtersets.access_policies.domains import ACIRoutedDomainFilterSet
from ....models.access_policies.domains import ACIRoutedDomain
from ....models.fabric.fabrics import ACIFabric
from ...models.base import ACIBaseTestCase


class ACIRoutedDomainFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACIRoutedDomainFilterSet."""

    queryset = ACIRoutedDomain.objects.all()
    filterset = ACIRoutedDomainFilterSet
    # security_domains: the filter is the singular `security_domain` method.
    ignore_fields = ("security_domains",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIRoutedDomainFilterSet tests."""
        super().setUpTestData()
        cls.aci_fabric_b = ACIFabric.objects.create(
            name="ACIRDFSTestFabricB", fabric_id=128, infra_vlan_vid=3901
        )
        cls.routed_domain_a = ACIRoutedDomain.objects.create(
            name="ACIRDFSTestDomainA",
            name_alias="DomainAliasA",
            description="Primary routed domain",
            aci_fabric=cls.aci_fabric,
            security_domains=["secdom-alpha", "secdom-beta"],
            nb_tenant=cls.nb_tenant,
        )
        cls.routed_domain_b = ACIRoutedDomain.objects.create(
            name="ACIRDFSTestDomainB",
            aci_fabric=cls.aci_fabric_b,
            security_domains=["secdom-gamma"],
        )
        cls.routed_domain_c = ACIRoutedDomain.objects.create(
            name="ACIRDFSTestDomainC",
            aci_fabric=cls.aci_fabric,
            security_domains=["secdom-delta"],
        )

    def test_q_name(self) -> None:
        """Test q search matches the name field."""
        params = {"q": "ACIRDFSTestDomainA"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.routed_domain_a, qs)
        self.assertNotIn(self.routed_domain_b, qs)

    def test_q_description(self) -> None:
        """Test q search matches the description field."""
        params = {"q": "Primary routed"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.routed_domain_a, qs)
        self.assertNotIn(self.routed_domain_b, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())

    def test_filter_security_domain_match(self) -> None:
        """Test filter_security_domain returns the matching domain."""
        params = {"security_domain": "secdom-alpha"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.routed_domain_a, qs)
        self.assertNotIn(self.routed_domain_b, qs)

    def test_filter_security_domain_no_match(self) -> None:
        """Test filter_security_domain with an absent value returns none."""
        params = {"security_domain": "secdom-missing"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_filter_security_domain_whitespace_returns_all(self) -> None:
        """Test filter_security_domain with whitespace returns the full set."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.filter_security_domain(qs, "security_domain", "   ")
        self.assertEqual(result.count(), qs.count())
