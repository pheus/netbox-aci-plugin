# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for the ACI Application Profile model."""

from utilities.testing import ChangeLoggedFilterSetTests

from ....filtersets.tenant.app_profiles import ACIAppProfileFilterSet
from ....models.tenant.app_profiles import ACIAppProfile
from ...models.base import ACIBaseTestCase


class ACIAppProfileFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACIAppProfileFilterSet."""

    queryset = ACIAppProfile.objects.all()
    filterset = ACIAppProfileFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIAppProfileFilterSet tests."""
        super().setUpTestData()
        cls.aci_app_profile_2 = ACIAppProfile.objects.create(
            name="ACIFSTestAppProfile2", aci_tenant=cls.aci_tenant
        )
        cls.aci_app_profile_3 = ACIAppProfile.objects.create(
            name="ACIFSTestAppProfile3", aci_tenant=cls.aci_tenant
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestAppProfile2"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_app_profile_2, qs)
        self.assertNotIn(self.aci_app_profile_3, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())
