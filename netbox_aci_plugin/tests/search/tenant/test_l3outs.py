# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Search index tests for tenant L3Out models."""

from django.contrib.contenttypes.models import ContentType

from extras.models import CachedValue
from netbox.search.backends import search_backend

from ....models.access_policies.domains import ACIRoutedDomain
from ....models.tenant.l3outs import (
    ACIExternalEndpointGroup,
    ACIExternalSubnet,
    ACIL3Out,
)
from ....search import (
    ACIExternalEndpointGroupIndex,
    ACIExternalSubnetIndex,
)
from ...models.base import ACIBaseTestCase


class ACIExternalSubnetSearchIndexTestCase(ACIBaseTestCase):
    """Search index tests for ACIExternalSubnet.matched_prefix."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create an external subnet hierarchy with known matched prefixes."""
        super().setUpTestData()
        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACISearchTestRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_l3out = ACIL3Out.objects.create(
            name="ACISearchTestL3Out",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.aci_epg = ACIExternalEndpointGroup.objects.create(
            name="ACISearchTestExternalEPG",
            aci_l3out=cls.aci_l3out,
        )
        cls.subnet = ACIExternalSubnet.objects.create(
            name="ACISearchTestSubnet",
            aci_external_endpoint_group=cls.aci_epg,
            matched_prefix="10.200.0.0/24",
        )
        cls.subnet_b = ACIExternalSubnet.objects.create(
            name="ACISearchTestSubnetB",
            aci_external_endpoint_group=cls.aci_epg,
            matched_prefix="10.201.0.0/24",
        )

    def test_matched_prefix_cached_as_string(self) -> None:
        """Test matched_prefix (IPNetworkField) caches as its string form."""
        search_backend.cache(self.subnet)
        weight = dict(ACIExternalSubnetIndex.fields)["matched_prefix"]
        content_type = ContentType.objects.get_for_model(ACIExternalSubnet)
        self.assertTrue(
            CachedValue.objects.filter(
                object_type=content_type,
                object_id=self.subnet.pk,
                field="matched_prefix",
                value="10.200.0.0/24",
                weight=weight,
            ).exists()
        )

    def test_search_finds_subnet_by_matched_prefix_substring(self) -> None:
        """Test global search matches a matched_prefix substring."""
        search_backend.cache(ACIExternalSubnet.objects.all())
        results = search_backend.search("10.200")
        found = [result.object for result in results]
        self.assertIn(self.subnet, found)
        self.assertNotIn(self.subnet_b, found)


class ACIExternalEndpointGroupSearchIndexTestCase(ACIBaseTestCase):
    """Search index tests for ACIExternalEndpointGroup display attrs."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create an external EPG under a known tenant and VRF."""
        super().setUpTestData()
        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIEPGSearchRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_l3out = ACIL3Out.objects.create(
            name="ACIEPGSearchL3Out",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.aci_epg = ACIExternalEndpointGroup.objects.create(
            name="ACIEPGSearchExternalEPG",
            aci_l3out=cls.aci_l3out,
        )

    def test_display_attrs_resolve_tenant_and_vrf(self) -> None:
        """Test ExtEPG search exposes the parent tenant and VRF."""
        self.assertIn("aci_tenant", ACIExternalEndpointGroupIndex.display_attrs)
        self.assertIn("aci_vrf", ACIExternalEndpointGroupIndex.display_attrs)
        self.assertEqual(self.aci_epg.aci_tenant, self.aci_tenant)
        self.assertEqual(self.aci_epg.aci_vrf, self.aci_vrf)
