# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the tenant ACI Tenant model."""

from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.bridge_domains import ACIBridgeDomain
from ....models.tenant.contracts import ACIContract
from ....models.tenant.endpoint_groups import ACIEndpointGroup
from ....models.tenant.endpoint_security_groups import ACIEndpointSecurityGroup
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF
from ..base import ACIModelViewTestCase


class ACITenantViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACITenant."""

    model = ACITenant

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACITenant view tests."""
        super().setUpTestData()

        # Snapshot the migration-seed tenants (common / infra / mgmt) and
        # the shared base-chain tenant that exist before this test creates
        # its own. Several carry PROTECT'd children, so NetBox's
        # bulk-delete-everything assertion (count() == 0) can never empty
        # the real table. Scoping the test queryset to only our own rows
        # keeps every inherited view test on deletable leaves.
        cls.fixture_pks = list(ACITenant.objects.values_list("pk", flat=True))

        # 3 ACITenant instances for list / bulk / get / edit / delete.
        tenant1 = ACITenant.objects.create(
            name="ACIViewTestTenant1", aci_fabric=cls.aci_fabric
        )
        tenant2 = ACITenant.objects.create(
            name="ACIViewTestTenant2", aci_fabric=cls.aci_fabric
        )
        tenant3 = ACITenant.objects.create(
            name="ACIViewTestTenant3", aci_fabric=cls.aci_fabric
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestTenantX",
            "name_alias": "TenantXAlias",
            "description": "Form-data Tenant",
            "aci_fabric": cls.aci_fabric.pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        cls.csv_data = (
            "name,name_alias,aci_fabric,description",
            f"ACIViewTestTenant4,Tenant4Alias,{fabric},CSV Tenant 4",
            f"ACIViewTestTenant5,Tenant5Alias,{fabric},CSV Tenant 5",
            f"ACIViewTestTenant6,Tenant6Alias,{fabric},CSV Tenant 6",
        )

        cls.csv_update_data = (
            "id,description",
            f"{tenant1.pk},Updated Tenant 1",
            f"{tenant2.pk},Updated Tenant 2",
            f"{tenant3.pk},Updated Tenant 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Tenant"}

    def _get_queryset(self):
        return self.model.objects.exclude(pk__in=self.fixture_pks)

    def test_acitenant_app_profiles_tab(self) -> None:
        """Application Profiles tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acitenant",
            "netbox_aci_plugin.view_aciappprofile",
            "netbox_aci_plugin.add_aciappprofile",
        )
        url = get_action_url(
            self.aci_tenant, action="appprofiles", kwargs={"pk": self.aci_tenant.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIAppProfile, action="add")
        self.assertContains(
            response, f'href="{add_url}?aci_tenant={self.aci_tenant.pk}'
        )

    def test_acitenant_endpoint_groups_tab(self) -> None:
        """Endpoint Groups tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acitenant",
            "netbox_aci_plugin.view_aciendpointgroup",
            "netbox_aci_plugin.add_aciendpointgroup",
        )
        url = get_action_url(
            self.aci_tenant, action="endpointgroups", kwargs={"pk": self.aci_tenant.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIEndpointGroup, action="add")
        self.assertContains(
            response, f'href="{add_url}?aci_tenant={self.aci_tenant.pk}'
        )

    def test_acitenant_endpoint_security_groups_tab(self) -> None:
        """Endpoint Security Groups tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acitenant",
            "netbox_aci_plugin.view_aciendpointsecuritygroup",
            "netbox_aci_plugin.add_aciendpointsecuritygroup",
        )
        url = get_action_url(
            self.aci_tenant,
            action="endpointsecuritygroups",
            kwargs={"pk": self.aci_tenant.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIEndpointSecurityGroup, action="add")
        self.assertContains(
            response, f'href="{add_url}?aci_tenant={self.aci_tenant.pk}'
        )

    def test_acitenant_bridge_domains_tab(self) -> None:
        """Bridge Domains tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acitenant",
            "netbox_aci_plugin.view_acibridgedomain",
            "netbox_aci_plugin.add_acibridgedomain",
        )
        url = get_action_url(
            self.aci_tenant, action="bridgedomains", kwargs={"pk": self.aci_tenant.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIBridgeDomain, action="add")
        self.assertContains(
            response, f'href="{add_url}?aci_tenant={self.aci_tenant.pk}'
        )

    def test_acitenant_vrfs_tab(self) -> None:
        """VRFs tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acitenant",
            "netbox_aci_plugin.view_acivrf",
            "netbox_aci_plugin.add_acivrf",
        )
        url = get_action_url(
            self.aci_tenant, action="vrfs", kwargs={"pk": self.aci_tenant.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIVRF, action="add")
        self.assertContains(
            response, f'href="{add_url}?aci_tenant={self.aci_tenant.pk}'
        )

    def test_acitenant_contracts_tab(self) -> None:
        """Contracts tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acitenant",
            "netbox_aci_plugin.view_acicontract",
            "netbox_aci_plugin.add_acicontract",
        )
        url = get_action_url(
            self.aci_tenant, action="contracts", kwargs={"pk": self.aci_tenant.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIContract, action="add")
        self.assertContains(
            response, f'href="{add_url}?aci_tenant={self.aci_tenant.pk}'
        )
