# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from tenancy.models import Tenant
from utilities.testing import ModelViewTestCase

from ...models.fabric.fabrics import ACIFabric
from ...models.tenant.app_profiles import ACIAppProfile
from ...models.tenant.bridge_domains import ACIBridgeDomain
from ...models.tenant.tenants import ACITenant
from ...models.tenant.vrfs import ACIVRF


class ACIModelViewTestCase(ModelViewTestCase):
    """Plugin base for ``ViewTestCases.*`` mixins.

    Prefixes the URL namespace with ``plugins:`` (NetBox's default
    omits this) and seeds the shared fabric / tenant / VRF / BD chain
    that downstream model fixtures depend on.
    """

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(
            self.model._meta.app_label,
            self.model._meta.model_name,
        )

    @classmethod
    def setUpTestData(cls) -> None:
        cls.nb_tenant = Tenant.objects.create(
            name="ACIBaseViewTestNBTenant",
            slug="acibaseviewtestnbtenant",
        )
        cls.aci_fabric = ACIFabric.objects.create(
            name="ACIBaseViewTestFabric",
            fabric_id=150,
            infra_vlan_vid=3900,
        )
        cls.aci_tenant = ACITenant.objects.create(
            name="ACIBaseViewTestTenant",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_vrf = ACIVRF.objects.create(
            name="ACIBaseViewTestVRF",
            aci_tenant=cls.aci_tenant,
        )
        cls.aci_bd = ACIBridgeDomain.objects.create(
            name="ACIBaseViewTestBD",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
        )
        cls.aci_app_profile = ACIAppProfile.objects.create(
            name="ACIBaseViewTestAppProfile",
            aci_tenant=cls.aci_tenant,
        )
