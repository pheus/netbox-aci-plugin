# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.models import MACAddress
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from ipam.models import IPAddress, Prefix
from tenancy.models import Tenant

from ....choices import (
    QualityOfServiceClassChoices,
    USegAttributeMatchOperatorChoices,
    USegAttributeTypeChoices,
)
from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.bridge_domains import ACIBridgeDomain
from ....models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
    ACIUSegNetworkAttribute,
)
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF


class ACIEndpointGroupTestCase(TestCase):
    """Test case for ACIEndpointGroup model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIBridgeDomainSubnet model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_app_profile_name = "ACITestAppProfile"
        cls.aci_vrf_name = "ACITestVRF"
        cls.aci_bd_name = "ACITestBD"
        cls.aci_epg_name = "ACITestEPG"
        cls.aci_epg_alias = "ACITestEPGAlias"
        cls.aci_epg_description = "ACI Test Endpoint Group for NetBox ACI Plugin"
        cls.aci_epg_comments = """
        ACI Endpoint Group for NetBox ACI Plugin testing.
        """
        cls.aci_epg_admin_shutdown = False
        cls.aci_epg_custom_qos_policy_name = "CustomQoSPolicy1"
        cls.aci_epg_flood_in_encap_enabled = False
        cls.aci_epg_intra_epg_isolation_enabled = False
        cls.aci_epg_qos_class = QualityOfServiceClassChoices.CLASS_LEVEL_3
        cls.aci_epg_preferred_group_member_enabled = False
        cls.aci_epg_proxy_arp_enabled = False
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
        cls.aci_bd = ACIBridgeDomain.objects.create(
            name=cls.aci_bd_name,
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
        )
        cls.aci_epg = ACIEndpointGroup.objects.create(
            name=cls.aci_epg_name,
            name_alias=cls.aci_epg_alias,
            description=cls.aci_epg_description,
            comments=cls.aci_epg_comments,
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
            nb_tenant=cls.nb_tenant,
            admin_shutdown=cls.aci_epg_admin_shutdown,
            custom_qos_policy_name=cls.aci_epg_custom_qos_policy_name,
            flood_in_encap_enabled=cls.aci_epg_flood_in_encap_enabled,
            intra_epg_isolation_enabled=(cls.aci_epg_intra_epg_isolation_enabled),
            qos_class=cls.aci_epg_qos_class,
            preferred_group_member_enabled=(cls.aci_epg_preferred_group_member_enabled),
            proxy_arp_enabled=cls.aci_epg_proxy_arp_enabled,
        )

    def test_create_aci_endpoint_group_instance(self) -> None:
        """Test type of created ACI Endpoint Group."""
        self.assertTrue(isinstance(self.aci_epg, ACIEndpointGroup))

    def test_aci_endpoint_group_str(self) -> None:
        """Test string representation of ACI Endpoint Group."""
        self.assertEqual(self.aci_epg.__str__(), self.aci_epg.name)

    def test_aci_endpoint_group_name_alias(self) -> None:
        """Test name alias of ACI Endpoint Group."""
        self.assertEqual(self.aci_epg.name_alias, self.aci_epg_alias)

    def test_aci_endpoint_group_description(self) -> None:
        """Test description of ACI Endpoint Group."""
        self.assertEqual(self.aci_epg.description, self.aci_epg_description)

    def test_aci_endpoint_group_aci_tenant_instance(self) -> None:
        """Test the ACI Tenant instance associated with ACI EPG."""
        self.assertTrue(isinstance(self.aci_epg.aci_tenant, ACITenant))

    def test_aci_endpoint_group_aci_tenant_name(self) -> None:
        """Test the ACI Tenant name associated with ACI EPG."""
        self.assertEqual(self.aci_epg.aci_tenant.name, self.aci_tenant_name)

    def test_aci_endpoint_group_aci_app_profile_instance(self) -> None:
        """Test the ACI App Profile instance associated with ACI EPG."""
        self.assertTrue(isinstance(self.aci_epg.aci_app_profile, ACIAppProfile))

    def test_aci_endpoint_group_aci_app_profile_name(self) -> None:
        """Test the ACI App Profile name associated with ACI EPG."""
        self.assertEqual(self.aci_epg.aci_app_profile.name, self.aci_app_profile_name)

    def test_aci_endpoint_group_aci_vrf_instance(self) -> None:
        """Test the ACI VRF instance associated with ACI EPG."""
        self.assertTrue(isinstance(self.aci_epg.aci_vrf, ACIVRF))

    def test_aci_endpoint_group_aci_vrf_name(self) -> None:
        """Test the ACI VRF name associated with ACI EPG."""
        self.assertEqual(self.aci_epg.aci_vrf.name, self.aci_vrf_name)

    def test_aci_endpoint_group_aci_bridge_domain_instance(self) -> None:
        """Test the ACI Bridge Domain instance associated with ACI EPG."""
        self.assertTrue(isinstance(self.aci_epg.aci_bridge_domain, ACIBridgeDomain))

    def test_aci_endpoint_group_aci_bridge_domain_name(self) -> None:
        """Test the ACI Bridge Domain name associated with ACI EPG."""
        self.assertEqual(self.aci_epg.aci_bridge_domain.name, self.aci_bd_name)

    def test_aci_endpoint_group_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with ACI EPG."""
        self.assertTrue(isinstance(self.aci_epg.nb_tenant, Tenant))

    def test_aci_endpoint_group_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ACI EPG."""
        self.assertEqual(self.aci_epg.nb_tenant.name, self.nb_tenant_name)

    def test_aci_endpoint_group_admin_shutdown(self) -> None:
        """Test 'admin shutdown' option of ACI Endpoint Group."""
        self.assertEqual(self.aci_epg.admin_shutdown, self.aci_epg_admin_shutdown)

    def test_aci_endpoint_group_custom_qos_policy_name(self) -> None:
        """Test 'custom QOS policy name' of ACI Endpoint Group."""
        self.assertEqual(
            self.aci_epg.custom_qos_policy_name,
            self.aci_epg_custom_qos_policy_name,
        )

    def test_aci_endpoint_group_flood_in_encap_enabled(self) -> None:
        """Test 'flood in encap enabled' option of ACI Endpoint Group."""
        self.assertEqual(
            self.aci_epg.flood_in_encap_enabled,
            self.aci_epg_flood_in_encap_enabled,
        )

    def test_aci_endpoint_group_intra_epg_isolation_enabled(self) -> None:
        """Test 'intra EPG isolation enabled' option of ACI Endpoint Group."""
        self.assertEqual(
            self.aci_epg.intra_epg_isolation_enabled,
            self.aci_epg_intra_epg_isolation_enabled,
        )

    def test_aci_endpoint_group_qos_class(self) -> None:
        """Test 'QoS class' of ACI Endpoint Group."""
        self.assertEqual(self.aci_epg.qos_class, self.aci_epg_qos_class)

    def test_aci_endpoint_group_preferred_group_member_enabled(self) -> None:
        """Test 'preferred group member enabled' option of ACI EPG."""
        self.assertEqual(
            self.aci_epg.preferred_group_member_enabled,
            self.aci_epg_preferred_group_member_enabled,
        )

    def test_aci_endpoint_group_proxy_arp_enabled(self) -> None:
        """Test 'proxy ARP enabled' option of ACI Endpoint Group."""
        self.assertEqual(self.aci_epg.proxy_arp_enabled, self.aci_epg_proxy_arp_enabled)

    def test_aci_endpoint_group_get_qos_class_color(self) -> None:
        """Test the 'get_qos_class_color' method of ACI Endpoint Group."""
        self.assertEqual(
            self.aci_epg.get_qos_class_color(),
            QualityOfServiceClassChoices.colors.get(
                QualityOfServiceClassChoices.CLASS_LEVEL_3
            ),
        )

    def test_invalid_aci_endpoint_group_name(self) -> None:
        """Test validation of ACI Endpoint Group naming."""
        epg = ACIEndpointGroup(
            name="ACI EPG Test 1",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_endpoint_group_name_length(self) -> None:
        """Test validation of ACI Endpoint Group name length."""
        epg = ACIEndpointGroup(
            name="A" * 65,  # Exceeding the maximum length of 64
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_endpoint_group_name_alias(self) -> None:
        """Test validation of ACI Endpoint Group aliasing."""
        epg = ACIEndpointGroup(
            name="ACIEPGTest1",
            name_alias="Invalid Alias",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_endpoint_group_name_alias_length(self) -> None:
        """Test validation of ACI Endpoint Group name alias length."""
        epg = ACIEndpointGroup(
            name="ACIEPGTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_endpoint_group_description(self) -> None:
        """Test validation of ACI Endpoint Group description."""
        epg = ACIEndpointGroup(
            name="ACIEPGTest1",
            description="Invalid Description: ö",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_endpoint_group_description_length(self) -> None:
        """Test validation of ACI Endpoint Group description length."""
        epg = ACIEndpointGroup(
            name="ACIEPGTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_valid_aci_endpoint_group_aci_bd_assignment_from_tenant_common(
        self,
    ) -> None:
        """Test valid assignment of ACI BD from ACI Tenant 'common'."""
        tenant_common = ACITenant.objects.get_or_create(name="common")[0]
        vrf_common = ACIVRF.objects.create(name="common_vrf", aci_tenant=tenant_common)
        bd_common = ACIBridgeDomain.objects.create(
            name="common_bd", aci_tenant=tenant_common, aci_vrf=vrf_common
        )
        epg = ACIEndpointGroup.objects.create(
            name="ACIEPGTest1",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=bd_common,
        )
        epg.full_clean()
        epg.save()
        self.assertEqual(epg.aci_bridge_domain, bd_common)

    def test_invalid_aci_endpoint_group_aci_bd_assignment_from_tenant_other(
        self,
    ) -> None:
        """Test invalid assignment of ACI BD from ACI Tenant 'other'."""
        tenant_other = ACITenant.objects.get_or_create(name="other")[0]
        vrf_other = ACIVRF.objects.create(name="other_vrf", aci_tenant=tenant_other)
        bd_other = ACIBridgeDomain.objects.create(
            name="other_bd", aci_tenant=tenant_other, aci_vrf=vrf_other
        )
        epg = ACIEndpointGroup(
            name="ACIEPGTest1",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=bd_other,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()
            epg.save()

    def test_constraint_unique_aci_endpoint_group_name_per_aci_app_profile(
        self,
    ) -> None:
        """Test unique constraint of ACI EPG name per ACI App Profile."""
        app_profile = ACIAppProfile.objects.get(name=self.aci_app_profile_name)
        bd = ACIBridgeDomain.objects.get(name=self.aci_bd_name)
        duplicate_epg = ACIEndpointGroup(
            name=self.aci_epg_name,
            aci_app_profile=app_profile,
            aci_bridge_domain=bd,
        )
        with self.assertRaises(IntegrityError):
            duplicate_epg.save()


class ACIUSegEndpointGroupTestCase(TestCase):
    """Test case for ACIUSegEndpointGroup model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIUSegEndpointGroup model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_app_profile_name = "ACITestAppProfile"
        cls.aci_vrf_name = "ACITestVRF"
        cls.aci_bd_name = "ACITestBD"
        cls.aci_useg_epg_name = "ACITestUSegEPG"
        cls.aci_useg_epg_alias = "ACITestUSegEPGAlias"
        cls.aci_useg_epg_description = (
            "ACI Test uSeg Endpoint Group for NetBox ACI Plugin"
        )
        cls.aci_useg_epg_comments = """
        ACI uSeg Endpoint Group for NetBox ACI Plugin testing.
        """
        cls.aci_useg_epg_admin_shutdown = False
        cls.aci_useg_epg_custom_qos_policy_name = "CustomQoSPolicy1"
        cls.aci_useg_epg_flood_in_encap_enabled = False
        cls.aci_useg_epg_intra_epg_isolation_enabled = False
        cls.aci_useg_epg_match_operator = USegAttributeMatchOperatorChoices.MATCH_ANY
        cls.aci_useg_epg_qos_class = QualityOfServiceClassChoices.CLASS_LEVEL_3
        cls.aci_useg_epg_preferred_group_member_enabled = False
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
        cls.aci_bd = ACIBridgeDomain.objects.create(
            name=cls.aci_bd_name,
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
        )
        cls.aci_useg_epg = ACIUSegEndpointGroup.objects.create(
            name=cls.aci_useg_epg_name,
            name_alias=cls.aci_useg_epg_alias,
            description=cls.aci_useg_epg_description,
            comments=cls.aci_useg_epg_comments,
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
            nb_tenant=cls.nb_tenant,
            admin_shutdown=cls.aci_useg_epg_admin_shutdown,
            custom_qos_policy_name=cls.aci_useg_epg_custom_qos_policy_name,
            flood_in_encap_enabled=cls.aci_useg_epg_flood_in_encap_enabled,
            intra_epg_isolation_enabled=(cls.aci_useg_epg_intra_epg_isolation_enabled),
            match_operator=cls.aci_useg_epg_match_operator,
            qos_class=cls.aci_useg_epg_qos_class,
            preferred_group_member_enabled=(
                cls.aci_useg_epg_preferred_group_member_enabled
            ),
        )

    def test_create_aci_useg_endpoint_group_instance(self) -> None:
        """Test type of created ACI uSeg Endpoint Group."""
        self.assertTrue(isinstance(self.aci_useg_epg, ACIUSegEndpointGroup))

    def test_aci_useg_endpoint_group_str(self) -> None:
        """Test string representation of ACI uSeg Endpoint Group."""
        self.assertEqual(self.aci_useg_epg.__str__(), self.aci_useg_epg.name)

    def test_aci_useg_endpoint_group_name_alias(self) -> None:
        """Test name alias of ACI uSeg Endpoint Group."""
        self.assertEqual(self.aci_useg_epg.name_alias, self.aci_useg_epg_alias)

    def test_aci_useg_endpoint_group_description(self) -> None:
        """Test description of ACI uSeg Endpoint Group."""
        self.assertEqual(self.aci_useg_epg.description, self.aci_useg_epg_description)

    def test_aci_useg_endpoint_group_aci_tenant_instance(self) -> None:
        """Test the ACI Tenant instance associated with ACI uSeg EPG."""
        self.assertTrue(isinstance(self.aci_useg_epg.aci_tenant, ACITenant))

    def test_aci_useg_endpoint_group_aci_tenant_name(self) -> None:
        """Test the ACI Tenant name associated with ACI uSeg EPG."""
        self.assertEqual(self.aci_useg_epg.aci_tenant.name, self.aci_tenant_name)

    def test_aci_useg_endpoint_group_aci_app_profile_instance(self) -> None:
        """Test the ACI App Profile instance associated with ACI uSeg EPG."""
        self.assertTrue(isinstance(self.aci_useg_epg.aci_app_profile, ACIAppProfile))

    def test_aci_useg_endpoint_group_aci_app_profile_name(self) -> None:
        """Test the ACI App Profile name associated with ACI uSeg EPG."""
        self.assertEqual(
            self.aci_useg_epg.aci_app_profile.name, self.aci_app_profile_name
        )

    def test_aci_useg_endpoint_group_aci_vrf_instance(self) -> None:
        """Test the ACI VRF instance associated with ACI uSeg EPG."""
        self.assertTrue(isinstance(self.aci_useg_epg.aci_vrf, ACIVRF))

    def test_aci_useg_endpoint_group_aci_vrf_name(self) -> None:
        """Test the ACI VRF name associated with ACI uSeg EPG."""
        self.assertEqual(self.aci_useg_epg.aci_vrf.name, self.aci_vrf_name)

    def test_aci_useg_endpoint_group_aci_bridge_domain_instance(self) -> None:
        """Test the ACI Bridge Domain instance associated with ACI uSeg EPG."""
        self.assertTrue(
            isinstance(self.aci_useg_epg.aci_bridge_domain, ACIBridgeDomain)
        )

    def test_aci_useg_endpoint_group_aci_bridge_domain_name(self) -> None:
        """Test the ACI Bridge Domain name associated with ACI uSeg EPG."""
        self.assertEqual(self.aci_useg_epg.aci_bridge_domain.name, self.aci_bd_name)

    def test_aci_useg_endpoint_group_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with ACI uSeg EPG."""
        self.assertTrue(isinstance(self.aci_useg_epg.nb_tenant, Tenant))

    def test_aci_useg_endpoint_group_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ACI uSeg EPG."""
        self.assertEqual(self.aci_useg_epg.nb_tenant.name, self.nb_tenant_name)

    def test_aci_useg_endpoint_group_admin_shutdown(self) -> None:
        """Test 'admin shutdown' option of ACI uSeg Endpoint Group."""
        self.assertEqual(
            self.aci_useg_epg.admin_shutdown, self.aci_useg_epg_admin_shutdown
        )

    def test_aci_useg_endpoint_group_custom_qos_policy_name(self) -> None:
        """Test 'custom QOS policy name' of ACI uSeg Endpoint Group."""
        self.assertEqual(
            self.aci_useg_epg.custom_qos_policy_name,
            self.aci_useg_epg_custom_qos_policy_name,
        )

    def test_aci_useg_endpoint_group_flood_in_encap_enabled(self) -> None:
        """Test 'flood in encap enabled' option of ACI uSeg Endpoint Group."""
        self.assertEqual(
            self.aci_useg_epg.flood_in_encap_enabled,
            self.aci_useg_epg_flood_in_encap_enabled,
        )

    def test_aci_useg_endpoint_group_intra_epg_isolation_enabled(self) -> None:
        """Test 'intra EPG isolation enabled' option of ACI uSeg EPG."""
        self.assertEqual(
            self.aci_useg_epg.intra_epg_isolation_enabled,
            self.aci_useg_epg_intra_epg_isolation_enabled,
        )

    def test_aci_useg_endpoint_group_match_operator(self) -> None:
        """Test 'match operator' of ACI uSeg Endpoint Group."""
        self.assertEqual(
            self.aci_useg_epg.match_operator, self.aci_useg_epg_match_operator
        )

    def test_aci_useg_endpoint_group_qos_class(self) -> None:
        """Test 'QoS class' of ACI uSeg Endpoint Group."""
        self.assertEqual(self.aci_useg_epg.qos_class, self.aci_useg_epg_qos_class)

    def test_aci_useg_endpoint_group_preferred_group_member_enabled(
        self,
    ) -> None:
        """Test 'preferred group member enabled' option of ACI uSeg EPG."""
        self.assertEqual(
            self.aci_useg_epg.preferred_group_member_enabled,
            self.aci_useg_epg_preferred_group_member_enabled,
        )

    def test_aci_useg_endpoint_group_get_qos_class_color(self) -> None:
        """Test the 'get_qos_class_color' method of ACI uSeg Endpoint Group."""
        self.assertEqual(
            self.aci_useg_epg.get_qos_class_color(),
            QualityOfServiceClassChoices.colors.get(
                QualityOfServiceClassChoices.CLASS_LEVEL_3
            ),
        )

    def test_invalid_aci_useg_endpoint_group_name(self) -> None:
        """Test validation of ACI uSeg Endpoint Group naming."""
        epg = ACIUSegEndpointGroup(
            name="ACI uSeg EPG Test 1",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_useg_endpoint_group_name_length(self) -> None:
        """Test validation of ACI uSeg Endpoint Group name length."""
        epg = ACIUSegEndpointGroup(
            name="A" * 65,  # Exceeding the maximum length of 64
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_useg_endpoint_group_name_alias(self) -> None:
        """Test validation of ACI uSeg Endpoint Group aliasing."""
        epg = ACIUSegEndpointGroup(
            name="ACIUSegEPGTest1",
            name_alias="Invalid Alias",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_useg_endpoint_group_name_alias_length(self) -> None:
        """Test validation of ACI uSeg Endpoint Group name alias length."""
        epg = ACIUSegEndpointGroup(
            name="ACIUSegEPGTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_useg_endpoint_group_description(self) -> None:
        """Test validation of ACI uSeg Endpoint Group description."""
        epg = ACIUSegEndpointGroup(
            name="ACIUSegEPGTest1",
            description="Invalid Description: ö",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_useg_endpoint_group_description_length(self) -> None:
        """Test validation of ACI uSeg Endpoint Group description length."""
        epg = ACIUSegEndpointGroup(
            name="ACIUSegEPGTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_valid_aci_useg_epg_aci_bd_assignment_from_tenant_common(
        self,
    ) -> None:
        """Test valid assignment of ACI BD from ACI Tenant 'common'."""
        tenant_common = ACITenant.objects.get_or_create(name="common")[0]
        vrf_common = ACIVRF.objects.create(name="common_vrf", aci_tenant=tenant_common)
        bd_common = ACIBridgeDomain.objects.create(
            name="common_bd", aci_tenant=tenant_common, aci_vrf=vrf_common
        )
        epg = ACIUSegEndpointGroup.objects.create(
            name="ACIUSegEPGTest1",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=bd_common,
        )
        epg.full_clean()
        epg.save()
        self.assertEqual(epg.aci_bridge_domain, bd_common)

    def test_invalid_aci_useg_epg_aci_bd_assignment_from_tenant_other(
        self,
    ) -> None:
        """Test invalid assignment of ACI BD from ACI Tenant 'other'."""
        tenant_other = ACITenant.objects.get_or_create(name="other")[0]
        vrf_other = ACIVRF.objects.create(name="other_vrf", aci_tenant=tenant_other)
        bd_other = ACIBridgeDomain.objects.create(
            name="other_bd", aci_tenant=tenant_other, aci_vrf=vrf_other
        )
        epg = ACIUSegEndpointGroup(
            name="ACIUSegEPGTest1",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=bd_other,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()
            epg.save()

    def test_constraint_unique_aci_useg_epg_name_per_aci_app_profile(
        self,
    ) -> None:
        """Test unique constraint of ACI uSeg EPG name per ACI App Profile."""
        app_profile = ACIAppProfile.objects.get(name=self.aci_app_profile_name)
        bd = ACIBridgeDomain.objects.get(name=self.aci_bd_name)
        duplicate_epg = ACIUSegEndpointGroup(
            name=self.aci_useg_epg_name,
            aci_app_profile=app_profile,
            aci_bridge_domain=bd,
        )
        with self.assertRaises(IntegrityError):
            duplicate_epg.save()


class ACIUSegNetworkAttributeTestCase(TestCase):
    """Test case for ACIUSegNetworkAttribute model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIUSegNetworkAttribute model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_app_profile_name = "ACITestAppProfile"
        cls.aci_vrf_name = "ACITestVRF"
        cls.aci_bd_name = "ACITestBD"
        cls.aci_useg_epg_name = "ACITestUSegEPG"
        cls.aci_useg_network_attr_ip_name = "ACITestUSegNetworkAttributeIPAddress"
        cls.aci_useg_network_attr_mac_name = "ACITestUSegNetworkAttributeMACAddress"
        cls.aci_useg_network_attr_prefix_name = "ACITestUSegNetworkAttributePrefix"
        cls.aci_useg_network_attr_subnet_name = "ACITestUSegNetworkAttributeEPGSubnet"
        cls.aci_useg_network_attr_alias = "ACITestUSegNetworkAttributeAlias"
        cls.aci_useg_network_attr_description = (
            "ACI Test uSeg Network Attribute for NetBox ACI Plugin"
        )
        cls.aci_useg_network_attr_comments = """
        ACI uSeg Network Attribute for NetBox ACI Plugin testing.
        """
        cls.aci_useg_network_attr_use_epg_subnet = True
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
        cls.aci_bd = ACIBridgeDomain.objects.create(
            name=cls.aci_bd_name,
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
        )
        cls.aci_useg_epg = ACIUSegEndpointGroup.objects.create(
            name=cls.aci_useg_epg_name,
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
            nb_tenant=cls.nb_tenant,
        )

        # Create attribute objects
        cls.ip_address1 = IPAddress.objects.create(address="192.168.1.1/24")
        cls.ip_address2 = IPAddress.objects.create(address="192.168.1.2/24")
        cls.mac_address1 = MACAddress.objects.create(mac_address="00:00:00:00:00:01")
        cls.mac_address2 = MACAddress.objects.create(mac_address="00:00:00:00:00:02")
        cls.prefix1 = Prefix.objects.create(prefix="192.168.1.0/24")
        cls.prefix2 = Prefix.objects.create(prefix="192.168.2.0/24")

        # Create model objects
        cls.aci_useg_network_attr_ip_address = ACIUSegNetworkAttribute.objects.create(
            name=cls.aci_useg_network_attr_ip_name,
            name_alias=cls.aci_useg_network_attr_alias,
            description=cls.aci_useg_network_attr_description,
            comments=cls.aci_useg_network_attr_comments,
            aci_useg_endpoint_group=cls.aci_useg_epg,
            attr_object=cls.ip_address1,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_useg_network_attr_mac_address = ACIUSegNetworkAttribute.objects.create(
            name=cls.aci_useg_network_attr_mac_name,
            name_alias=cls.aci_useg_network_attr_alias,
            description=cls.aci_useg_network_attr_description,
            comments=cls.aci_useg_network_attr_comments,
            aci_useg_endpoint_group=cls.aci_useg_epg,
            attr_object=cls.mac_address1,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_useg_network_attr_prefix = ACIUSegNetworkAttribute.objects.create(
            name=cls.aci_useg_network_attr_prefix_name,
            name_alias=cls.aci_useg_network_attr_alias,
            description=cls.aci_useg_network_attr_description,
            comments=cls.aci_useg_network_attr_comments,
            aci_useg_endpoint_group=cls.aci_useg_epg,
            attr_object=cls.prefix1,
            nb_tenant=cls.nb_tenant,
        )
        cls.aci_useg_network_attr_epg_subnet = ACIUSegNetworkAttribute.objects.create(
            name=cls.aci_useg_network_attr_subnet_name,
            name_alias=cls.aci_useg_network_attr_alias,
            description=cls.aci_useg_network_attr_description,
            comments=cls.aci_useg_network_attr_comments,
            aci_useg_endpoint_group=cls.aci_useg_epg,
            nb_tenant=cls.nb_tenant,
            use_epg_subnet=cls.aci_useg_network_attr_use_epg_subnet,
        )

    def test_create_aci_useg_network_attr_instance(self) -> None:
        """Test type of created ACI uSeg Network Attribute."""
        self.assertTrue(
            isinstance(self.aci_useg_network_attr_ip_address, ACIUSegNetworkAttribute)
        )
        self.assertTrue(
            isinstance(self.aci_useg_network_attr_mac_address, ACIUSegNetworkAttribute)
        )
        self.assertTrue(
            isinstance(self.aci_useg_network_attr_prefix, ACIUSegNetworkAttribute)
        )
        self.assertTrue(
            isinstance(self.aci_useg_network_attr_epg_subnet, ACIUSegNetworkAttribute)
        )

    def test_aci_useg_network_attr_str(self) -> None:
        """Test string representation of ACI uSeg Network Attribute."""
        self.assertEqual(
            self.aci_useg_network_attr_ip_address.__str__(),
            f"{self.aci_useg_network_attr_ip_address.name} ({self.aci_useg_epg_name})",
        )
        self.assertEqual(
            self.aci_useg_network_attr_mac_address.__str__(),
            f"{self.aci_useg_network_attr_mac_address.name} ({self.aci_useg_epg_name})",
        )
        self.assertEqual(
            self.aci_useg_network_attr_prefix.__str__(),
            f"{self.aci_useg_network_attr_prefix.name} ({self.aci_useg_epg_name})",
        )
        self.assertEqual(
            self.aci_useg_network_attr_epg_subnet.__str__(),
            f"{self.aci_useg_network_attr_epg_subnet.name} ({self.aci_useg_epg_name})",
        )

    def test_aci_useg_network_attr_name_alias(self) -> None:
        """Test name alias of ACI uSeg Network Attribute."""
        self.assertEqual(
            self.aci_useg_network_attr_ip_address.name_alias,
            self.aci_useg_network_attr_alias,
        )
        self.assertEqual(
            self.aci_useg_network_attr_mac_address.name_alias,
            self.aci_useg_network_attr_alias,
        )
        self.assertEqual(
            self.aci_useg_network_attr_prefix.name_alias,
            self.aci_useg_network_attr_alias,
        )
        self.assertEqual(
            self.aci_useg_network_attr_epg_subnet.name_alias,
            self.aci_useg_network_attr_alias,
        )

    def test_aci_useg_network_attr_description(self) -> None:
        """Test description of ACI uSeg Network Attribute."""
        self.assertEqual(
            self.aci_useg_network_attr_ip_address.description,
            self.aci_useg_network_attr_description,
        )
        self.assertEqual(
            self.aci_useg_network_attr_mac_address.description,
            self.aci_useg_network_attr_description,
        )
        self.assertEqual(
            self.aci_useg_network_attr_prefix.description,
            self.aci_useg_network_attr_description,
        )
        self.assertEqual(
            self.aci_useg_network_attr_epg_subnet.description,
            self.aci_useg_network_attr_description,
        )

    def test_aci_useg_network_attr_aci_useg_endpoint_group_instance(
        self,
    ) -> None:
        """Test the ACI uSeg EPG instance associated with uSeg Attribute."""
        self.assertTrue(
            isinstance(
                self.aci_useg_network_attr_ip_address.aci_useg_endpoint_group,
                ACIUSegEndpointGroup,
            )
        )
        self.assertTrue(
            isinstance(
                self.aci_useg_network_attr_mac_address.aci_useg_endpoint_group,
                ACIUSegEndpointGroup,
            )
        )
        self.assertTrue(
            isinstance(
                self.aci_useg_network_attr_prefix.aci_useg_endpoint_group,
                ACIUSegEndpointGroup,
            )
        )
        self.assertTrue(
            isinstance(
                self.aci_useg_network_attr_epg_subnet.aci_useg_endpoint_group,
                ACIUSegEndpointGroup,
            )
        )

    def test_aci_useg_network_attr_aci_useg_endpoint_group_name(self) -> None:
        """Test the ACI uSeg EPG name associated with ACI uSeg Attribute."""
        self.assertEqual(
            self.aci_useg_network_attr_ip_address.aci_useg_endpoint_group.name,
            self.aci_useg_epg_name,
        )
        self.assertEqual(
            self.aci_useg_network_attr_mac_address.aci_useg_endpoint_group.name,
            self.aci_useg_epg_name,
        )
        self.assertEqual(
            self.aci_useg_network_attr_prefix.aci_useg_endpoint_group.name,
            self.aci_useg_epg_name,
        )
        self.assertEqual(
            self.aci_useg_network_attr_epg_subnet.aci_useg_endpoint_group.name,
            self.aci_useg_epg_name,
        )

    def test_aci_useg_network_attr_attr_object_instance(self) -> None:
        """Test the object instance associated with ACI uSeg Attribute."""
        self.assertTrue(
            isinstance(self.aci_useg_network_attr_ip_address.attr_object, IPAddress)
        )
        self.assertTrue(
            isinstance(self.aci_useg_network_attr_mac_address.attr_object, MACAddress)
        )
        self.assertTrue(
            isinstance(self.aci_useg_network_attr_prefix.attr_object, Prefix)
        )

    def test_aci_useg_network_attr_aci_tenant_instance(self) -> None:
        """Test the ACI Tenant instance associated with ACI uSeg Attribute."""
        self.assertTrue(
            isinstance(self.aci_useg_network_attr_ip_address.aci_tenant, ACITenant)
        )
        self.assertTrue(
            isinstance(self.aci_useg_network_attr_mac_address.aci_tenant, ACITenant)
        )
        self.assertTrue(
            isinstance(self.aci_useg_network_attr_prefix.aci_tenant, ACITenant)
        )
        self.assertTrue(
            isinstance(self.aci_useg_network_attr_epg_subnet.aci_tenant, ACITenant)
        )

    def test_aci_useg_network_attr_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with uSeg Attribute."""
        self.assertTrue(
            isinstance(self.aci_useg_network_attr_ip_address.nb_tenant, Tenant)
        )
        self.assertTrue(
            isinstance(self.aci_useg_network_attr_mac_address.nb_tenant, Tenant)
        )
        self.assertTrue(isinstance(self.aci_useg_network_attr_prefix.nb_tenant, Tenant))
        self.assertTrue(
            isinstance(self.aci_useg_network_attr_epg_subnet.nb_tenant, Tenant)
        )

    def test_aci_useg_network_attr_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ACI uSeg Attribute."""
        self.assertEqual(
            self.aci_useg_network_attr_ip_address.nb_tenant.name,
            self.nb_tenant_name,
        )
        self.assertEqual(
            self.aci_useg_network_attr_mac_address.nb_tenant.name,
            self.nb_tenant_name,
        )
        self.assertEqual(
            self.aci_useg_network_attr_prefix.nb_tenant.name,
            self.nb_tenant_name,
        )
        self.assertEqual(
            self.aci_useg_network_attr_epg_subnet.nb_tenant.name,
            self.nb_tenant_name,
        )

    def test_aci_useg_network_attr_type(self) -> None:
        """Test 'type' choice of ACI uSeg Network Attribute."""
        self.assertEqual(
            self.aci_useg_network_attr_ip_address.type,
            USegAttributeTypeChoices.TYPE_IP,
        )
        self.assertEqual(
            self.aci_useg_network_attr_mac_address.type,
            USegAttributeTypeChoices.TYPE_MAC,
        )
        self.assertEqual(
            self.aci_useg_network_attr_prefix.type,
            USegAttributeTypeChoices.TYPE_IP,
        )
        self.assertEqual(
            self.aci_useg_network_attr_epg_subnet.type,
            USegAttributeTypeChoices.TYPE_IP,
        )

    def test_aci_useg_network_attr_get_type_color(self) -> None:
        """Test the 'get_type_color' method of ACI uSeg Network Attribute."""
        self.assertEqual(
            self.aci_useg_network_attr_ip_address.get_type_color(),
            USegAttributeTypeChoices.colors.get(USegAttributeTypeChoices.TYPE_IP),
        )
        self.assertEqual(
            self.aci_useg_network_attr_mac_address.get_type_color(),
            USegAttributeTypeChoices.colors.get(USegAttributeTypeChoices.TYPE_MAC),
        )
        self.assertEqual(
            self.aci_useg_network_attr_prefix.get_type_color(),
            USegAttributeTypeChoices.colors.get(USegAttributeTypeChoices.TYPE_IP),
        )
        self.assertEqual(
            self.aci_useg_network_attr_epg_subnet.get_type_color(),
            USegAttributeTypeChoices.colors.get(USegAttributeTypeChoices.TYPE_IP),
        )

    def test_aci_useg_network_attr_use_epg_subnet(self) -> None:
        """Test 'use_epg_subnet' option of ACI uSeg Network Attribute."""
        self.assertEqual(self.aci_useg_network_attr_ip_address.use_epg_subnet, False)
        self.assertEqual(self.aci_useg_network_attr_mac_address.use_epg_subnet, False)
        self.assertEqual(self.aci_useg_network_attr_prefix.use_epg_subnet, False)
        self.assertEqual(self.aci_useg_network_attr_epg_subnet.use_epg_subnet, True)

    def test_invalid_aci_useg_network_attr_name(self) -> None:
        """Test validation of ACI uSeg Network Attribute naming."""
        useg_network_attr = ACIUSegNetworkAttribute(
            name="ACI uSeg Network Attribute Test 1",
            aci_useg_endpoint_group=self.aci_useg_epg,
        )
        with self.assertRaises(ValidationError):
            useg_network_attr.full_clean()

    def test_invalid_aci_useg_network_attr_name_length(self) -> None:
        """Test validation of ACI uSeg Network Attribute name length."""
        useg_network_attr = ACIUSegNetworkAttribute(
            name="A" * 65,  # Exceeding the maximum length of 64
            aci_useg_endpoint_group=self.aci_useg_epg,
        )
        with self.assertRaises(ValidationError):
            useg_network_attr.full_clean()

    def test_invalid_aci_useg_network_attr_name_alias(self) -> None:
        """Test validation of ACI uSeg Network Attribute aliasing."""
        useg_network_attr = ACIUSegNetworkAttribute(
            name="ACIUSegNetworkAttrTest1",
            name_alias="Invalid Alias",
            aci_useg_endpoint_group=self.aci_useg_epg,
        )
        with self.assertRaises(ValidationError):
            useg_network_attr.full_clean()

    def test_invalid_aci_useg_network_attr_name_alias_length(self) -> None:
        """Test validation of ACI uSeg Network Attribute name alias length."""
        useg_network_attr = ACIUSegNetworkAttribute(
            name="ACIUSegNetworkAttrTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
            aci_useg_endpoint_group=self.aci_useg_epg,
        )
        with self.assertRaises(ValidationError):
            useg_network_attr.full_clean()

    def test_invalid_aci_useg_network_attr_description(self) -> None:
        """Test validation of ACI uSeg Network Attribute description."""
        useg_network_attr = ACIUSegNetworkAttribute(
            name="ACIUSegNetworkAttrTest1",
            description="Invalid Description: ö",
            aci_useg_endpoint_group=self.aci_useg_epg,
        )
        with self.assertRaises(ValidationError):
            useg_network_attr.full_clean()

    def test_invalid_aci_useg_network_attr_description_length(self) -> None:
        """Test validation of ACI uSeg Network Attribute description length."""
        useg_network_attr = ACIUSegNetworkAttribute(
            name="ACIUSegNetworkAttrTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
            aci_useg_endpoint_group=self.aci_useg_epg,
        )
        with self.assertRaises(ValidationError):
            useg_network_attr.full_clean()

    def test_invalid_aci_useg_network_attr_attr_object(self) -> None:
        """Test validation of the object assignment for ACI uSeg Attribute."""
        useg_network_attr = ACIUSegNetworkAttribute(
            name=self.aci_useg_network_attr_ip_name,
            aci_useg_endpoint_group=self.aci_useg_epg,
            attr_object=self.aci_bd,
        )
        with self.assertRaises(ValidationError):
            useg_network_attr.full_clean()

    def test_constraint_unique_aci_useg_network_attr_name_per_aci_useg_epg(
        self,
    ) -> None:
        """Test unique constraint of ACI uSeg Attribute name per uSeg EPG."""
        duplicate_useg_network_attr = ACIUSegNetworkAttribute(
            name=self.aci_useg_network_attr_ip_name,
            aci_useg_endpoint_group=self.aci_useg_epg,
        )
        with self.assertRaises(IntegrityError):
            duplicate_useg_network_attr.save()

    def test_constraint_unique_aci_useg_network_attr_epg_subnet_per_aci_useg_epg(
        self,
    ) -> None:
        """Test unique constraint of one 'use_epg_subnet' per ACI uSeg EPG."""
        duplicate_useg_network_attr_use_epg_subnet = ACIUSegNetworkAttribute(
            name="ACITestUSegNetworkAttributeEPGSubnetDuplicate",
            aci_useg_endpoint_group=self.aci_useg_epg,
            use_epg_subnet=True,
        )
        with self.assertRaises(IntegrityError):
            duplicate_useg_network_attr_use_epg_subnet.save()
