# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from dcim.models import MACAddress
from ipam.models import IPAddress, Prefix
from tenancy.models import Tenant

from ....choices import (
    QualityOfServiceClassChoices,
    USegAttributeMatchOperatorChoices,
    USegAttributeTypeChoices,
)
from ....models.fabric.fabrics import ACIFabric
from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.bridge_domains import ACIBridgeDomain
from ....models.tenant.endpoint_groups import (
    ACIEndpointGroup,
    ACIUSegEndpointGroup,
    ACIUSegNetworkAttribute,
)
from ....models.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroup,
    ACIEsgEndpointGroupSelector,
)
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF
from ..base import ACIBaseTestCase


class ACIEndpointGroupTestCase(ACIBaseTestCase):
    """Test case for ACIEndpointGroup model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIBridgeDomainSubnet model."""
        super().setUpTestData()

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
            intra_epg_isolation_enabled=cls.aci_epg_intra_epg_isolation_enabled,
            qos_class=cls.aci_epg_qos_class,
            preferred_group_member_enabled=cls.aci_epg_preferred_group_member_enabled,
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
        self.assertEqual(self.aci_epg.aci_tenant.name, self.aci_tenant_name)

    def test_aci_endpoint_group_aci_app_profile_instance(self) -> None:
        """Test the ACI App Profile instance associated with ACI EPG."""
        self.assertTrue(isinstance(self.aci_epg.aci_app_profile, ACIAppProfile))
        self.assertEqual(self.aci_epg.aci_app_profile.name, self.aci_app_profile_name)

    def test_aci_endpoint_group_aci_vrf_instance(self) -> None:
        """Test the ACI VRF instance associated with ACI EPG."""
        self.assertTrue(isinstance(self.aci_epg.aci_vrf, ACIVRF))
        self.assertEqual(self.aci_epg.aci_vrf.name, self.aci_vrf_name)

    def test_aci_endpoint_group_aci_bridge_domain_instance(self) -> None:
        """Test the ACI Bridge Domain instance associated with ACI EPG."""
        self.assertTrue(isinstance(self.aci_epg.aci_bridge_domain, ACIBridgeDomain))
        self.assertEqual(self.aci_epg.aci_bridge_domain.name, self.aci_bd_name)

    def test_aci_endpoint_group_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with ACI EPG."""
        self.assertTrue(isinstance(self.aci_epg.nb_tenant, Tenant))
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
        tenant_common = ACITenant.objects.get_or_create(
            name="common", aci_fabric=self.aci_fabric
        )[0]
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
        tenant_other = ACITenant.objects.get_or_create(
            name="other", aci_fabric=self.aci_fabric
        )[0]
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

    def test_aci_endpoint_group_parent_object(self) -> None:
        """Test parent object of ACI Endpoint Group is the ACI App Profile."""
        self.assertEqual(self.aci_epg.parent_object, self.aci_app_profile)

    def test_invalid_aci_epg_clean_aci_bd_from_other_fabric(self) -> None:
        """Test clean rejects an ACI Bridge Domain from another fabric."""
        fabric_other = ACIFabric.objects.create(
            name="OtherFabricEPGClean", fabric_id=123, infra_vlan_vid=3954
        )
        tenant_other = ACITenant.objects.create(
            name="other_fabric_epg_clean_tenant", aci_fabric=fabric_other
        )
        vrf_other = ACIVRF.objects.create(
            name="other_fabric_epg_clean_vrf", aci_tenant=tenant_other
        )
        bd_other = ACIBridgeDomain.objects.create(
            name="other_fabric_epg_clean_bd",
            aci_tenant=tenant_other,
            aci_vrf=vrf_other,
        )
        epg = ACIEndpointGroup(
            name="ACIEPGOtherFabric",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=bd_other,
        )
        with self.assertRaises(ValidationError):
            epg.full_clean()

    def test_invalid_aci_epg_save_aci_bd_from_other_fabric(self) -> None:
        """Test save rejects an ACI Bridge Domain from another fabric."""
        fabric_other = ACIFabric.objects.create(
            name="OtherFabricEPGSave", fabric_id=124, infra_vlan_vid=3955
        )
        tenant_other = ACITenant.objects.create(
            name="other_fabric_epg_save_tenant", aci_fabric=fabric_other
        )
        vrf_other = ACIVRF.objects.create(
            name="other_fabric_epg_save_vrf", aci_tenant=tenant_other
        )
        bd_other = ACIBridgeDomain.objects.create(
            name="other_fabric_epg_save_bd",
            aci_tenant=tenant_other,
            aci_vrf=vrf_other,
        )
        epg = ACIEndpointGroup(
            name="ACIEPGOtherFabricSave",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=bd_other,
        )
        with self.assertRaises(ValidationError):
            epg.save()

    def test_invalid_aci_epg_save_aci_bd_from_other_tenant(self) -> None:
        """Test save rejects an ACI BD from another non-common ACI Tenant."""
        tenant_other = ACITenant.objects.get_or_create(
            name="other", aci_fabric=self.aci_fabric
        )[0]
        vrf_other = ACIVRF.objects.create(
            name="other_tenant_epg_vrf", aci_tenant=tenant_other
        )
        bd_other = ACIBridgeDomain.objects.create(
            name="other_tenant_epg_bd", aci_tenant=tenant_other, aci_vrf=vrf_other
        )
        epg = ACIEndpointGroup(
            name="ACIEPGOtherTenantSave",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=bd_other,
        )
        with self.assertRaises(ValidationError):
            epg.save()

    def test_invalid_aci_epg_bd_change_to_other_vrf_with_esg_selector(
        self,
    ) -> None:
        """Test clean rejects moving a selected EPG to another VRF's BD."""
        epg = ACIEndpointGroup.objects.create(
            name="ACIEPGVrfGuard",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIESGForEPGVrfGuard",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        ACIEsgEndpointGroupSelector.objects.create(
            name="ACIESGSelForEPGVrfGuard",
            aci_endpoint_security_group=esg,
            aci_epg_object=epg,
        )
        vrf_other = ACIVRF.objects.create(
            name="epg_vrf_guard_other_vrf", aci_tenant=self.aci_tenant
        )
        bd_other = ACIBridgeDomain.objects.create(
            name="epg_vrf_guard_other_bd",
            aci_tenant=self.aci_tenant,
            aci_vrf=vrf_other,
        )
        epg.aci_bridge_domain = bd_other
        with self.assertRaises(ValidationError) as cm:
            epg.full_clean()
        self.assertIn("aci_bridge_domain", cm.exception.error_dict)

    def test_valid_aci_epg_bd_change_same_vrf_with_esg_selector(self) -> None:
        """Test clean allows moving a selected EPG within the same VRF."""
        epg = ACIEndpointGroup.objects.create(
            name="ACIEPGVrfGuardSame",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIESGForEPGVrfGuardSame",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        ACIEsgEndpointGroupSelector.objects.create(
            name="ACIESGSelForEPGVrfGuardSame",
            aci_endpoint_security_group=esg,
            aci_epg_object=epg,
        )
        bd_same_vrf = ACIBridgeDomain.objects.create(
            name="epg_vrf_guard_same_bd",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
        )
        epg.aci_bridge_domain = bd_same_vrf
        epg.full_clean()

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
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_epg.save()


