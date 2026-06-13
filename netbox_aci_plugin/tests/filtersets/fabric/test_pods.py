# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for the ACI Pod model."""

from ipam.models import Prefix
from utilities.testing import ChangeLoggedFilterSetTests

from ....filtersets.fabric.pods import ACIPodFilterSet
from ....models.fabric.pods import ACIPod
from ...models.base import ACIBaseTestCase


class ACIPodFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACIPodFilterSet."""

    queryset = ACIPod.objects.all()
    filterset = ACIPodFilterSet
    # scope_id: filtered via ScopedFilterSet, not by a same-named filter.
    ignore_fields = ("scope_id",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIPodFilterSet tests."""
        super().setUpTestData()
        cls.tep_pool_2 = Prefix.objects.create(prefix="10.1.0.0/19")
        cls.tep_pool_3 = Prefix.objects.create(prefix="10.2.0.0/19")
        cls.aci_pod_2 = ACIPod.objects.create(
            name="ACIFSTestPod2",
            aci_fabric=cls.aci_fabric,
            pod_id=2,
            tep_pool=cls.tep_pool_2,
        )
        cls.aci_pod_3 = ACIPod.objects.create(
            name="ACIFSTestPod3",
            aci_fabric=cls.aci_fabric,
            pod_id=3,
            tep_pool=cls.tep_pool_3,
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestPod2"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_pod_2, qs)
        self.assertNotIn(self.aci_pod_3, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())
