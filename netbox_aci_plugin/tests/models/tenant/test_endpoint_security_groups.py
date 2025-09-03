# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from ipam.models import IPAddress, Prefix
from tenancy.models import Tenant

from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.bridge_domains import ACIBridgeDomain
from ....models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
)
from ....models.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroup,
    ACIEsgEndpointGroupSelector,
    ACIEsgEndpointSelector,
)
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF


class ACIEndpointSecurityGroupTestCase(TestCase):
    """Test case for ACIEndpointSecurityGroup model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEndpointSecurityGroup model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_app_profile_name = "ACITestAppProfile"
        cls.aci_vrf_name = "ACITestVRF"
        cls.aci_esg_name = "ACITestESG"
        cls.aci_esg_alias = "ACITestESGAlias"
        cls.aci_esg_description = (
            "ACI Test Endpoint Security Group for NetBox ACI Plugin"
        )
        cls.aci_esg_comments = """
        ACI Endpoint Security Group for NetBox ACI Plugin testing.
        """
        cls.aci_esg_admin_shutdown = False
        cls.aci_esg_intra_esg_isolation_enabled = False
        cls.aci_esg_preferred_group_member_enabled = False
        cls.nb_tenant_name = "NetBoxTestTenant"

        # Create objects
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.aci_app_profile = ACIAppProfile.objects.create(
            name=cls.aci_app_profile_name, aci_tenant=cls.aci_tenant
        )
        cls.aci_vrf = ACIVRF.objects.create(
            name=cls.aci_vrf_name, aci_tenant=cls.aci_tenant
        )
        cls.aci_esg = ACIEndpointSecurityGroup.objects.create(
            name=cls.aci_esg_name,
            name_alias=cls.aci_esg_alias,
            description=cls.aci_esg_description,
            comments=cls.aci_esg_comments,
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
            nb_tenant=cls.nb_tenant,
            admin_shutdown=cls.aci_esg_admin_shutdown,
            intra_esg_isolation_enabled=(cls.aci_esg_intra_esg_isolation_enabled),
            preferred_group_member_enabled=(cls.aci_esg_preferred_group_member_enabled),
        )

    def test_create_aci_endpoint_security_group_instance(self) -> None:
        """Test type of created ACI Endpoint Security Group."""
        self.assertTrue(isinstance(self.aci_esg, ACIEndpointSecurityGroup))

    def test_aci_endpoint_security_group_str(self) -> None:
        """Test string representation of ACI Endpoint Security Group."""
        self.assertEqual(self.aci_esg.__str__(), self.aci_esg.name)

    def test_aci_endpoint_security_group_name_alias(self) -> None:
        """Test name alias of ACI Endpoint Security Group."""
        self.assertEqual(self.aci_esg.name_alias, self.aci_esg_alias)

    def test_aci_endpoint_security_group_description(self) -> None:
        """Test description of ACI Endpoint Security Group."""
        self.assertEqual(self.aci_esg.description, self.aci_esg_description)

    def test_aci_endpoint_security_group_aci_tenant_instance(self) -> None:
        """Test the ACI Tenant instance associated with ACI ESG."""
        self.assertTrue(isinstance(self.aci_esg.aci_tenant, ACITenant))

    def test_aci_endpoint_security_group_aci_tenant_name(self) -> None:
        """Test the ACI Tenant name associated with ACI ESG."""
        self.assertEqual(self.aci_esg.aci_tenant.name, self.aci_tenant_name)

    def test_aci_endpoint_security_group_aci_app_profile_instance(
        self,
    ) -> None:
        """Test the ACI App Profile instance associated with ACI ESG."""
        self.assertTrue(isinstance(self.aci_esg.aci_app_profile, ACIAppProfile))

    def test_aci_endpoint_security_group_aci_app_profile_name(self) -> None:
        """Test the ACI App Profile name associated with ACI ESG."""
        self.assertEqual(self.aci_esg.aci_app_profile.name, self.aci_app_profile_name)

    def test_aci_endpoint_security_group_aci_vrf_instance(self) -> None:
        """Test the ACI VRF instance associated with ACI ESG."""
        self.assertTrue(isinstance(self.aci_esg.aci_vrf, ACIVRF))

    def test_aci_endpoint_security_group_aci_vrf_name(self) -> None:
        """Test the ACI VRF name associated with ACI ESG."""
        self.assertEqual(self.aci_esg.aci_vrf.name, self.aci_vrf_name)

    def test_aci_endpoint_security_group_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with ACI ESG."""
        self.assertTrue(isinstance(self.aci_esg.nb_tenant, Tenant))

    def test_aci_endpoint_security_group_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ACI ESG."""
        self.assertEqual(self.aci_esg.nb_tenant.name, self.nb_tenant_name)

    def test_aci_endpoint_security_group_admin_shutdown(self) -> None:
        """Test 'admin shutdown' option of ACI Endpoint Security Group."""
        self.assertEqual(self.aci_esg.admin_shutdown, self.aci_esg_admin_shutdown)

    def test_aci_endpoint_security_group_intra_esg_isolation_enabled(
        self,
    ) -> None:
        """Test 'intra ESG isolation enabled' option of ACI ESG."""
        self.assertEqual(
            self.aci_esg.intra_esg_isolation_enabled,
            self.aci_esg_intra_esg_isolation_enabled,
        )

    def test_aci_endpoint_security_group_preferred_group_member_enabled(
        self,
    ) -> None:
        """Test 'preferred group member enabled' option of ACI ESG."""
        self.assertEqual(
            self.aci_esg.preferred_group_member_enabled,
            self.aci_esg_preferred_group_member_enabled,
        )

    def test_invalid_aci_endpoint_security_group_name(self) -> None:
        """Test validation of ACI Endpoint Security Group naming."""
        esg = ACIEndpointSecurityGroup(
            name="ACI ESG Test 1",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            esg.full_clean()

    def test_invalid_aci_endpoint_security_group_name_length(self) -> None:
        """Test validation of ACI Endpoint Security Group name length."""
        esg = ACIEndpointSecurityGroup(
            name="A" * 65,  # Exceeding the maximum length of 64
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            esg.full_clean()

    def test_invalid_aci_endpoint_security_group_name_alias(self) -> None:
        """Test validation of ACI Endpoint Security Group aliasing."""
        esg = ACIEndpointSecurityGroup(
            name="ACIESGTest1",
            name_alias="Invalid Alias",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            esg.full_clean()

    def test_invalid_aci_endpoint_security_group_name_alias_length(
        self,
    ) -> None:
        """Test validation of ACI Endpoint Security Group name alias length."""
        esg = ACIEndpointSecurityGroup(
            name="ACIESGTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            esg.full_clean()

    def test_invalid_aci_endpoint_security_group_description(self) -> None:
        """Test validation of ACI Endpoint Security Group description."""
        esg = ACIEndpointSecurityGroup(
            name="ACIESGTest1",
            description="Invalid Description: ö",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            esg.full_clean()

    def test_invalid_aci_endpoint_security_group_description_length(
        self,
    ) -> None:
        """Test validation of ACI ESG description length."""
        esg = ACIEndpointSecurityGroup(
            name="ACIESGTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            esg.full_clean()

    def test_valid_aci_esg_aci_vrf_assignment_from_tenant_common(
        self,
    ) -> None:
        """Test valid assignment of ACI VRF from ACI Tenant 'common'."""
        tenant_common = ACITenant.objects.get_or_create(name="common")[0]
        vrf_common = ACIVRF.objects.create(name="common_vrf", aci_tenant=tenant_common)
        esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIESGTest1",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=vrf_common,
        )
        esg.full_clean()
        esg.save()
        self.assertEqual(esg.aci_vrf, vrf_common)

    def test_invalid_aci_esg_aci_vrf_assignment_from_tenant_other(
        self,
    ) -> None:
        """Test invalid assignment of ACI VRF from ACI Tenant 'other'."""
        tenant_other = ACITenant.objects.get_or_create(name="other")[0]
        vrf_other = ACIVRF.objects.create(name="other_vrf", aci_tenant=tenant_other)
        esg = ACIEndpointSecurityGroup(
            name="ACIESGTest1",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=vrf_other,
        )
        with self.assertRaises(ValidationError):
            esg.full_clean()
            esg.save()

    def test_constraint_unique_aci_esg_name_per_aci_app_profile(
        self,
    ) -> None:
        """Test unique constraint of ACI ESG name per ACI App Profile."""
        app_profile = ACIAppProfile.objects.get(name=self.aci_app_profile_name)
        vrf = ACIVRF.objects.get(name=self.aci_vrf_name)
        duplicate_esg = ACIEndpointSecurityGroup(
            name=self.aci_esg_name,
            aci_app_profile=app_profile,
            aci_vrf=vrf,
        )
        with self.assertRaises(IntegrityError):
            duplicate_esg.save()


class ACIEsgEndpointGroupSelectorTestCase(TestCase):
    """Test case for ACIEsgEndpointGroupSelector model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEsgEndpointGroupSelector model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_app_profile_name = "ACITestAppProfile"
        cls.aci_vrf_name = "ACITestVRF"
        cls.aci_bd_name = "ACITestBD"
        cls.aci_esg_name = "ACITestESG"
        cls.aci_esg_epg_sel1_name = "ACITestESGEPGSelector1"
        cls.aci_esg_epg_sel2_name = "ACITestESGEPGSelector2"
        cls.aci_esg_epg_sel3_name = "ACITestESGEPGSelector3"
        cls.aci_esg_epg_sel_alias = "ACITestESGEPGSelectorAlias"
        cls.aci_esg_epg_sel_description = (
            "ACI Test ESG Endpoint Group Selector for NetBox ACI Plugin"
        )
        cls.aci_esg_epg_sel_comments = """
        ACI ESG Endpoint Group Selector for NetBox ACI Plugin testing.
        """
        cls.aci_epg1_name = "ACITestEPG1"
        cls.aci_epg2_name = "ACITestEPG2"
        cls.aci_useg_epg1_name = "ACITestuSegEPG1"
        cls.nb_tenant_name = "NetBoxTestTenant"

        # Create depending objects
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

        # Create parent objects
        cls.aci_esg = ACIEndpointSecurityGroup.objects.create(
            name=cls.aci_esg_name,
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
            nb_tenant=cls.nb_tenant,
        )

        # Create selector objects
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

        # Create model objects
        cls.aci_esg_epg_sel1 = ACIEsgEndpointGroupSelector.objects.create(
            name=cls.aci_esg_epg_sel1_name,
            name_alias=cls.aci_esg_epg_sel_alias,
            description=cls.aci_esg_epg_sel_description,
            comments=cls.aci_esg_epg_sel_comments,
            aci_endpoint_security_group=cls.aci_esg,
            aci_epg_object=cls.aci_epg1,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_esg_epg_sel2 = ACIEsgEndpointGroupSelector.objects.create(
            name=cls.aci_esg_epg_sel2_name,
            name_alias=cls.aci_esg_epg_sel_alias,
            description=cls.aci_esg_epg_sel_description,
            comments=cls.aci_esg_epg_sel_comments,
            aci_endpoint_security_group=cls.aci_esg,
            aci_epg_object=cls.aci_epg2,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_esg_epg_sel3 = ACIEsgEndpointGroupSelector.objects.create(
            name=cls.aci_esg_epg_sel3_name,
            name_alias=cls.aci_esg_epg_sel_alias,
            description=cls.aci_esg_epg_sel_description,
            comments=cls.aci_esg_epg_sel_comments,
            aci_endpoint_security_group=cls.aci_esg,
            aci_epg_object=cls.aci_useg_epg1,
            nb_tenant=cls.nb_tenant,
        )

    def test_create_aci_esg_endpoint_group_selector_instance(self) -> None:
        """Test type of created ACI ESG Endpoint Group Selector."""
        self.assertTrue(isinstance(self.aci_esg_epg_sel1, ACIEsgEndpointGroupSelector))
        self.assertTrue(isinstance(self.aci_esg_epg_sel2, ACIEsgEndpointGroupSelector))
        self.assertTrue(isinstance(self.aci_esg_epg_sel3, ACIEsgEndpointGroupSelector))

    def test_aci_esg_endpoint_group_selector_str(self) -> None:
        """Test string representation of ACI ESG Endpoint Group Selector."""
        self.assertEqual(
            self.aci_esg_epg_sel1.__str__(),
            f"{self.aci_esg_epg_sel1_name} "
            f"({self.aci_esg_epg_sel1.aci_endpoint_security_group.name})",
        )
        self.assertEqual(
            self.aci_esg_epg_sel2.__str__(),
            f"{self.aci_esg_epg_sel2_name} "
            f"({self.aci_esg_epg_sel2.aci_endpoint_security_group.name})",
        )
        self.assertEqual(
            self.aci_esg_epg_sel3.__str__(),
            f"{self.aci_esg_epg_sel3_name} "
            f"({self.aci_esg_epg_sel3.aci_endpoint_security_group.name})",
        )

    def test_aci_esg_endpoint_group_selector_name_alias(self) -> None:
        """Test name alias of ACI ESG Endpoint Group Selector."""
        self.assertEqual(self.aci_esg_epg_sel1.name_alias, self.aci_esg_epg_sel_alias)
        self.assertEqual(self.aci_esg_epg_sel2.name_alias, self.aci_esg_epg_sel_alias)
        self.assertEqual(self.aci_esg_epg_sel3.name_alias, self.aci_esg_epg_sel_alias)

    def test_aci_esg_endpoint_group_selector_description(self) -> None:
        """Test description of ACI ESG Endpoint Group Selector."""
        self.assertEqual(
            self.aci_esg_epg_sel1.description, self.aci_esg_epg_sel_description
        )
        self.assertEqual(
            self.aci_esg_epg_sel2.description, self.aci_esg_epg_sel_description
        )
        self.assertEqual(
            self.aci_esg_epg_sel3.description, self.aci_esg_epg_sel_description
        )

    def test_aci_esg_epg_selector_aci_endpoint_security_group_instance(
        self,
    ) -> None:
        """Test the ACI ESG instance associated with ACI ESG EPG Selector."""
        self.assertTrue(
            isinstance(
                self.aci_esg_epg_sel1.aci_endpoint_security_group,
                ACIEndpointSecurityGroup,
            )
        )
        self.assertTrue(
            isinstance(
                self.aci_esg_epg_sel2.aci_endpoint_security_group,
                ACIEndpointSecurityGroup,
            )
        )
        self.assertTrue(
            isinstance(
                self.aci_esg_epg_sel3.aci_endpoint_security_group,
                ACIEndpointSecurityGroup,
            )
        )

    def test_aci_esg_epg_selector_aci_endpoint_security_group_name(
        self,
    ) -> None:
        """Test the ACI ESG name associated with ACI ESG EPG Selector."""
        self.assertEqual(
            self.aci_esg_epg_sel1.aci_endpoint_security_group.name,
            self.aci_esg_name,
        )
        self.assertEqual(
            self.aci_esg_epg_sel2.aci_endpoint_security_group.name,
            self.aci_esg_name,
        )
        self.assertEqual(
            self.aci_esg_epg_sel3.aci_endpoint_security_group.name,
            self.aci_esg_name,
        )

    def test_aci_esg_epg_selector_aci_endpoint_group_instance(self) -> None:
        """Test the ACI EPG instance associated with ACI ESG EPG Selector."""
        self.assertTrue(
            isinstance(self.aci_esg_epg_sel1.aci_epg_object, ACIEndpointGroup)
        )
        self.assertTrue(
            isinstance(self.aci_esg_epg_sel2.aci_epg_object, ACIEndpointGroup)
        )
        self.assertTrue(
            isinstance(self.aci_esg_epg_sel3.aci_epg_object, ACIUSegEndpointGroup)
        )

    def test_aci_esg_epg_selector_aci_endpoint_group_name(self) -> None:
        """Test the ACI EPG name associated with ACI ESG EPG Selector."""
        self.assertEqual(self.aci_esg_epg_sel1.aci_epg_object.name, self.aci_epg1_name)
        self.assertEqual(self.aci_esg_epg_sel2.aci_epg_object.name, self.aci_epg2_name)
        self.assertEqual(
            self.aci_esg_epg_sel3.aci_epg_object.name, self.aci_useg_epg1_name
        )

    def test_aci_esg_endpoint_group_selector_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with ESG EPG Selector."""
        self.assertTrue(isinstance(self.aci_esg_epg_sel1.nb_tenant, Tenant))
        self.assertTrue(isinstance(self.aci_esg_epg_sel2.nb_tenant, Tenant))
        self.assertTrue(isinstance(self.aci_esg_epg_sel3.nb_tenant, Tenant))

    def test_aci_esg_endpoint_group_selector_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ESG EPG Selector."""
        self.assertEqual(self.aci_esg_epg_sel1.nb_tenant.name, self.nb_tenant_name)
        self.assertEqual(self.aci_esg_epg_sel2.nb_tenant.name, self.nb_tenant_name)
        self.assertEqual(self.aci_esg_epg_sel3.nb_tenant.name, self.nb_tenant_name)

    def test_invalid_aci_esg_endpoint_group_selector_name(self) -> None:
        """Test validation of ACI ESG Endpoint Group Selector naming."""
        invalid_esg_epg_sel = ACIEsgEndpointGroupSelector(
            name="ACI ESG Endpoint Group Selector Test 1",
            aci_endpoint_security_group=self.aci_esg,
            aci_epg_object=self.aci_epg1,
        )
        with self.assertRaises(ValidationError):
            invalid_esg_epg_sel.full_clean()

    def test_invalid_aci_esg_endpoint_group_selector_name_length(self) -> None:
        """Test validation of ACI ESG Endpoint Group Selector name length."""
        invalid_esg_epg_sel = ACIEsgEndpointGroupSelector(
            name="A" * 65,  # Exceeding the maximum length of 64
            aci_endpoint_security_group=self.aci_esg,
            aci_epg_object=self.aci_epg1,
        )
        with self.assertRaises(ValidationError):
            invalid_esg_epg_sel.full_clean()

    def test_invalid_aci_esg_endpoint_group_selector_name_alias(self) -> None:
        """Test validation of ACI ESG Endpoint Group Selector aliasing."""
        invalid_esg_epg_sel = ACIEsgEndpointGroupSelector(
            name="ACIESGTest1",
            name_alias="Invalid Alias",
            aci_endpoint_security_group=self.aci_esg,
            aci_epg_object=self.aci_epg1,
        )
        with self.assertRaises(ValidationError):
            invalid_esg_epg_sel.full_clean()

    def test_invalid_aci_esg_endpoint_group_selector_name_alias_length(
        self,
    ) -> None:
        """Test validation of ESG Endpoint Group Selector name alias length."""
        invalid_esg_epg_sel = ACIEsgEndpointGroupSelector(
            name="ACIESGTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
            aci_endpoint_security_group=self.aci_esg,
            aci_epg_object=self.aci_epg1,
        )
        with self.assertRaises(ValidationError):
            invalid_esg_epg_sel.full_clean()

    def test_invalid_aci_esg_endpoint_group_selector_description(self) -> None:
        """Test validation of ACI ESG Endpoint Group Selector description."""
        invalid_esg_epg_sel = ACIEsgEndpointGroupSelector(
            name="ACIESGTest1",
            description="Invalid Description: ö",
            aci_endpoint_security_group=self.aci_esg,
            aci_epg_object=self.aci_epg1,
        )
        with self.assertRaises(ValidationError):
            invalid_esg_epg_sel.full_clean()

    def test_invalid_aci_esg_endpoint_group_selector_description_length(
        self,
    ) -> None:
        """Test validation of ACI ESG EPG Selector description length."""
        invalid_esg_epg_sel = ACIEsgEndpointGroupSelector(
            name="ACIESGTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
            aci_endpoint_security_group=self.aci_esg,
            aci_epg_object=self.aci_epg1,
        )
        with self.assertRaises(ValidationError):
            invalid_esg_epg_sel.full_clean()

    def test_invalid_aci_esg_epg_selector_aci_epg_object(self) -> None:
        """Test validation of the object assignment for ESG EPG Selector."""
        invalid_esg_epg_sel = ACIEsgEndpointGroupSelector(
            name="ACIESGEPGSelectorInvalidTest1",
            aci_endpoint_security_group=self.aci_esg,
            aci_epg_object=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            invalid_esg_epg_sel.full_clean()

    def test_invalid_aci_esg_epg_selector_aci_epg_assignment_from_vrf_other(
        self,
    ) -> None:
        """Test invalid assignment of ACI EPG from ACI VRF 'other'."""
        vrf_other = ACIVRF.objects.create(name="other_vrf", aci_tenant=self.aci_tenant)
        bd_other = ACIBridgeDomain.objects.create(
            name="other_bd", aci_tenant=self.aci_tenant, aci_vrf=vrf_other
        )
        epg_other = ACIEndpointGroup.objects.create(
            name="other_vrf_epg",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=bd_other,
        )
        esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIESGInvalidTest1",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        esg_epg_sel = ACIEsgEndpointGroupSelector(
            name="ACIESGEPGSelectorInvalidTest1",
            aci_endpoint_security_group=esg,
            aci_epg_object=epg_other,
        )
        with self.assertRaises(ValidationError):
            esg_epg_sel.full_clean()
            esg_epg_sel.save()

    def test_invalid_aci_esg_epg_selector_aci_epg_assignment_from_tenant_other(
        self,
    ) -> None:
        """Test invalid assignment of ACI EPG from ACI Tenant 'other'."""
        tenant_other = ACITenant.objects.get_or_create(name="other")[0]
        vrf_other = ACIVRF.objects.create(
            name="other_tenant_vrf", aci_tenant=tenant_other
        )
        bd_other = ACIBridgeDomain.objects.create(
            name="other_tenant_bd", aci_tenant=tenant_other, aci_vrf=vrf_other
        )
        app_profile_other = ACIAppProfile.objects.create(
            name="other_tenant_app_profile", aci_tenant=tenant_other
        )
        epg_other = ACIEndpointGroup.objects.create(
            name="other_tenant_epg",
            aci_app_profile=app_profile_other,
            aci_bridge_domain=bd_other,
        )
        esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIESGInvalidTest2",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        esg_epg_sel = ACIEsgEndpointGroupSelector(
            name="ACIESGEPGSelectorInvalidTest1",
            aci_endpoint_security_group=esg,
            aci_epg_object=epg_other,
        )
        with self.assertRaises(ValidationError):
            esg_epg_sel.full_clean()
            esg_epg_sel.save()

    def test_constraint_unique_aci_esg_epg_selector_name_per_aci_app_profile(
        self,
    ) -> None:
        """Test unique constraint of ESG EPG Selector name per App Profile."""
        aci_epg = ACIEndpointGroup.objects.create(
            name="ACIESGEPGSelectorDuplicateTest",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        duplicate_esg_epg_selector = ACIEsgEndpointGroupSelector(
            name=self.aci_esg_epg_sel1_name,
            aci_endpoint_security_group=self.aci_esg,
            aci_epg_object=aci_epg,
        )
        with self.assertRaises(IntegrityError):
            duplicate_esg_epg_selector.save()

    def test_constraint_unique_aci_esg_epg_selector_epg_per_aci_app_profile(
        self,
    ) -> None:
        """Test unique constraint of ESG EPG Selector EPG per App Profile."""
        duplicate_esg_epg_selector = ACIEsgEndpointGroupSelector(
            name="ACIESGEPGSelectorDuplicateTest",
            aci_endpoint_security_group=self.aci_esg,
            aci_epg_object=self.aci_epg1,
        )
        with self.assertRaises(IntegrityError):
            duplicate_esg_epg_selector.save()


class ACIEsgEndpointSelectorTestCase(TestCase):
    """Test case for ACIEsgEndpointSelector model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEsgEndpointSelector model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_app_profile_name = "ACITestAppProfile"
        cls.aci_vrf_name = "ACITestVRF"
        cls.aci_bd_name = "ACITestBD"
        cls.aci_esg_name = "ACITestESG"
        cls.aci_esg_ep_sel1_name = "ACITestESGEndpointSelector1"
        cls.aci_esg_ep_sel2_name = "ACITestESGEndpointSelector2"
        cls.aci_esg_ep_sel3_name = "ACITestESGEndpointSelector3"
        cls.aci_esg_ep_sel_alias = "ACITestESGEndpointSelectorAlias"
        cls.aci_esg_ep_sel_description = (
            "ACI Test ESG Endpoint Selector for NetBox ACI Plugin"
        )
        cls.aci_esg_ep_sel_comments = """
        ACI ESG Endpoint Selector for NetBox ACI Plugin testing.
        """
        cls.nb_tenant_name = "NetBoxTestTenant"

        # Create depending objects
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.aci_app_profile = ACIAppProfile.objects.create(
            name=cls.aci_app_profile_name, aci_tenant=cls.aci_tenant
        )
        cls.aci_vrf = ACIVRF.objects.create(
            name=cls.aci_vrf_name, aci_tenant=cls.aci_tenant
        )

        # Create parent objects
        cls.aci_esg = ACIEndpointSecurityGroup.objects.create(
            name=cls.aci_esg_name,
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
            nb_tenant=cls.nb_tenant,
        )

        # Create selector objects
        cls.ip_address1 = IPAddress.objects.create(address="192.168.1.1/24")
        cls.ip_address2 = IPAddress.objects.create(address="192.168.1.2/24")
        cls.prefix1 = Prefix.objects.create(prefix="192.168.1.0/24")

        # Create model objects
        cls.aci_esg_ep_sel1 = ACIEsgEndpointSelector.objects.create(
            name=cls.aci_esg_ep_sel1_name,
            name_alias=cls.aci_esg_ep_sel_alias,
            description=cls.aci_esg_ep_sel_description,
            comments=cls.aci_esg_ep_sel_comments,
            aci_endpoint_security_group=cls.aci_esg,
            ep_object=cls.ip_address1,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_esg_ep_sel2 = ACIEsgEndpointSelector.objects.create(
            name=cls.aci_esg_ep_sel2_name,
            name_alias=cls.aci_esg_ep_sel_alias,
            description=cls.aci_esg_ep_sel_description,
            comments=cls.aci_esg_ep_sel_comments,
            aci_endpoint_security_group=cls.aci_esg,
            ep_object=cls.ip_address2,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_esg_ep_sel3 = ACIEsgEndpointSelector.objects.create(
            name=cls.aci_esg_ep_sel3_name,
            name_alias=cls.aci_esg_ep_sel_alias,
            description=cls.aci_esg_ep_sel_description,
            comments=cls.aci_esg_ep_sel_comments,
            aci_endpoint_security_group=cls.aci_esg,
            ep_object=cls.prefix1,
            nb_tenant=cls.nb_tenant,
        )

    def test_create_aci_esg_endpoint_selector_instance(self) -> None:
        """Test type of created ACI ESG Endpoint Selector."""
        self.assertTrue(isinstance(self.aci_esg_ep_sel1, ACIEsgEndpointSelector))
        self.assertTrue(isinstance(self.aci_esg_ep_sel2, ACIEsgEndpointSelector))
        self.assertTrue(isinstance(self.aci_esg_ep_sel3, ACIEsgEndpointSelector))

    def test_aci_esg_endpoint_selector_str(self) -> None:
        """Test string representation of ACI ESG Endpoint Selector."""
        self.assertEqual(
            self.aci_esg_ep_sel1.__str__(),
            f"{self.aci_esg_ep_sel1_name} "
            f"({self.aci_esg_ep_sel1.aci_endpoint_security_group.name})",
        )
        self.assertEqual(
            self.aci_esg_ep_sel2.__str__(),
            f"{self.aci_esg_ep_sel2_name} "
            f"({self.aci_esg_ep_sel2.aci_endpoint_security_group.name})",
        )
        self.assertEqual(
            self.aci_esg_ep_sel3.__str__(),
            f"{self.aci_esg_ep_sel3_name} "
            f"({self.aci_esg_ep_sel3.aci_endpoint_security_group.name})",
        )

    def test_aci_esg_endpoint_selector_name_alias(self) -> None:
        """Test name alias of ACI ESG Endpoint Selector."""
        self.assertEqual(self.aci_esg_ep_sel1.name_alias, self.aci_esg_ep_sel_alias)
        self.assertEqual(self.aci_esg_ep_sel2.name_alias, self.aci_esg_ep_sel_alias)
        self.assertEqual(self.aci_esg_ep_sel3.name_alias, self.aci_esg_ep_sel_alias)

    def test_aci_esg_endpoint_selector_description(self) -> None:
        """Test description of ACI ESG Endpoint Selector."""
        self.assertEqual(
            self.aci_esg_ep_sel1.description, self.aci_esg_ep_sel_description
        )
        self.assertEqual(
            self.aci_esg_ep_sel2.description, self.aci_esg_ep_sel_description
        )
        self.assertEqual(
            self.aci_esg_ep_sel3.description, self.aci_esg_ep_sel_description
        )

    def test_aci_esg_ep_selector_aci_endpoint_security_group_instance(
        self,
    ) -> None:
        """Test the ACI ESG instance associated with ESG Endpoint Selector."""
        self.assertTrue(
            isinstance(
                self.aci_esg_ep_sel1.aci_endpoint_security_group,
                ACIEndpointSecurityGroup,
            )
        )
        self.assertTrue(
            isinstance(
                self.aci_esg_ep_sel2.aci_endpoint_security_group,
                ACIEndpointSecurityGroup,
            )
        )
        self.assertTrue(
            isinstance(
                self.aci_esg_ep_sel3.aci_endpoint_security_group,
                ACIEndpointSecurityGroup,
            )
        )

    def test_aci_esg_ep_selector_aci_endpoint_security_group_name(
        self,
    ) -> None:
        """Test the ACI ESG name associated with ACI ESG Endpoint Selector."""
        self.assertEqual(
            self.aci_esg_ep_sel1.aci_endpoint_security_group.name,
            self.aci_esg_name,
        )
        self.assertEqual(
            self.aci_esg_ep_sel2.aci_endpoint_security_group.name,
            self.aci_esg_name,
        )
        self.assertEqual(
            self.aci_esg_ep_sel3.aci_endpoint_security_group.name,
            self.aci_esg_name,
        )

    def test_aci_esg_ep_selector_aci_endpoint_group_instance(self) -> None:
        """Test the Endpoint instance associated with ESG Endpoint Selector."""
        self.assertTrue(isinstance(self.aci_esg_ep_sel1.ep_object, IPAddress))
        self.assertTrue(isinstance(self.aci_esg_ep_sel2.ep_object, IPAddress))
        self.assertTrue(isinstance(self.aci_esg_ep_sel3.ep_object, Prefix))

    def test_aci_esg_endpoint_selector_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with ESG EP Selector."""
        self.assertTrue(isinstance(self.aci_esg_ep_sel1.nb_tenant, Tenant))
        self.assertTrue(isinstance(self.aci_esg_ep_sel2.nb_tenant, Tenant))
        self.assertTrue(isinstance(self.aci_esg_ep_sel3.nb_tenant, Tenant))

    def test_aci_esg_endpoint_selector_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ESG EP Selector."""
        self.assertEqual(self.aci_esg_ep_sel1.nb_tenant.name, self.nb_tenant_name)
        self.assertEqual(self.aci_esg_ep_sel2.nb_tenant.name, self.nb_tenant_name)
        self.assertEqual(self.aci_esg_ep_sel3.nb_tenant.name, self.nb_tenant_name)

    def test_invalid_aci_esg_endpoint_selector_name(self) -> None:
        """Test validation of ACI ESG Endpoint Selector naming."""
        invalid_esg_ep_sel = ACIEsgEndpointSelector(
            name="ACI ESG Endpoint Selector Test 1",
            aci_endpoint_security_group=self.aci_esg,
            ep_object=self.ip_address1,
        )
        with self.assertRaises(ValidationError):
            invalid_esg_ep_sel.full_clean()

    def test_invalid_aci_esg_endpoint_selector_name_length(self) -> None:
        """Test validation of ACI ESG Endpoint Selector name length."""
        invalid_esg_ep_sel = ACIEsgEndpointSelector(
            name="A" * 65,  # Exceeding the maximum length of 64
            aci_endpoint_security_group=self.aci_esg,
            ep_object=self.ip_address1,
        )
        with self.assertRaises(ValidationError):
            invalid_esg_ep_sel.full_clean()

    def test_invalid_aci_esg_endpoint_selector_name_alias(self) -> None:
        """Test validation of ACI ESG Endpoint Selector aliasing."""
        invalid_esg_ep_sel = ACIEsgEndpointSelector(
            name="ACIESGTest1",
            name_alias="Invalid Alias",
            aci_endpoint_security_group=self.aci_esg,
            ep_object=self.ip_address1,
        )
        with self.assertRaises(ValidationError):
            invalid_esg_ep_sel.full_clean()

    def test_invalid_aci_esg_endpoint_selector_name_alias_length(self) -> None:
        """Test validation of ACI ESG Endpoint Selector name alias length."""
        invalid_esg_ep_sel = ACIEsgEndpointSelector(
            name="ACIESGTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
            aci_endpoint_security_group=self.aci_esg,
            ep_object=self.ip_address1,
        )
        with self.assertRaises(ValidationError):
            invalid_esg_ep_sel.full_clean()

    def test_invalid_aci_esg_endpoint_selector_description(self) -> None:
        """Test validation of ACI ESG Endpoint Selector description."""
        invalid_esg_ep_sel = ACIEsgEndpointSelector(
            name="ACIESGTest1",
            description="Invalid Description: ö",
            aci_endpoint_security_group=self.aci_esg,
            ep_object=self.ip_address1,
        )
        with self.assertRaises(ValidationError):
            invalid_esg_ep_sel.full_clean()

    def test_invalid_aci_esg_endpoint_selector_description_length(
        self,
    ) -> None:
        """Test validation of ACI ESG Endpoint Selector description length."""
        invalid_esg_ep_sel = ACIEsgEndpointSelector(
            name="ACIESGTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
            aci_endpoint_security_group=self.aci_esg,
            ep_object=self.ip_address1,
        )
        with self.assertRaises(ValidationError):
            invalid_esg_ep_sel.full_clean()

    def test_invalid_aci_esg_ep_selector_aci_epg_object(self) -> None:
        """Test validation of the object assignment for ESG EP Selector."""
        invalid_esg_ep_sel = ACIEsgEndpointSelector(
            name="ACIESGEndpointSelectorInvalidTest1",
            aci_endpoint_security_group=self.aci_esg,
            ep_object=self.aci_vrf,
        )
        with self.assertRaises(ValidationError):
            invalid_esg_ep_sel.full_clean()

    def test_constraint_unique_aci_esg_ep_selector_name_per_aci_app_profile(
        self,
    ) -> None:
        """Test unique constraint of ESG EP Selector name per App Profile."""
        prefix2 = Prefix.objects.create(prefix="192.168.2.0/24")
        duplicate_esg_ep_selector = ACIEsgEndpointSelector(
            name=self.aci_esg_ep_sel1_name,
            aci_endpoint_security_group=self.aci_esg,
            ep_object=prefix2,
        )
        with self.assertRaises(IntegrityError):
            duplicate_esg_ep_selector.save()

    def test_constraint_unique_aci_esg_ep_selector_epg_per_aci_app_profile(
        self,
    ) -> None:
        """Test unique constraint of ESG EP Selector EP per App Profile."""
        duplicate_esg_ep_selector = ACIEsgEndpointSelector(
            name="ACIESGEndpointSelectorDuplicateTest",
            aci_endpoint_security_group=self.aci_esg,
            ep_object=self.ip_address1,
        )
        with self.assertRaises(IntegrityError):
            duplicate_esg_ep_selector.save()
