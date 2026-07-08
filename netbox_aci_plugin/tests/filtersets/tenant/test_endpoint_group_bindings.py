# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for tenant Endpoint Group Domain Binding models."""

from utilities.testing import ChangeLoggedFilterSetTests

from ....choices import DeploymentImmediacyChoices, ResolutionImmediacyChoices
from ....filtersets.tenant.endpoint_group_bindings import (
    ACIEndpointGroupDomainBindingFilterSet,
)
from ....models.access_policies.domains import ACIPhysicalDomain
from ....models.tenant.endpoint_group_bindings import (
    ACIEndpointGroupDomainBinding,
)
from ....models.tenant.endpoint_groups import ACIEndpointGroup, ACIUSegEndpointGroup
from ...models.base import ACIBaseTestCase


class ACIEndpointGroupDomainBindingFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTests
):
    """Test case for ACIEndpointGroupDomainBindingFilterSet."""

    queryset = ACIEndpointGroupDomainBinding.objects.all()
    filterset = ACIEndpointGroupDomainBindingFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEndpointGroupDomainBindingFilterSet."""
        super().setUpTestData()
        cls.aci_epg_a = ACIEndpointGroup.objects.create(
            name="EPGDBFSTestA",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_epg_b = ACIEndpointGroup.objects.create(
            name="EPGDBFSTestB",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_useg_epg_a = ACIUSegEndpointGroup.objects.create(
            name="USegEPGDBFSTestA",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.physical_domain_a = ACIPhysicalDomain.objects.create(
            name="PhysDomDBFSTestA",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool1,
        )
        cls.physical_domain_b = ACIPhysicalDomain.objects.create(
            name="PhysDomDBFSTestB",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool2,
        )
        cls.binding_1 = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg_a,
            aci_domain_object=cls.physical_domain_a,
            deployment_immediacy=DeploymentImmediacyChoices.IMMEDIACY_IMMEDIATE,
            resolution_immediacy=ResolutionImmediacyChoices.IMMEDIACY_PRE_PROVISION,
        )
        cls.binding_2 = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg_b,
            aci_domain_object=cls.physical_domain_b,
        )
        cls.binding_3 = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_useg_epg_a,
            aci_domain_object=cls.physical_domain_b,
        )

    def test_q(self) -> None:
        """Test search() by the related ACI Endpoint Group name."""
        params = {"q": "EPGDBFSTestA"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_q_useg_endpoint_group_name(self) -> None:
        """Test search() by the related ACI uSeg Endpoint Group name."""
        params = {"q": "USegEPGDBFSTestA"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_3, qs)
        self.assertNotIn(self.binding_1, qs)

    def test_q_physical_domain_name(self) -> None:
        """Test search() by the related ACI Physical Domain name."""
        params = {"q": "PhysDomDBFSTestB"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_2, qs)
        self.assertIn(self.binding_3, qs)
        self.assertNotIn(self.binding_1, qs)

    def test_aci_fabric(self) -> None:
        """Test filtering bindings by ACI Fabric name."""
        params = {"aci_fabric": [self.aci_fabric.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertIn(self.binding_2, qs)
        self.assertIn(self.binding_3, qs)

    def test_aci_fabric_id(self) -> None:
        """Test filtering bindings by ACI Fabric ID."""
        params = {"aci_fabric_id": [self.aci_fabric.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertIn(self.binding_2, qs)
        self.assertIn(self.binding_3, qs)

    def test_aci_epg_object_type(self) -> None:
        """Test filtering bindings by the ACI EPG object type."""
        params = {"aci_epg_object_type": "netbox_aci_plugin.aciendpointgroup"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertIn(self.binding_2, qs)
        self.assertNotIn(self.binding_3, qs)

    def test_aci_epg_object_id(self) -> None:
        """Test filtering bindings by the ACI EPG object ID."""
        params = {"aci_epg_object_id": [self.aci_epg_a.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_aci_domain_object_type(self) -> None:
        """Test filtering bindings by the ACI domain object type."""
        params = {"aci_domain_object_type": "netbox_aci_plugin.aciphysicaldomain"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertIn(self.binding_2, qs)
        self.assertIn(self.binding_3, qs)

    def test_aci_domain_object_id(self) -> None:
        """Test filtering bindings by the ACI domain object ID."""
        params = {"aci_domain_object_id": [self.physical_domain_a.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_aci_endpoint_group(self) -> None:
        """Test filtering bindings by the cached ACI Endpoint Group name."""
        params = {"aci_endpoint_group": [self.aci_epg_a.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)
        self.assertNotIn(self.binding_3, qs)

    def test_aci_endpoint_group_id(self) -> None:
        """Test filtering bindings by the cached ACI Endpoint Group ID."""
        params = {"aci_endpoint_group_id": [self.aci_epg_a.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_aci_useg_endpoint_group(self) -> None:
        """Test filtering bindings by cached ACI uSeg Endpoint Group name."""
        params = {"aci_useg_endpoint_group": [self.aci_useg_epg_a.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_3, qs)
        self.assertNotIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_aci_useg_endpoint_group_id(self) -> None:
        """Test filtering bindings by the cached ACI uSeg Endpoint Group ID."""
        params = {"aci_useg_endpoint_group_id": [self.aci_useg_epg_a.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_3, qs)
        self.assertNotIn(self.binding_1, qs)

    def test_aci_physical_domain(self) -> None:
        """Test filtering bindings by the cached ACI Physical Domain name."""
        params = {"aci_physical_domain": [self.physical_domain_b.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_2, qs)
        self.assertIn(self.binding_3, qs)
        self.assertNotIn(self.binding_1, qs)

    def test_aci_physical_domain_id(self) -> None:
        """Test filtering bindings by the cached ACI Physical Domain ID."""
        params = {"aci_physical_domain_id": [self.physical_domain_b.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_2, qs)
        self.assertIn(self.binding_3, qs)
        self.assertNotIn(self.binding_1, qs)

    def test_deployment_immediacy(self) -> None:
        """Test filtering bindings by deployment immediacy."""
        params = {
            "deployment_immediacy": [DeploymentImmediacyChoices.IMMEDIACY_IMMEDIATE]
        }
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_resolution_immediacy(self) -> None:
        """Test filtering bindings by resolution immediacy."""
        params = {
            "resolution_immediacy": [ResolutionImmediacyChoices.IMMEDIACY_PRE_PROVISION]
        }
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())
