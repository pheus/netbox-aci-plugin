# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for tenant L3Out models."""

from ....filtersets.tenant.l3outs import (
    ACIExternalEndpointGroupFilterSet,
    ACIExternalSubnetFilterSet,
    ACIL3OutFilterSet,
)
from ....models.access_policies.domains import ACIRoutedDomain
from ....models.tenant.l3outs import (
    ACIExternalEndpointGroup,
    ACIExternalSubnet,
    ACIL3Out,
)
from ...models.base import ACIBaseTestCase


class ACIL3OutFilterSetTestCase(ACIBaseTestCase):
    """Test case for ACIL3OutFilterSet."""

    queryset = ACIL3Out.objects.all()
    filterset = ACIL3OutFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIL3OutFilterSet tests."""
        super().setUpTestData()
        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIFSTestRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_l3out = ACIL3Out.objects.create(
            name="ACIFSTestL3Out",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )

    def test_q(self) -> None:
        """Test search() with a name substring returns matching objects."""
        params = {"q": "ACIFSTestL3Out"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())


class ACIExternalEndpointGroupFilterSetTestCase(ACIBaseTestCase):
    """Test case for ACIExternalEndpointGroupFilterSet."""

    queryset = ACIExternalEndpointGroup.objects.all()
    filterset = ACIExternalEndpointGroupFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIExternalEndpointGroupFilterSet tests."""
        super().setUpTestData()
        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIFSEPGTestRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_l3out = ACIL3Out.objects.create(
            name="ACIFSEPGTestL3Out",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.aci_epg = ACIExternalEndpointGroup.objects.create(
            name="ACIFSTestExternalEPG",
            aci_l3out=cls.aci_l3out,
        )

    def test_q(self) -> None:
        """Test search() with a name substring returns matching objects."""
        params = {"q": "ACIFSTestExternalEPG"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())


class ACIExternalSubnetFilterSetTestCase(ACIBaseTestCase):
    """Test case for ACIExternalSubnetFilterSet."""

    queryset = ACIExternalSubnet.objects.all()
    filterset = ACIExternalSubnetFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIExternalSubnetFilterSet tests."""
        super().setUpTestData()
        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIFSSNTestRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_l3out = ACIL3Out.objects.create(
            name="ACIFSSNTestL3Out",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.aci_epg = ACIExternalEndpointGroup.objects.create(
            name="ACIFSSNTestExternalEPG",
            aci_l3out=cls.aci_l3out,
        )
        cls.subnet = ACIExternalSubnet.objects.create(
            name="ACIFSSNTestSubnet",
            aci_external_endpoint_group=cls.aci_epg,
            matched_prefix="10.200.0.0/24",
        )
        cls.subnet_b = ACIExternalSubnet.objects.create(
            name="ACIFSSNTestSubnetB",
            aci_external_endpoint_group=cls.aci_epg,
            matched_prefix="10.201.0.0/24",
        )

    def test_q(self) -> None:
        """Test search() with a name substring returns matching objects."""
        params = {"q": "ACIFSSNTestSubnet"}
        self.assertIn(self.subnet, self.filterset(params, self.queryset).qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())

    def test_filter_prefix_exact_match(self) -> None:
        """Test filter_prefix() returns exact matched_prefix values."""
        params = {"matched_prefix": ["10.200.0.0/24"]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.subnet, qs)
        self.assertNotIn(self.subnet_b, qs)

    def test_filter_prefix_invalid_value_returns_none(self) -> None:
        """Test filter_prefix() skips invalid prefix strings."""
        params = {"matched_prefix": ["not-a-prefix"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_filter_prefix_within_include_match(self) -> None:
        """Test filter_prefix_within_include() matches subnets in prefix."""
        params = {"matched_prefix_within_include": "10.200.0.0/16"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.subnet, qs)
        self.assertNotIn(self.subnet_b, qs)

    def test_filter_prefix_within_include_whitespace_returns_all(self) -> None:
        """Test filter_prefix_within_include() with whitespace returns all."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.filter_prefix_within_include(
            qs, "matched_prefix_within_include", "  "
        )
        self.assertEqual(result.count(), qs.count())

    def test_filter_prefix_within_include_invalid_returns_none(self) -> None:
        """Test filter_prefix_within_include() with invalid prefix is empty."""
        params = {"matched_prefix_within_include": "not-a-prefix"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