class ACIUSegEndpointGroupTestCase(ACIBaseTestCase):
    """Test case for ACIUSegEndpointGroup model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIUSegEndpointGroup model."""
        super().setUpTestData()

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

        # Create objects
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
            intra_epg_isolation_enabled=cls.aci_useg_epg_intra_epg_isolation_enabled,
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
        self.assertEqual(self.aci_useg_epg.aci_tenant.name, self.aci_tenant_name)

    def test_aci_useg_endpoint_group_aci_app_profile_instance(self) -> None:
        """Test the ACI App Profile instance associated with ACI uSeg EPG."""
        self.assertTrue(isinstance(self.aci_useg_epg.aci_app_profile, ACIAppProfile))
        self.assertEqual(
            self.aci_useg_epg.aci_app_profile.name, self.aci_app_profile_name
        )

    def test_aci_useg_endpoint_group_aci_vrf_instance(self) -> None:
        """Test the ACI VRF instance associated with ACI uSeg EPG."""
        self.assertTrue(isinstance(self.aci_useg_epg.aci_vrf, ACIVRF))
        self.assertEqual(self.aci_useg_epg.aci_vrf.name, self.aci_vrf_name)

    def test_aci_useg_endpoint_group_aci_bridge_domain_instance(self) -> None:
        """Test the ACI Bridge Domain instance associated with ACI uSeg EPG."""
        self.assertTrue(
            isinstance(self.aci_useg_epg.aci_bridge_domain, ACIBridgeDomain)
        )
        self.assertEqual(self.aci_useg_epg.aci_bridge_domain.name, self.aci_bd_name)

    def test_aci_useg_endpoint_group_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant instance associated with ACI uSeg EPG."""
        self.assertTrue(isinstance(self.aci_useg_epg.nb_tenant, Tenant))
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

    def test_aci_useg_endpoint_group_get_match_operator_color(self) -> None:
        """Test the 'get_match_operator_color' method of ACI uSeg EPG."""
        self.assertEqual(
            self.aci_useg_epg.get_match_operator_color(),
            USegAttributeMatchOperatorChoices.colors.get(
                self.aci_useg_epg_match_operator
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
        tenant_common = ACITenant.objects.get_or_create(
            name="common", aci_fabric=self.aci_fabric
        )[0]
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
        tenant_other = ACITenant.objects.get_or_create(
            name="other", aci_fabric=self.aci_fabric
        )[0]
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

    def test_invalid_aci_useg_epg_bd_change_to_other_vrf_with_esg_selector(
        self,
    ) -> None:
        """Test clean rejects moving a selected uSeg EPG to another VRF."""
        useg_epg = ACIUSegEndpointGroup.objects.create(
            name="ACIUSegEPGVrfGuard",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIESGForUSegEPGVrfGuard",
            aci_app_profile=self.aci_app_profile,
            aci_vrf=self.aci_vrf,
        )
        ACIEsgEndpointGroupSelector.objects.create(
            name="ACIESGSelForUSegEPGVrfGuard",
            aci_endpoint_security_group=esg,
            aci_epg_object=useg_epg,
        )
        vrf_other = ACIVRF.objects.create(
            name="useg_epg_vrf_guard_other_vrf", aci_tenant=self.aci_tenant
        )
        bd_other = ACIBridgeDomain.objects.create(
            name="useg_epg_vrf_guard_other_bd",
            aci_tenant=self.aci_tenant,
            aci_vrf=vrf_other,
        )
        useg_epg.aci_bridge_domain = bd_other
        with self.assertRaises(ValidationError) as cm:
            useg_epg.full_clean()
        self.assertIn("aci_bridge_domain", cm.exception.error_dict)

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
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_epg.save()


class ACIUSegNetworkAttributeTestCase(ACIBaseTestCase):
    """Test case for ACIUSegNetworkAttribute model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIUSegNetworkAttribute model."""
        super().setUpTestData()

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
        cls.aci_useg_epg = ACIUSegEndpointGroup.objects.create(
            name=cls.aci_useg_epg_name,
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
            nb_tenant=cls.nb_tenant,
        )

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

    def test_aci_useg_network_attr_parent_object(self) -> None:
        """Test parent object of uSeg Attribute is the uSeg Endpoint Group."""
        self.assertEqual(
            self.aci_useg_network_attr_ip_address.parent_object,
            self.aci_useg_epg,
        )

    def test_aci_useg_network_attr_clone_fields_excludes_object_id(self) -> None:
        """Test clone fields omit the unique generic attr object id."""
        self.assertNotIn("attr_object_id", ACIUSegNetworkAttribute.clone_fields)
        self.assertIn("attr_object_type", ACIUSegNetworkAttribute.clone_fields)

    def test_invalid_aci_useg_network_attr_object_type_without_object(
        self,
    ) -> None:
        """Test clean requires an attr object when an object type is set."""
        useg_network_attr = ACIUSegNetworkAttribute(
            name="ACIUSegNetworkAttrTypeOnly",
            aci_useg_endpoint_group=self.aci_useg_epg,
            attr_object_type=ContentType.objects.get_for_model(IPAddress),
        )
        with self.assertRaises(ValidationError) as cm:
            useg_network_attr.full_clean()
        self.assertIn("attr_object", cm.exception.error_dict)

    def test_invalid_aci_useg_network_attr_use_epg_subnet_with_object(
        self,
    ) -> None:
        """Test use_epg_subnet conflicts with an assigned attr object."""
        useg_network_attr = ACIUSegNetworkAttribute(
            name="ACIUSegNetworkAttrSubnetConflict",
            aci_useg_endpoint_group=self.aci_useg_epg,
            use_epg_subnet=True,
            attr_object=self.ip_address2,
        )
        with self.assertRaises(ValidationError) as cm:
            useg_network_attr.full_clean()
        self.assertIn("attr_object_type", cm.exception.error_dict)

    def test_invalid_aci_useg_network_attr_without_object_or_epg_subnet(
        self,
    ) -> None:
        """Test clean requires an attr object or 'use_epg_subnet'."""
        useg_network_attr = ACIUSegNetworkAttribute(
            name="ACIUSegNetworkAttrEmpty",
            aci_useg_endpoint_group=self.aci_useg_epg,
        )
        with self.assertRaises(ValidationError) as cm:
            useg_network_attr.full_clean()
        self.assertIn("attr_object", cm.exception.error_dict)

    def test_constraint_unique_aci_useg_network_attr_name_per_aci_useg_epg(
        self,
    ) -> None:
        """Test unique constraint of ACI uSeg Attribute name per uSeg EPG."""
        duplicate_useg_network_attr = ACIUSegNetworkAttribute(
            name=self.aci_useg_network_attr_ip_name,
            aci_useg_endpoint_group=self.aci_useg_epg,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
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
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_useg_network_attr_use_epg_subnet.save()
