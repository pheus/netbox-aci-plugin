# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dcim.models import MACAddress
from django.test import TestCase
from ipam.models import VRF, IPAddress, Prefix
from tenancy.models import Tenant

from ...models.fabric.fabrics import ACIFabric
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

        # ACI Tenant object configurations
        cls.aci_tenant_name = "ACIBaseTestTenant"
        cls.aci_app_profile_name = "ACIBaseTestAppProfile"
        cls.aci_vrf_name = "ACIBaseTestVRF"
        cls.aci_bd_name = "ACIBaseTestBD"

        # NetBox Tenant configuration
        cls.nb_tenant_name = "NetBoxTestTenant"
        cls.nb_vrf_name = "NetBoxTestVRF"

        # Create NetBox objects
        cls.nb_tenant = Tenant.objects.create(name=cls.nb_tenant_name)
        cls.nb_vrf = VRF.objects.create(name=cls.nb_vrf_name, tenant=cls.nb_tenant)
        cls.ip_address1 = IPAddress.objects.create(address="192.168.1.1/24")
        cls.ip_address2 = IPAddress.objects.create(address="192.168.1.2/24")
        cls.mac_address1 = MACAddress.objects.create(mac_address="00:00:00:00:00:01")
        cls.mac_address2 = MACAddress.objects.create(mac_address="00:00:00:00:00:02")
        cls.prefix1 = Prefix.objects.create(prefix="192.168.1.0/24")
        cls.prefix2 = Prefix.objects.create(prefix="192.168.2.0/24")

        # Create ACIFabric object
        cls.aci_fabric = ACIFabric.objects.create(
            name=cls.aci_fabric_name,
            fabric_id=cls.aci_fabric_id,
            infra_vlan_vid=cls.aci_fabric_infra_vlan_vid,
        )

        # Create ACITenant objects
        cls.aci_tenant = ACITenant.objects.create(
            name=cls.aci_tenant_name,
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
