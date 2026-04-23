# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for tenant L3Out models."""

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from ipam.models import VRF, Prefix
from tenancy.models import Tenant

from ....choices import QualityOfServiceClassChoices, QualityOfServiceDSCPChoices
from ....models.access_policies.domains import ACIRoutedDomain
from ....models.fabric.fabrics import ACIFabric
from ....models.tenant.contracts import ACIContract, ACIContractRelation
from ....models.tenant.l3outs import (
    ACIExternalEndpointGroup,
    ACIExternalSubnet,
    ACIL3Out,
)
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF
from ..base import ACIBaseTestCase


class ACIL3OutTestCase(ACIBaseTestCase):
    """Test case for ACIL3Out model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIL3Out model."""
        super().setUpTestData()

        cls.aci_routed_domain_name = "ACIBaseTestRoutedDomain"
        cls.aci_l3out_name = "ACITestL3Out"
        cls.aci_l3out_alias = "ACITestL3OutAlias"
        cls.aci_l3out_description = "ACI Test L3Out for NetBox ACI Plugin"
        cls.aci_l3out_comments = """
        ACI L3Out for NetBox ACI Plugin testing.
        """
        cls.aci_l3out_bfd_policy_name = "BFDPolicy1"
        cls.aci_l3out_bgp_enabled = True
        cls.aci_l3out_custom_qos_policy_name = "CustomQoSPolicy1"
        cls.aci_l3out_egress_dpp_policy_name = "EgressDPPPolicy1"
        cls.aci_l3out_eigrp_enabled = True
        cls.aci_l3out_eigrp_interface_policy_name = "EIGRPIfPolicy1"
        cls.aci_l3out_export_route_control_enforcement_enabled = True
        cls.aci_l3out_igmp_interface_policy_name = "IGMPIfPolicy1"
        cls.aci_l3out_import_route_control_enforcement_enabled = True
        cls.aci_l3out_ingress_dpp_policy_name = "IngressDPPPolicy1"
        cls.aci_l3out_interleak_route_map_name = "InterleakRouteMap1"
        cls.aci_l3out_l3_multicast_ipv4_enabled = True
        cls.aci_l3out_l3_multicast_ipv6_enabled = True
        cls.aci_l3out_multipod_enabled = False
        cls.aci_l3out_ospf_enabled = True
        cls.aci_l3out_ospf_external_policy_name = "OSPFExternalPolicy1"
        cls.aci_l3out_pim_policy_name = "PIMPolicy1"
        cls.aci_l3out_target_dscp = QualityOfServiceDSCPChoices.DSCP_AF11

        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name=cls.aci_routed_domain_name,
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_l3out = ACIL3Out.objects.create(
            name=cls.aci_l3out_name,
            name_alias=cls.aci_l3out_alias,
            description=cls.aci_l3out_description,
            comments=cls.aci_l3out_comments,
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
            nb_tenant=cls.nb_tenant,
            bfd_policy_name=cls.aci_l3out_bfd_policy_name,
            bgp_enabled=cls.aci_l3out_bgp_enabled,
            custom_qos_policy_name=cls.aci_l3out_custom_qos_policy_name,
            egress_data_plane_policing_policy_name=(
                cls.aci_l3out_egress_dpp_policy_name
            ),
            eigrp_enabled=cls.aci_l3out_eigrp_enabled,
            eigrp_interface_policy_name=cls.aci_l3out_eigrp_interface_policy_name,
            export_route_control_enforcement_enabled=(
                cls.aci_l3out_export_route_control_enforcement_enabled
            ),
            igmp_interface_policy_name=cls.aci_l3out_igmp_interface_policy_name,
            import_route_control_enforcement_enabled=(
                cls.aci_l3out_import_route_control_enforcement_enabled
            ),
            ingress_data_plane_policing_policy_name=(
                cls.aci_l3out_ingress_dpp_policy_name
            ),
            interleak_route_map_name=cls.aci_l3out_interleak_route_map_name,
            l3_multicast_ipv4_enabled=cls.aci_l3out_l3_multicast_ipv4_enabled,
            l3_multicast_ipv6_enabled=cls.aci_l3out_l3_multicast_ipv6_enabled,
            multipod_enabled=cls.aci_l3out_multipod_enabled,
            ospf_enabled=cls.aci_l3out_ospf_enabled,
            ospf_external_policy_name=cls.aci_l3out_ospf_external_policy_name,
            pim_policy_name=cls.aci_l3out_pim_policy_name,
            target_dscp=cls.aci_l3out_target_dscp,
        )

    def test_aci_l3out_instance(self) -> None:
        """Test instance of created ACI L3Out."""
        self.assertTrue(isinstance(self.aci_l3out, ACIL3Out))

    def test_aci_l3out_str(self) -> None:
        """Test string representation of ACI L3Out."""
        self.assertEqual(self.aci_l3out.__str__(), self.aci_l3out.name)

    def test_aci_l3out_name_alias(self) -> None:
        """Test ACI L3Out name alias."""
        self.assertEqual(self.aci_l3out.name_alias, self.aci_l3out_alias)

    def test_aci_l3out_description(self) -> None:
        """Test ACI L3Out description."""
        self.assertEqual(self.aci_l3out.description, self.aci_l3out_description)

    def test_aci_l3out_aci_tenant_instance(self) -> None:
        """Test ACI Tenant instance associated with ACI L3Out."""
        self.assertTrue(isinstance(self.aci_l3out.aci_tenant, ACITenant))
        self.assertEqual(self.aci_l3out.aci_tenant.name, self.aci_tenant_name)

    def test_aci_l3out_aci_vrf_instance(self) -> None:
        """Test ACI VRF instance associated with ACI L3Out."""
        self.assertTrue(isinstance(self.aci_l3out.aci_vrf, ACIVRF))
        self.assertEqual(self.aci_l3out.aci_vrf.name, self.aci_vrf_name)

    def test_aci_l3out_aci_routed_domain_instance(self) -> None:
        """Test ACI Routed Domain instance associated with ACI L3Out."""
        self.assertTrue(isinstance(self.aci_l3out.aci_routed_domain, ACIRoutedDomain))
        self.assertEqual(
            self.aci_l3out.aci_routed_domain.name,
            self.aci_routed_domain_name,
        )

    def test_aci_l3out_nb_tenant_instance(self) -> None:
        """Test NetBox tenant instance associated with ACI L3Out."""
        self.assertTrue(isinstance(self.aci_l3out.nb_tenant, Tenant))
        self.assertEqual(self.aci_l3out.nb_tenant.name, self.nb_tenant_name)

    def test_aci_l3out_parent_object(self) -> None:
        """Test parent object of ACI L3Out."""
        self.assertEqual(self.aci_l3out.parent_object, self.aci_tenant)

    def test_aci_l3out_bfd_policy_name(self) -> None:
        """Test ACI L3Out BFD policy name."""
        self.assertEqual(
            self.aci_l3out.bfd_policy_name,
            self.aci_l3out_bfd_policy_name,
        )

    def test_aci_l3out_bgp_enabled(self) -> None:
        """Test ACI L3Out BGP enabled option."""
        self.assertEqual(self.aci_l3out.bgp_enabled, self.aci_l3out_bgp_enabled)

    def test_aci_l3out_custom_qos_policy_name(self) -> None:
        """Test ACI L3Out custom QoS policy name."""
        self.assertEqual(
            self.aci_l3out.custom_qos_policy_name,
            self.aci_l3out_custom_qos_policy_name,
        )

    def test_aci_l3out_egress_data_plane_policing_policy_name(self) -> None:
        """Test ACI L3Out egress data plane policing policy name."""
        self.assertEqual(
            self.aci_l3out.egress_data_plane_policing_policy_name,
            self.aci_l3out_egress_dpp_policy_name,
        )

    def test_aci_l3out_eigrp_enabled(self) -> None:
        """Test ACI L3Out EIGRP enabled option."""
        self.assertEqual(
            self.aci_l3out.eigrp_enabled,
            self.aci_l3out_eigrp_enabled,
        )

    def test_aci_l3out_eigrp_interface_policy_name(self) -> None:
        """Test ACI L3Out EIGRP interface policy name."""
        self.assertEqual(
            self.aci_l3out.eigrp_interface_policy_name,
            self.aci_l3out_eigrp_interface_policy_name,
        )

    def test_aci_l3out_export_route_control_enforcement_enabled(self) -> None:
        """Test ACI L3Out export route control enforcement option."""
        self.assertEqual(
            self.aci_l3out.export_route_control_enforcement_enabled,
            self.aci_l3out_export_route_control_enforcement_enabled,
        )

    def test_aci_l3out_igmp_interface_policy_name(self) -> None:
        """Test ACI L3Out IGMP interface policy name."""
        self.assertEqual(
            self.aci_l3out.igmp_interface_policy_name,
            self.aci_l3out_igmp_interface_policy_name,
        )

    def test_aci_l3out_import_route_control_enforcement_enabled(self) -> None:
        """Test ACI L3Out import route control enforcement option."""
        self.assertEqual(
            self.aci_l3out.import_route_control_enforcement_enabled,
            self.aci_l3out_import_route_control_enforcement_enabled,
        )

    def test_aci_l3out_ingress_data_plane_policing_policy_name(self) -> None:
        """Test ACI L3Out ingress data plane policing policy name."""
        self.assertEqual(
            self.aci_l3out.ingress_data_plane_policing_policy_name,
            self.aci_l3out_ingress_dpp_policy_name,
        )

    def test_aci_l3out_interleak_route_map_name(self) -> None:
        """Test ACI L3Out interleak route map name."""
        self.assertEqual(
            self.aci_l3out.interleak_route_map_name,
            self.aci_l3out_interleak_route_map_name,
        )

    def test_aci_l3out_l3_multicast_ipv4_enabled(self) -> None:
        """Test ACI L3Out L3 multicast IPv4 enabled option."""
        self.assertEqual(
            self.aci_l3out.l3_multicast_ipv4_enabled,
            self.aci_l3out_l3_multicast_ipv4_enabled,
        )

    def test_aci_l3out_l3_multicast_ipv6_enabled(self) -> None:
        """Test ACI L3Out L3 multicast IPv6 enabled option."""
        self.assertEqual(
            self.aci_l3out.l3_multicast_ipv6_enabled,
            self.aci_l3out_l3_multicast_ipv6_enabled,
        )

    def test_aci_l3out_multipod_enabled(self) -> None:
        """Test ACI L3Out Multi-Pod enabled option."""
        self.assertEqual(
            self.aci_l3out.multipod_enabled,
            self.aci_l3out_multipod_enabled,
        )

    def test_aci_l3out_ospf_enabled(self) -> None:
        """Test ACI L3Out OSPF enabled option."""
        self.assertEqual(self.aci_l3out.ospf_enabled, self.aci_l3out_ospf_enabled)

    def test_aci_l3out_ospf_external_policy_name(self) -> None:
        """Test ACI L3Out OSPF external policy name."""
        self.assertEqual(
            self.aci_l3out.ospf_external_policy_name,
            self.aci_l3out_ospf_external_policy_name,
        )

    def test_aci_l3out_pim_policy_name(self) -> None:
        """Test ACI L3Out PIM policy name."""
        self.assertEqual(
            self.aci_l3out.pim_policy_name,
            self.aci_l3out_pim_policy_name,
        )

    def test_aci_l3out_target_dscp(self) -> None:
        """Test ACI L3Out target DSCP option."""
        self.assertEqual(self.aci_l3out.target_dscp, self.aci_l3out_target_dscp)

    def test_aci_l3out_get_target_dscp_color(self) -> None:
        """Test the 'get_target_dscp_color' method of ACI L3Out."""
        self.assertEqual(
            self.aci_l3out.get_target_dscp_color(),
            QualityOfServiceDSCPChoices.colors.get(self.aci_l3out_target_dscp),
        )

    def test_invalid_aci_l3out_name(self) -> None:
        """Test validation of ACI L3Out naming."""
        l3out = ACIL3Out(
            name="ACI L3Out Test 1",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
        )
        with self.assertRaises(ValidationError):
            l3out.full_clean()

    def test_invalid_aci_l3out_name_length(self) -> None:
        """Test validation of ACI L3Out name length."""
        l3out = ACIL3Out(
            name="A" * 65,
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
        )
        with self.assertRaises(ValidationError):
            l3out.full_clean()

    def test_invalid_aci_l3out_name_alias(self) -> None:
        """Test validation of ACI L3Out aliasing."""
        l3out = ACIL3Out(
            name="ACIL3OutTest1",
            name_alias="Invalid Alias",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
        )
        with self.assertRaises(ValidationError):
            l3out.full_clean()

    def test_invalid_aci_l3out_description(self) -> None:
        """Test validation of ACI L3Out description."""
        l3out = ACIL3Out(
            name="ACIL3OutTest1",
            description="Invalid Description: ö",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
        )
        with self.assertRaises(ValidationError):
            l3out.full_clean()

    def test_valid_aci_l3out_aci_vrf_assignment_from_tenant_common(self) -> None:
        """Test valid assignment of ACI VRF from ACI Tenant 'common'."""
        tenant_common = ACITenant.objects.create(
            name="common",
            aci_fabric=self.aci_fabric,
        )
        vrf_common = ACIVRF.objects.create(
            name="common_vrf",
            aci_tenant=tenant_common,
        )
        l3out = ACIL3Out(
            name="ACIL3OutTest1",
            aci_tenant=self.aci_tenant,
            aci_vrf=vrf_common,
            aci_routed_domain=self.aci_routed_domain,
        )
        l3out.full_clean()
        l3out.save()
        self.assertEqual(l3out.aci_vrf, vrf_common)

    def test_invalid_aci_l3out_aci_vrf_assignment_from_other_fabric(self) -> None:
        """Test invalid assignment of ACI VRF from another ACI Fabric."""
        aci_fabric_other = ACIFabric.objects.create(
            name="OtherFabric1",
            fabric_id=126,
            infra_vlan_vid=3901,
        )
        tenant_other = ACITenant.objects.create(
            name="other",
            aci_fabric=aci_fabric_other,
        )
        vrf_other = ACIVRF.objects.create(
            name="other_vrf",
            aci_tenant=tenant_other,
        )
        l3out = ACIL3Out(
            name="ACIL3OutTest1",
            aci_tenant=self.aci_tenant,
            aci_vrf=vrf_other,
            aci_routed_domain=self.aci_routed_domain,
        )
        with self.assertRaises(ValidationError):
            l3out.full_clean()

    def test_invalid_aci_l3out_aci_vrf_assignment_from_tenant_other(self) -> None:
        """Test invalid assignment of ACI VRF from another ACI Tenant."""
        tenant_other = ACITenant.objects.create(
            name="other",
            aci_fabric=self.aci_fabric,
        )
        vrf_other = ACIVRF.objects.create(
            name="other_vrf",
            aci_tenant=tenant_other,
        )
        l3out = ACIL3Out(
            name="ACIL3OutTest1",
            aci_tenant=self.aci_tenant,
            aci_vrf=vrf_other,
            aci_routed_domain=self.aci_routed_domain,
        )
        with self.assertRaises(ValidationError):
            l3out.full_clean()

    def test_invalid_aci_l3out_aci_routed_domain_from_other_fabric(self) -> None:
        """Test invalid assignment of ACI Routed Domain from another Fabric."""
        aci_fabric_other = ACIFabric.objects.create(
            name="OtherFabric2",
            fabric_id=125,
            infra_vlan_vid=3902,
        )
        routed_domain_other = ACIRoutedDomain.objects.create(
            name="OtherRoutedDomain",
            aci_fabric=aci_fabric_other,
        )
        l3out = ACIL3Out(
            name="ACIL3OutTest1",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=routed_domain_other,
        )
        with self.assertRaises(ValidationError):
            l3out.full_clean()

    def test_valid_aci_l3out_multipod_enabled_in_tenant_infra(self) -> None:
        """Test valid Multi-Pod enabled option in ACI Tenant 'infra'."""
        tenant_infra = ACITenant.objects.create(
            name="infra",
            aci_fabric=self.aci_fabric,
        )
        vrf_infra = ACIVRF.objects.create(
            name="infra_vrf",
            aci_tenant=tenant_infra,
        )
        l3out = ACIL3Out(
            name="ACIL3OutInfra",
            aci_tenant=tenant_infra,
            aci_vrf=vrf_infra,
            aci_routed_domain=self.aci_routed_domain,
            multipod_enabled=True,
        )
        l3out.full_clean()
        l3out.save()
        self.assertTrue(l3out.multipod_enabled)

    def test_invalid_aci_l3out_multipod_enabled_in_non_infra_tenant(self) -> None:
        """Test invalid Multi-Pod enabled option in non-infra ACI Tenant."""
        l3out = ACIL3Out(
            name="ACIL3OutMultiPod",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            multipod_enabled=True,
        )
        with self.assertRaises(ValidationError):
            l3out.full_clean()

    def test_invalid_aci_l3out_multipod_enabled_save(self) -> None:
        """Test Multi-Pod validation on direct save of ACI L3Out."""
        l3out = ACIL3Out(
            name="ACIL3OutMultiPodSave",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            multipod_enabled=True,
        )
        with self.assertRaises(ValidationError):
            l3out.save()

    def test_aci_l3out_str_in_tenant_common(self) -> None:
        """Test string representation of ACI L3Out in ACI Tenant 'common'."""
        tenant_common = ACITenant.objects.create(
            name="common",
            aci_fabric=self.aci_fabric,
        )
        vrf_common = ACIVRF.objects.create(
            name="common_vrf",
            aci_tenant=tenant_common,
        )
        l3out_common = ACIL3Out.objects.create(
            name="ACIL3OutCommon",
            aci_tenant=tenant_common,
            aci_vrf=vrf_common,
            aci_routed_domain=self.aci_routed_domain,
        )
        self.assertEqual(l3out_common.__str__(), "ACIL3OutCommon (common)")

    def test_constraint_unique_aci_l3out_name_per_aci_tenant(self) -> None:
        """Test unique constraint of ACI L3Out name per ACI Tenant."""
        duplicate_l3out = ACIL3Out(
            name=self.aci_l3out_name,
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
        )
        with self.assertRaises(IntegrityError):
            duplicate_l3out.save()

    def test_invalid_aci_l3out_eigrp_with_bgp(self) -> None:
        """Test invalid EIGRP enabled together with BGP on ACI L3Out."""
        l3out = ACIL3Out(
            name="ACIL3OutEIGRPBGP",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            eigrp_enabled=True,
            bgp_enabled=True,
        )
        with self.assertRaises(ValidationError):
            l3out.full_clean()

    def test_invalid_aci_l3out_eigrp_with_ospf(self) -> None:
        """Test invalid EIGRP enabled together with OSPF on ACI L3Out."""
        l3out = ACIL3Out(
            name="ACIL3OutEIGRPOSPF",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            eigrp_enabled=True,
            ospf_enabled=True,
        )
        with self.assertRaises(ValidationError):
            l3out.full_clean()

    def test_valid_aci_l3out_import_rtctrl_enforcement_with_bgp(self) -> None:
        """Test valid L3Out import route control enforcement with BGP."""
        l3out = ACIL3Out(
            name="ACIL3OutImportBGP",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            bgp_enabled=True,
            import_route_control_enforcement_enabled=True,
        )
        l3out.full_clean()
        l3out.save()
        self.assertTrue(l3out.import_route_control_enforcement_enabled)

    def test_valid_aci_l3out_import_rtctrl_enforcement_with_ospf(self) -> None:
        """Test valid L3Out import route control enforcement with OSPF."""
        l3out = ACIL3Out(
            name="ACIL3OutImportOSPF",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            ospf_enabled=True,
            import_route_control_enforcement_enabled=True,
        )
        l3out.full_clean()
        l3out.save()
        self.assertTrue(l3out.import_route_control_enforcement_enabled)

    def test_invalid_aci_l3out_import_rtctrl_enforcement_without_bgp_or_ospf(
        self,
    ) -> None:
        """Test invalid import rtctrl enforcement - no BGP or OSPF."""
        l3out = ACIL3Out(
            name="ACIL3OutImportNoProto",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            import_route_control_enforcement_enabled=True,
        )
        with self.assertRaises(ValidationError):
            l3out.full_clean()

    def test_valid_aci_l3out_ospf_external_policy_with_ospf(self) -> None:
        """Test valid OSPF external policy assignment with OSPF enabled."""
        l3out = ACIL3Out(
            name="ACIL3OutOSPFPolicy",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            ospf_enabled=True,
            ospf_external_policy_name="OSPFExtPolicy1",
        )
        l3out.full_clean()
        l3out.save()
        self.assertEqual(l3out.ospf_external_policy_name, "OSPFExtPolicy1")

    def test_invalid_aci_l3out_ospf_external_policy_without_ospf(self) -> None:
        """Test invalid OSPF external policy assignment without OSPF."""
        l3out = ACIL3Out(
            name="ACIL3OutOSPFPolicyNoOSPF",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            ospf_enabled=False,
            ospf_external_policy_name="OSPFExtPolicy1",
        )
        with self.assertRaises(ValidationError):
            l3out.full_clean()

    def test_valid_aci_l3out_eigrp_interface_policy_with_eigrp(self) -> None:
        """Test valid EIGRP interface policy assignment with EIGRP enabled."""
        l3out = ACIL3Out(
            name="ACIL3OutEIGRPPolicy",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            eigrp_enabled=True,
            eigrp_interface_policy_name="EIGRPIfPolicy2",
        )
        l3out.full_clean()
        l3out.save()
        self.assertEqual(l3out.eigrp_interface_policy_name, "EIGRPIfPolicy2")

    def test_invalid_aci_l3out_eigrp_interface_policy_without_eigrp(self) -> None:
        """Test invalid EIGRP interface policy assignment without EIGRP."""
        l3out = ACIL3Out(
            name="ACIL3OutEIGRPPolicyNoEIGRP",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            eigrp_enabled=False,
            eigrp_interface_policy_name="EIGRPIfPolicy2",
        )
        with self.assertRaises(ValidationError):
            l3out.full_clean()

    def test_valid_aci_l3out_pim_policy_with_l3_multicast_ipv4(self) -> None:
        """Test valid PIM policy assignment with L3 multicast IPv4 enabled."""
        l3out = ACIL3Out(
            name="ACIL3OutPIMIPv4",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            l3_multicast_ipv4_enabled=True,
            pim_policy_name="PIMPolicy2",
        )
        l3out.full_clean()
        l3out.save()
        self.assertEqual(l3out.pim_policy_name, "PIMPolicy2")

    def test_valid_aci_l3out_pim_policy_with_l3_multicast_ipv6(self) -> None:
        """Test valid PIM policy assignment with L3 multicast IPv6 enabled."""
        l3out = ACIL3Out(
            name="ACIL3OutPIMIPv6",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            l3_multicast_ipv6_enabled=True,
            pim_policy_name="PIMPolicy3",
        )
        l3out.full_clean()
        l3out.save()
        self.assertEqual(l3out.pim_policy_name, "PIMPolicy3")

    def test_invalid_aci_l3out_pim_policy_without_l3_multicast(self) -> None:
        """Test invalid PIM policy assignment without L3 multicast enabled."""
        l3out = ACIL3Out(
            name="ACIL3OutPIMNoMulticast",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            pim_policy_name="PIMPolicy2",
        )
        with self.assertRaises(ValidationError):
            l3out.full_clean()

    def test_valid_aci_l3out_igmp_interface_policy_with_ipv4_multicast(self) -> None:
        """Test valid IGMP interface policy with IPv4 multicast enabled."""
        l3out = ACIL3Out(
            name="ACIL3OutIGMPIPv4",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            l3_multicast_ipv4_enabled=True,
            igmp_interface_policy_name="IGMPIfPolicy2",
        )
        l3out.full_clean()
        l3out.save()
        self.assertEqual(l3out.igmp_interface_policy_name, "IGMPIfPolicy2")

    def test_invalid_aci_l3out_igmp_interface_policy_without_ipv4_multicast(
        self,
    ) -> None:
        """Test invalid IGMP interface policy without IPv4 multicast."""
        l3out = ACIL3Out(
            name="ACIL3OutIGMPNoIPv4",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            igmp_interface_policy_name="IGMPIfPolicy2",
        )
        with self.assertRaises(ValidationError):
            l3out.full_clean()

    def test_aci_l3out_save_raises_for_vrf_from_wrong_fabric(self) -> None:
        """Test that save() raises for a VRF from a different ACI Fabric."""
        aci_fabric_b = ACIFabric.objects.create(
            name="FabricSaveTestB",
            fabric_id=201,
            infra_vlan_vid=3901,
        )
        aci_tenant_b = ACITenant.objects.create(
            name="TenantSaveTestB",
            aci_fabric=aci_fabric_b,
        )
        aci_vrf_b = ACIVRF.objects.create(
            name="VRFSaveTestB",
            aci_tenant=aci_tenant_b,
        )
        l3out = ACIL3Out(
            name="L3OutWrongFabricSave",
            aci_tenant=self.aci_tenant,
            aci_vrf=aci_vrf_b,
            aci_routed_domain=self.aci_routed_domain,
        )
        with self.assertRaises(ValidationError):
            l3out.save()

    def test_aci_l3out_save_raises_for_vrf_from_wrong_tenant(self) -> None:
        """Test that save() raises for a VRF from a different ACI Tenant."""
        aci_tenant_other = ACITenant.objects.create(
            name="TenantSaveTestOther",
            aci_fabric=self.aci_fabric,
        )
        aci_vrf_other = ACIVRF.objects.create(
            name="VRFSaveTestOther",
            aci_tenant=aci_tenant_other,
        )
        l3out = ACIL3Out(
            name="L3OutWrongTenantSave",
            aci_tenant=self.aci_tenant,
            aci_vrf=aci_vrf_other,
            aci_routed_domain=self.aci_routed_domain,
        )
        with self.assertRaises(ValidationError):
            l3out.save()


