# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for tenant Endpoint Security Group models."""

from ipam.models import IPAddress, Prefix
from utilities.testing import ChangeLoggedFilterSetTests

from ....filtersets.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroupFilterSet,
    ACIEsgEndpointGroupSelectorFilterSet,
    ACIEsgEndpointSelectorFilterSet,
)
from ....models.tenant.endpoint_groups import ACIEndpointGroup
from ....models.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroup,
    ACIEsgEndpointGroupSelector,
    ACIEsgEndpointSelector,
)
from ...models.base import ACIBaseTestCase


class ACIEndpointSecurityGroupFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTests
):
    """Test case for ACIEndpointSecurityGroupFilterSet."""

    queryset = ACIEndpointSecurityGroup.objects.all()
    filterset = ACIEndpointSecurityGroupFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEndpointSecurityGroupFilterSet tests."""
        super().setUpTestData()
        cls.aci_esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIFSTestESG1",
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
        )
        cls.aci_esg_2 = ACIEndpointSecurityGroup.objects.create(
            name="ACIFSTestESG2",
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
        )
        cls.aci_esg_3 = ACIEndpointSecurityGroup.objects.create(
            name="ACIFSTestESG3",
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestESG1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_esg, qs)
        self.assertNotIn(self.aci_esg_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())


class ACIEsgEndpointGroupSelectorFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTests
):
    """Test case for ACIEsgEndpointGroupSelectorFilterSet."""

    queryset = ACIEsgEndpointGroupSelector.objects.all()
    filterset = ACIEsgEndpointGroupSelectorFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEsgEndpointGroupSelectorFilterSet tests."""
        super().setUpTestData()
        cls.aci_esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIFSEpgSelESG",
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
        )
        cls.sel_epg_1 = ACIEndpointGroup.objects.create(
            name="ACIFSEpgSelEPG1",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.sel_epg_2 = ACIEndpointGroup.objects.create(
            name="ACIFSEpgSelEPG2",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.sel_epg_3 = ACIEndpointGroup.objects.create(
            name="ACIFSEpgSelEPG3",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.epg_sel_1 = ACIEsgEndpointGroupSelector.objects.create(
            name="ACIFSTestEpgSel1",
            aci_endpoint_security_group=cls.aci_esg,
            aci_epg_object=cls.sel_epg_1,
        )
        cls.epg_sel_2 = ACIEsgEndpointGroupSelector.objects.create(
            name="ACIFSTestEpgSel2",
            aci_endpoint_security_group=cls.aci_esg,
            aci_epg_object=cls.sel_epg_2,
        )
        cls.epg_sel_3 = ACIEsgEndpointGroupSelector.objects.create(
            name="ACIFSTestEpgSel3",
            aci_endpoint_security_group=cls.aci_esg,
            aci_epg_object=cls.sel_epg_3,
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestEpgSel1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.epg_sel_1, qs)
        self.assertNotIn(self.epg_sel_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())


class ACIEsgEndpointSelectorFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTests
):
    """Test case for ACIEsgEndpointSelectorFilterSet."""

    queryset = ACIEsgEndpointSelector.objects.all()
    filterset = ACIEsgEndpointSelectorFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEsgEndpointSelectorFilterSet tests."""
        super().setUpTestData()
        cls.aci_esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIFSEpSelESG",
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
        )
        cls.ep_ip_1 = IPAddress.objects.create(address="10.20.0.1/24")
        cls.ep_ip_2 = IPAddress.objects.create(address="10.20.0.2/24")
        cls.ep_ip_3 = IPAddress.objects.create(address="10.20.0.3/24")
        cls.ep_sel_1 = ACIEsgEndpointSelector.objects.create(
            name="ACIFSTestEpSel1",
            aci_endpoint_security_group=cls.aci_esg,
            ep_object=cls.ep_ip_1,
        )
        cls.ep_sel_2 = ACIEsgEndpointSelector.objects.create(
            name="ACIFSTestEpSel2",
            aci_endpoint_security_group=cls.aci_esg,
            ep_object=cls.ep_ip_2,
        )
        cls.ep_sel_3 = ACIEsgEndpointSelector.objects.create(
            name="ACIFSTestEpSel3",
            aci_endpoint_security_group=cls.aci_esg,
            ep_object=cls.ep_ip_3,
        )
        cls.ep_prefix = Prefix.objects.create(prefix="10.20.1.0/24")
        cls.ep_sel_4 = ACIEsgEndpointSelector.objects.create(
            name="ACIFSTestEpSel4",
            aci_endpoint_security_group=cls.aci_esg,
            ep_object=cls.ep_prefix,
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestEpSel1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.ep_sel_1, qs)
        self.assertNotIn(self.ep_sel_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())

    def test_ip_address(self) -> None:
        """Test filtering by the cached IP address string."""
        params = {"ip_address": ["10.20.0.1/24", "10.20.0.2/24"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_prefix(self) -> None:
        """Test filtering by the cached prefix string."""
        params = {"prefix": ["10.20.1.0/24"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_ip_address_invalid_returns_empty(self) -> None:
        """Test an unparseable IP address yields no results."""
        params = {"ip_address": ["not-an-ip"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_prefix_invalid_returns_empty(self) -> None:
        """Test an unparseable prefix yields no results."""
        params = {"prefix": ["not-a-prefix"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
