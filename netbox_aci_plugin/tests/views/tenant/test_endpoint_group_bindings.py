# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the tenant ACI Endpoint Group Binding models."""

from django.contrib.contenttypes.models import ContentType

from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....choices import (
    DeploymentImmediacyChoices,
    PortModeChoices,
    ResolutionImmediacyChoices,
)
from ....models.access_policies.aaep import (
    ACIAAEPDomainBinding,
    ACIAttachableAccessEntityProfile,
)
from ....models.access_policies.domains import ACIPhysicalDomain
from ....models.access_policies.vlan_pools import ACIVLANPool, ACIVLANPoolRange
from ....models.tenant.endpoint_group_bindings import (
    ACIEndpointGroupAAEPBinding,
    ACIEndpointGroupDomainBinding,
)
from ....models.tenant.endpoint_groups import ACIEndpointGroup, ACIUSegEndpointGroup
from ..base import ACIModelViewTestCase


class ACIEndpointGroupDomainBindingViewTestCase(
    ACIModelViewTestCase,
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    """Standard view tests for ACIEndpointGroupDomainBinding.

    ``BulkRenameObjectsViewTestCase`` is intentionally excluded - the
    binding has no ``name`` field.
    """

    model = ACIEndpointGroupDomainBinding

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEndpointGroupDomainBinding view tests."""
        super().setUpTestData()

        cls.aci_vlan_pool = ACIVLANPool.objects.create(
            name="ACIViewTestBindingVLANPool",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_epg = ACIEndpointGroup.objects.create(
            name="ACIViewTestEPGForDomainBinding",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_useg_epg = ACIUSegEndpointGroup.objects.create(
            name="ACIViewTestUSegEPGForDomainBinding",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )

        # Physical domains: #1 is shared by the 2 initial bindings that
        # vary the EPG side, #2 is for the 3rd initial binding, #3 is for
        # form_data, #4-#6 are for csv_data import.
        cls.aci_physical_domain = ACIPhysicalDomain.objects.create(
            name="ACIViewTestBindingPhysicalDomain1",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool,
        )
        cls.aci_physical_domain2 = ACIPhysicalDomain.objects.create(
            name="ACIViewTestBindingPhysicalDomain2",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool,
        )
        cls.aci_physical_domain3 = ACIPhysicalDomain.objects.create(
            name="ACIViewTestBindingPhysicalDomain3",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool,
        )
        cls.aci_physical_domain4 = ACIPhysicalDomain.objects.create(
            name="ACIViewTestBindingPhysicalDomain4",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool,
        )
        cls.aci_physical_domain5 = ACIPhysicalDomain.objects.create(
            name="ACIViewTestBindingPhysicalDomain5",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool,
        )
        cls.aci_physical_domain6 = ACIPhysicalDomain.objects.create(
            name="ACIViewTestBindingPhysicalDomain6",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool,
        )

        # 3 domain bindings on distinct EPG object / domain object pairs.
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg,
            aci_domain_object=cls.aci_physical_domain,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_useg_epg,
            aci_domain_object=cls.aci_physical_domain,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg,
            aci_domain_object=cls.aci_physical_domain2,
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        useg_epg_ct = ContentType.objects.get_for_model(ACIUSegEndpointGroup)
        phys_ct = ContentType.objects.get_for_model(ACIPhysicalDomain)
        cls.form_data = {
            "aci_epg_object_type": useg_epg_ct.pk,
            "aci_epg_object": cls.aci_useg_epg.pk,
            "aci_domain_object_type": phys_ct.pk,
            "aci_domain_object": cls.aci_physical_domain3.pk,
            "deployment_immediacy": DeploymentImmediacyChoices.IMMEDIACY_IMMEDIATE,
            "resolution_immediacy": ResolutionImmediacyChoices.IMMEDIACY_IMMEDIATE,
            "comments": "Form-data domain binding",
            "tags": [t.pk for t in tags],
        }

        epg_ct = ContentType.objects.get_for_model(ACIEndpointGroup)
        epg_ct_label = f"{epg_ct.app_label}.{epg_ct.model}"
        phys_ct_label = f"{phys_ct.app_label}.{phys_ct.model}"
        epg_id = cls.aci_epg.pk
        pd4 = cls.aci_physical_domain4.pk
        pd5 = cls.aci_physical_domain5.pk
        pd6 = cls.aci_physical_domain6.pk
        cls.csv_data = (
            (
                "aci_epg_object_type,aci_epg_object_id,"
                "aci_domain_object_type,aci_domain_object_id"
            ),
            f"{epg_ct_label},{epg_id},{phys_ct_label},{pd4}",
            f"{epg_ct_label},{epg_id},{phys_ct_label},{pd5}",
            f"{epg_ct_label},{epg_id},{phys_ct_label},{pd6}",
        )

        bindings = list(ACIEndpointGroupDomainBinding.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,comments",
            f"{bindings[0].pk},Updated binding 1",
            f"{bindings[1].pk},Updated binding 2",
            f"{bindings[2].pk},Updated binding 3",
        )

        cls.bulk_edit_data = {
            "deployment_immediacy": DeploymentImmediacyChoices.IMMEDIACY_IMMEDIATE,
            "resolution_immediacy": ResolutionImmediacyChoices.IMMEDIACY_PRE_PROVISION,
            "comments": "Bulk-edited binding",
        }

    def test_aciendpointgroup_domain_bindings_tab(self) -> None:
        """Domain Bindings tab on the EPG detail renders the Bind button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciendpointgroup",
            "netbox_aci_plugin.view_aciendpointgroupdomainbinding",
            "netbox_aci_plugin.add_aciendpointgroupdomainbinding",
        )
        url = get_action_url(
            self.aci_epg,
            action="domainbindings",
            kwargs={"pk": self.aci_epg.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIEndpointGroupDomainBinding, action="add")
        epg_ct = ContentType.objects.get_for_model(ACIEndpointGroup)
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={self.aci_fabric.pk}&amp;'
            f"aci_epg_object={self.aci_epg.pk}&amp;"
            f"aci_epg_object_type={epg_ct.pk}",
        )

    def test_aciusegendpointgroup_domain_bindings_tab(self) -> None:
        """Domain Bindings tab on the uSeg EPG detail renders the button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciusegendpointgroup",
            "netbox_aci_plugin.view_aciendpointgroupdomainbinding",
            "netbox_aci_plugin.add_aciendpointgroupdomainbinding",
        )
        url = get_action_url(
            self.aci_useg_epg,
            action="domainbindings",
            kwargs={"pk": self.aci_useg_epg.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIEndpointGroupDomainBinding, action="add")
        useg_epg_ct = ContentType.objects.get_for_model(ACIUSegEndpointGroup)
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={self.aci_fabric.pk}&amp;'
            f"aci_epg_object={self.aci_useg_epg.pk}&amp;"
            f"aci_epg_object_type={useg_epg_ct.pk}",
        )

    def test_aciphysicaldomain_endpoint_group_bindings_tab(self) -> None:
        """Endpoint Groups tab on the Physical Domain renders the button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciphysicaldomain",
            "netbox_aci_plugin.view_aciendpointgroupdomainbinding",
            "netbox_aci_plugin.add_aciendpointgroupdomainbinding",
        )
        url = get_action_url(
            self.aci_physical_domain,
            action="endpointgroupbindings",
            kwargs={"pk": self.aci_physical_domain.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIEndpointGroupDomainBinding, action="add")
        phys_ct = ContentType.objects.get_for_model(ACIPhysicalDomain)
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={self.aci_fabric.pk}&amp;'
            f"aci_domain_object={self.aci_physical_domain.pk}&amp;"
            f"aci_domain_object_type={phys_ct.pk}",
        )


