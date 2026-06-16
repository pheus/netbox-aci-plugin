# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the tenant ACI Application Profile model."""

from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.endpoint_groups import ACIEndpointGroup, ACIUSegEndpointGroup
from ....models.tenant.endpoint_security_groups import ACIEndpointSecurityGroup
from ..base import ACIModelViewTestCase


class ACIAppProfileViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIAppProfile."""

    model = ACIAppProfile

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIAppProfile view tests."""
        super().setUpTestData()

        # 3 ACIAppProfile instances under the shared base tenant.
        ACIAppProfile.objects.create(
            name="ACIViewTestAppProfile1", aci_tenant=cls.aci_tenant
        )
        ACIAppProfile.objects.create(
            name="ACIViewTestAppProfile2", aci_tenant=cls.aci_tenant
        )
        ACIAppProfile.objects.create(
            name="ACIViewTestAppProfile3", aci_tenant=cls.aci_tenant
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestAppProfileX",
            "name_alias": "AppProfileXAlias",
            "description": "Form-data Application Profile",
            "aci_tenant": cls.aci_tenant.pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        tenant = cls.aci_tenant.name
        cls.csv_data = (
            "name,aci_fabric,aci_tenant,description",
            f"ACIViewTestAppProfile4,{fabric},{tenant},CSV App Profile 4",
            f"ACIViewTestAppProfile5,{fabric},{tenant},CSV App Profile 5",
            f"ACIViewTestAppProfile6,{fabric},{tenant},CSV App Profile 6",
        )

        app_profiles = list(ACIAppProfile.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{app_profiles[0].pk},Updated App Profile 1",
            f"{app_profiles[1].pk},Updated App Profile 2",
            f"{app_profiles[2].pk},Updated App Profile 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Application Profile"}

    def test_aciappprofile_endpoint_groups_tab(self) -> None:
        """Endpoint Groups tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciappprofile",
            "netbox_aci_plugin.view_aciendpointgroup",
            "netbox_aci_plugin.add_aciendpointgroup",
        )
        url = get_action_url(
            self.aci_app_profile,
            action="endpointgroups",
            kwargs={"pk": self.aci_app_profile.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIEndpointGroup, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={self.aci_app_profile.aci_tenant_id}&amp;'
            f"aci_app_profile={self.aci_app_profile.pk}",
        )

    def test_aciappprofile_useg_endpoint_groups_tab(self) -> None:
        """uSeg Endpoint Groups tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciappprofile",
            "netbox_aci_plugin.view_aciusegendpointgroup",
            "netbox_aci_plugin.add_aciusegendpointgroup",
        )
        url = get_action_url(
            self.aci_app_profile,
            action="usegendpointgroups",
            kwargs={"pk": self.aci_app_profile.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIUSegEndpointGroup, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={self.aci_app_profile.aci_tenant_id}&amp;'
            f"aci_app_profile={self.aci_app_profile.pk}",
        )

    def test_aciappprofile_endpoint_security_groups_tab(self) -> None:
        """Endpoint Security Groups tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciappprofile",
            "netbox_aci_plugin.view_aciendpointsecuritygroup",
            "netbox_aci_plugin.add_aciendpointsecuritygroup",
        )
        url = get_action_url(
            self.aci_app_profile,
            action="endpointsecuritygroups",
            kwargs={"pk": self.aci_app_profile.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIEndpointSecurityGroup, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_tenant={self.aci_app_profile.aci_tenant_id}&amp;'
            f"aci_app_profile={self.aci_app_profile.pk}",
        )
