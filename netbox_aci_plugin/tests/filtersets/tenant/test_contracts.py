# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for tenant Contract models."""

from utilities.testing import ChangeLoggedFilterSetTests

from ....choices import ContractRelationRoleChoices
from ....filtersets.tenant.contracts import (
    ACIContractFilterSet,
    ACIContractRelationFilterSet,
    ACIContractSubjectFilterFilterSet,
    ACIContractSubjectFilterSet,
)
from ....models.tenant.contract_filters import ACIContractFilter
from ....models.tenant.contracts import (
    ACIContract,
    ACIContractRelation,
    ACIContractSubject,
    ACIContractSubjectFilter,
)
from ....models.tenant.endpoint_groups import ACIEndpointGroup
from ...models.base import ACIBaseTestCase


class ACIContractFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACIContractFilterSet."""

    queryset = ACIContract.objects.all()
    filterset = ACIContractFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractFilterSet tests."""
        super().setUpTestData()
        cls.aci_contract = ACIContract.objects.create(
            name="ACIFSTestContract1", aci_tenant=cls.aci_tenant
        )
        cls.aci_contract_2 = ACIContract.objects.create(
            name="ACIFSTestContract2", aci_tenant=cls.aci_tenant
        )
        cls.aci_contract_3 = ACIContract.objects.create(
            name="ACIFSTestContract3", aci_tenant=cls.aci_tenant
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestContract1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_contract, qs)
        self.assertNotIn(self.aci_contract_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())


class ACIContractRelationFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACIContractRelationFilterSet."""

    queryset = ACIContractRelation.objects.all()
    filterset = ACIContractRelationFilterSet
    # Cached GFK-target FKs the filterset does not expose (only EPG + VRF).
    ignore_fields = (
        "aci_endpoint_security_group",
        "aci_external_endpoint_group",
        "aci_useg_endpoint_group",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractRelationFilterSet tests."""
        super().setUpTestData()
        cls.aci_contract = ACIContract.objects.create(
            name="ACIFSRelContract", aci_tenant=cls.aci_tenant
        )
        cls.aci_epg_1 = ACIEndpointGroup.objects.create(
            name="ACIFSRelEPG1",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_epg_2 = ACIEndpointGroup.objects.create(
            name="ACIFSRelEPG2",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_epg_3 = ACIEndpointGroup.objects.create(
            name="ACIFSRelEPG3",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.relation_1 = ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract,
            aci_object=cls.aci_epg_1,
            role=ContractRelationRoleChoices.ROLE_CONSUMER,
        )
        cls.relation_2 = ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract,
            aci_object=cls.aci_epg_2,
            role=ContractRelationRoleChoices.ROLE_CONSUMER,
        )
        cls.relation_3 = ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract,
            aci_object=cls.aci_epg_3,
            role=ContractRelationRoleChoices.ROLE_CONSUMER,
        )

    def test_q(self) -> None:
        """Test search() by the related ACI Contract name."""
        params = {"q": "ACIFSRelContract"}
        self.assertIn(self.relation_1, self.filterset(params, self.queryset).qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())


class ACIContractSubjectFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTests):
    """Test case for ACIContractSubjectFilterSet."""

    queryset = ACIContractSubject.objects.all()
    filterset = ACIContractSubjectFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractSubjectFilterSet tests."""
        super().setUpTestData()
        cls.aci_contract = ACIContract.objects.create(
            name="ACIFSSubjContract", aci_tenant=cls.aci_tenant
        )
        cls.subject_1 = ACIContractSubject.objects.create(
            name="ACIFSTestSubject1", aci_contract=cls.aci_contract
        )
        cls.subject_2 = ACIContractSubject.objects.create(
            name="ACIFSTestSubject2", aci_contract=cls.aci_contract
        )
        cls.subject_3 = ACIContractSubject.objects.create(
            name="ACIFSTestSubject3", aci_contract=cls.aci_contract
        )

    def test_q(self) -> None:
        """Test search() with a name substring matches one object."""
        params = {"q": "ACIFSTestSubject1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.subject_1, qs)
        self.assertNotIn(self.subject_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())


class ACIContractSubjectFilterFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTests
):
    """Test case for ACIContractSubjectFilterFilterSet."""

    queryset = ACIContractSubjectFilter.objects.all()
    filterset = ACIContractSubjectFilterFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractSubjectFilterFilterSet tests."""
        super().setUpTestData()
        cls.aci_contract = ACIContract.objects.create(
            name="ACIFSSFContract", aci_tenant=cls.aci_tenant
        )
        cls.aci_subject = ACIContractSubject.objects.create(
            name="ACIFSSFSubject", aci_contract=cls.aci_contract
        )
        cls.filter_1 = ACIContractFilter.objects.create(
            name="ACIFSSFFilter1", aci_tenant=cls.aci_tenant
        )
        cls.filter_2 = ACIContractFilter.objects.create(
            name="ACIFSSFFilter2", aci_tenant=cls.aci_tenant
        )
        cls.filter_3 = ACIContractFilter.objects.create(
            name="ACIFSSFFilter3", aci_tenant=cls.aci_tenant
        )
        cls.sf_1 = ACIContractSubjectFilter.objects.create(
            aci_contract_subject=cls.aci_subject, aci_contract_filter=cls.filter_1
        )
        cls.sf_2 = ACIContractSubjectFilter.objects.create(
            aci_contract_subject=cls.aci_subject, aci_contract_filter=cls.filter_2
        )
        cls.sf_3 = ACIContractSubjectFilter.objects.create(
            aci_contract_subject=cls.aci_subject, aci_contract_filter=cls.filter_3
        )

    def test_q(self) -> None:
        """Test search() by the related ACI Contract Subject name."""
        params = {"q": "ACIFSSFSubject"}
        self.assertIn(self.sf_1, self.filterset(params, self.queryset).qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())
