# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for tenant Contract Filter models."""

from utilities.testing import ChangeLoggedFilterSetTests

from ....filtersets.tenant.contract_filters import (
    ACIContractFilterEntryFilterSet,
    ACIContractFilterFilterSet,
)
from ....models.tenant.contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from ...models.base import ACIBaseTestCase


class ACIContractFilterFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACIContractFilterFilterSet."""

    queryset = ACIContractFilter.objects.all()
    filterset = ACIContractFilterFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractFilterFilterSet tests."""
        super().setUpTestData()
        cls.aci_contract_filter = ACIContractFilter.objects.create(
            name="ACIFSTestFilter1", aci_tenant=cls.aci_tenant
        )
        cls.aci_contract_filter_2 = ACIContractFilter.objects.create(
            name="ACIFSTestFilter2", aci_tenant=cls.aci_tenant
        )
        cls.aci_contract_filter_3 = ACIContractFilter.objects.create(
            name="ACIFSTestFilter3", aci_tenant=cls.aci_tenant
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestFilter1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_contract_filter, qs)
        self.assertNotIn(self.aci_contract_filter_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())


class ACIContractFilterEntryFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTests
):
    """Test case for ACIContractFilterEntryFilterSet."""

    queryset = ACIContractFilterEntry.objects.all()
    filterset = ACIContractFilterEntryFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractFilterEntryFilterSet tests."""
        super().setUpTestData()
        cls.aci_contract_filter = ACIContractFilter.objects.create(
            name="ACIFSTestEntryFilter", aci_tenant=cls.aci_tenant
        )
        cls.entry_1 = ACIContractFilterEntry.objects.create(
            name="ACIFSTestEntry1", aci_contract_filter=cls.aci_contract_filter
        )
        cls.entry_2 = ACIContractFilterEntry.objects.create(
            name="ACIFSTestEntry2", aci_contract_filter=cls.aci_contract_filter
        )
        cls.entry_3 = ACIContractFilterEntry.objects.create(
            name="ACIFSTestEntry3", aci_contract_filter=cls.aci_contract_filter
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestEntry1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.entry_1, qs)
        self.assertNotIn(self.entry_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())
