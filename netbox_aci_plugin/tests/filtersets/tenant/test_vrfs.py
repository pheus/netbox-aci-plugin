# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for the ACI VRF model."""

from utilities.testing import ChangeLoggedFilterSetTests

from ....filtersets.tenant.vrfs import ACIVRFFilterSet
from ....models.tenant.vrfs import ACIVRF
from ...models.base import ACIBaseTestCase


class ACIVRFFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACIVRFFilterSet."""

    queryset = ACIVRF.objects.all()
    filterset = ACIVRFFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIVRFFilterSet tests."""
        super().setUpTestData()
        cls.aci_vrf_2 = ACIVRF.objects.create(
            name="ACIFSTestVRF2", aci_tenant=cls.aci_tenant
        )
        cls.aci_vrf_3 = ACIVRF.objects.create(
            name="ACIFSTestVRF3", aci_tenant=cls.aci_tenant
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestVRF2"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_vrf_2, qs)
        self.assertNotIn(self.aci_vrf_3, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())
