# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.models import Device, DeviceRole, DeviceType, MACAddress, Manufacturer, Site
from django.test import TestCase
from ipam.models import VRF, IPAddress, Prefix
from tenancy.models import Tenant

from ...choices import NodeRoleChoices
from ...models.fabric.fabrics import ACIFabric
from ...models.fabric.nodes import ACINode
from ...models.fabric.pods import ACIPod
from ...models.tenant.app_profiles import ACIAppProfile
from ...models.tenant.bridge_domains import ACIBridgeDomain
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF


class ACIBaseTestCase(TestCase):
    """Base test case for netbox_aci_plugin models."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for netbox_aci_plugin models."""
        # ACI Fabric configuration
        cls.aci_fabric_name = "ACIBaseTestFabric"
        cls.aci_fabric_id = 127
        cls.aci_fabric_infra_vlan_vid = 3900
        cls.aci_fabric_gipo_pool_prefix = "225.0.0.0/15"

        # ACI Pod configuration
        cls.aci_pod_name = "ACIBaseTestPod"
        cls.aci_pod_id = 1
        cls.aci_pod_tep_pool_prefix = "10.0.0.0/19"

        # ACI Node configuration
        cls.aci_node_name = "ACIBaseTestNode"
        cls.aci_node_id = 101
        cls.aci_node_role = NodeRoleChoices.ROLE_LEAF
        cls.aci_node_tep_ip_str = "10.0.0.1/19"

        # ACI Tenant object configurations
        cls.aci_tenant_name = "ACIBaseTestTenant"
        cls.aci_app_profile_name = "ACIBaseTestAppProfile"
        cls.aci_vrf_name = "ACIBaseTestVRF"
        cls.aci_bd_name = "ACIBaseTestBD"

        # NetBox configuration
        cls.nb_tenant_name = "NetBoxTestTenant"
        cls.site_name = "NetBoxBaseTestSite"
        cls.manufacturer_name = "NetBox"
        cls.device_role_name = "BaseTest-DeviceRole1"
        cls.device_type_name = "BaseTestDevice1"
        cls.nb_vrf_name = "NetBoxTestVRF"

        # Create NetBox objects
        cls.nb_tenant = Tenant.objects.create(
            name=cls.nb_tenant_name, slug=cls.nb_tenant_name.lower()
        )
        cls.site = Site.objects.create(name=cls.site_name, slug=cls.site_name.lower())
        cls.manufacturer = Manufacturer.objects.create(
            name=cls.manufacturer_name, slug=cls.manufacturer_name.lower()
        )
        cls.device_type1 = DeviceType.objects.create(
            manufacturer=cls.manufacturer,
            model=cls.device_type_name,
            slug=cls.device_type_name.lower(),
        )
        cls.device_role1 = DeviceRole.objects.create(
            name=cls.device_role_name, slug=cls.device_role_name.lower()
        )
        cls.nb_vrf = VRF.objects.create(name=cls.nb_vrf_name, tenant=cls.nb_tenant)
        cls.ip_address1 = IPAddress(address="192.168.1.1/24")
        cls.ip_address1.full_clean()
        cls.ip_address1.save()
        cls.ip_address2 = IPAddress(address="192.168.1.2/24")
        cls.ip_address2.full_clean()
        cls.ip_address2.save()
        cls.mac_address1 = MACAddress.objects.create(mac_address="00:00:00:00:00:01")
        cls.mac_address2 = MACAddress.objects.create(mac_address="00:00:00:00:00:02")
        cls.prefix1 = Prefix(prefix="192.168.1.0/24")
        cls.prefix1.full_clean()
        cls.prefix1.save()
        cls.prefix2 = Prefix(prefix="192.168.2.0/24")
        cls.prefix2.full_clean()
        cls.prefix2.save()

        # Create ACIFabric object
        cls.aci_gipo_pool = Prefix(prefix=cls.aci_fabric_gipo_pool_prefix)
        cls.aci_gipo_pool.full_clean()
        cls.aci_gipo_pool.save()
        cls.aci_fabric = ACIFabric.objects.create(
            name=cls.aci_fabric_name,
            fabric_id=cls.aci_fabric_id,
            infra_vlan_vid=cls.aci_fabric_infra_vlan_vid,
            gipo_pool=cls.aci_gipo_pool,
        )
        # Create ACIPod object
        cls.aci_pod_tep_pool = Prefix(prefix=cls.aci_pod_tep_pool_prefix)
        cls.aci_pod_tep_pool.full_clean()
        cls.aci_pod_tep_pool.save()
        cls.aci_pod = ACIPod.objects.create(
            name=cls.aci_pod_name,
            aci_fabric=cls.aci_fabric,
            pod_id=cls.aci_pod_id,
            tep_pool=cls.aci_pod_tep_pool,
            scope=cls.site,
        )
        # Create ACINode object
        cls.aci_node_object1 = Device.objects.create(
            name=cls.aci_node_name,
            device_type=cls.device_type1,
            role=cls.device_role1,
            site=cls.site,
        )
        cls.aci_node_tep_ip_address = IPAddress.objects.create(
            address=cls.aci_node_tep_ip_str
        )
        cls.aci_node = ACINode.objects.create(
            name=cls.aci_node_name,
            aci_pod=cls.aci_pod,
            node_id=cls.aci_node_id,
            node_object=cls.aci_node_object1,
            role=cls.aci_node_role,
            tep_ip_address=cls.aci_node_tep_ip_address,
        )

        # Create ACITenant objects
        cls.aci_tenant = ACITenant.objects.create(
            name=cls.aci_tenant_name,
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_app_profile = ACIAppProfile.objects.create(
            name=cls.aci_app_profile_name,
            aci_tenant=cls.aci_tenant,
        )
        cls.aci_vrf = ACIVRF.objects.create(
            name=cls.aci_vrf_name,
            aci_tenant=cls.aci_tenant,
            nb_vrf=cls.nb_vrf,
        )
        cls.aci_bd = ACIBridgeDomain.objects.create(
            name=cls.aci_bd_name,
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
        )
