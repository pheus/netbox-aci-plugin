# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for the ACI Tenant model."""

from utilities.testing import ChangeLoggedFilterSetTests

from ....filtersets.tenant.tenants import ACITenantFilterSet
from ....models.tenant.tenants import ACITenant
from ...models.base import ACIBaseTestCase


class ACITenantFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACITenantFilterSet."""

    queryset = ACITenant.objects.all()
    filterset = ACITenantFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACITenantFilterSet tests."""
        super().setUpTestData()
        cls.aci_tenant_2 = ACITenant.objects.create(
            name="ACIFSTestTenant2", aci_fabric=cls.aci_fabric
        )
        cls.aci_tenant_3 = ACITenant.objects.create(
            name="ACIFSTestTenant3", aci_fabric=cls.aci_fabric
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestTenant2"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_tenant_2, qs)
        self.assertNotIn(self.aci_tenant_3, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())
