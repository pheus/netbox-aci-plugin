# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for tenant Endpoint Group models."""

from ipam.models import IPAddress
from utilities.testing import ChangeLoggedFilterSetTests

from ....filtersets.tenant.endpoint_groups import (
    ACIEndpointGroupFilterSet,
    ACIUSegEndpointGroupFilterSet,
    ACIUSegNetworkAttributeFilterSet,
)
from ....models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
    ACIUSegNetworkAttribute,
)
from ....models.tenant.endpoint_security_groups import ACIEndpointSecurityGroup
from ...models.base import ACIBaseTestCase


class ACIEndpointGroupFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACIEndpointGroupFilterSet."""

    queryset = ACIEndpointGroup.objects.all()
    filterset = ACIEndpointGroupFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEndpointGroupFilterSet tests."""
        super().setUpTestData()
        cls.aci_epg = ACIEndpointGroup.objects.create(
            name="ACIFSTestEPG1",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_epg_2 = ACIEndpointGroup.objects.create(
            name="ACIFSTestEPG2",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_epg_3 = ACIEndpointGroup.objects.create(
            name="ACIFSTestEPG3",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestEPG1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_epg, qs)
        self.assertNotIn(self.aci_epg_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())

    def test_filter_shares_aci_vrf_with_aci_esg(self) -> None:
        """Test filtering EPGs sharing an ACI VRF with a given ESG."""
        esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIFSTestSharedESG",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        fs = self.filterset(queryset=self.queryset)
        result = fs.filter_shares_aci_vrf_with_aci_esg_id(self.queryset, "name", esg)
        self.assertIn(self.aci_epg, result)

    def test_filter_shares_aci_vrf_with_aci_esg_none(self) -> None:
        """Test the shared-VRF filter returns none for a missing ESG."""
        fs = self.filterset(queryset=self.queryset)
        result = fs.filter_shares_aci_vrf_with_aci_esg_id(self.queryset, "name", None)
        self.assertEqual(result.count(), 0)


class ACIUSegEndpointGroupFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTests
):
    """Test case for ACIUSegEndpointGroupFilterSet."""

    queryset = ACIUSegEndpointGroup.objects.all()
    filterset = ACIUSegEndpointGroupFilterSet
    ignore_fields = ("match_operator",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIUSegEndpointGroupFilterSet tests."""
        super().setUpTestData()
        cls.aci_useg_epg = ACIUSegEndpointGroup.objects.create(
            name="ACIFSTestUSegEPG1",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_useg_epg_2 = ACIUSegEndpointGroup.objects.create(
            name="ACIFSTestUSegEPG2",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_useg_epg_3 = ACIUSegEndpointGroup.objects.create(
            name="ACIFSTestUSegEPG3",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestUSegEPG1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_useg_epg, qs)
        self.assertNotIn(self.aci_useg_epg_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())

    def test_filter_shares_aci_vrf_with_aci_esg(self) -> None:
        """Test filtering uSeg EPGs sharing an ACI VRF with a given ESG."""
        esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIFSTestSharedESGUSeg",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        fs = self.filterset(queryset=self.queryset)
        result = fs.filter_shares_aci_vrf_with_aci_esg_id(self.queryset, "name", esg)
        self.assertIn(self.aci_useg_epg, result)

    def test_filter_shares_aci_vrf_with_aci_esg_none(self) -> None:
        """Test the shared-VRF filter returns none for a missing ESG."""
        fs = self.filterset(queryset=self.queryset)
        result = fs.filter_shares_aci_vrf_with_aci_esg_id(self.queryset, "name", None)
        self.assertEqual(result.count(), 0)


class ACIUSegNetworkAttributeFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTests
):
    """Test case for ACIUSegNetworkAttributeFilterSet."""

    queryset = ACIUSegNetworkAttribute.objects.all()
    filterset = ACIUSegNetworkAttributeFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIUSegNetworkAttributeFilterSet tests."""
        super().setUpTestData()
        cls.aci_useg_epg = ACIUSegEndpointGroup.objects.create(
            name="ACIFSAttrUSegEPG",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.attr_ip_1 = IPAddress.objects.create(address="10.10.0.1/24")
        cls.attr_ip_2 = IPAddress.objects.create(address="10.10.0.2/24")
        cls.attr_ip_3 = IPAddress.objects.create(address="10.10.0.3/24")
        cls.attr_1 = ACIUSegNetworkAttribute.objects.create(
            name="ACIFSTestAttr1",
            aci_useg_endpoint_group=cls.aci_useg_epg,
            attr_object=cls.attr_ip_1,
        )
        cls.attr_2 = ACIUSegNetworkAttribute.objects.create(
            name="ACIFSTestAttr2",
            aci_useg_endpoint_group=cls.aci_useg_epg,
            attr_object=cls.attr_ip_2,
        )
        cls.attr_3 = ACIUSegNetworkAttribute.objects.create(
            name="ACIFSTestAttr3",
            aci_useg_endpoint_group=cls.aci_useg_epg,
            attr_object=cls.attr_ip_3,
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestAttr1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.attr_1, qs)
        self.assertNotIn(self.attr_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())
