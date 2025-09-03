# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from tenancy.models import Tenant

from ....choices import (
    ContractRelationRoleChoices,
    ContractScopeChoices,
    ContractSubjectFilterActionChoices,
    ContractSubjectFilterApplyDirectionChoices,
    ContractSubjectFilterPriorityChoices,
    QualityOfServiceClassChoices,
    QualityOfServiceDSCPChoices,
)
from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.bridge_domains import ACIBridgeDomain
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
from ....models.tenant.endpoint_security_groups import ACIEndpointSecurityGroup
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF


class ACIContractTestCase(TestCase):
    """Test case for ACIContract model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContract model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_contract_name = "ACITestContract"
        cls.aci_contract_alias = "ACITestContractAlias"
        cls.aci_contract_description = "ACI Test Contract for NetBox ACI Plugin"
        cls.aci_contract_comments = """
        ACI Contract for NetBox ACI Plugin testing.
        """
        cls.nb_tenant_name = "NetBoxTestTenant"
        cls.aci_contract_qos_class = QualityOfServiceClassChoices.CLASS_UNSPECIFIED
        cls.aci_contract_scope = ContractScopeChoices.SCOPE_VRF
        cls.aci_contract_target_dscp = QualityOfServiceDSCPChoices.DSCP_EF

        # Create objects
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.aci_contract = ACIContract.objects.create(
            name=cls.aci_contract_name,
            name_alias=cls.aci_contract_alias,
            description=cls.aci_contract_description,
            comments=cls.aci_contract_comments,
            aci_tenant=cls.aci_tenant,
            nb_tenant=cls.nb_tenant,
            qos_class=cls.aci_contract_qos_class,
            scope=cls.aci_contract_scope,
            target_dscp=cls.aci_contract_target_dscp,
        )

    def test_aci_contract_instance(self) -> None:
        """Test type of created ACI Contract."""
        self.assertTrue(isinstance(self.aci_contract, ACIContract))

    def test_aci_contract_str(self) -> None:
        """Test string value of created ACI Contract."""
        self.assertEqual(self.aci_contract.__str__(), self.aci_contract.name)

    def test_aci_contract_alias(self) -> None:
        """Test alias of ACI Contract."""
        self.assertEqual(self.aci_contract.name_alias, self.aci_contract_alias)

    def test_aci_contract_description(self) -> None:
        """Test description of ACI Contract."""
        self.assertEqual(
            self.aci_contract.description,
            self.aci_contract_description,
        )

    def test_aci_contract_aci_tenant_instance(self) -> None:
        """Test the ACI Tenant instance associated with ACI Contract."""
        self.assertTrue(isinstance(self.aci_contract.aci_tenant, ACITenant))

    def test_aci_contract_aci_tenant_name(self) -> None:
        """Test the ACI Tenant name associated with ACI Contract."""
        self.assertEqual(self.aci_contract.aci_tenant.name, self.aci_tenant_name)

    def test_aci_contract_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with ACI Contract."""
        self.assertTrue(isinstance(self.aci_contract.nb_tenant, Tenant))

    def test_aci_contract_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ACI Contract."""
        self.assertEqual(self.aci_contract.nb_tenant.name, self.nb_tenant_name)

    def test_aci_contract_qos_class(self) -> None:
        """Test 'qos_class' choice of ACI Contract."""
        self.assertEqual(self.aci_contract.qos_class, self.aci_contract_qos_class)

    def test_aci_contract_get_qos_class_color(self) -> None:
        """Test the 'get_qos_class_color' method of ACI Contract."""
        self.assertEqual(
            self.aci_contract.get_qos_class_color(),
            QualityOfServiceClassChoices.colors.get(self.aci_contract_qos_class),
        )

    def test_aci_contract_scope(self) -> None:
        """Test 'scope' choice of ACI Contract."""
        self.assertEqual(self.aci_contract.scope, self.aci_contract_scope)

    def test_aci_contract_get_scope_color(self) -> None:
        """Test the 'get_scope_color' method of ACI Contract."""
        self.assertEqual(
            self.aci_contract.get_scope_color(),
            ContractScopeChoices.colors.get(self.aci_contract_scope),
        )

    def test_aci_contract_target_dscp(self) -> None:
        """Test 'target_dscp' choice of ACI Contract."""
        self.assertEqual(self.aci_contract.target_dscp, self.aci_contract_target_dscp)

    def test_invalid_aci_contract_name(self) -> None:
        """Test validation of ACI Contract naming."""
        contract = ACIContract(name="ACI Contract Test 1")
        with self.assertRaises(ValidationError):
            contract.full_clean()

    def test_invalid_aci_contract_name_length(self) -> None:
        """Test validation of ACI Contract name length."""
        contract = ACIContract(
            name="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            contract.full_clean()

    def test_invalid_aci_contract_name_alias(self) -> None:
        """Test validation of ACI Contract Filter aliasing."""
        contract = ACIContract(name="ACIContractTest1", name_alias="Invalid Alias")
        with self.assertRaises(ValidationError):
            contract.full_clean()

    def test_invalid_aci_contract_name_alias_length(self) -> None:
        """Test validation of ACI Contract Filter name alias length."""
        contract = ACIContract(
            name="ACIContractTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            contract.full_clean()

    def test_invalid_aci_contract_description(self) -> None:
        """Test validation of ACI Contract description."""
        contract = ACIContract(
            name="ACIContractTest1", description="Invalid Description: ö"
        )
        with self.assertRaises(ValidationError):
            contract.full_clean()

    def test_invalid_aci_contract_description_length(self) -> None:
        """Test validation of ACI Contract description length."""
        contract = ACIContract(
            name="ACIContractTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
        )
        with self.assertRaises(ValidationError):
            contract.full_clean()

    def test_constraint_unique_aci_contract_name_per_aci_tenant(
        self,
    ) -> None:
        """Test unique constraint of ACI Contract name per ACI Tenant."""
        tenant = ACITenant.objects.get(name=self.aci_tenant_name)
        duplicate_contract = ACIContract(name=self.aci_contract_name, aci_tenant=tenant)
        with self.assertRaises(IntegrityError):
            duplicate_contract.save()


class ACIContractRelationTestCase(TestCase):
    """Test case for ACIContractRelation model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContract model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_contract_epg_name = "ACITestContractEPG"
        cls.aci_contract_esg_name = "ACITestContractESG"
        cls.nb_tenant_name = "NetBoxTestTenant"
        cls.aci_app_profile_name = "ACITestAppProfile"
        cls.aci_vrf_name = "ACITestVRF"
        cls.aci_bd_name = "ACITestBD"
        cls.aci_epg1_name = "ACITestEPG1"
        cls.aci_epg2_name = "ACITestEPG2"
        cls.aci_useg_epg1_name = "ACITestUSegEPG1"
        cls.aci_useg_epg2_name = "ACITestUSegEPG2"
        cls.aci_esg1_name = "ACITestESG1"
        cls.aci_esg2_name = "ACITestESG2"
        cls.aci_contract_qos_class = QualityOfServiceClassChoices.CLASS_UNSPECIFIED
        cls.aci_contract_scope = ContractScopeChoices.SCOPE_VRF
        cls.aci_contract_target_dscp = QualityOfServiceDSCPChoices.DSCP_EF
        cls.aci_contract_relation_role_cons = ContractRelationRoleChoices.ROLE_CONSUMER
        cls.aci_contract_relation_role_prov = ContractRelationRoleChoices.ROLE_PROVIDER
        cls.aci_contract_relation_comments = """
        ACI Contract Relation for NetBox ACI Plugin testing.
        """

        # Create objects
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.aci_app_profile = ACIAppProfile.objects.create(
            name=cls.aci_app_profile_name, aci_tenant=cls.aci_tenant
        )
        cls.aci_vrf = ACIVRF.objects.create(
            name=cls.aci_vrf_name, aci_tenant=cls.aci_tenant
        )
        cls.aci_bd = ACIBridgeDomain.objects.create(
            name=cls.aci_bd_name,
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
        )
        cls.aci_epg1 = ACIEndpointGroup.objects.create(
            name=cls.aci_epg1_name,
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_epg2 = ACIEndpointGroup.objects.create(
            name=cls.aci_epg2_name,
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_useg_epg1 = ACIUSegEndpointGroup.objects.create(
            name=cls.aci_useg_epg1_name,
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_useg_epg2 = ACIUSegEndpointGroup.objects.create(
            name=cls.aci_useg_epg2_name,
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_esg1 = ACIEndpointSecurityGroup.objects.create(
            name=cls.aci_esg1_name,
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_esg2 = ACIEndpointSecurityGroup.objects.create(
            name=cls.aci_esg2_name,
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_contract_epg = ACIContract.objects.create(
            name=cls.aci_contract_epg_name,
            aci_tenant=cls.aci_tenant,
            nb_tenant=cls.nb_tenant,
            qos_class=cls.aci_contract_qos_class,
            scope=cls.aci_contract_scope,
            target_dscp=cls.aci_contract_target_dscp,
        )
        cls.aci_contract_esg = ACIContract.objects.create(
            name=cls.aci_contract_esg_name,
            aci_tenant=cls.aci_tenant,
            nb_tenant=cls.nb_tenant,
            qos_class=cls.aci_contract_qos_class,
            scope=cls.aci_contract_scope,
            target_dscp=cls.aci_contract_target_dscp,
        )
        cls.aci_contract_relation_epg_cons = ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract_epg,
            aci_object=cls.aci_epg1,
            role=cls.aci_contract_relation_role_cons,
            comments=cls.aci_contract_relation_comments,
        )
        cls.aci_contract_relation_epg_prov = ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract_epg,
            aci_object=cls.aci_epg2,
            role=cls.aci_contract_relation_role_prov,
        )
        cls.aci_contract_relation_useg_epg_cons = ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract_epg,
            aci_object=cls.aci_useg_epg1,
            role=cls.aci_contract_relation_role_cons,
            comments=cls.aci_contract_relation_comments,
        )
        cls.aci_contract_relation_useg_epg_prov = ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract_epg,
            aci_object=cls.aci_useg_epg2,
            role=cls.aci_contract_relation_role_prov,
        )
        cls.aci_contract_relation_epg_vz_any = ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract_epg,
            aci_object=cls.aci_vrf,
            role=cls.aci_contract_relation_role_prov,
        )
        cls.aci_contract_relation_esg_cons = ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract_esg,
            aci_object=cls.aci_esg1,
            role=cls.aci_contract_relation_role_cons,
            comments=cls.aci_contract_relation_comments,
        )
        cls.aci_contract_relation_esg_prov = ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract_esg,
            aci_object=cls.aci_esg2,
            role=cls.aci_contract_relation_role_prov,
        )
        cls.aci_contract_relation_esg_vz_any = ACIContractRelation.objects.create(
            aci_contract=cls.aci_contract_esg,
            aci_object=cls.aci_vrf,
            role=cls.aci_contract_relation_role_prov,
        )

    def test_aci_contract_relation_instance(self) -> None:
        """Test type of created ACI Contract Relation instances."""
        self.assertTrue(
            isinstance(self.aci_contract_relation_epg_cons, ACIContractRelation)
        )
        self.assertTrue(
            isinstance(self.aci_contract_relation_epg_prov, ACIContractRelation)
        )
        self.assertTrue(
            isinstance(self.aci_contract_relation_useg_epg_cons, ACIContractRelation)
        )
        self.assertTrue(
            isinstance(self.aci_contract_relation_useg_epg_prov, ACIContractRelation)
        )
        self.assertTrue(
            isinstance(self.aci_contract_relation_epg_vz_any, ACIContractRelation)
        )
        self.assertTrue(
            isinstance(self.aci_contract_relation_esg_cons, ACIContractRelation)
        )
        self.assertTrue(
            isinstance(self.aci_contract_relation_esg_prov, ACIContractRelation)
        )
        self.assertTrue(
            isinstance(self.aci_contract_relation_esg_vz_any, ACIContractRelation)
        )

    def test_aci_contract_str(self) -> None:
        """Test string values of created ACI Contract Relation instances."""
        self.assertEqual(
            self.aci_contract_relation_epg_cons.__str__(),
            f"{self.aci_contract_epg_name} - "
            f"{self.aci_contract_relation_role_cons} - "
            f"{self.aci_epg1_name}",
        )
        self.assertEqual(
            self.aci_contract_relation_epg_prov.__str__(),
            f"{self.aci_contract_epg_name} - "
            f"{self.aci_contract_relation_role_prov} - "
            f"{self.aci_epg2_name}",
        )
        self.assertEqual(
            self.aci_contract_relation_useg_epg_cons.__str__(),
            f"{self.aci_contract_epg_name} - "
            f"{self.aci_contract_relation_role_cons} - "
            f"{self.aci_useg_epg1_name}",
        )
        self.assertEqual(
            self.aci_contract_relation_useg_epg_prov.__str__(),
            f"{self.aci_contract_epg_name} - "
            f"{self.aci_contract_relation_role_prov} - "
            f"{self.aci_useg_epg2_name}",
        )
        self.assertEqual(
            self.aci_contract_relation_epg_vz_any.__str__(),
            f"{self.aci_contract_epg_name} - "
            f"{self.aci_contract_relation_role_prov} - "
            f"{self.aci_vrf_name}",
        )
        self.assertEqual(
            self.aci_contract_relation_esg_cons.__str__(),
            f"{self.aci_contract_esg_name} - "
            f"{self.aci_contract_relation_role_cons} - "
            f"{self.aci_esg1_name}",
        )
        self.assertEqual(
            self.aci_contract_relation_esg_prov.__str__(),
            f"{self.aci_contract_esg_name} - "
            f"{self.aci_contract_relation_role_prov} - "
            f"{self.aci_esg2_name}",
        )
        self.assertEqual(
            self.aci_contract_relation_esg_vz_any.__str__(),
            f"{self.aci_contract_esg_name} - "
            f"{self.aci_contract_relation_role_prov} - "
            f"{self.aci_vrf_name}",
        )

    def test_aci_contract_relation_aci_contract_instance(self) -> None:
        """Test the Contract instance associated with ACI Contract Relation."""
        self.assertTrue(
            isinstance(self.aci_contract_relation_epg_cons.aci_contract, ACIContract)
        )
        self.assertTrue(
            isinstance(self.aci_contract_relation_epg_prov.aci_contract, ACIContract)
        )
        self.assertTrue(
            isinstance(
                self.aci_contract_relation_useg_epg_cons.aci_contract,
                ACIContract,
            )
        )
        self.assertTrue(
            isinstance(
                self.aci_contract_relation_useg_epg_prov.aci_contract,
                ACIContract,
            )
        )
        self.assertTrue(
            isinstance(self.aci_contract_relation_epg_vz_any.aci_contract, ACIContract)
        )
        self.assertTrue(
            isinstance(self.aci_contract_relation_esg_cons.aci_contract, ACIContract)
        )
        self.assertTrue(
            isinstance(self.aci_contract_relation_esg_prov.aci_contract, ACIContract)
        )
        self.assertTrue(
            isinstance(self.aci_contract_relation_esg_vz_any.aci_contract, ACIContract)
        )

    def test_aci_contract_relation_aci_contract_name(self) -> None:
        """Test the ACI Contract name associated with ACI Contract Relation."""
        self.assertEqual(
            self.aci_contract_relation_epg_cons.aci_contract.name,
            self.aci_contract_epg_name,
        )
        self.assertEqual(
            self.aci_contract_relation_epg_prov.aci_contract.name,
            self.aci_contract_epg_name,
        )
        self.assertEqual(
            self.aci_contract_relation_useg_epg_cons.aci_contract.name,
            self.aci_contract_epg_name,
        )
        self.assertEqual(
            self.aci_contract_relation_useg_epg_prov.aci_contract.name,
            self.aci_contract_epg_name,
        )
        self.assertEqual(
            self.aci_contract_relation_epg_vz_any.aci_contract.name,
            self.aci_contract_epg_name,
        )
        self.assertEqual(
            self.aci_contract_relation_esg_cons.aci_contract.name,
            self.aci_contract_esg_name,
        )
        self.assertEqual(
            self.aci_contract_relation_esg_prov.aci_contract.name,
            self.aci_contract_esg_name,
        )
        self.assertEqual(
            self.aci_contract_relation_esg_vz_any.aci_contract.name,
            self.aci_contract_esg_name,
        )

    def test_aci_contract_relation_aci_object_instance(self) -> None:
        """Test the ACI object instance associated with Contract Relation."""
        self.assertTrue(
            isinstance(
                self.aci_contract_relation_epg_cons.aci_object,
                ACIEndpointGroup,
            )
        )
        self.assertTrue(
            isinstance(
                self.aci_contract_relation_epg_prov.aci_object,
                ACIEndpointGroup,
            )
        )
        self.assertTrue(
            isinstance(
                self.aci_contract_relation_useg_epg_cons.aci_object,
                ACIUSegEndpointGroup,
            )
        )
        self.assertTrue(
            isinstance(
                self.aci_contract_relation_useg_epg_prov.aci_object,
                ACIUSegEndpointGroup,
            )
        )
        self.assertTrue(
            isinstance(self.aci_contract_relation_epg_vz_any.aci_object, ACIVRF)
        )
        self.assertTrue(
            isinstance(
                self.aci_contract_relation_esg_cons.aci_object,
                ACIEndpointSecurityGroup,
            )
        )
        self.assertTrue(
            isinstance(
                self.aci_contract_relation_esg_prov.aci_object,
                ACIEndpointSecurityGroup,
            )
        )
        self.assertTrue(
            isinstance(self.aci_contract_relation_esg_vz_any.aci_object, ACIVRF)
        )

    def test_aci_contract_relation_aci_object_name(self) -> None:
        """Test the ACI object name associated with ACI Contract Relation."""
        self.assertEqual(
            self.aci_contract_relation_epg_cons.aci_object.name,
            self.aci_epg1_name,
        )
        self.assertEqual(
            self.aci_contract_relation_epg_prov.aci_object.name,
            self.aci_epg2_name,
        )
        self.assertEqual(
            self.aci_contract_relation_useg_epg_cons.aci_object.name,
            self.aci_useg_epg1_name,
        )
        self.assertEqual(
            self.aci_contract_relation_useg_epg_prov.aci_object.name,
            self.aci_useg_epg2_name,
        )
        self.assertEqual(
            self.aci_contract_relation_epg_vz_any.aci_object.name,
            self.aci_vrf_name,
        )
        self.assertEqual(
            self.aci_contract_relation_esg_cons.aci_object.name,
            self.aci_esg1_name,
        )
        self.assertEqual(
            self.aci_contract_relation_esg_prov.aci_object.name,
            self.aci_esg2_name,
        )
        self.assertEqual(
            self.aci_contract_relation_esg_vz_any.aci_object.name,
            self.aci_vrf_name,
        )

    def test_aci_contract_relation_role(self) -> None:
        """Test 'role' choice of ACI Contract Relation."""
        self.assertEqual(
            self.aci_contract_relation_epg_cons.role,
            self.aci_contract_relation_role_cons,
        )
        self.assertEqual(
            self.aci_contract_relation_epg_prov.role,
            self.aci_contract_relation_role_prov,
        )
        self.assertEqual(
            self.aci_contract_relation_useg_epg_cons.role,
            self.aci_contract_relation_role_cons,
        )
        self.assertEqual(
            self.aci_contract_relation_useg_epg_prov.role,
            self.aci_contract_relation_role_prov,
        )
        self.assertEqual(
            self.aci_contract_relation_epg_vz_any.role,
            self.aci_contract_relation_role_prov,
        )
        self.assertEqual(
            self.aci_contract_relation_esg_cons.role,
            self.aci_contract_relation_role_cons,
        )
        self.assertEqual(
            self.aci_contract_relation_esg_prov.role,
            self.aci_contract_relation_role_prov,
        )
        self.assertEqual(
            self.aci_contract_relation_esg_vz_any.role,
            self.aci_contract_relation_role_prov,
        )

    def test_aci_contract_relation_get_role_color(self) -> None:
        """Test the 'get_role_color' method of ACI Contract Relation."""
        self.assertEqual(
            self.aci_contract_relation_epg_cons.get_role_color(),
            ContractRelationRoleChoices.colors.get(
                self.aci_contract_relation_role_cons
            ),
        )
        self.assertEqual(
            self.aci_contract_relation_epg_prov.get_role_color(),
            ContractRelationRoleChoices.colors.get(
                self.aci_contract_relation_role_prov
            ),
        )
        self.assertEqual(
            self.aci_contract_relation_useg_epg_cons.get_role_color(),
            ContractRelationRoleChoices.colors.get(
                self.aci_contract_relation_role_cons
            ),
        )
        self.assertEqual(
            self.aci_contract_relation_useg_epg_prov.get_role_color(),
            ContractRelationRoleChoices.colors.get(
                self.aci_contract_relation_role_prov
            ),
        )
        self.assertEqual(
            self.aci_contract_relation_epg_vz_any.get_role_color(),
            ContractRelationRoleChoices.colors.get(
                self.aci_contract_relation_role_prov
            ),
        )
        self.assertEqual(
            self.aci_contract_relation_esg_cons.get_role_color(),
            ContractRelationRoleChoices.colors.get(
                self.aci_contract_relation_role_cons
            ),
        )
        self.assertEqual(
            self.aci_contract_relation_esg_prov.get_role_color(),
            ContractRelationRoleChoices.colors.get(
                self.aci_contract_relation_role_prov
            ),
        )
        self.assertEqual(
            self.aci_contract_relation_esg_vz_any.get_role_color(),
            ContractRelationRoleChoices.colors.get(
                self.aci_contract_relation_role_prov
            ),
        )

    def test_invalid_aci_contract_relation_aci_tenant(self) -> None:
        """Test validation of the same ACI Tenant assignment for Relation."""
        other_tenant = ACITenant.objects.create(name="OtherTenant")
        contract = ACIContract.objects.create(
            name="ACIContractOtherTenant",
            aci_tenant=other_tenant,
            qos_class=self.aci_contract_qos_class,
            scope=self.aci_contract_scope,
            target_dscp=self.aci_contract_target_dscp,
        )
        contract_relation = ACIContractRelation(
            aci_contract=contract,
            aci_object=self.aci_epg1,
            role=self.aci_contract_relation_role_cons,
        )
        with self.assertRaises(ValidationError):
            contract_relation.full_clean()

    def test_invalid_aci_contract_relation_aci_object(self) -> None:
        """Test validation of the correct object assignment for Relation."""
        contract_relation = ACIContractRelation(
            aci_contract=self.aci_contract_epg,
            aci_object=self.aci_bd,
            role=self.aci_contract_relation_role_cons,
        )
        with self.assertRaises(ValidationError):
            contract_relation.full_clean()

    def test_invalid_aci_contract_relation_aci_object_conflict(self) -> None:
        """Test validation of conflicting object assignment for Relation."""
        contract_relation = ACIContractRelation(
            aci_contract=self.aci_contract_epg,
            aci_object=self.aci_epg1,
            role=self.aci_contract_relation_role_cons,
        )
        with self.assertRaises(ValidationError):
            contract_relation.full_clean()

    def test_constraint_unique_aci_object_relation_per_aci_contract(
        self,
    ) -> None:
        """Test unique constraint of ACI Contract Relation per ACI Contract."""
        duplicate_contract_relation = ACIContractRelation(
            aci_contract=self.aci_contract_epg,
            aci_object=self.aci_epg1,
            role=self.aci_contract_relation_role_cons,
        )
        with self.assertRaises(IntegrityError):
            duplicate_contract_relation.save()


