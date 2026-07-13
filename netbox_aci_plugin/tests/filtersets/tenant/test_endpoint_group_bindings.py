# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for tenant Endpoint Group Domain and AAEP Binding models."""

from ipam.models import VLAN
from utilities.testing import ChangeLoggedFilterSetTests

from ....choices import (
    DeploymentImmediacyChoices,
    PortModeChoices,
    ResolutionImmediacyChoices,
)
from ....filtersets.tenant.endpoint_group_bindings import (
    ACIEndpointGroupAAEPBindingFilterSet,
    ACIEndpointGroupDomainBindingFilterSet,
)
from ....models.access_policies.aaep import (
    ACIAAEPDomainBinding,
    ACIAttachableAccessEntityProfile,
)
from ....models.access_policies.domains import ACIPhysicalDomain
from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.bridge_domains import ACIBridgeDomain
from ....models.tenant.endpoint_group_bindings import (
    ACIEndpointGroupAAEPBinding,
    ACIEndpointGroupDomainBinding,
)
from ....models.tenant.endpoint_groups import ACIEndpointGroup, ACIUSegEndpointGroup
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF
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


class ACIEndpointGroupAAEPBindingFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTests
):
    """Test case for ACIEndpointGroupAAEPBindingFilterSet."""

    queryset = ACIEndpointGroupAAEPBinding.objects.all()
    filterset = ACIEndpointGroupAAEPBindingFilterSet
    # Primary VLAN scalars the filterset does not expose.
    ignore_fields = (
        "primary_encap_vlan_id",
        "primary_nb_vlan",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEndpointGroupAAEPBindingFilterSet."""
        super().setUpTestData()
        cls.aci_epg_a = ACIEndpointGroup.objects.create(
            name="EPGABFSTestA",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_epg_b = ACIEndpointGroup.objects.create(
            name="EPGABFSTestB",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.physical_domain = ACIPhysicalDomain.objects.create(
            name="PhysDomABFSTest",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool1,
        )
        cls.epg_domain_binding_a = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg_a,
            aci_domain_object=cls.physical_domain,
        )
        cls.epg_domain_binding_b = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg_b,
            aci_domain_object=cls.physical_domain,
        )
        cls.aci_aaep_a = ACIAttachableAccessEntityProfile.objects.create(
            name="AAEPABFSTestA",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_aaep_b = ACIAttachableAccessEntityProfile.objects.create(
            name="AAEPABFSTestB",
            aci_fabric=cls.aci_fabric,
        )
        ACIAAEPDomainBinding.objects.create(
            aci_aaep=cls.aci_aaep_a, aci_domain_object=cls.physical_domain
        )
        ACIAAEPDomainBinding.objects.create(
            aci_aaep=cls.aci_aaep_b, aci_domain_object=cls.physical_domain
        )
        cls.nb_vlan = VLAN.objects.create(vid=150, name="VLANABFSTest")
        cls.binding_1 = ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=cls.aci_epg_a,
            aci_aaep=cls.aci_aaep_a,
            nb_vlan=cls.nb_vlan,
            deployment_immediacy=DeploymentImmediacyChoices.IMMEDIACY_IMMEDIATE,
        )
        cls.binding_2 = ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=cls.aci_epg_b,
            aci_aaep=cls.aci_aaep_b,
            encap_vlan_id=180,
            mode=PortModeChoices.MODE_NATIVE,
        )
        cls.binding_3 = ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=cls.aci_epg_a,
            aci_aaep=cls.aci_aaep_b,
            encap_vlan_id=250,
        )

        # Cross-tenant fixtures: a second ACITenant sharing the same ACI
        # Fabric, giving the aci_tenant/aci_app_profile filters a genuine
        # negative case.
        cls.aci_tenant_other = ACITenant.objects.create(
            name="TenantABFSTestOther",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_vrf_other = ACIVRF.objects.create(
            name="VRFABFSTestOther",
            aci_tenant=cls.aci_tenant_other,
        )
        cls.aci_bd_other = ACIBridgeDomain.objects.create(
            name="BDABFSTestOther",
            aci_tenant=cls.aci_tenant_other,
            aci_vrf=cls.aci_vrf_other,
        )
        cls.aci_app_profile_other = ACIAppProfile.objects.create(
            name="APABFSTestOther",
            aci_tenant=cls.aci_tenant_other,
        )
        cls.aci_epg_other = ACIEndpointGroup.objects.create(
            name="EPGABFSTestOther",
            aci_app_profile=cls.aci_app_profile_other,
            aci_bridge_domain=cls.aci_bd_other,
        )
        cls.epg_domain_binding_other = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg_other,
            aci_domain_object=cls.physical_domain,
        )
        cls.binding_other_tenant = ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=cls.aci_epg_other,
            aci_aaep=cls.aci_aaep_a,
            encap_vlan_id=190,
        )

    def test_q(self) -> None:
        """Test search() by the related ACI AAEP name."""
        params = {"q": "AAEPABFSTestA"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_q_endpoint_group_name(self) -> None:
        """Test search() by the related ACI Endpoint Group name."""
        params = {"q": "EPGABFSTestA"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

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

    def test_aci_tenant(self) -> None:
        """Test filtering bindings by ACI Tenant name."""
        params = {"aci_tenant": [self.aci_tenant.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertIn(self.binding_2, qs)
        self.assertIn(self.binding_3, qs)
        self.assertNotIn(self.binding_other_tenant, qs)

    def test_aci_tenant_id(self) -> None:
        """Test filtering bindings by ACI Tenant ID."""
        params = {"aci_tenant_id": [self.aci_tenant.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertIn(self.binding_2, qs)
        self.assertIn(self.binding_3, qs)
        self.assertNotIn(self.binding_other_tenant, qs)

    def test_aci_app_profile(self) -> None:
        """Test filtering bindings by ACI Application Profile name."""
        params = {"aci_app_profile": [self.aci_app_profile.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertIn(self.binding_2, qs)
        self.assertIn(self.binding_3, qs)
        self.assertNotIn(self.binding_other_tenant, qs)

    def test_aci_app_profile_id(self) -> None:
        """Test filtering bindings by ACI Application Profile ID."""
        params = {"aci_app_profile_id": [self.aci_app_profile.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertIn(self.binding_2, qs)
        self.assertIn(self.binding_3, qs)
        self.assertNotIn(self.binding_other_tenant, qs)

    def test_aci_endpoint_group(self) -> None:
        """Test filtering bindings by the ACI Endpoint Group name."""
        params = {"aci_endpoint_group": [self.aci_epg_a.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_aci_endpoint_group_id(self) -> None:
        """Test filtering bindings by the ACI Endpoint Group ID."""
        params = {"aci_endpoint_group_id": [self.aci_epg_a.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_aci_aaep(self) -> None:
        """Test filtering bindings by ACI AAEP name."""
        params = {"aci_aaep": [self.aci_aaep_a.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_aci_aaep_id(self) -> None:
        """Test filtering bindings by ACI AAEP ID."""
        params = {"aci_aaep_id": [self.aci_aaep_a.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_nb_vlan(self) -> None:
        """Test filtering bindings by the NetBox VLAN's VID."""
        params = {"nb_vlan": [self.nb_vlan.vid]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_nb_vlan_id(self) -> None:
        """Test filtering bindings by the NetBox VLAN's ID."""
        params = {"nb_vlan_id": [self.nb_vlan.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_mode(self) -> None:
        """Test filtering bindings by mode."""
        params = {"mode": [PortModeChoices.MODE_NATIVE]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_2, qs)
        self.assertNotIn(self.binding_1, qs)

    def test_deployment_immediacy(self) -> None:
        """Test filtering bindings by deployment immediacy."""
        params = {
            "deployment_immediacy": [DeploymentImmediacyChoices.IMMEDIACY_IMMEDIATE]
        }
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_encap_vlan_id(self) -> None:
        """Test filtering bindings by the stored encap VLAN ID."""
        params = {"encap_vlan_id": [150]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_effective_encap_vlan_id_live_vid(self) -> None:
        """Test effective_encap_vlan_id matches the live NetBox VLAN's vid."""
        params = {"effective_encap_vlan_id": 150}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_1, qs)
        self.assertNotIn(self.binding_2, qs)

    def test_effective_encap_vlan_id_snapshot(self) -> None:
        """Test effective_encap_vlan_id matches a snapshot-only encap ID."""
        params = {"effective_encap_vlan_id": 180}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.binding_2, qs)
        self.assertNotIn(self.binding_1, qs)

    def test_effective_encap_vlan_id_live_wins_over_stale_snapshot(self) -> None:
        """Test effective_encap_vlan_id ignores a stale snapshot VLAN ID."""
        # binding_1 snapshotted encap_vlan_id=150 from nb_vlan; move the
        # live VLAN to 151 without re-saving so the snapshot goes stale.
        self.nb_vlan.vid = 151
        self.nb_vlan.save(update_fields=("vid",))

        # The stale snapshot (150) must NOT match; the live VLAN wins.
        params = {"effective_encap_vlan_id": 150}
        self.assertNotIn(self.binding_1, self.filterset(params, self.queryset).qs)

        # The live vid (151) matches.
        params = {"effective_encap_vlan_id": 151}
        self.assertIn(self.binding_1, self.filterset(params, self.queryset).qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())
