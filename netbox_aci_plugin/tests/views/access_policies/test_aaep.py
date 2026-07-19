# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the access policies ACI AAEP models."""

from django.contrib.contenttypes.models import ContentType

from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....models.access_policies.aaep import (
    ACIAAEPDomainBinding,
    ACIAttachableAccessEntityProfile,
)
from ....models.access_policies.domains import ACIPhysicalDomain, ACIRoutedDomain
from ....models.access_policies.vlan_pools import ACIVLANPool
from ..base import ACIModelViewTestCase


class ACIAttachableAccessEntityProfileViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIAttachableAccessEntityProfile."""

    model = ACIAttachableAccessEntityProfile

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIAttachableAccessEntityProfile view tests."""
        super().setUpTestData()

        # 3 ACIAttachableAccessEntityProfile instances under the shared fabric.
        ACIAttachableAccessEntityProfile.objects.create(
            name="ACIViewTestAAEP1", aci_fabric=cls.aci_fabric
        )
        ACIAttachableAccessEntityProfile.objects.create(
            name="ACIViewTestAAEP2", aci_fabric=cls.aci_fabric
        )
        ACIAttachableAccessEntityProfile.objects.create(
            name="ACIViewTestAAEP3", aci_fabric=cls.aci_fabric
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestAAEPX",
            "name_alias": "AAEPXAlias",
            "description": "Form-data AAEP",
            "aci_fabric": cls.aci_fabric.pk,
            "infra_vlan": False,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        cls.csv_data = (
            "aci_fabric,name,description",
            f"{fabric},ACIViewTestAAEP4,CSV AAEP 4",
            f"{fabric},ACIViewTestAAEP5,CSV AAEP 5",
            f"{fabric},ACIViewTestAAEP6,CSV AAEP 6",
        )

        aaeps = list(ACIAttachableAccessEntityProfile.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{aaeps[0].pk},Updated AAEP 1",
            f"{aaeps[1].pk},Updated AAEP 2",
            f"{aaeps[2].pk},Updated AAEP 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited AAEP"}

    def test_acifabric_aaeps_tab(self) -> None:
        """AAEPs tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acifabric",
            "netbox_aci_plugin.view_aciattachableaccessentityprofile",
            "netbox_aci_plugin.add_aciattachableaccessentityprofile",
        )
        url = get_action_url(
            self.aci_fabric,
            action="aaeps",
            kwargs={"pk": self.aci_fabric.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIAttachableAccessEntityProfile, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={self.aci_fabric.pk}',
        )


class ACIAAEPDomainBindingViewTestCase(
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
    """Standard view tests for ACIAAEPDomainBinding.

    ``BulkRenameObjectsViewTestCase`` is intentionally excluded - the
    binding has no ``name`` field.
    """

    model = ACIAAEPDomainBinding

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIAAEPDomainBinding view tests."""
        super().setUpTestData()

        cls.aci_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACIViewTestAAEPForBindings",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_vlan_pool = ACIVLANPool.objects.create(
            name="ACIViewTestBindingVLANPool",
            aci_fabric=cls.aci_fabric,
            allocation_mode="static",
        )
        cls.aci_routed_domain1 = ACIRoutedDomain.objects.create(
            name="ACIViewTestBindingRoutedDomain1",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool,
        )
        cls.aci_routed_domain2 = ACIRoutedDomain.objects.create(
            name="ACIViewTestBindingRoutedDomain2",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool,
        )
        cls.aci_routed_domain3 = ACIRoutedDomain.objects.create(
            name="ACIViewTestBindingRoutedDomain3",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool,
        )
        # Physical domains: 1 for form_data, 3 for csv_data import.
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

        # 3 domain bindings on distinct routed domain objects.
        ACIAAEPDomainBinding.objects.create(
            aci_aaep=cls.aci_aaep,
            aci_domain_object=cls.aci_routed_domain1,
        )
        ACIAAEPDomainBinding.objects.create(
            aci_aaep=cls.aci_aaep,
            aci_domain_object=cls.aci_routed_domain2,
        )
        ACIAAEPDomainBinding.objects.create(
            aci_aaep=cls.aci_aaep,
            aci_domain_object=cls.aci_routed_domain3,
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        phys_ct = ContentType.objects.get_for_model(ACIPhysicalDomain)
        cls.form_data = {
            "aci_aaep": cls.aci_aaep.pk,
            "aci_domain_object_type": phys_ct.pk,
            "aci_domain_object": cls.aci_physical_domain.pk,
            "comments": "Form-data domain binding",
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        aaep = cls.aci_aaep.name
        pd2 = cls.aci_physical_domain2.pk
        pd3 = cls.aci_physical_domain3.pk
        pd4 = cls.aci_physical_domain4.pk
        cls.csv_data = (
            "aci_fabric,aci_aaep,aci_domain_object_type,aci_domain_object_id",
            f"{fabric},{aaep},netbox_aci_plugin.aciphysicaldomain,{pd2}",
            f"{fabric},{aaep},netbox_aci_plugin.aciphysicaldomain,{pd3}",
            f"{fabric},{aaep},netbox_aci_plugin.aciphysicaldomain,{pd4}",
        )

        bindings = list(ACIAAEPDomainBinding.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,comments",
            f"{bindings[0].pk},Updated binding 1",
            f"{bindings[1].pk},Updated binding 2",
            f"{bindings[2].pk},Updated binding 3",
        )

        cls.bulk_edit_data = {
            "comments": "Bulk-edited binding",
        }

    def test_aciaaep_domain_bindings_tab(self) -> None:
        """Domain Bindings tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciattachableaccessentityprofile",
            "netbox_aci_plugin.view_aciaaepdomainbinding",
            "netbox_aci_plugin.add_aciaaepdomainbinding",
        )
        url = get_action_url(
            self.aci_aaep,
            action="domainbindings",
            kwargs={"pk": self.aci_aaep.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIAAEPDomainBinding, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={self.aci_fabric.pk}&amp;'
            f"aci_aaep={self.aci_aaep.pk}",
        )

    def test_acirouteddomain_aaep_bindings_tab(self) -> None:
        """AAEPs tab on the Routed Domain detail renders the Bind button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acirouteddomain",
            "netbox_aci_plugin.view_aciaaepdomainbinding",
            "netbox_aci_plugin.add_aciaaepdomainbinding",
        )
        url = get_action_url(
            self.aci_routed_domain1,
            action="aaepbindings",
            kwargs={"pk": self.aci_routed_domain1.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIAAEPDomainBinding, action="add")
        routed_ct = ContentType.objects.get_for_model(ACIRoutedDomain)
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={self.aci_fabric.pk}&amp;'
            f"aci_domain_object={self.aci_routed_domain1.pk}&amp;"
            f"aci_domain_object_type={routed_ct.pk}",
        )

    def test_aciphysicaldomain_aaep_bindings_tab(self) -> None:
        """AAEPs tab on the Physical Domain detail renders the Bind button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciphysicaldomain",
            "netbox_aci_plugin.view_aciaaepdomainbinding",
            "netbox_aci_plugin.add_aciaaepdomainbinding",
        )
        url = get_action_url(
            self.aci_physical_domain,
            action="aaepbindings",
            kwargs={"pk": self.aci_physical_domain.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIAAEPDomainBinding, action="add")
        phys_ct = ContentType.objects.get_for_model(ACIPhysicalDomain)
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={self.aci_fabric.pk}&amp;'
            f"aci_domain_object={self.aci_physical_domain.pk}&amp;"
            f"aci_domain_object_type={phys_ct.pk}",
        )
