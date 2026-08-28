# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for ACI AAEP and AAEP Domain Binding models."""

from utilities.testing import ChangeLoggedFilterSetTestMixin

from ....filtersets.access_policies.aaep import (
    ACIAAEPDomainBindingFilterSet,
    ACIAttachableAccessEntityProfileFilterSet,
)
from ....models.access_policies.aaep import (
    ACIAAEPDomainBinding,
    ACIAttachableAccessEntityProfile,
)
from ....models.access_policies.domains import ACIPhysicalDomain, ACIRoutedDomain
from ...models.base import ACIBaseTestCase


class ACIAttachableAccessEntityProfileFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTestMixin
):
    """Test case for ACIAttachableAccessEntityProfileFilterSet."""

    queryset = ACIAttachableAccessEntityProfile.objects.all()
    filterset = ACIAttachableAccessEntityProfileFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for AAEP filterset tests."""
        super().setUpTestData()
        cls.aaep_a = ACIAttachableAccessEntityProfile.objects.create(
            name="AAEPFSTestA",
            name_alias="AAEPFSAliasA",
            aci_fabric=cls.aci_fabric,
        )
        cls.aaep_b = ACIAttachableAccessEntityProfile.objects.create(
            name="AAEPFSTestB",
            aci_fabric=cls.aci_fabric,
        )
        cls.aaep_c = ACIAttachableAccessEntityProfile.objects.create(
            name="AAEPFSTestC",
            aci_fabric=cls.aci_fabric,
        )

    def test_q(self) -> None:
        """Test q search matches the name field."""
        params = {"q": "AAEPFSTestA"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aaep_a, qs)
        self.assertNotIn(self.aaep_b, qs)

    def test_q_name_alias(self) -> None:
        """Test q search matches the name_alias field."""
        params = {"q": "AAEPFSAliasA"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aaep_a, qs)
        self.assertNotIn(self.aaep_b, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())


class ACIAAEPDomainBindingFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTestMixin
):
    """Test case for ACIAAEPDomainBindingFilterSet."""

    queryset = ACIAAEPDomainBinding.objects.all()
    filterset = ACIAAEPDomainBindingFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIAAEPDomainBindingFilterSet tests."""
        super().setUpTestData()
        cls.aaep_a = ACIAttachableAccessEntityProfile.objects.create(
            name="AAEPDBFSTestA",
            aci_fabric=cls.aci_fabric,
        )
        cls.aaep_b = ACIAttachableAccessEntityProfile.objects.create(
            name="AAEPDBFSTestB",
            aci_fabric=cls.aci_fabric,
        )
        cls.physical_domain_a = ACIPhysicalDomain.objects.create(
            name="PhysDomDBFSTestA",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool1,
        )
        cls.routed_domain_a = ACIRoutedDomain.objects.create(
            name="RoutedDomDBFSTestA",
            aci_fabric=cls.aci_fabric,
        )
        cls.routed_domain_b = ACIRoutedDomain.objects.create(
            name="RoutedDomDBFSTestB",
            aci_fabric=cls.aci_fabric,
        )
        cls.binding_1 = ACIAAEPDomainBinding.objects.create(
            aci_aaep=cls.aaep_a,
            aci_domain_object=cls.physical_domain_a,
        )
        cls.binding_2 = ACIAAEPDomainBinding.objects.create(
            aci_aaep=cls.aaep_b,
            aci_domain_object=cls.routed_domain_a,
        )
        cls.binding_3 = ACIAAEPDomainBinding.objects.create(
            aci_aaep=cls.aaep_b,
            aci_domain_object=cls.routed_domain_b,
        )

    def test_q(self) -> None:
        """Test search() by the related ACI AAEP name."""
        params = {"q": "AAEPDBFSTestA"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_q_physical_domain_name(self) -> None:
        """Test search() by the related ACI Physical Domain name."""
        params = {"q": "PhysDomDBFSTestA"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_q_routed_domain_name(self) -> None:
        """Test search() by the related ACI Routed Domain name."""
        params = {"q": "RoutedDomDBFSTestA"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_2, qs)
        self.assertNotIn(self.binding_1, qs)

    def test_aci_fabric(self) -> None:
        """Test filtering bindings by ACI Fabric name."""
        params = {"aci_fabric": [self.aci_fabric.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertIn(self.binding_2, qs)

    def test_aci_fabric_id(self) -> None:
        """Test filtering bindings by ACI Fabric ID."""
        params = {"aci_fabric_id": [self.aci_fabric.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertIn(self.binding_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())