class ACIExternalEndpointGroupTestCase(ACIBaseTestCase):
    """Test case for ACIExternalEndpointGroup model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIExternalEndpointGroup model."""
        super().setUpTestData()

        cls.aci_ext_epg_name = "ACITestExtEPG"
        cls.aci_ext_epg_alias = "ACITestExtEPGAlias"
        cls.aci_ext_epg_description = "ACI Test External EPG"
        cls.aci_ext_epg_comments = """
        ACI External Endpoint Group for NetBox ACI Plugin testing.
        """
        cls.aci_ext_epg_preferred_group_member_enabled = True
        cls.aci_ext_epg_qos_class = QualityOfServiceClassChoices.CLASS_LEVEL_3
        cls.aci_ext_epg_target_dscp = QualityOfServiceDSCPChoices.DSCP_AF21

        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIBaseTestRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_l3out = ACIL3Out.objects.create(
            name="ACIBaseTestL3Out",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.aci_external_endpoint_group = ACIExternalEndpointGroup.objects.create(
            name=cls.aci_ext_epg_name,
            name_alias=cls.aci_ext_epg_alias,
            description=cls.aci_ext_epg_description,
            comments=cls.aci_ext_epg_comments,
            aci_l3out=cls.aci_l3out,
            nb_tenant=cls.nb_tenant,
            preferred_group_member_enabled=(
                cls.aci_ext_epg_preferred_group_member_enabled
            ),
            qos_class=cls.aci_ext_epg_qos_class,
            target_dscp=cls.aci_ext_epg_target_dscp,
        )

    def test_aci_external_endpoint_group_instance(self) -> None:
        """Test instance of created ACI External Endpoint Group."""
        self.assertTrue(
            isinstance(self.aci_external_endpoint_group, ACIExternalEndpointGroup)
        )

    def test_aci_external_endpoint_group_str(self) -> None:
        """Test string representation of ACI External Endpoint Group."""
        self.assertEqual(
            self.aci_external_endpoint_group.__str__(),
            f"{self.aci_ext_epg_name} ({self.aci_l3out.name})",
        )

    def test_aci_external_endpoint_group_aci_l3out_instance(self) -> None:
        """Test ACI L3Out instance in ACI External Endpoint Group."""
        self.assertTrue(
            isinstance(self.aci_external_endpoint_group.aci_l3out, ACIL3Out)
        )
        self.assertEqual(
            self.aci_external_endpoint_group.aci_l3out.name,
            self.aci_l3out.name,
        )

    def test_aci_external_endpoint_group_aci_tenant_instance(self) -> None:
        """Test ACI Tenant instance in ACI External Endpoint Group."""
        self.assertTrue(
            isinstance(self.aci_external_endpoint_group.aci_tenant, ACITenant)
        )
        self.assertEqual(
            self.aci_external_endpoint_group.aci_tenant.name,
            self.aci_tenant_name,
        )

    def test_aci_external_endpoint_group_aci_vrf_instance(self) -> None:
        """Test ACI VRF instance in ACI External Endpoint Group."""
        self.assertTrue(isinstance(self.aci_external_endpoint_group.aci_vrf, ACIVRF))
        self.assertEqual(
            self.aci_external_endpoint_group.aci_vrf.name,
            self.aci_vrf_name,
        )

    def test_aci_external_endpoint_group_parent_object(self) -> None:
        """Test parent object of ACI External Endpoint Group."""
        self.assertEqual(
            self.aci_external_endpoint_group.parent_object,
            self.aci_l3out,
        )

    def test_aci_external_endpoint_group_name_alias(self) -> None:
        """Test ACI External Endpoint Group name alias."""
        self.assertEqual(
            self.aci_external_endpoint_group.name_alias,
            self.aci_ext_epg_alias,
        )

    def test_aci_external_endpoint_group_description(self) -> None:
        """Test ACI External Endpoint Group description."""
        self.assertEqual(
            self.aci_external_endpoint_group.description,
            self.aci_ext_epg_description,
        )

    def test_aci_external_endpoint_group_nb_tenant_instance(self) -> None:
        """Test NetBox tenant instance in ACI External Endpoint Group."""
        self.assertTrue(isinstance(self.aci_external_endpoint_group.nb_tenant, Tenant))
        self.assertEqual(
            self.aci_external_endpoint_group.nb_tenant.name,
            self.nb_tenant_name,
        )

    def test_aci_external_endpoint_group_preferred_group_member_enabled(
        self,
    ) -> None:
        """Test preferred group member option in ACI External EPG."""
        self.assertEqual(
            self.aci_external_endpoint_group.preferred_group_member_enabled,
            self.aci_ext_epg_preferred_group_member_enabled,
        )

    def test_aci_external_endpoint_group_qos_class(self) -> None:
        """Test QoS class option in ACI External Endpoint Group."""
        self.assertEqual(
            self.aci_external_endpoint_group.qos_class,
            self.aci_ext_epg_qos_class,
        )

    def test_aci_external_endpoint_group_target_dscp(self) -> None:
        """Test target DSCP option in ACI External Endpoint Group."""
        self.assertEqual(
            self.aci_external_endpoint_group.target_dscp,
            self.aci_ext_epg_target_dscp,
        )

    def test_aci_external_endpoint_group_get_qos_class_color(self) -> None:
        """Test the 'get_qos_class_color' method of ACI External EPG."""
        self.assertEqual(
            self.aci_external_endpoint_group.get_qos_class_color(),
            QualityOfServiceClassChoices.colors.get(self.aci_ext_epg_qos_class),
        )

    def test_aci_external_endpoint_group_get_target_dscp_color(self) -> None:
        """Test the 'get_target_dscp_color' method of ACI External EPG."""
        self.assertEqual(
            self.aci_external_endpoint_group.get_target_dscp_color(),
            QualityOfServiceDSCPChoices.colors.get(self.aci_ext_epg_target_dscp),
        )

    def test_aci_external_endpoint_group_contract_relation(self) -> None:
        """Test ACI Contract Relation support for ACI External EPG."""
        aci_contract = ACIContract.objects.create(
            name="ACITestExternalEPGContract",
            aci_tenant=self.aci_tenant,
        )
        aci_object_type = ContentType.objects.get_for_model(
            self.aci_external_endpoint_group
        )
        aci_contract_relation = ACIContractRelation.objects.create(
            aci_contract=aci_contract,
            aci_object_type=aci_object_type,
            aci_object_id=self.aci_external_endpoint_group.pk,
        )
        self.assertEqual(
            aci_contract_relation.aci_object,
            self.aci_external_endpoint_group,
        )
        self.assertIn(
            aci_contract_relation,
            self.aci_external_endpoint_group.aci_contract_relations.all(),
        )

    def test_invalid_aci_external_endpoint_group_name(self) -> None:
        """Test validation of ACI External Endpoint Group naming."""
        external_epg = ACIExternalEndpointGroup(
            name="ACI External EPG Test 1",
            aci_l3out=self.aci_l3out,
        )
        with self.assertRaises(ValidationError):
            external_epg.full_clean()

    def test_invalid_aci_external_endpoint_group_name_alias(self) -> None:
        """Test validation of ACI External Endpoint Group aliasing."""
        external_epg = ACIExternalEndpointGroup(
            name="ACIExtEPGTest1",
            name_alias="Invalid Alias",
            aci_l3out=self.aci_l3out,
        )
        with self.assertRaises(ValidationError):
            external_epg.full_clean()

    def test_invalid_aci_external_endpoint_group_description(self) -> None:
        """Test validation of ACI External Endpoint Group description."""
        external_epg = ACIExternalEndpointGroup(
            name="ACIExtEPGTest1",
            description="Invalid Description: ö",
            aci_l3out=self.aci_l3out,
        )
        with self.assertRaises(ValidationError):
            external_epg.full_clean()

    def test_constraint_unique_aci_external_epg_name_per_l3out(self) -> None:
        """Test unique constraint of External EPG name per ACI L3Out."""
        duplicate_external_epg = ACIExternalEndpointGroup(
            name=self.aci_ext_epg_name,
            aci_l3out=self.aci_l3out,
        )
        with self.assertRaises(IntegrityError):
            duplicate_external_epg.save()


class ACIExternalSubnetTestCase(ACIBaseTestCase):
    """Test case for ACIExternalSubnet model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIExternalSubnet model."""
        super().setUpTestData()

        cls.aci_external_subnet_name = "ACITestExternalSubnet"
        cls.aci_external_subnet_alias = "ACITestExternalSubnetAlias"
        cls.aci_external_subnet_description = "ACI Test External Subnet"
        cls.aci_external_subnet_comments = """
        ACI External Subnet for NetBox ACI Plugin testing.
        """
        cls.aci_external_subnet_aggregate_export_rtctrl_enabled = True
        cls.aci_external_subnet_aggregate_import_rtctrl_enabled = True
        cls.aci_external_subnet_aggregate_shared_rtctrl_enabled = True
        cls.aci_external_subnet_bgp_route_summarization_enabled = True
        cls.aci_external_subnet_bgp_route_sum_policy_name = "BGPSummaryPolicy1"
        cls.aci_external_subnet_eigrp_route_summarization_enabled = True
        cls.aci_external_subnet_export_route_control_enabled = True
        cls.aci_external_subnet_import_route_control_enabled = True
        cls.aci_external_subnet_import_security_enabled = True
        cls.aci_external_subnet_ospf_route_summarization_enabled = True
        cls.aci_external_subnet_ospf_route_sum_policy_name = "OSPFSummaryPolicy1"
        cls.aci_external_subnet_prefix_value = "10.10.0.0/24"
        cls.aci_external_subnet_shared_route_control_enabled = True
        cls.aci_external_subnet_shared_security_enabled = True

        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIBaseTestRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_l3out = ACIL3Out.objects.create(
            name="ACIBaseTestL3Out",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.aci_external_endpoint_group = ACIExternalEndpointGroup.objects.create(
            name="ACIBaseTestExternalEPG",
            aci_l3out=cls.aci_l3out,
        )
        cls.prefix = Prefix.objects.create(
            prefix=cls.aci_external_subnet_prefix_value,
            vrf=cls.nb_vrf,
        )
        cls.aci_external_subnet = ACIExternalSubnet.objects.create(
            name=cls.aci_external_subnet_name,
            name_alias=cls.aci_external_subnet_alias,
            description=cls.aci_external_subnet_description,
            comments=cls.aci_external_subnet_comments,
            aci_external_endpoint_group=cls.aci_external_endpoint_group,
            nb_prefix=cls.prefix,
            nb_tenant=cls.nb_tenant,
            aggregate_export_route_control_enabled=(
                cls.aci_external_subnet_aggregate_export_rtctrl_enabled
            ),
            aggregate_import_route_control_enabled=(
                cls.aci_external_subnet_aggregate_import_rtctrl_enabled
            ),
            aggregate_shared_route_control_enabled=(
                cls.aci_external_subnet_aggregate_shared_rtctrl_enabled
            ),
            bgp_route_summarization_enabled=(
                cls.aci_external_subnet_bgp_route_summarization_enabled
            ),
            bgp_route_summarization_policy_name=(
                cls.aci_external_subnet_bgp_route_sum_policy_name
            ),
            eigrp_route_summarization_enabled=(
                cls.aci_external_subnet_eigrp_route_summarization_enabled
            ),
            export_route_control_enabled=(
                cls.aci_external_subnet_export_route_control_enabled
            ),
            import_route_control_enabled=(
                cls.aci_external_subnet_import_route_control_enabled
            ),
            import_security_enabled=cls.aci_external_subnet_import_security_enabled,
            ospf_route_summarization_enabled=(
                cls.aci_external_subnet_ospf_route_summarization_enabled
            ),
            ospf_route_summarization_policy_name=(
                cls.aci_external_subnet_ospf_route_sum_policy_name
            ),
            shared_route_control_enabled=(
                cls.aci_external_subnet_shared_route_control_enabled
            ),
            shared_security_enabled=cls.aci_external_subnet_shared_security_enabled,
        )
        cls.aci_l3out_bgp = ACIL3Out.objects.create(
            name="ACIBaseTestL3OutBGP",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
            bgp_enabled=True,
            import_route_control_enforcement_enabled=True,
        )
        cls.aci_epg_bgp = ACIExternalEndpointGroup.objects.create(
            name="ACIBaseTestExternalEPGBGP",
            aci_l3out=cls.aci_l3out_bgp,
        )
        cls.aci_l3out_ospf = ACIL3Out.objects.create(
            name="ACIBaseTestL3OutOSPF",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
            ospf_enabled=True,
            import_route_control_enforcement_enabled=True,
        )
        cls.aci_epg_ospf = ACIExternalEndpointGroup.objects.create(
            name="ACIBaseTestExternalEPGOSPF",
            aci_l3out=cls.aci_l3out_ospf,
        )
        cls.aci_l3out_eigrp = ACIL3Out.objects.create(
            name="ACIBaseTestL3OutEIGRP",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
            eigrp_enabled=True,
        )
        cls.aci_epg_eigrp = ACIExternalEndpointGroup.objects.create(
            name="ACIBaseTestExternalEPGEIGRP",
            aci_l3out=cls.aci_l3out_eigrp,
        )
        cls.prefix_default_route = Prefix.objects.create(
            prefix="0.0.0.0/0",
            vrf=cls.nb_vrf,
        )

    def test_aci_external_subnet_instance(self) -> None:
        """Test instance of created ACI External Subnet."""
        self.assertTrue(isinstance(self.aci_external_subnet, ACIExternalSubnet))

    def test_aci_external_subnet_str(self) -> None:
        """Test string representation of ACI External Subnet."""
        self.assertEqual(
            self.aci_external_subnet.__str__(),
            f"{self.aci_external_subnet_prefix_value}"
            f" ({self.aci_external_endpoint_group.name})",
        )

    def test_aci_external_subnet_name_alias(self) -> None:
        """Test ACI External Subnet name alias."""
        self.assertEqual(
            self.aci_external_subnet.name_alias,
            self.aci_external_subnet_alias,
        )

    def test_aci_external_subnet_description(self) -> None:
        """Test ACI External Subnet description."""
        self.assertEqual(
            self.aci_external_subnet.description,
            self.aci_external_subnet_description,
        )

    def test_aci_external_subnet_aci_external_epg_instance(self) -> None:
        """Test ACI External Endpoint Group instance in ACI External Subnet."""
        self.assertTrue(
            isinstance(
                self.aci_external_subnet.aci_external_endpoint_group,
                ACIExternalEndpointGroup,
            )
        )
        self.assertEqual(
            self.aci_external_subnet.aci_external_endpoint_group.name,
            self.aci_external_endpoint_group.name,
        )

    def test_aci_external_subnet_aci_l3out_instance(self) -> None:
        """Test ACI L3Out instance in ACI External Subnet."""
        self.assertTrue(isinstance(self.aci_external_subnet.aci_l3out, ACIL3Out))
        self.assertEqual(
            self.aci_external_subnet.aci_l3out.name,
            self.aci_l3out.name,
        )

    def test_aci_external_subnet_aci_tenant_instance(self) -> None:
        """Test ACI Tenant instance in ACI External Subnet."""
        self.assertTrue(isinstance(self.aci_external_subnet.aci_tenant, ACITenant))
        self.assertEqual(self.aci_external_subnet.aci_tenant.name, self.aci_tenant_name)

    def test_aci_external_subnet_aci_vrf_instance(self) -> None:
        """Test ACI VRF instance in ACI External Subnet."""
        self.assertTrue(isinstance(self.aci_external_subnet.aci_vrf, ACIVRF))
        self.assertEqual(self.aci_external_subnet.aci_vrf.name, self.aci_vrf_name)

    def test_aci_external_subnet_nb_prefix_instance(self) -> None:
        """Test NetBox Prefix FK instance in ACI External Subnet."""
        self.assertTrue(isinstance(self.aci_external_subnet.nb_prefix, Prefix))
        self.assertEqual(
            str(self.aci_external_subnet.nb_prefix.prefix),
            self.aci_external_subnet_prefix_value,
        )

    def test_aci_external_subnet_matched_prefix_synced_from_nb_prefix(
        self,
    ) -> None:
        """Test matched prefix is synced from NetBox Prefix on save."""
        self.assertEqual(
            str(self.aci_external_subnet.matched_prefix),
            self.aci_external_subnet_prefix_value,
        )

    def test_aci_external_subnet_parent_object(self) -> None:
        """Test parent object of ACI External Subnet."""
        self.assertEqual(
            self.aci_external_subnet.parent_object,
            self.aci_external_endpoint_group,
        )

    def test_aci_external_subnet_nb_tenant_instance(self) -> None:
        """Test NetBox tenant instance in ACI External Subnet."""
        self.assertTrue(isinstance(self.aci_external_subnet.nb_tenant, Tenant))
        self.assertEqual(self.aci_external_subnet.nb_tenant.name, self.nb_tenant_name)

    def test_aci_external_subnet_aggregate_export_route_control_enabled(self) -> None:
        """Test aggregate export route control option in External Subnet."""
        self.assertEqual(
            self.aci_external_subnet.aggregate_export_route_control_enabled,
            self.aci_external_subnet_aggregate_export_rtctrl_enabled,
        )

    def test_aci_external_subnet_aggregate_import_route_control_enabled(self) -> None:
        """Test aggregate import route control option in External Subnet."""
        self.assertEqual(
            self.aci_external_subnet.aggregate_import_route_control_enabled,
            self.aci_external_subnet_aggregate_import_rtctrl_enabled,
        )

    def test_aci_external_subnet_aggregate_shared_route_control_enabled(self) -> None:
        """Test aggregate shared route control option in External Subnet."""
        self.assertEqual(
            self.aci_external_subnet.aggregate_shared_route_control_enabled,
            self.aci_external_subnet_aggregate_shared_rtctrl_enabled,
        )

    def test_aci_external_subnet_bgp_route_summarization_enabled(self) -> None:
        """Test BGP route summarization option in ACI External Subnet."""
        self.assertEqual(
            self.aci_external_subnet.bgp_route_summarization_enabled,
            self.aci_external_subnet_bgp_route_summarization_enabled,
        )

    def test_aci_external_subnet_bgp_route_summarization_policy_name(self) -> None:
        """Test BGP route summarization policy name in External Subnet."""
        self.assertEqual(
            self.aci_external_subnet.bgp_route_summarization_policy_name,
            self.aci_external_subnet_bgp_route_sum_policy_name,
        )

    def test_aci_external_subnet_eigrp_route_summarization_enabled(self) -> None:
        """Test EIGRP route summarization option in ACI External Subnet."""
        self.assertEqual(
            self.aci_external_subnet.eigrp_route_summarization_enabled,
            self.aci_external_subnet_eigrp_route_summarization_enabled,
        )

    def test_aci_external_subnet_export_route_control_enabled(self) -> None:
        """Test export route control option in ACI External Subnet."""
        self.assertEqual(
            self.aci_external_subnet.export_route_control_enabled,
            self.aci_external_subnet_export_route_control_enabled,
        )

    def test_aci_external_subnet_import_route_control_enabled(self) -> None:
        """Test import route control option in ACI External Subnet."""
        self.assertEqual(
            self.aci_external_subnet.import_route_control_enabled,
            self.aci_external_subnet_import_route_control_enabled,
        )

    def test_aci_external_subnet_import_security_enabled(self) -> None:
        """Test import security option in ACI External Subnet."""
        self.assertEqual(
            self.aci_external_subnet.import_security_enabled,
            self.aci_external_subnet_import_security_enabled,
        )

    def test_aci_external_subnet_ospf_route_summarization_enabled(self) -> None:
        """Test OSPF route summarization option in ACI External Subnet."""
        self.assertEqual(
            self.aci_external_subnet.ospf_route_summarization_enabled,
            self.aci_external_subnet_ospf_route_summarization_enabled,
        )

    def test_aci_external_subnet_ospf_route_summarization_policy_name(self) -> None:
        """Test OSPF route summarization policy name in External Subnet."""
        self.assertEqual(
            self.aci_external_subnet.ospf_route_summarization_policy_name,
            self.aci_external_subnet_ospf_route_sum_policy_name,
        )

    def test_aci_external_subnet_shared_route_control_enabled(self) -> None:
        """Test shared route control option in ACI External Subnet."""
        self.assertEqual(
            self.aci_external_subnet.shared_route_control_enabled,
            self.aci_external_subnet_shared_route_control_enabled,
        )

    def test_aci_external_subnet_shared_security_enabled(self) -> None:
        """Test shared security option in ACI External Subnet."""
        self.assertEqual(
            self.aci_external_subnet.shared_security_enabled,
            self.aci_external_subnet_shared_security_enabled,
        )

    def test_invalid_aci_external_subnet_name(self) -> None:
        """Test validation of ACI External Subnet naming."""
        external_subnet = ACIExternalSubnet(
            name="ACI External Subnet Test 1",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            nb_prefix=self.prefix,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_invalid_aci_external_subnet_nb_prefix_vrf(self) -> None:
        """Test validation of NetBox Prefix VRF assignment."""
        nb_tenant_other = Tenant.objects.create(name="OtherNetBoxTenant")
        nb_vrf_other = VRF.objects.create(
            name="OtherNetBoxVRF",
            tenant=nb_tenant_other,
        )
        prefix_other = Prefix.objects.create(
            prefix="10.20.0.0/24",
            vrf=nb_vrf_other,
        )
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetTest1",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            nb_prefix=prefix_other,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_invalid_aci_external_subnet_global_nb_prefix_with_mapped_vrf(
        self,
    ) -> None:
        """Test global NB Prefix rejected when ACI VRF has a mapped NB VRF."""
        prefix_without_vrf = Prefix.objects.create(prefix="10.30.0.0/24")
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetGlobalPrefix",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            nb_prefix=prefix_without_vrf,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_valid_aci_external_subnet_nb_prefix_no_vrf_mapping(self) -> None:
        """Test global NB Prefix valid when ACI VRF has no mapped NB VRF."""
        aci_vrf_no_nb = ACIVRF.objects.create(
            name="ACIVRFNoNBVRF",
            aci_tenant=self.aci_tenant,
        )
        aci_l3out_no_nb = ACIL3Out.objects.create(
            name="ACIL3OutNoNBVRF",
            aci_tenant=self.aci_tenant,
            aci_vrf=aci_vrf_no_nb,
            aci_routed_domain=self.aci_routed_domain,
        )
        aci_epg_no_nb = ACIExternalEndpointGroup.objects.create(
            name="ACIExternalEPGNoNBVRF",
            aci_l3out=aci_l3out_no_nb,
        )
        prefix_without_vrf = Prefix.objects.create(prefix="10.30.0.0/24")
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetNoVRFMapping",
            aci_external_endpoint_group=aci_epg_no_nb,
            nb_prefix=prefix_without_vrf,
        )
        external_subnet.full_clean()
        external_subnet.save()
        self.assertEqual(external_subnet.nb_prefix, prefix_without_vrf)
        self.assertEqual(
            str(external_subnet.matched_prefix),
            str(prefix_without_vrf.prefix),
        )

    def test_valid_aci_external_subnet_direct_matched_prefix(self) -> None:
        """Test creating an External Subnet with a direct matched prefix."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetDirect",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            matched_prefix="10.50.0.0/24",
        )
        external_subnet.full_clean()
        external_subnet.save()
        self.assertIsNone(external_subnet.nb_prefix)
        self.assertEqual(str(external_subnet.matched_prefix), "10.50.0.0/24")

    def test_invalid_aci_external_subnet_missing_matched_prefix(self) -> None:
        """Test ValidationError when no prefix field is set."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetNoPrefix",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_constraint_unique_aci_external_subnet_name_per_external_epg(
        self,
    ) -> None:
        """Test unique constraint of External Subnet name per External EPG."""
        prefix_other = Prefix.objects.create(prefix="10.40.0.0/24", vrf=self.nb_vrf)
        duplicate_external_subnet = ACIExternalSubnet(
            name=self.aci_external_subnet_name,
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            nb_prefix=prefix_other,
        )
        with self.assertRaises(IntegrityError):
            duplicate_external_subnet.save()

    def test_constraint_unique_matched_prefix_per_external_epg(self) -> None:
        """Test unique constraint of matched prefix per ACI External EPG."""
        duplicate_external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetDuplicatePrefix",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            nb_prefix=self.prefix,
        )
        with self.assertRaises(IntegrityError):
            duplicate_external_subnet.save()

    def test_constraint_unique_direct_matched_prefix_per_external_epg(
        self,
    ) -> None:
        """Test unique constraint on direct matched prefix per External EPG."""
        duplicate_external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetDuplicateDirect",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            matched_prefix=self.aci_external_subnet_prefix_value,
        )
        with self.assertRaises(IntegrityError):
            duplicate_external_subnet.save()

    def test_valid_aci_external_subnet_import_rtctrl_with_enforcement(self) -> None:
        """Test valid import route control on subnet with enforcement."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetImportRtCtrl",
            aci_external_endpoint_group=self.aci_epg_bgp,
            matched_prefix="10.60.0.0/24",
            import_route_control_enabled=True,
        )
        external_subnet.full_clean()
        external_subnet.save()
        self.assertTrue(external_subnet.import_route_control_enabled)

    def test_invalid_aci_external_subnet_import_rtctrl_without_enforcement(
        self,
    ) -> None:
        """Test invalid import route control when enforcement is disabled."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetImportNoEnforce",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            matched_prefix="10.61.0.0/24",
            import_route_control_enabled=True,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_invalid_aci_external_subnet_import_rtctrl_on_eigrp_only_l3out(
        self,
    ) -> None:
        """Test invalid import route control on an EIGRP-only ACI L3Out."""
        aci_l3out_eigrp_enforcement = ACIL3Out.objects.create(
            name="ACIBaseTestL3OutEIGRPEnforcement",
            aci_tenant=self.aci_tenant,
            aci_vrf=self.aci_vrf,
            aci_routed_domain=self.aci_routed_domain,
            eigrp_enabled=True,
            import_route_control_enforcement_enabled=True,
        )
        aci_epg_eigrp_enforcement = ACIExternalEndpointGroup.objects.create(
            name="ACIBaseTestExternalEPGEIGRPEnforcement",
            aci_l3out=aci_l3out_eigrp_enforcement,
        )
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetImportEIGRP",
            aci_external_endpoint_group=aci_epg_eigrp_enforcement,
            matched_prefix="10.62.0.0/24",
            import_route_control_enabled=True,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_invalid_aci_external_subnet_aggregate_import_without_import(
        self,
    ) -> None:
        """Test invalid aggregate import route control without import."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetAggImportNoImport",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            matched_prefix="10.63.0.0/24",
            aggregate_import_route_control_enabled=True,
            import_route_control_enabled=False,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_invalid_aci_external_subnet_aggregate_export_without_export(
        self,
    ) -> None:
        """Test invalid aggregate export route control without export."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetAggExportNoExport",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            matched_prefix="10.64.0.0/24",
            aggregate_export_route_control_enabled=True,
            export_route_control_enabled=False,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_invalid_aci_external_subnet_aggregate_shared_without_shared(
        self,
    ) -> None:
        """Test invalid aggregate shared route control without shared."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetAggSharedNoShared",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            matched_prefix="10.65.0.0/24",
            aggregate_shared_route_control_enabled=True,
            shared_route_control_enabled=False,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_invalid_aci_external_subnet_aggregate_import_on_non_default_route(
        self,
    ) -> None:
        """Test invalid aggregate import route control on non-default route."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetAggImportNonDefault",
            aci_external_endpoint_group=self.aci_epg_bgp,
            matched_prefix="10.66.0.0/24",
            import_route_control_enabled=True,
            aggregate_import_route_control_enabled=True,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_invalid_aci_external_subnet_aggregate_export_on_non_default_route(
        self,
    ) -> None:
        """Test invalid aggregate export route control on non-default route."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetAggExportNonDefault",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            matched_prefix="10.67.0.0/24",
            export_route_control_enabled=True,
            aggregate_export_route_control_enabled=True,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_valid_aci_external_subnet_aggregate_import_on_default_route(
        self,
    ) -> None:
        """Test valid aggregate import route control on default-route."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetAggImportDefault",
            aci_external_endpoint_group=self.aci_epg_bgp,
            nb_prefix=self.prefix_default_route,
            import_route_control_enabled=True,
            aggregate_import_route_control_enabled=True,
        )
        external_subnet.full_clean()
        external_subnet.save()
        self.assertTrue(external_subnet.aggregate_import_route_control_enabled)

    def test_valid_aci_external_subnet_aggregate_export_on_default_route(
        self,
    ) -> None:
        """Test valid aggregate export route control on default-route."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetAggExportDefault",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            matched_prefix="0.0.0.0/0",
            export_route_control_enabled=True,
            aggregate_export_route_control_enabled=True,
        )
        external_subnet.full_clean()
        external_subnet.save()
        self.assertTrue(external_subnet.aggregate_export_route_control_enabled)

    def test_invalid_aci_external_subnet_shared_security_without_import_security(
        self,
    ) -> None:
        """Test invalid shared security enabled without import security."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetSharedSecNoImport",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            matched_prefix="10.68.0.0/24",
            import_security_enabled=False,
            shared_security_enabled=True,
            shared_route_control_enabled=True,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_invalid_aci_external_subnet_shared_security_without_shared_route_control(
        self,
    ) -> None:
        """Test invalid shared security without shared route coverage."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetSharedSecNoRtCtrl",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            matched_prefix="10.69.0.0/24",
            import_security_enabled=True,
            shared_security_enabled=True,
            shared_route_control_enabled=False,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_invalid_aci_external_subnet_multiple_route_summarization_types(
        self,
    ) -> None:
        """Test invalid enabling of multiple route summarization types."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetMultiSumm",
            aci_external_endpoint_group=self.aci_epg_bgp,
            matched_prefix="10.70.0.0/24",
            bgp_route_summarization_enabled=True,
            ospf_route_summarization_enabled=True,
            export_route_control_enabled=True,
            import_security_enabled=True,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_invalid_aci_external_subnet_route_summarization_without_export_rtctrl(
        self,
    ) -> None:
        """Test invalid route summarization without export route control."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetSummNoExport",
            aci_external_endpoint_group=self.aci_epg_bgp,
            matched_prefix="10.71.0.0/24",
            bgp_route_summarization_enabled=True,
            export_route_control_enabled=False,
            import_security_enabled=True,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_invalid_aci_external_subnet_route_summarization_without_import_security(
        self,
    ) -> None:
        """Test invalid route summarization without import security."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetSummNoImportSec",
            aci_external_endpoint_group=self.aci_epg_bgp,
            matched_prefix="10.72.0.0/24",
            bgp_route_summarization_enabled=True,
            export_route_control_enabled=True,
            import_security_enabled=False,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_valid_aci_external_subnet_bgp_route_summarization(self) -> None:
        """Test valid BGP route summarization on a BGP-enabled L3Out."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetBGPSumm",
            aci_external_endpoint_group=self.aci_epg_bgp,
            matched_prefix="10.73.0.0/24",
            bgp_route_summarization_enabled=True,
            export_route_control_enabled=True,
            import_security_enabled=True,
        )
        external_subnet.full_clean()
        external_subnet.save()
        self.assertTrue(external_subnet.bgp_route_summarization_enabled)

    def test_invalid_aci_external_subnet_bgp_route_summarization_without_bgp(
        self,
    ) -> None:
        """Test invalid BGP route summarization on a non-BGP L3Out."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetBGPSummNoBGP",
            aci_external_endpoint_group=self.aci_epg_ospf,
            matched_prefix="10.74.0.0/24",
            bgp_route_summarization_enabled=True,
            export_route_control_enabled=True,
            import_security_enabled=True,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_valid_aci_external_subnet_ospf_route_summarization(self) -> None:
        """Test valid OSPF route summarization on an OSPF-enabled L3Out."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetOSPFSumm",
            aci_external_endpoint_group=self.aci_epg_ospf,
            matched_prefix="10.75.0.0/24",
            ospf_route_summarization_enabled=True,
            export_route_control_enabled=True,
            import_security_enabled=True,
        )
        external_subnet.full_clean()
        external_subnet.save()
        self.assertTrue(external_subnet.ospf_route_summarization_enabled)

    def test_invalid_aci_external_subnet_ospf_route_summarization_without_ospf(
        self,
    ) -> None:
        """Test invalid OSPF route summarization on a non-OSPF L3Out."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetOSPFSummNoOSPF",
            aci_external_endpoint_group=self.aci_epg_bgp,
            matched_prefix="10.76.0.0/24",
            ospf_route_summarization_enabled=True,
            export_route_control_enabled=True,
            import_security_enabled=True,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_valid_aci_external_subnet_eigrp_route_summarization(self) -> None:
        """Test valid EIGRP route summarization on an EIGRP-enabled L3Out."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetEIGRPSumm",
            aci_external_endpoint_group=self.aci_epg_eigrp,
            matched_prefix="10.77.0.0/24",
            eigrp_route_summarization_enabled=True,
            export_route_control_enabled=True,
            import_security_enabled=True,
        )
        external_subnet.full_clean()
        external_subnet.save()
        self.assertTrue(external_subnet.eigrp_route_summarization_enabled)

    def test_invalid_aci_external_subnet_eigrp_route_summarization_without_eigrp(
        self,
    ) -> None:
        """Test invalid EIGRP route summarization on a non-EIGRP L3Out."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetEIGRPSummNoEIGRP",
            aci_external_endpoint_group=self.aci_epg_bgp,
            matched_prefix="10.78.0.0/24",
            eigrp_route_summarization_enabled=True,
            export_route_control_enabled=True,
            import_security_enabled=True,
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_invalid_aci_external_subnet_bgp_summarization_policy_without_summarization(
        self,
    ) -> None:
        """Test invalid BGP summarization policy without BGP summarization."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetBGPSummPolicyNoSumm",
            aci_external_endpoint_group=self.aci_epg_bgp,
            matched_prefix="10.79.0.0/24",
            bgp_route_summarization_policy_name="BGPSummPolicy2",
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_invalid_aci_external_subnet_ospf_summ_policy_without_summarization(
        self,
    ) -> None:
        """Test invalid OSPF summ policy without OSPF summarization."""
        external_subnet = ACIExternalSubnet(
            name="ACIExternalSubnetOSPFSummPolicyNoSumm",
            aci_external_endpoint_group=self.aci_epg_ospf,
            matched_prefix="10.80.0.0/24",
            ospf_route_summarization_policy_name="OSPFSummPolicy2",
        )
        with self.assertRaises(ValidationError):
            external_subnet.full_clean()

    def test_aci_external_subnet_prefix_source_direct(self) -> None:
        """Test prefix_source returns 'direct' when no NetBox Prefix is set."""
        subnet = ACIExternalSubnet(
            name="ACIExternalSubnetDirect",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            matched_prefix="10.99.0.0/24",
        )
        self.assertEqual(subnet.prefix_source, "direct")

    def test_aci_external_subnet_save_adds_matched_prefix_to_update_fields(
        self,
    ) -> None:
        """Test save() adds matched_prefix to update_fields for nb_prefix."""
        prefix_uf = Prefix.objects.create(
            prefix="10.97.0.0/24",
            vrf=self.nb_vrf,
        )
        subnet = ACIExternalSubnet.objects.create(
            name="ACIExternalSubnetSaveUF",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            nb_prefix=prefix_uf,
        )
        subnet.name_alias = "Updated"
        subnet.save(update_fields=["name_alias"])
        subnet.refresh_from_db()
        self.assertIsNotNone(subnet.matched_prefix)

    def test_aci_external_subnet_has_no_shared_rtctl_without_matched_prefix(
        self,
    ) -> None:
        """Test _has_shared_route_control_covering_prefix() no prefix."""
        subnet = ACIExternalSubnet(
            aci_external_endpoint_group=self.aci_external_endpoint_group,
        )
        self.assertFalse(subnet._has_shared_route_control_covering_prefix())  # noqa: SLF001

    def test_aci_external_subnet_shared_rtctl_covering_prefix_with_pk_excludes_self(
        self,
    ) -> None:
        """Test pk exclusion in _has_shared_route_control_covering()."""
        subnet = ACIExternalSubnet.objects.create(
            name="ACIExternalSubnetPKExcl",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            matched_prefix="10.100.0.0/24",
            shared_route_control_enabled=False,
            shared_security_enabled=False,
        )
        subnet.refresh_from_db()
        result = subnet._has_shared_route_control_covering_prefix()  # noqa: SLF001
        self.assertFalse(result)

    def test_aci_external_subnet_shared_rtctl_covering_prefix_via_sibling(
        self,
    ) -> None:
        """Test _has_shared_route_control_covering_prefix() via sibling."""
        ACIExternalSubnet.objects.create(
            name="ACIExternalSubnetParent",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            matched_prefix="10.101.0.0/16",
            shared_route_control_enabled=True,
            import_security_enabled=True,
            shared_security_enabled=True,
        )
        subnet_child = ACIExternalSubnet.objects.create(
            name="ACIExternalSubnetChild",
            aci_external_endpoint_group=self.aci_external_endpoint_group,
            matched_prefix="10.101.1.0/24",
            shared_route_control_enabled=False,
            import_security_enabled=True,
            shared_security_enabled=True,
        )
        subnet_child.refresh_from_db()
        result = subnet_child._has_shared_route_control_covering_prefix()  # noqa: SLF001
        self.assertTrue(result)