class ACIEndpointGroupAAEPBindingViewTestCase(
    ACIModelViewTestCase,
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    """Standard view tests for ACIEndpointGroupAAEPBinding.

    ``BulkRenameObjectsViewTestCase`` is intentionally excluded - the
    binding has no ``name`` field.
    """

    model = ACIEndpointGroupAAEPBinding

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIEndpointGroupAAEPBinding view tests."""
        super().setUpTestData()

        cls.aci_vlan_pool = ACIVLANPool.objects.create(
            name="ACIViewTestAAEPBindingVLANPool",
            aci_fabric=cls.aci_fabric,
        )
        ACIVLANPoolRange.objects.create(
            aci_vlan_pool=cls.aci_vlan_pool,
            vlan_id_from=100,
            vlan_id_to=999,
        )
        cls.aci_physical_domain = ACIPhysicalDomain.objects.create(
            name="ACIViewTestAAEPBindingPhysicalDomain",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool,
        )
        cls.aci_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACIViewTestAAEPForEPGBinding",
            aci_fabric=cls.aci_fabric,
        )
        ACIAAEPDomainBinding.objects.create(
            aci_aaep=cls.aci_aaep,
            aci_domain_object=cls.aci_physical_domain,
        )

        # 7 distinct EPGs bound once each to the shared physical domain,
        # giving 7 distinct EPG/AAEP bindings: #1-#3 for the initial
        # bindings, #4 for form_data, #5-#7 for csv_data import.
        cls.aci_epg1 = ACIEndpointGroup.objects.create(
            name="ACIViewTestEPGForAAEPBinding1",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_epg2 = ACIEndpointGroup.objects.create(
            name="ACIViewTestEPGForAAEPBinding2",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_epg3 = ACIEndpointGroup.objects.create(
            name="ACIViewTestEPGForAAEPBinding3",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_epg4 = ACIEndpointGroup.objects.create(
            name="ACIViewTestEPGForAAEPBinding4",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_epg5 = ACIEndpointGroup.objects.create(
            name="ACIViewTestEPGForAAEPBinding5",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_epg6 = ACIEndpointGroup.objects.create(
            name="ACIViewTestEPGForAAEPBinding6",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_epg7 = ACIEndpointGroup.objects.create(
            name="ACIViewTestEPGForAAEPBinding7",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )

        cls.aci_epg_domain_binding = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg1,
            aci_domain_object=cls.aci_physical_domain,
        )
        cls.aci_epg_domain_binding2 = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg2,
            aci_domain_object=cls.aci_physical_domain,
        )
        cls.aci_epg_domain_binding3 = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg3,
            aci_domain_object=cls.aci_physical_domain,
        )
        cls.aci_epg_domain_binding4 = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg4,
            aci_domain_object=cls.aci_physical_domain,
        )
        cls.aci_epg_domain_binding5 = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg5,
            aci_domain_object=cls.aci_physical_domain,
        )
        cls.aci_epg_domain_binding6 = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg6,
            aci_domain_object=cls.aci_physical_domain,
        )
        cls.aci_epg_domain_binding7 = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg7,
            aci_domain_object=cls.aci_physical_domain,
        )

        # 3 initial AAEP bindings on distinct EPGs. The EPGs' own
        # ACIEndpointGroupDomainBinding fixtures above are prerequisites
        # only (F0467 shared-domain check) - no longer referenced by FK.
        ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=cls.aci_epg1,
            aci_aaep=cls.aci_aaep,
            encap_vlan_id=150,
        )
        ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=cls.aci_epg2,
            aci_aaep=cls.aci_aaep,
            encap_vlan_id=151,
        )
        ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=cls.aci_epg3,
            aci_aaep=cls.aci_aaep,
            encap_vlan_id=152,
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "aci_endpoint_group": cls.aci_epg4.pk,
            "aci_aaep": cls.aci_aaep.pk,
            "encap_vlan_id": 160,
            "mode": PortModeChoices.MODE_NATIVE,
            "deployment_immediacy": DeploymentImmediacyChoices.IMMEDIACY_IMMEDIATE,
            "comments": "Form-data AAEP binding",
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        app_profile = cls.aci_app_profile.name
        aaep_name = cls.aci_aaep.name
        cls.csv_data = (
            (
                "aci_fabric,aci_tenant,aci_app_profile,aci_endpoint_group,"
                "aci_aaep,encap_vlan_id"
            ),
            f"{fabric},{tenant},{app_profile},{cls.aci_epg5.name},{aaep_name},170",
            f"{fabric},{tenant},{app_profile},{cls.aci_epg6.name},{aaep_name},171",
            f"{fabric},{tenant},{app_profile},{cls.aci_epg7.name},{aaep_name},172",
        )

        bindings = list(ACIEndpointGroupAAEPBinding.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,comments",
            f"{bindings[0].pk},Updated binding 1",
            f"{bindings[1].pk},Updated binding 2",
            f"{bindings[2].pk},Updated binding 3",
        )

        cls.bulk_edit_data = {
            "mode": PortModeChoices.MODE_NATIVE,
            "deployment_immediacy": DeploymentImmediacyChoices.IMMEDIACY_IMMEDIATE,
            "comments": "Bulk-edited binding",
        }

    def test_aciendpointgroup_aaep_bindings_tab(self) -> None:
        """AAEP Bindings tab on the Endpoint Group renders the button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciendpointgroup",
            "netbox_aci_plugin.view_aciendpointgroupaaepbinding",
            "netbox_aci_plugin.add_aciendpointgroupaaepbinding",
        )
        url = get_action_url(
            self.aci_epg1,
            action="aaepbindings",
            kwargs={"pk": self.aci_epg1.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIEndpointGroupAAEPBinding, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={self.aci_fabric.pk}&amp;'
            f"aci_endpoint_group={self.aci_epg1.pk}",
        )

    def test_aciattachableaccessentityprofile_epg_bindings_tab(self) -> None:
        """EPG Bindings tab on the AAEP detail renders the button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciattachableaccessentityprofile",
            "netbox_aci_plugin.view_aciendpointgroupaaepbinding",
            "netbox_aci_plugin.add_aciendpointgroupaaepbinding",
        )
        url = get_action_url(
            self.aci_aaep,
            action="epgbindings",
            kwargs={"pk": self.aci_aaep.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIEndpointGroupAAEPBinding, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={self.aci_fabric.pk}&amp;'
            f"aci_aaep={self.aci_aaep.pk}",
        )
