# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for tenant L3Out models."""

from utilities.testing import ChangeLoggedFilterSetTests

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


class ACIL3OutFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACIL3OutFilterSet."""

    queryset = ACIL3Out.objects.all()
    filterset = ACIL3OutFilterSet
    # Scalar policy fields the filterset does not expose, plus the
    # currently-unfiltered export_route_control_enforcement_enabled field.
    ignore_fields = (
        "bfd_policy_name",
        "custom_qos_policy_name",
        "egress_data_plane_policing_policy_name",
        "eigrp_interface_policy_name",
        "export_route_control_enforcement_enabled",
        "igmp_interface_policy_name",
        "ingress_data_plane_policing_policy_name",
        "interleak_route_map_name",
        "ospf_external_policy_name",
        "pim_policy_name",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIL3OutFilterSet tests."""
        super().setUpTestData()
        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIFSTestRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_l3out = ACIL3Out.objects.create(
            name="ACIFSTestL3Out1",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.aci_l3out_2 = ACIL3Out.objects.create(
            name="ACIFSTestL3Out2",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.aci_l3out_3 = ACIL3Out.objects.create(
            name="ACIFSTestL3Out3",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestL3Out1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_l3out, qs)
        self.assertNotIn(self.aci_l3out_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())


class ACIExternalEndpointGroupFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTests
):
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
            name="ACIFSTestExternalEPG1", aci_l3out=cls.aci_l3out
        )
        cls.aci_epg_2 = ACIExternalEndpointGroup.objects.create(
            name="ACIFSTestExternalEPG2", aci_l3out=cls.aci_l3out
        )
        cls.aci_epg_3 = ACIExternalEndpointGroup.objects.create(
            name="ACIFSTestExternalEPG3", aci_l3out=cls.aci_l3out
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestExternalEPG1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_epg, qs)
        self.assertNotIn(self.aci_epg_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())


class ACIExternalSubnetFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACIExternalSubnetFilterSet."""

    queryset = ACIExternalSubnet.objects.all()
    filterset = ACIExternalSubnetFilterSet
    # Summarization policy-name scalars the filterset does not expose.
    ignore_fields = (
        "bgp_route_summarization_policy_name",
        "ospf_route_summarization_policy_name",
    )

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
        cls.subnet_c = ACIExternalSubnet.objects.create(
            name="ACIFSSNTestSubnetC",
            aci_external_endpoint_group=cls.aci_epg,
            matched_prefix="10.202.0.0/24",
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches the subnet."""
        params = {"q": "ACIFSSNTestSubnet"}
        self.assertIn(self.subnet, self.filterset(params, self.queryset).qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
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
