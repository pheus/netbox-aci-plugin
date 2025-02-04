# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from tenancy.models import Tenant

from ...choices import QualityOfServiceClassChoices
from ...models.tenant_app_profiles import ACIAppProfile, ACIEndpointGroup
from ...models.tenant_networks import ACIVRF, ACIBridgeDomain
from ...models.tenants import ACITenant


class ACIAppProfileTestCase(TestCase):
    """Test case for ACIAppProfile model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIAppProfile model."""
        cls.aci_tenant_name = "ACITestTenant"
        cls.aci_app_profile_name = "ACITestAppProfile"
        cls.aci_app_profile_alias = "ACITestAppProfileAlias"
        cls.aci_app_profile_description = (
            "ACI Test Application Profile for NetBox ACI Plugin"
        )
        cls.aci_app_profile_comments = """
        ACI Application Profile for NetBox ACI Plugin testing.
        """
        cls.nb_tenant_name = "NetBoxTestTenant"

        # Create objects
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.aci_tenant = ACITenant.objects.create(name=cls.aci_tenant_name)
        cls.aci_app_profile = ACIAppProfile.objects.create(
            name=cls.aci_app_profile_name,
            name_alias=cls.aci_app_profile_alias,
            description=cls.aci_app_profile_description,
            comments=cls.aci_app_profile_comments,
            aci_tenant=cls.aci_tenant,
            nb_tenant=cls.nb_tenant,
        )

    def test_aci_app_profile_instance(self) -> None:
        """Test type of created ACI Application Profile."""
        self.assertTrue(isinstance(self.aci_app_profile, ACIAppProfile))

    def test_aci_app_profile_str(self) -> None:
        """Test string value of created ACI Application Profile."""
        self.assertEqual(
            self.aci_app_profile.__str__(), self.aci_app_profile.name
        )

    def test_aci_app_profile_alias(self) -> None:
        """Test alias of ACI Application Profile."""
        self.assertEqual(
            self.aci_app_profile.name_alias, self.aci_app_profile_alias
        )

    def test_aci_app_profile_description(self) -> None:
        """Test description of ACI Application Profile."""
        self.assertEqual(
            self.aci_app_profile.description, self.aci_app_profile_description
        )

    def test_aci_app_profile_aci_tenant_instance(self) -> None:
        """Test the ACI Tenant instance associated with ACI App Profile."""
        self.assertTrue(isinstance(self.aci_app_profile.aci_tenant, ACITenant))

    def test_aci_app_profile_aci_tenant_name(self) -> None:
        """Test the ACI Tenant name associated with ACI Application Profile."""
        self.assertEqual(
            self.aci_app_profile.aci_tenant.name, self.aci_tenant_name
        )

    def test_aci_app_profile_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant associated with ACI Application Profile."""
        self.assertTrue(isinstance(self.aci_app_profile.nb_tenant, Tenant))

    def test_aci_app_profile_nb_tenant_name(self) -> None:
        """Test the NetBox tenant name associated with ACI App Profile."""
        self.assertEqual(
            self.aci_app_profile.nb_tenant.name, self.nb_tenant_name
        )

    def test_invalid_aci_app_profile_name(self) -> None:
        """Test validation of ACI Application Profile naming."""
        app_profile = ACIAppProfile(name="ACI App Profile Test 1")
        with self.assertRaises(ValidationError):
            app_profile.full_clean()

    def test_invalid_aci_app_profile_name_length(self) -> None:
        """Test validation of ACI Application Profile name length."""
        app_profile = ACIAppProfile(
            name="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            app_profile.full_clean()

    def test_invalid_aci_app_profile_name_alias(self) -> None:
        """Test validation of ACI Application Profile aliasing."""
        app_profile = ACIAppProfile(
            name="ACIAppProfileTest1", name_alias="Invalid Alias"
        )
        with self.assertRaises(ValidationError):
            app_profile.full_clean()

    def test_invalid_aci_app_profile_name_alias_length(self) -> None:
        """Test validation of ACI Application Profile name alias length."""
        app_profile = ACIAppProfile(
            name="ACIAppProfileTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            app_profile.full_clean()

    def test_invalid_aci_app_profile_description(self) -> None:
        """Test validation of ACI Application Profile description."""
        app_profile = ACIAppProfile(
            name="ACIAppProfileTest1", description="Invalid Description: ö"
        )
        with self.assertRaises(ValidationError):
            app_profile.full_clean()

    def test_invalid_aci_app_profile_description_length(self) -> None:
        """Test validation of ACI Application Profile description length."""
        app_profile = ACIAppProfile(
            name="ACIAppProfileTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
        )
        with self.assertRaises(ValidationError):
            app_profile.full_clean()

    def test_constraint_unique_aci_app_profile_name_per_aci_tenant(
        self,
    ) -> None:
        """Test unique constraint of ACI AppProfile name per ACI Tenant."""
        tenant = ACITenant.objects.get(name=self.aci_tenant_name)
        duplicate_app_profile = ACIAppProfile(
            name=self.aci_app_profile_name, aci_tenant=tenant
        )
        with self.assertRaises(IntegrityError):
            duplicate_app_profile.save()


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
        cls.aci_epg_description = (
            "ACI Test Endpoint Group for NetBox ACI Plugin"
        )
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
            intra_epg_isolation_enabled=(
                cls.aci_epg_intra_epg_isolation_enabled
            ),
            qos_class=cls.aci_epg_qos_class,
            preferred_group_member_enabled=(
                cls.aci_epg_preferred_group_member_enabled
            ),
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
        self.assertTrue(
            isinstance(self.aci_epg.aci_app_profile, ACIAppProfile)
        )

    def test_aci_endpoint_group_aci_app_profile_name(self) -> None:
        """Test the ACI App Profile name associated with ACI EPG."""
        self.assertEqual(
            self.aci_epg.aci_app_profile.name, self.aci_app_profile_name
        )

    def test_aci_endpoint_group_aci_vrf_instance(self) -> None:
        """Test the ACI VRF instance associated with ACI EPG."""
        self.assertTrue(isinstance(self.aci_epg.aci_vrf, ACIVRF))

    def test_aci_endpoint_group_aci_vrf_name(self) -> None:
        """Test the ACI VRF name associated with ACI EPG."""
        self.assertEqual(self.aci_epg.aci_vrf.name, self.aci_vrf_name)

    def test_aci_endpoint_group_aci_bridge_domain_instance(self) -> None:
        """Test the ACI Bridge Domain instance associated with ACI EPG."""
        self.assertTrue(
            isinstance(self.aci_epg.aci_bridge_domain, ACIBridgeDomain)
        )

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
        self.assertEqual(
            self.aci_epg.admin_shutdown, self.aci_epg_admin_shutdown
        )

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
        self.assertEqual(
            self.aci_epg.proxy_arp_enabled, self.aci_epg_proxy_arp_enabled
        )

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
        vrf_common = ACIVRF.objects.create(
            name="common_vrf", aci_tenant=tenant_common
        )
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
        vrf_other = ACIVRF.objects.create(
            name="other_vrf", aci_tenant=tenant_other
        )
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
