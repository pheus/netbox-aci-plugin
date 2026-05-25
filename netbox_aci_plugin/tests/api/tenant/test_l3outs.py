# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""API tests for tenant L3Out models."""

from rest_framework import status

from core.models import ObjectType
from ipam.models import VRF, Prefix
from tenancy.models import Tenant
from users.models import ObjectPermission
from utilities.testing import APIViewTestCases

from ....api.serializers.tenant.l3outs import ACIL3OutSerializer
from ....api.urls import app_name
from ....choices import QualityOfServiceClassChoices, QualityOfServiceDSCPChoices
from ....models.access_policies.domains import ACIRoutedDomain
from ....models.fabric.fabrics import ACIFabric
from ....models.tenant.l3outs import (
    ACIExternalEndpointGroup,
    ACIExternalSubnet,
    ACIL3Out,
)
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF


class ACIL3OutAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI L3Out."""

    model = ACIL3Out
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_tenant",
        "aci_vrf",
        "description",
        "display",
        "id",
        "name",
        "url",
    ]
    user_permissions = (
        "netbox_aci_plugin.view_acifabric",
        "netbox_aci_plugin.view_acirouteddomain",
        "netbox_aci_plugin.view_acitenant",
        "netbox_aci_plugin.view_acivrf",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI L3Out for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1",
            slug="netbox-tenant-api-1",
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2",
            slug="netbox-tenant-api-2",
        )
        nb_vrf1 = VRF.objects.create(name="NetBox VRF API 1", tenant=nb_tenant1)
        nb_vrf2 = VRF.objects.create(name="NetBox VRF API 2", tenant=nb_tenant2)
        aci_fabric = ACIFabric.objects.create(
            name="ACIL3OutTestFabricAPI",
            fabric_id=120,
            infra_vlan_vid=3900,
        )
        aci_tenant1 = ACITenant.objects.create(
            name="ACIL3OutTestTenantAPI1",
            aci_fabric=aci_fabric,
        )
        aci_tenant2 = ACITenant.objects.create(
            name="ACIL3OutTestTenantAPI2",
            aci_fabric=aci_fabric,
        )
        aci_vrf1 = ACIVRF.objects.create(
            name="ACIL3OutTestVRFAPI1",
            aci_tenant=aci_tenant1,
            nb_vrf=nb_vrf1,
        )
        aci_vrf2 = ACIVRF.objects.create(
            name="ACIL3OutTestVRFAPI2",
            aci_tenant=aci_tenant2,
            nb_vrf=nb_vrf2,
        )
        aci_routed_domain1 = ACIRoutedDomain.objects.create(
            name="ACIL3OutTestRoutedDomainAPI1",
            aci_fabric=aci_fabric,
            nb_tenant=nb_tenant1,
        )
        aci_routed_domain2 = ACIRoutedDomain.objects.create(
            name="ACIL3OutTestRoutedDomainAPI2",
            aci_fabric=aci_fabric,
            nb_tenant=nb_tenant2,
        )
        l3outs: tuple = (
            ACIL3Out(
                name="ACIL3OutTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_tenant=aci_tenant1,
                aci_vrf=aci_vrf1,
                aci_routed_domain=aci_routed_domain1,
                nb_tenant=nb_tenant1,
                bfd_policy_name="BFDPolicy1",
                bgp_enabled=True,
                custom_qos_policy_name="CustomQoSPolicy1",
                egress_data_plane_policing_policy_name="EgressDPPPolicy1",
                export_route_control_enforcement_enabled=True,
                import_route_control_enforcement_enabled=True,
                ingress_data_plane_policing_policy_name="IngressDPPPolicy1",
                interleak_route_map_name="InterleakRouteMap1",
                ospf_enabled=True,
                ospf_external_policy_name="OSPFExternalPolicy1",
                target_dscp=QualityOfServiceDSCPChoices.DSCP_AF11,
            ),
            ACIL3Out(
                name="ACIL3OutTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_tenant=aci_tenant2,
                aci_vrf=aci_vrf2,
                aci_routed_domain=aci_routed_domain2,
                nb_tenant=nb_tenant2,
            ),
            ACIL3Out(
                name="ACIL3OutTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_tenant=aci_tenant1,
                aci_vrf=aci_vrf1,
                aci_routed_domain=aci_routed_domain1,
                nb_tenant=nb_tenant2,
                bgp_enabled=True,
                import_route_control_enforcement_enabled=False,
                export_route_control_enforcement_enabled=True,
                target_dscp=QualityOfServiceDSCPChoices.DSCP_AF12,
            ),
        )
        ACIL3Out.objects.bulk_create(l3outs)

        cls.create_data: list[dict] = [
            {
                "name": "ACIL3OutTestAPI4",
                "name_alias": "Testing",
                "description": "Fourth ACI Test",
                "comments": "# ACI Test 4",
                "aci_tenant": aci_tenant2.id,
                "aci_vrf": aci_vrf2.id,
                "aci_routed_domain": aci_routed_domain2.id,
                "nb_tenant": nb_tenant1.id,
                "bfd_policy_name": "BFDPolicy4",
                "bgp_enabled": True,
                "custom_qos_policy_name": "CustomQoSPolicy4",
                "egress_data_plane_policing_policy_name": "EgressDPPPolicy4",
                "eigrp_enabled": False,
                "import_route_control_enforcement_enabled": False,
                "ingress_data_plane_policing_policy_name": "IngressDPPPolicy4",
                "interleak_route_map_name": "InterleakRouteMap4",
                "l3_multicast_ipv4_enabled": False,
                "l3_multicast_ipv6_enabled": False,
                "multipod_enabled": False,
                "ospf_enabled": True,
                "ospf_external_policy_name": "OSPFExternalPolicy4",
                "target_dscp": QualityOfServiceDSCPChoices.DSCP_AF21,
            },
            {
                "name": "ACIL3OutTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_tenant": aci_tenant1.id,
                "aci_vrf": aci_vrf1.id,
                "aci_routed_domain": aci_routed_domain1.id,
                "nb_tenant": nb_tenant2.id,
                "bgp_enabled": False,
                "eigrp_enabled": True,
                "import_route_control_enforcement_enabled": False,
                "multipod_enabled": False,
                "ospf_enabled": False,
                "target_dscp": QualityOfServiceDSCPChoices.DSCP_AF22,
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }

    def test_export_route_control_enforcement_read_only(self) -> None:
        """Test export route control enforcement is read-only in the API."""
        serializer = ACIL3OutSerializer()
        self.assertTrue(
            serializer.fields["export_route_control_enforcement_enabled"].read_only
        )

    def test_export_route_control_enforcement_false_is_ignored(self) -> None:
        """Test API input cannot change export route control enforcement."""
        l3out = ACIL3Out.objects.first()
        serializer = ACIL3OutSerializer(
            l3out,
            data={"export_route_control_enforcement_enabled": False},
            partial=True,
        )
        self.assertTrue(serializer.is_valid())
        self.assertNotIn(
            "export_route_control_enforcement_enabled",
            serializer.validated_data,
        )


class ACIExternalEndpointGroupAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI External Endpoint Group."""

    model = ACIExternalEndpointGroup
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_l3out",
        "description",
        "display",
        "id",
        "name",
        "url",
    ]
    user_permissions = (
        "netbox_aci_plugin.view_acifabric",
        "netbox_aci_plugin.view_acil3out",
        "netbox_aci_plugin.view_acirouteddomain",
        "netbox_aci_plugin.view_acitenant",
        "netbox_aci_plugin.view_acivrf",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI External Endpoint Group for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1",
            slug="netbox-tenant-api-1",
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2",
            slug="netbox-tenant-api-2",
        )
        aci_fabric = ACIFabric.objects.create(
            name="ACIExternalEPGTestFabricAPI",
            fabric_id=121,
            infra_vlan_vid=3900,
        )
        aci_tenant = ACITenant.objects.create(
            name="ACIExternalEPGTestTenantAPI",
            aci_fabric=aci_fabric,
        )
        aci_vrf = ACIVRF.objects.create(
            name="ACIExternalEPGTestVRFAPI",
            aci_tenant=aci_tenant,
        )
        aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIExternalEPGTestRoutedDomainAPI",
            aci_fabric=aci_fabric,
        )
        aci_l3out1 = ACIL3Out.objects.create(
            name="ACIExternalEPGTestL3OutAPI1",
            aci_tenant=aci_tenant,
            aci_vrf=aci_vrf,
            aci_routed_domain=aci_routed_domain,
        )
        aci_l3out2 = ACIL3Out.objects.create(
            name="ACIExternalEPGTestL3OutAPI2",
            aci_tenant=aci_tenant,
            aci_vrf=aci_vrf,
            aci_routed_domain=aci_routed_domain,
        )
        external_epgs: tuple = (
            ACIExternalEndpointGroup(
                name="ACIExternalEndpointGroupTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_l3out=aci_l3out1,
                nb_tenant=nb_tenant1,
                preferred_group_member_enabled=True,
                qos_class=QualityOfServiceClassChoices.CLASS_LEVEL_1,
                target_dscp=QualityOfServiceDSCPChoices.DSCP_AF11,
            ),
            ACIExternalEndpointGroup(
                name="ACIExternalEndpointGroupTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_l3out=aci_l3out1,
                nb_tenant=nb_tenant2,
            ),
            ACIExternalEndpointGroup(
                name="ACIExternalEndpointGroupTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_l3out=aci_l3out2,
                nb_tenant=nb_tenant2,
                preferred_group_member_enabled=False,
                qos_class=QualityOfServiceClassChoices.CLASS_LEVEL_2,
                target_dscp=QualityOfServiceDSCPChoices.DSCP_AF12,
            ),
        )
        ACIExternalEndpointGroup.objects.bulk_create(external_epgs)

        cls.create_data: list[dict] = [
            {
                "name": "ACIExternalEndpointGroupTestAPI4",
                "name_alias": "Testing",
                "description": "Fourth ACI Test",
                "comments": "# ACI Test 4",
                "aci_l3out": aci_l3out2.id,
                "nb_tenant": nb_tenant1.id,
                "preferred_group_member_enabled": True,
                "qos_class": QualityOfServiceClassChoices.CLASS_LEVEL_3,
                "target_dscp": QualityOfServiceDSCPChoices.DSCP_AF21,
            },
            {
                "name": "ACIExternalEndpointGroupTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_l3out": aci_l3out2.id,
                "nb_tenant": nb_tenant2.id,
                "preferred_group_member_enabled": False,
                "qos_class": QualityOfServiceClassChoices.CLASS_LEVEL_4,
                "target_dscp": QualityOfServiceDSCPChoices.DSCP_AF22,
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIExternalSubnetAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI External Subnet."""

    model = ACIExternalSubnet
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_external_endpoint_group",
        "description",
        "display",
        "id",
        "matched_prefix",
        "name",
        "url",
    ]
    user_permissions = (
        "ipam.view_prefix",
        "netbox_aci_plugin.view_aciexternalendpointgroup",
        "netbox_aci_plugin.view_acifabric",
        "netbox_aci_plugin.view_acil3out",
        "netbox_aci_plugin.view_acirouteddomain",
        "netbox_aci_plugin.view_acitenant",
        "netbox_aci_plugin.view_acivrf",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI External Subnet for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1",
            slug="netbox-tenant-api-1",
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2",
            slug="netbox-tenant-api-2",
        )
        nb_vrf = VRF.objects.create(name="NetBox VRF API", tenant=nb_tenant1)
        aci_fabric = ACIFabric.objects.create(
            name="ACIExternalSubnetTestFabricAPI",
            fabric_id=122,
            infra_vlan_vid=3900,
        )
        aci_tenant = ACITenant.objects.create(
            name="ACIExternalSubnetTestTenantAPI",
            aci_fabric=aci_fabric,
        )
        aci_vrf = ACIVRF.objects.create(
            name="ACIExternalSubnetTestVRFAPI",
            aci_tenant=aci_tenant,
            nb_vrf=nb_vrf,
        )
        aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIExternalSubnetTestRoutedDomainAPI",
            aci_fabric=aci_fabric,
        )
        aci_l3out = ACIL3Out.objects.create(
            name="ACIExternalSubnetTestL3OutAPI",
            aci_tenant=aci_tenant,
            aci_vrf=aci_vrf,
            aci_routed_domain=aci_routed_domain,
            bgp_enabled=True,
            import_route_control_enforcement_enabled=True,
        )
        external_epg1 = ACIExternalEndpointGroup.objects.create(
            name="ACIExternalSubnetTestExternalEPGAPI1",
            aci_l3out=aci_l3out,
        )
        external_epg2 = ACIExternalEndpointGroup.objects.create(
            name="ACIExternalSubnetTestExternalEPGAPI2",
            aci_l3out=aci_l3out,
        )
        prefix1 = Prefix.objects.create(prefix="10.10.0.0/24", vrf=nb_vrf)
        prefix2 = Prefix.objects.create(prefix="10.10.1.0/24", vrf=nb_vrf)
        prefix3 = Prefix.objects.create(prefix="10.10.2.0/24", vrf=nb_vrf)
        prefix4 = Prefix.objects.create(prefix="10.10.3.0/24", vrf=nb_vrf)
        prefix5 = Prefix.objects.create(prefix="10.10.4.0/24", vrf=nb_vrf)
        external_subnets: tuple = (
            ACIExternalSubnet(
                name="ACIExternalSubnetTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                comments="# ACI Test 1",
                aci_external_endpoint_group=external_epg1,
                nb_prefix=prefix1,
                matched_prefix=prefix1.prefix,
                nb_tenant=nb_tenant1,
                export_route_control_enabled=True,
                import_route_control_enabled=True,
                import_security_enabled=True,
                bgp_route_summarization_enabled=True,
                bgp_route_summarization_policy_name="BGPSummaryPolicy1",
            ),
            ACIExternalSubnet(
                name="ACIExternalSubnetTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                comments="# ACI Test 2",
                aci_external_endpoint_group=external_epg1,
                nb_prefix=prefix2,
                matched_prefix=prefix2.prefix,
                nb_tenant=nb_tenant2,
            ),
            ACIExternalSubnet(
                name="ACIExternalSubnetTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                comments="# ACI Test 3",
                aci_external_endpoint_group=external_epg2,
                nb_prefix=prefix3,
                matched_prefix=prefix3.prefix,
                nb_tenant=nb_tenant2,
                export_route_control_enabled=True,
                import_security_enabled=True,
                shared_route_control_enabled=True,
                shared_security_enabled=True,
            ),
        )
        ACIExternalSubnet.objects.bulk_create(external_subnets)

        cls.create_data: list[dict] = [
            {
                "name": "ACIExternalSubnetTestAPI4",
                "name_alias": "Testing",
                "description": "Fourth ACI Test",
                "comments": "# ACI Test 4",
                "aci_external_endpoint_group": external_epg2.id,
                "nb_prefix": prefix4.id,
                "nb_tenant": nb_tenant1.id,
                "bgp_route_summarization_enabled": False,
                "bgp_route_summarization_policy_name": "",
                "eigrp_route_summarization_enabled": False,
                "export_route_control_enabled": True,
                "import_route_control_enabled": True,
                "import_security_enabled": True,
                "ospf_route_summarization_enabled": False,
                "ospf_route_summarization_policy_name": "",
                "shared_route_control_enabled": False,
                "shared_security_enabled": False,
            },
            {
                "name": "ACIExternalSubnetTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "comments": "# ACI Test 5",
                "aci_external_endpoint_group": external_epg2.id,
                "nb_prefix": prefix5.id,
                "nb_tenant": nb_tenant2.id,
                "bgp_route_summarization_enabled": False,
                "bgp_route_summarization_policy_name": "",
                "eigrp_route_summarization_enabled": False,
                "export_route_control_enabled": True,
                "import_security_enabled": True,
                "ospf_route_summarization_enabled": False,
                "ospf_route_summarization_policy_name": "",
                "shared_route_control_enabled": True,
                "shared_security_enabled": True,
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ACIExternalSubnetSerializerValidationTestCase(ACIExternalSubnetAPIViewTestCase):
    """Test ACIExternalSubnetSerializer.validate() error paths."""

    def test_mismatched_matched_prefix_and_nb_prefix_returns_400(self) -> None:
        """Test supplying matched_prefix differing from nb_prefix raises."""
        obj_perm = ObjectPermission(name="Test serializer perm add", actions=["add"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(ACIExternalSubnet))

        epg = ACIExternalEndpointGroup.objects.first()
        prefix = Prefix.objects.filter(prefix="10.10.0.0/24").first()
        url = self._get_list_url()
        response = self.client.post(
            url,
            {
                "name": "SubnetMismatch",
                "aci_external_endpoint_group": epg.pk,
                "nb_prefix": prefix.pk,
                "matched_prefix": "10.99.99.0/24",
            },
            format="json",
            **self.header,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("matched_prefix", response.data)

    def test_no_nb_prefix_and_no_matched_prefix_returns_400(self) -> None:
        """Test that omitting both nb_prefix and matched_prefix raises."""
        obj_perm = ObjectPermission(name="Test serializer perm add2", actions=["add"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(ACIExternalSubnet))

        epg = ACIExternalEndpointGroup.objects.first()
        url = self._get_list_url()
        response = self.client.post(
            url,
            {
                "name": "SubnetNoPrefix",
                "aci_external_endpoint_group": epg.pk,
            },
            format="json",
            **self.header,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("matched_prefix", response.data)

    def test_matched_prefix_equal_to_nb_prefix_on_patch_returns_200(self) -> None:
        """Re-saving with matched_prefix equal to nb_prefix.prefix must pass.

        Regression: when editing an existing subnet whose matched_prefix was
        auto-synced from nb_prefix, the client may PATCH the same values back.
        The serializer must not reject when matched_prefix == nb_prefix.prefix.
        """
        obj_perm = ObjectPermission(
            name="Test serializer perm change", actions=["change"]
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(ACIExternalSubnet))

        subnet = ACIExternalSubnet.objects.filter(
            name="ACIExternalSubnetTestAPI1",
        ).first()
        url = self._get_detail_url(subnet)
        response = self.client.patch(
            url,
            {
                "nb_prefix": subnet.nb_prefix.pk,
                "matched_prefix": str(subnet.nb_prefix.prefix),
            },
            format="json",
            **self.header,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