class ACIContractSubjectTestCase(TestCase):
    """Test case for ACIContractSubject model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractSubject model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_contract_name = "ACITestContract"
        cls.aci_contract_qos_class = QualityOfServiceClassChoices.CLASS_UNSPECIFIED
        cls.aci_contract_scope = ContractScopeChoices.SCOPE_VRF
        cls.aci_contract_target_dscp = QualityOfServiceDSCPChoices.DSCP_EF
        cls.aci_contract_subject_name = "ACITestContractSubject"
        cls.aci_contract_subject_alias = "ACITestContractSubjectAlias"
        cls.aci_contract_subject_description = (
            "ACI Test Contract Subject for NetBox ACI Plugin"
        )
        cls.aci_contract_subject_comments = """
        ACI Contract Subject for NetBox ACI Plugin testing.
        """
        cls.nb_tenant_name = "NetBoxTestTenant"
        cls.aci_contract_subject_apply_both_directions_enabled = True
        cls.aci_contract_subject_qos_class = (
            QualityOfServiceClassChoices.CLASS_UNSPECIFIED
        )
        cls.aci_contract_subject_qos_class_cons_to_prov = (
            QualityOfServiceClassChoices.CLASS_UNSPECIFIED
        )
        cls.aci_contract_subject_qos_class_prov_to_cons = (
            QualityOfServiceClassChoices.CLASS_UNSPECIFIED
        )
        cls.aci_contract_subject_reverse_filter_ports_enabled = True
        cls.aci_contract_subject_service_graph_name = "ACITestServiceGraph"
        cls.aci_contract_subject_service_graph_name_cons_to_prov = "ACITestServiceGraph"
        cls.aci_contract_subject_service_graph_name_prov_to_cons = "ACITestServiceGraph"
        cls.aci_contract_subject_target_dscp = QualityOfServiceDSCPChoices.DSCP_EF
        cls.aci_contract_subject_target_dscp_cons_to_prov = (
            QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED
        )
        cls.aci_contract_subject_target_dscp_prov_to_cons = (
            QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED
        )

        # Create objects
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.aci_contract = ACIContract.objects.create(
            name=cls.aci_contract_name,
            aci_tenant=cls.aci_tenant,
            nb_tenant=cls.nb_tenant,
            qos_class=cls.aci_contract_qos_class,
            scope=cls.aci_contract_scope,
            target_dscp=cls.aci_contract_target_dscp,
        )
        cls.aci_contract_subject = ACIContractSubject.objects.create(
            name=cls.aci_contract_subject_name,
            name_alias=cls.aci_contract_subject_alias,
            description=cls.aci_contract_subject_description,
            comments=cls.aci_contract_subject_comments,
            aci_contract=cls.aci_contract,
            nb_tenant=cls.nb_tenant,
            apply_both_directions_enabled=(
                cls.aci_contract_subject_apply_both_directions_enabled
            ),
            qos_class=cls.aci_contract_subject_qos_class,
            qos_class_cons_to_prov=(cls.aci_contract_subject_qos_class_cons_to_prov),
            qos_class_prov_to_cons=(cls.aci_contract_subject_qos_class_prov_to_cons),
            reverse_filter_ports_enabled=(
                cls.aci_contract_subject_reverse_filter_ports_enabled
            ),
            service_graph_name=cls.aci_contract_subject_service_graph_name,
            service_graph_name_cons_to_prov=(
                cls.aci_contract_subject_service_graph_name_cons_to_prov
            ),
            service_graph_name_prov_to_cons=(
                cls.aci_contract_subject_service_graph_name_prov_to_cons
            ),
            target_dscp=cls.aci_contract_subject_target_dscp,
            target_dscp_cons_to_prov=(
                cls.aci_contract_subject_target_dscp_cons_to_prov
            ),
            target_dscp_prov_to_cons=(
                cls.aci_contract_subject_target_dscp_prov_to_cons
            ),
        )

    def test_aci_contract_subject_instance(self) -> None:
        """Test type of created ACI Contract Subject."""
        self.assertTrue(isinstance(self.aci_contract_subject, ACIContractSubject))

    def test_aci_contract_subject_str(self) -> None:
        """Test string value of created ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.__str__(),
            f"{self.aci_contract_subject_name}",
        )

    def test_aci_contract_subject_alias(self) -> None:
        """Test alias of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.name_alias,
            self.aci_contract_subject_alias,
        )

    def test_aci_contract_subject_description(self) -> None:
        """Test description of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.description,
            self.aci_contract_subject_description,
        )

    def test_aci_contract_subject_aci_contract_instance(
        self,
    ) -> None:
        """Test the Contract instance associated with Contract Subject."""
        self.assertTrue(isinstance(self.aci_contract_subject.aci_contract, ACIContract))

    def test_aci_contract_subject_aci_contract_name(self) -> None:
        """Test the Contract name associated with Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.aci_contract.name,
            self.aci_contract_name,
        )

    def test_aci_contract_subject_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with Contract Subject."""
        self.assertTrue(isinstance(self.aci_contract_subject.nb_tenant, Tenant))

    def test_aci_contract_subject_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with Contract Subject."""
        self.assertEqual(self.aci_contract_subject.nb_tenant.name, self.nb_tenant_name)

    def test_aci_contract_subject_apply_both_directions_enabled(self) -> None:
        """Test the 'apply_both_directions_enabled' of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.apply_both_directions_enabled,
            self.aci_contract_subject_apply_both_directions_enabled,
        )

    def test_aci_contract_subject_qos_class(self) -> None:
        """Test 'qos_class' choice of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.qos_class,
            self.aci_contract_subject_qos_class,
        )

    def test_aci_contract_subject_get_qos_class_color(self) -> None:
        """Test the 'get_qos_class_color' method of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.get_qos_class_color(),
            QualityOfServiceClassChoices.colors.get(
                self.aci_contract_subject_qos_class
            ),
        )

    def test_aci_contract_subject_qos_class_cons_to_prov(self) -> None:
        """Test 'qos_class_cons_to_prov' choice of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.qos_class_cons_to_prov,
            self.aci_contract_subject_qos_class_cons_to_prov,
        )

    def test_aci_contract_subject_get_qos_class_cons_to_prov_color(
        self,
    ) -> None:
        """Test the 'get_qos_class_cons_to_prov_color' method of Subject."""
        self.assertEqual(
            self.aci_contract_subject.get_qos_class_cons_to_prov_color(),
            QualityOfServiceClassChoices.colors.get(
                self.aci_contract_subject_qos_class_cons_to_prov
            ),
        )

    def test_aci_contract_subject_qos_class_prov_to_cons(self) -> None:
        """Test 'qos_class_prov_to_cons' choice of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.qos_class_prov_to_cons,
            self.aci_contract_subject_qos_class_prov_to_cons,
        )

    def test_aci_contract_subject_get_qos_class_prov_to_cons_color(
        self,
    ) -> None:
        """Test the 'get_qos_class_prov_to_cons_color' method of Subject."""
        self.assertEqual(
            self.aci_contract_subject.get_qos_class_prov_to_cons_color(),
            QualityOfServiceClassChoices.colors.get(
                self.aci_contract_subject_qos_class_prov_to_cons
            ),
        )

    def test_aci_contract_subject_reverse_filter_ports_enabled(self) -> None:
        """Test the 'reverse_filter_ports_enabled' of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.reverse_filter_ports_enabled,
            self.aci_contract_subject_reverse_filter_ports_enabled,
        )

    def test_aci_contract_subject_service_graph_name(self) -> None:
        """Test the 'service_graph_name' of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.service_graph_name,
            self.aci_contract_subject_service_graph_name,
        )

    def test_aci_contract_subject_service_graph_name_cons_to_prov(
        self,
    ) -> None:
        """Test the 'service_graph_name_cons_to_prov' of Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.service_graph_name_cons_to_prov,
            self.aci_contract_subject_service_graph_name_cons_to_prov,
        )

    def test_aci_contract_subject_service_graph_name_prov_to_cons(
        self,
    ) -> None:
        """Test the 'service_graph_name_prov_to_cons' of Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.service_graph_name_prov_to_cons,
            self.aci_contract_subject_service_graph_name_prov_to_cons,
        )

    def test_aci_contract_subject_target_dscp(self) -> None:
        """Test 'target_dscp' choice of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.target_dscp,
            self.aci_contract_subject_target_dscp,
        )

    def test_aci_contract_subject_target_dscp_cons_to_prov(self) -> None:
        """Test 'target_dscp_cons_to_prov' choice of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.target_dscp_cons_to_prov,
            self.aci_contract_subject_target_dscp_cons_to_prov,
        )

    def test_aci_contract_subject_target_dscp_prov_to_cons(self) -> None:
        """Test 'target_dscp_prov_to_cons' choice of ACI Contract Subject."""
        self.assertEqual(
            self.aci_contract_subject.target_dscp_prov_to_cons,
            self.aci_contract_subject_target_dscp_prov_to_cons,
        )

    def test_invalid_aci_contract_subject_name(self) -> None:
        """Test validation of ACI Contract Subject naming."""
        contract_subject = ACIContractSubject(name="ACI Contract Filter Entry Test 1")
        with self.assertRaises(ValidationError):
            contract_subject.full_clean()

    def test_invalid_aci_contract_subject_name_length(self) -> None:
        """Test validation of ACI Contract Subject name length."""
        contract_subject = ACIContractSubject(
            name="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            contract_subject.full_clean()

    def test_invalid_aci_contract_subject_name_alias(self) -> None:
        """Test validation of ACI Contract Subject aliasing."""
        contract_subject = ACIContractSubject(
            name="ACIContractSubjectTest1", name_alias="Invalid Alias"
        )
        with self.assertRaises(ValidationError):
            contract_subject.full_clean()

    def test_invalid_aci_contract_subject_name_alias_length(self) -> None:
        """Test validation of ACI Contract Subject name alias length."""
        contract_subject = ACIContractSubject(
            name="ACIContractSubjectTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            contract_subject.full_clean()

    def test_invalid_aci_contract_subject_description(self) -> None:
        """Test validation of ACI Contract Subject description."""
        contract_subject = ACIContractSubject(
            name="ACIContractSubjectTest1",
            description="Invalid Description: ö",
        )
        with self.assertRaises(ValidationError):
            contract_subject.full_clean()

    def test_invalid_aci_contract_subject_description_length(
        self,
    ) -> None:
        """Test validation of ACI Contract Subject description length."""
        contract_subject = ACIContractSubject(
            name="ACIContractSubjectTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
        )
        with self.assertRaises(ValidationError):
            contract_subject.full_clean()

    def test_constraint_unique_aci_contract_subject_name_per_aci_contract(
        self,
    ) -> None:
        """Test unique constraint of ACI Contract Subject name."""
        contract = ACIContract.objects.get(name=self.aci_contract_name)
        duplicate_contract_subject = ACIContractSubject(
            name=self.aci_contract_subject_name,
            aci_contract=contract,
        )
        with self.assertRaises(IntegrityError):
            duplicate_contract_subject.save()


class ACIContractSubjectFilterTestCase(TestCase):
    """Test case for ACIContractSubjectFilter model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIContractSubjectFilter model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_contract_name = "ACITestContract"
        cls.aci_contract_qos_class = QualityOfServiceClassChoices.CLASS_UNSPECIFIED
        cls.aci_contract_scope = ContractScopeChoices.SCOPE_VRF
        cls.aci_contract_target_dscp = QualityOfServiceDSCPChoices.DSCP_EF
        cls.aci_contract_subject_name = "ACITestContractSubject"
        cls.nb_tenant_name = "NetBoxTestTenant"
        cls.aci_contract_subject_apply_both_directions_enabled = True
        cls.aci_contract_subject_qos_class = (
            QualityOfServiceClassChoices.CLASS_UNSPECIFIED
        )
        cls.aci_contract_subject_qos_class_cons_to_prov = (
            QualityOfServiceClassChoices.CLASS_UNSPECIFIED
        )
        cls.aci_contract_subject_qos_class_prov_to_cons = (
            QualityOfServiceClassChoices.CLASS_UNSPECIFIED
        )
        cls.aci_contract_subject_reverse_filter_ports_enabled = True
        cls.aci_contract_subject_target_dscp = QualityOfServiceDSCPChoices.DSCP_EF
        cls.aci_contract_subject_target_dscp_cons_to_prov = (
            QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED
        )
        cls.aci_contract_subject_target_dscp_prov_to_cons = (
            QualityOfServiceDSCPChoices.DSCP_UNSPECIFIED
        )
        cls.aci_contract_subject_filter_action = (
            ContractSubjectFilterActionChoices.ACTION_PERMIT
        )
        cls.aci_contract_subject_filter_apply_direction = (
            ContractSubjectFilterApplyDirectionChoices.DIR_BOTH
        )
        cls.aci_contract_subject_filter_log_enabled = True
        cls.aci_contract_subject_filter_policy_compression_enabled = False
        cls.aci_contract_subject_filter_priority = (
            ContractSubjectFilterPriorityChoices.CLASS_DEFAULT
        )
        cls.aci_contract_filter_name = "ACITestContractFilter"

        # Create objects
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.aci_contract_filter = ACIContractFilter.objects.create(
            name=cls.aci_contract_filter_name,
            aci_tenant=cls.aci_tenant,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_contract = ACIContract.objects.create(
            name=cls.aci_contract_name,
            aci_tenant=cls.aci_tenant,
            nb_tenant=cls.nb_tenant,
            qos_class=cls.aci_contract_qos_class,
            scope=cls.aci_contract_scope,
            target_dscp=cls.aci_contract_target_dscp,
        )
        cls.aci_contract_subject = ACIContractSubject.objects.create(
            name=cls.aci_contract_subject_name,
            aci_contract=cls.aci_contract,
            nb_tenant=cls.nb_tenant,
            apply_both_directions_enabled=(
                cls.aci_contract_subject_apply_both_directions_enabled
            ),
            qos_class=cls.aci_contract_subject_qos_class,
            qos_class_cons_to_prov=(cls.aci_contract_subject_qos_class_cons_to_prov),
            qos_class_prov_to_cons=(cls.aci_contract_subject_qos_class_prov_to_cons),
            reverse_filter_ports_enabled=(
                cls.aci_contract_subject_reverse_filter_ports_enabled
            ),
            target_dscp=cls.aci_contract_subject_target_dscp,
            target_dscp_cons_to_prov=(
                cls.aci_contract_subject_target_dscp_cons_to_prov
            ),
            target_dscp_prov_to_cons=(
                cls.aci_contract_subject_target_dscp_prov_to_cons
            ),
        )
        cls.aci_contract_subject_filter = ACIContractSubjectFilter.objects.create(
            aci_contract_filter=cls.aci_contract_filter,
            aci_contract_subject=cls.aci_contract_subject,
            action=cls.aci_contract_subject_filter_action,
            apply_direction=cls.aci_contract_subject_filter_apply_direction,
            log_enabled=cls.aci_contract_subject_filter_log_enabled,
            policy_compression_enabled=(
                cls.aci_contract_subject_filter_policy_compression_enabled
            ),
            priority=cls.aci_contract_subject_filter_priority,
        )

    def test_aci_contract_subject_filter_instance(self) -> None:
        """Test type of created ACI Contract Subject Filter."""
        self.assertTrue(
            isinstance(self.aci_contract_subject_filter, ACIContractSubjectFilter)
        )

    def test_aci_contract_subject_filter_str(self) -> None:
        """Test string value of created ACI Contract Subject Filter."""
        self.assertEqual(
            self.aci_contract_subject_filter.__str__(),
            f"{self.aci_contract_subject_name}-{self.aci_contract_filter_name}",
        )

    def test_aci_contract_subject_filter_aci_contract_instance(
        self,
    ) -> None:
        """Test the Contract instance associated with Subject Filter."""
        self.assertTrue(
            isinstance(self.aci_contract_subject_filter.aci_contract, ACIContract)
        )

    def test_aci_contract_subject_filter_aci_contract_filter_instance(
        self,
    ) -> None:
        """Test the Contract Filter instance associated with Subject Filter."""
        self.assertTrue(
            isinstance(
                self.aci_contract_subject_filter.aci_contract_filter,
                ACIContractFilter,
            )
        )

    def test_aci_contract_subject_filter_aci_contract_name(self) -> None:
        """Test the Contract name associated with Contract Subject Filter."""
        self.assertEqual(
            self.aci_contract_subject_filter.aci_contract.name,
            self.aci_contract_name,
        )

    def test_aci_contract_subject_filter_aci_contract_filter_name(
        self,
    ) -> None:
        """Test the Contract Filter name associated with Subject Filter."""
        self.assertEqual(
            self.aci_contract_subject_filter.aci_contract_filter.name,
            self.aci_contract_filter_name,
        )

    def test_aci_contract_subject_filter_action(self) -> None:
        """Test the 'action' of ACI Contract Subject Filter."""
        self.assertEqual(
            self.aci_contract_subject_filter.action,
            self.aci_contract_subject_filter_action,
        )

    def test_aci_contract_subject_filter_get_action_color(self) -> None:
        """Test the 'get_action_color' method of Contract Subject Filter."""
        self.assertEqual(
            self.aci_contract_subject_filter.get_action_color(),
            ContractSubjectFilterActionChoices.colors.get(
                self.aci_contract_subject_filter_action
            ),
        )

    def test_aci_contract_subject_filter_apply_direction(self) -> None:
        """Test the 'apply_direction' of ACI Contract Subject Filter."""
        self.assertEqual(
            self.aci_contract_subject_filter.apply_direction,
            self.aci_contract_subject_filter_apply_direction,
        )

    def test_aci_contract_subject_filter_get_apply_direction_color(
        self,
    ) -> None:
        """Test the 'get_apply_direction_color' method of Subject Filter."""
        self.assertEqual(
            self.aci_contract_subject_filter.get_apply_direction_color(),
            ContractSubjectFilterApplyDirectionChoices.colors.get(
                self.aci_contract_subject_filter_apply_direction
            ),
        )

    def test_aci_contract_subject_filter_log_enabled(self) -> None:
        """Test the 'log_enabled' of ACI Contract Subject Filter."""
        self.assertEqual(
            self.aci_contract_subject_filter.log_enabled,
            self.aci_contract_subject_filter_log_enabled,
        )

    def test_aci_contract_subject_filter_policy_compression_enabled(
        self,
    ) -> None:
        """Test the 'policy_compression_enabled' of Contract Subject Filter."""
        self.assertEqual(
            self.aci_contract_subject_filter.policy_compression_enabled,
            self.aci_contract_subject_filter_policy_compression_enabled,
        )

    def test_aci_contract_subject_filter_priority(self) -> None:
        """Test the 'priority' of ACI Contract Subject Filter."""
        self.assertEqual(
            self.aci_contract_subject_filter.priority,
            self.aci_contract_subject_filter_priority,
        )

    def test_aci_contract_subject_filter_get_priority_color(self) -> None:
        """Test the 'get_priority_color' method of Contract Subject Filter."""
        self.assertEqual(
            self.aci_contract_subject_filter.get_priority_color(),
            ContractSubjectFilterPriorityChoices.colors.get(
                self.aci_contract_subject_filter_priority
            ),
        )

    def test_constraint_unique_aci_contract_subject_filter_per_aci_contract_subject(
        self,
    ) -> None:
        """Test unique constraint of ACI Contract Subject Filter assigment."""
        contract_subject = ACIContractSubject.objects.get(
            name=self.aci_contract_subject_name
        )
        duplicate_contract_subject_filter = ACIContractSubjectFilter(
            aci_contract_filter=self.aci_contract_filter,
            aci_contract_subject=contract_subject,
        )
        with self.assertRaises(IntegrityError):
            duplicate_contract_subject_filter.save()
