# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the fabric ACI Fabric model."""

from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....models.access_policies.domains import ACIRoutedDomain
from ....models.fabric.fabrics import ACIFabric
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ....models.tenant.tenants import ACITenant
from ..base import ACIModelViewTestCase


class ACIFabricViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIFabric."""

    model = ACIFabric

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIFabric view tests."""
        super().setUpTestData()

        # Snapshot the seeded Fabric1 and the shared base-chain fabric that
        # exist before this test creates its own. They carry PROTECT'd
        # children, so NetBox's bulk-delete-everything assertion
        # (count() == 0) can never empty the real table. Scoping the test
        # queryset to only our own rows keeps every inherited view test on
        # deletable leaves.
        cls.fixture_pks = list(ACIFabric.objects.values_list("pk", flat=True))

        # 3 ACIFabric instances for list / bulk / get / edit / delete.
        ACIFabric.objects.create(
            name="ACIViewTestFabric1", fabric_id=101, infra_vlan_vid=3001
        )
        ACIFabric.objects.create(
            name="ACIViewTestFabric2", fabric_id=102, infra_vlan_vid=3002
        )
        ACIFabric.objects.create(
            name="ACIViewTestFabric3", fabric_id=103, infra_vlan_vid=3003
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestFabricX",
            "description": "Form-data Fabric",
            "fabric_id": 104,
            "infra_vlan_vid": 3004,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,fabric_id,infra_vlan_vid,description",
            "ACIViewTestFabric4,105,3005,CSV Fabric 4",
            "ACIViewTestFabric5,106,3006,CSV Fabric 5",
            "ACIViewTestFabric6,107,3007,CSV Fabric 6",
        )

        fabrics = list(ACIFabric.objects.exclude(pk__in=cls.fixture_pks).order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{fabrics[0].pk},Updated Fabric 1",
            f"{fabrics[1].pk},Updated Fabric 2",
            f"{fabrics[2].pk},Updated Fabric 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Fabric"}

    def _get_queryset(self):
        return self.model.objects.exclude(pk__in=self.fixture_pks)

    def test_acifabric_pods_tab_add_button(self) -> None:
        """Fabric Pods tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acifabric",
            "netbox_aci_plugin.view_acipod",
            "netbox_aci_plugin.add_acipod",
        )
        url = get_action_url(
            self.aci_fabric, action="pods", kwargs={"pk": self.aci_fabric.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIPod, action="add")
        self.assertContains(
            response, f'href="{add_url}?aci_fabric={self.aci_fabric.pk}'
        )

    def test_acifabric_nodes_tab_add_button(self) -> None:
        """Fabric Nodes tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acifabric",
            "netbox_aci_plugin.view_acinode",
            "netbox_aci_plugin.add_acinode",
        )
        url = get_action_url(
            self.aci_fabric, action="nodes", kwargs={"pk": self.aci_fabric.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACINode, action="add")
        self.assertContains(
            response, f'href="{add_url}?aci_fabric={self.aci_fabric.pk}'
        )

    def test_acifabric_tenants_tab_add_button(self) -> None:
        """Fabric Tenants tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acifabric",
            "netbox_aci_plugin.view_acitenant",
            "netbox_aci_plugin.add_acitenant",
        )
        url = get_action_url(
            self.aci_fabric, action="tenants", kwargs={"pk": self.aci_fabric.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACITenant, action="add")
        self.assertContains(
            response, f'href="{add_url}?aci_fabric={self.aci_fabric.pk}'
        )

    def test_acifabric_routed_domains_tab_add_button(self) -> None:
        """Fabric Routed Domains tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acifabric",
            "netbox_aci_plugin.view_acirouteddomain",
            "netbox_aci_plugin.add_acirouteddomain",
        )
        url = get_action_url(
            self.aci_fabric, action="routed_domains", kwargs={"pk": self.aci_fabric.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIRoutedDomain, action="add")
        self.assertContains(
            response, f'href="{add_url}?aci_fabric={self.aci_fabric.pk}'
        )
