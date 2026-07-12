# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the tenant ACI Endpoint Group Domain Binding model."""

from django.contrib.contenttypes.models import ContentType

from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....choices import DeploymentImmediacyChoices, ResolutionImmediacyChoices
from ....models.access_policies.domains import ACIPhysicalDomain
from ....models.access_policies.vlan_pools import ACIVLANPool
from ....models.tenant.endpoint_group_bindings import ACIEndpointGroupDomainBinding
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
