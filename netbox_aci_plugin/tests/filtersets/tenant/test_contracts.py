# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for tenant Contract models."""

from utilities.testing import ChangeLoggedFilterSetTestMixin

from ....choices import ContractRelationRoleChoices
from ....filtersets.tenant.contracts import (
    ACIContractFilterSet,
    ACIContractRelationFilterSet,
    ACIContractSubjectFilterFilterSet,
    ACIContractSubjectFilterSet,
)
from ....models.access_policies.domains import ACIRoutedDomain
from ....models.fabric.fabrics import ACIFabric
from ....models.tenant.contract_filters import ACIContractFilter
from ....models.tenant.contracts import (
    ACIContract,
    ACIContractRelation,
    ACIContractSubject,
    ACIContractSubjectFilter,
)
from ....models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
)
from ....models.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroup,
)
from ....models.tenant.l3outs import ACIExternalEndpointGroup, ACIL3Out
from ....models.tenant.tenants import ACITenant
from ...models.base import ACIBaseTestCase


class ACIContractFilterSetTestCase(ACIBaseTestCase, ChangeLoggedFilterSetTestMixin):
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


class ACIContractRelationFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTestMixin
):
    """Test case for ACIContractRelationFilterSet."""

    queryset = ACIContractRelation.objects.all()
    filterset = ACIContractRelationFilterSet

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
        cls.aci_esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIFSRelESG",
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
        )
        cls.aci_useg_epg = ACIUSegEndpointGroup.objects.create(
            name="ACIFSRelUSegEPG",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIFSRelRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_l3out = ACIL3Out.objects.create(
            name="ACIFSRelL3Out",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.aci_ext_epg = ACIExternalEndpointGroup.objects.create(
            name="ACIFSRelExtEPG",
            aci_l3out=cls.aci_l3out,
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
        cls.relation_esg = ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract,
            aci_object=cls.aci_esg,
            role=ContractRelationRoleChoices.ROLE_PROVIDER,
        )
        cls.relation_useg = ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract,
            aci_object=cls.aci_useg_epg,
            role=ContractRelationRoleChoices.ROLE_PROVIDER,
        )
        cls.relation_ext = ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract,
            aci_object=cls.aci_ext_epg,
            role=ContractRelationRoleChoices.ROLE_PROVIDER,
        )

    def test_aci_endpoint_security_group(self) -> None:
        """Test filtering relations by ACI Endpoint Security Group name."""
        params = {"aci_endpoint_security_group": [self.aci_esg.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.relation_esg, qs)
        self.assertNotIn(self.relation_1, qs)

    def test_aci_endpoint_security_group_id(self) -> None:
        """Test filtering relations by ACI Endpoint Security Group ID."""
        params = {"aci_endpoint_security_group_id": [self.aci_esg.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.relation_esg, qs)
        self.assertNotIn(self.relation_1, qs)

    def test_aci_endpoint_security_group_tenant(self) -> None:
        """Test filtering by the Endpoint Security Group's ACI Tenant name."""
        params = {"aci_endpoint_security_group_tenant": [self.aci_tenant.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.relation_esg, qs)
        self.assertNotIn(self.relation_1, qs)

    def test_aci_endpoint_security_group_tenant_id(self) -> None:
        """Test filtering by the Endpoint Security Group's ACI Tenant ID."""
        params = {"aci_endpoint_security_group_tenant_id": [self.aci_tenant.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.relation_esg, qs)
        self.assertNotIn(self.relation_1, qs)

    def test_aci_useg_endpoint_group(self) -> None:
        """Test filtering relations by ACI uSeg Endpoint Group name."""
        params = {"aci_useg_endpoint_group": [self.aci_useg_epg.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.relation_useg, qs)
        self.assertNotIn(self.relation_1, qs)

    def test_aci_useg_endpoint_group_id(self) -> None:
        """Test filtering relations by ACI uSeg Endpoint Group ID."""
        params = {"aci_useg_endpoint_group_id": [self.aci_useg_epg.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.relation_useg, qs)
        self.assertNotIn(self.relation_1, qs)

    def test_aci_useg_endpoint_group_tenant(self) -> None:
        """Test filtering by the uSeg Endpoint Group's ACI Tenant name."""
        params = {"aci_useg_endpoint_group_tenant": [self.aci_tenant.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.relation_useg, qs)
        self.assertNotIn(self.relation_1, qs)

    def test_aci_useg_endpoint_group_tenant_id(self) -> None:
        """Test filtering by the uSeg Endpoint Group's ACI Tenant ID."""
        params = {"aci_useg_endpoint_group_tenant_id": [self.aci_tenant.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.relation_useg, qs)
        self.assertNotIn(self.relation_1, qs)

    def test_aci_external_endpoint_group(self) -> None:
        """Test filtering relations by ACI External Endpoint Group name."""
        params = {"aci_external_endpoint_group": [self.aci_ext_epg.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.relation_ext, qs)
        self.assertNotIn(self.relation_1, qs)

    def test_aci_external_endpoint_group_id(self) -> None:
        """Test filtering relations by ACI External Endpoint Group ID."""
        params = {"aci_external_endpoint_group_id": [self.aci_ext_epg.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.relation_ext, qs)
        self.assertNotIn(self.relation_1, qs)

    def test_aci_external_endpoint_group_tenant(self) -> None:
        """Test filtering by the External Endpoint Group's ACI Tenant name."""
        params = {"aci_external_endpoint_group_tenant": [self.aci_tenant.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.relation_ext, qs)
        self.assertNotIn(self.relation_1, qs)

    def test_aci_external_endpoint_group_tenant_id(self) -> None:
        """Test filtering by the External Endpoint Group's ACI Tenant ID."""
        params = {"aci_external_endpoint_group_tenant_id": [self.aci_tenant.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.relation_ext, qs)
        self.assertNotIn(self.relation_1, qs)

    def test_q(self) -> None:
        """Test search() by the related ACI Contract name."""
        params = {"q": "ACIFSRelContract"}
        self.assertIn(self.relation_1, self.filterset(params, self.queryset).qs)

    def test_q_endpoint_group_name(self) -> None:
        """Test search() by the related ACI Endpoint Group name."""
        params = {"q": self.aci_epg_1.name}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.relation_1, qs)
        self.assertNotIn(self.relation_esg, qs)

    def test_q_endpoint_security_group_name(self) -> None:
        """Test search() by the related ACI Endpoint Security Group name."""
        params = {"q": self.aci_esg.name}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.relation_esg, qs)
        self.assertNotIn(self.relation_1, qs)

    def test_q_useg_endpoint_group_name(self) -> None:
        """Test search() by the related ACI uSeg Endpoint Group name."""
        params = {"q": self.aci_useg_epg.name}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.relation_useg, qs)
        self.assertNotIn(self.relation_1, qs)

    def test_q_external_endpoint_group_name(self) -> None:
        """Test search() by the related ACI External Endpoint Group name."""
        params = {"q": self.aci_ext_epg.name}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.relation_ext, qs)
        self.assertNotIn(self.relation_1, qs)

    def test_q_vrf_name(self) -> None:
        """Test search() by the related ACI VRF name."""
        relation_vrf = ACIContractRelation.objects.create(
            aci_contract=self.aci_contract,
            aci_object=self.aci_vrf,
            role=ContractRelationRoleChoices.ROLE_PROVIDER,
        )
        params = {"q": self.aci_vrf.name}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(relation_vrf, qs)
        self.assertNotIn(self.relation_1, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())


class ACIContractSubjectFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTestMixin
):
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
    ACIBaseTestCase, ChangeLoggedFilterSetTestMixin
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
        # Second ACI Fabric/Tenant chain, to give the aci_fabric(_id) filter
        # tests a real negative control. The PK is explicit and far outside
        # any auto-assigned range, so it cannot coincidentally match an
        # unrelated ACITenant PK (which is the bug this test covers).
        cls.aci_fabric_b = ACIFabric.objects.create(
            pk=999999,
            name="ACIFSSFFabricB",
            fabric_id=126,
            infra_vlan_vid=3901,
        )
        cls.aci_tenant_b = ACITenant.objects.create(
            name="ACIFSSFTenantB", aci_fabric=cls.aci_fabric_b
        )
        cls.aci_contract_b = ACIContract.objects.create(
            name="ACIFSSFContractB", aci_tenant=cls.aci_tenant_b
        )
        cls.aci_subject_b = ACIContractSubject.objects.create(
            name="ACIFSSFSubjectB", aci_contract=cls.aci_contract_b
        )
        cls.filter_b = ACIContractFilter.objects.create(
            name="ACIFSSFFilterB", aci_tenant=cls.aci_tenant_b
        )
        cls.sf_b = ACIContractSubjectFilter.objects.create(
            aci_contract_subject=cls.aci_subject_b, aci_contract_filter=cls.filter_b
        )

    def test_q(self) -> None:
        """Test search() by the related ACI Contract Subject name."""
        params = {"q": "ACIFSSFSubject"}
        self.assertIn(self.sf_1, self.filterset(params, self.queryset).qs)

    def test_aci_fabric(self) -> None:
        """Test aci_fabric filters by the Subject Filter's own ACI Fabric."""
        params = {"aci_fabric": [self.aci_fabric.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.sf_1, qs)
        self.assertIn(self.sf_2, qs)
        self.assertIn(self.sf_3, qs)
        self.assertNotIn(self.sf_b, qs)

    def test_aci_fabric_id(self) -> None:
        """Test aci_fabric_id filters by the Subject Filter's Fabric."""
        params = {"aci_fabric_id": [self.aci_fabric.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.sf_1, qs)
        self.assertIn(self.sf_2, qs)
        self.assertIn(self.sf_3, qs)
        self.assertNotIn(self.sf_b, qs)

        params_b = {"aci_fabric_id": [self.aci_fabric_b.pk]}
        qs_b = self.filterset(params_b, self.queryset).qs
        self.assertIn(self.sf_b, qs_b)
        self.assertNotIn(self.sf_1, qs_b)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())
