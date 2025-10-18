# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.test import TestCase
from ipam.models import VRF
from tenancy.models import Tenant

from ...models.fabric.fabrics import ACIFabric
from ...models.fabric.pods import ACIPod
from ...models.tenant.app_profiles import ACIAppProfile
from ...models.tenant.bridge_domains import ACIBridgeDomain
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF


class ACIBaseFormTestCase(TestCase):
    """Base test case for netbox_aci_plugin forms."""

    name_error_message: str = "Only alphanumeric characters, periods, underscores, colons and hyphens are allowed."
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

    @classmethod
    def setUp(cls):
        """Set up required objects for form tests."""
        # Create NetBox objects
        cls.nb_tenant = Tenant.objects.create(
            name="NetBoxBaseFormTestTenant",
        )
        cls.nb_vrf = VRF.objects.create(
            name="NetBoxBaseFormTestVRF",
            tenant=cls.nb_tenant,
        )

        # Create ACIFabric objects
        cls.aci_fabric = ACIFabric.objects.create(
            name="ACIBaseFormTestFabric",
            fabric_id=101,
            infra_vlan_vid=3900,
        )
        cls.aci_pod = ACIPod.objects.create(
            name="ACIBaseFormTestPod",
            aci_fabric=cls.aci_fabric,
            pod_id=101,
        )

        # Create ACITenant objects
        cls.aci_tenant = ACITenant.objects.create(
            name="ACIBaseFormTestTenant",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_vrf = ACIVRF.objects.create(
            name="ACIBaseFormTestVRF",
            aci_tenant=cls.aci_tenant,
        )
        cls.aci_bd = ACIBridgeDomain.objects.create(
            name="ACIBaseFormTestBridgeDomain",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
        )
        cls.aci_app_profile = ACIAppProfile.objects.create(
            name="ACIBaseFormTestAppProfile",
            aci_tenant=cls.aci_tenant,
        )
