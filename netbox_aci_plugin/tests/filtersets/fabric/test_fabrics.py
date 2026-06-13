# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for the ACI Fabric model."""

from utilities.testing import ChangeLoggedFilterSetTests

from ....filtersets.fabric.fabrics import ACIFabricFilterSet
from ....models.fabric.fabrics import ACIFabric
from ...models.base import ACIBaseTestCase


class ACIFabricFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACIFabricFilterSet."""

    queryset = ACIFabric.objects.all()
    filterset = ACIFabricFilterSet
    # scope_id: filtered via ScopedFilterSet, not by a same-named filter.
    ignore_fields = ("scope_id",)

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIFabricFilterSet tests."""
        super().setUpTestData()
        cls.aci_fabric_2 = ACIFabric.objects.create(
            name="ACIFSTestFabric2", fabric_id=128, infra_vlan_vid=3901
        )
        cls.aci_fabric_3 = ACIFabric.objects.create(
            name="ACIFSTestFabric3", fabric_id=129, infra_vlan_vid=3902
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestFabric2"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_fabric_2, qs)
        self.assertNotIn(self.aci_fabric_3, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())
