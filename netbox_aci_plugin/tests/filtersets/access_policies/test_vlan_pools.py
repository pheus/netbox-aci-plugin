# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for access-policy VLAN pool models."""

from utilities.testing import ChangeLoggedFilterSetTests

from ....choices import (
    VLANAllocationModeChoices,
    VLANPoolRangeAllocationModeChoices,
    VLANPoolRangeRoleChoices,
)
from ....filtersets.access_policies.vlan_pools import (
    ACIVLANPoolFilterSet,
    ACIVLANPoolRangeFilterSet,
)
from ....models.access_policies.vlan_pools import ACIVLANPool, ACIVLANPoolRange
from ...models.base import ACIBaseTestCase


class ACIVLANPoolFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACIVLANPoolFilterSet."""

    queryset = ACIVLANPool.objects.all()
    filterset = ACIVLANPoolFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIVLANPoolFilterSet tests."""
        super().setUpTestData()
        # Base provides aci_vlan_pool1 (static) and aci_vlan_pool2 (dynamic);
        # add more so test_id has more than two objects to filter.
        cls.aci_vlan_pool3 = ACIVLANPool.objects.create(
            name="VLANPoolFSA",
            name_alias="VLANPoolFSAAlias",
            aci_fabric=cls.aci_fabric,
            allocation_mode=VLANAllocationModeChoices.MODE_STATIC,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_vlan_pool4 = ACIVLANPool.objects.create(
            name="VLANPoolFSB",
            aci_fabric=cls.aci_fabric,
            allocation_mode=VLANAllocationModeChoices.MODE_DYNAMIC,
        )

    def test_q(self) -> None:
        """Test q search matches the name field."""
        params = {"q": "VLANPool1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_vlan_pool1, qs)
        self.assertNotIn(self.aci_vlan_pool2, qs)

    def test_q_name_alias(self) -> None:
        """Test q search matches the name alias field."""
        params = {"q": "VLANPoolFSAAlias"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_vlan_pool3, qs)
        self.assertNotIn(self.aci_vlan_pool1, qs)

    def test_search_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())

    def test_filter_allocation_mode(self) -> None:
        """Test filtering by allocation mode."""
        params = {"allocation_mode": [VLANAllocationModeChoices.MODE_DYNAMIC]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_vlan_pool2, qs)
        self.assertNotIn(self.aci_vlan_pool1, qs)

    def test_filter_aci_fabric(self) -> None:
        """Test filtering by the ACI fabric."""
        params = {"aci_fabric_id": [self.aci_fabric.pk]}
        self.assertEqual(
            self.filterset(params, self.queryset).qs.count(),
            self.queryset.filter(aci_fabric=self.aci_fabric).count(),
        )


class ACIVLANPoolRangeFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACIVLANPoolRangeFilterSet."""

    queryset = ACIVLANPoolRange.objects.all()
    filterset = ACIVLANPoolRangeFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIVLANPoolRangeFilterSet tests."""
        super().setUpTestData()
        # Base provides three ranges; add more so test_id has more than two
        # objects to filter.
        cls.aci_vlan_pool_range4 = ACIVLANPoolRange.objects.create(
            aci_vlan_pool=cls.aci_vlan_pool1,
            vlan_id_from=400,
            vlan_id_to=499,
        )
        cls.aci_vlan_pool_range5 = ACIVLANPoolRange.objects.create(
            aci_vlan_pool=cls.aci_vlan_pool2,
            vlan_id_from=400,
            vlan_id_to=499,
        )

    def test_q(self) -> None:
        """Test q search matches the parent VLAN pool name."""
        params = {"q": "VLANPool1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_vlan_pool_range1, qs)
        self.assertIn(self.aci_vlan_pool_range2, qs)
        self.assertNotIn(self.aci_vlan_pool_range3, qs)

    def test_search_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())

    def test_filter_aci_vlan_pool(self) -> None:
        """Test filtering by the parent VLAN pool."""
        params = {"aci_vlan_pool_id": [self.aci_vlan_pool1.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_vlan_pool_range1, qs)
        self.assertNotIn(self.aci_vlan_pool_range3, qs)

    def test_filter_role(self) -> None:
        """Test filtering by role."""
        params = {"role": [VLANPoolRangeRoleChoices.ROLE_INTERNAL]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_vlan_pool_range2, qs)
        self.assertNotIn(self.aci_vlan_pool_range1, qs)

    def test_filter_allocation_mode(self) -> None:
        """Test filtering by allocation mode."""
        params = {"allocation_mode": [VLANPoolRangeAllocationModeChoices.MODE_DYNAMIC]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_vlan_pool_range2, qs)
        self.assertNotIn(self.aci_vlan_pool_range1, qs)

    def test_filter_aci_fabric(self) -> None:
        """Test filtering ranges by the ACI fabric of the parent pool."""
        params = {"aci_fabric_id": [self.aci_fabric.pk]}
        self.assertEqual(
            self.filterset(params, self.queryset).qs.count(),
            self.queryset.count(),
        )
