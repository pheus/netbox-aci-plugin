# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the access policies ACI VLAN Pool models."""

from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....models.access_policies.vlan_pools import ACIVLANPool, ACIVLANPoolRange
from ..base import ACIModelViewTestCase


class ACIVLANPoolViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIVLANPool."""

    model = ACIVLANPool

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIVLANPool view tests."""
        super().setUpTestData()

        # 3 ACIVLANPool instances under the shared base fabric.
        ACIVLANPool.objects.create(
            name="ACIViewTestVLANPool1",
            aci_fabric=cls.aci_fabric,
            allocation_mode="static",
        )
        ACIVLANPool.objects.create(
            name="ACIViewTestVLANPool2",
            aci_fabric=cls.aci_fabric,
            allocation_mode="static",
        )
        ACIVLANPool.objects.create(
            name="ACIViewTestVLANPool3",
            aci_fabric=cls.aci_fabric,
            allocation_mode="dynamic",
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestVLANPoolX",
            "name_alias": "VLANPoolXAlias",
            "description": "Form-data VLAN Pool",
            "aci_fabric": cls.aci_fabric.pk,
            "allocation_mode": "static",
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        cls.csv_data = (
            "aci_fabric,name,allocation_mode",
            f"{fabric},ACIViewTestVLANPool4,static",
            f"{fabric},ACIViewTestVLANPool5,dynamic",
            f"{fabric},ACIViewTestVLANPool6,static",
        )

        pools = list(ACIVLANPool.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{pools[0].pk},Updated VLAN Pool 1",
            f"{pools[1].pk},Updated VLAN Pool 2",
            f"{pools[2].pk},Updated VLAN Pool 3",
        )

        cls.bulk_edit_data = {
            "description": "Bulk-edited VLAN Pool",
            "name_alias": "BulkAlias",
        }

    def test_acifabric_vlan_pools_tab(self) -> None:
        """VLAN Pools tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acifabric",
            "netbox_aci_plugin.view_acivlanpool",
            "netbox_aci_plugin.add_acivlanpool",
        )
        url = get_action_url(
            self.aci_fabric,
            action="vlan_pools",
            kwargs={"pk": self.aci_fabric.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIVLANPool, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={self.aci_fabric.pk}',
        )


class ACIVLANPoolRangeViewTestCase(
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
    """Standard view tests for ACIVLANPoolRange.

    ``BulkRenameObjectsViewTestCase`` is intentionally excluded - the
    range has no ``name`` field.
    """

    model = ACIVLANPoolRange

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIVLANPoolRange view tests."""
        super().setUpTestData()

        cls.aci_vlan_pool = ACIVLANPool.objects.create(
            name="ACIViewTestVLANPoolForRanges",
            aci_fabric=cls.aci_fabric,
            allocation_mode="static",
        )

        # 3 non-overlapping ranges in distinct 100-VLAN blocks.
        ACIVLANPoolRange.objects.create(
            aci_vlan_pool=cls.aci_vlan_pool,
            vlan_id_from=100,
            vlan_id_to=199,
            role="external",
        )
        ACIVLANPoolRange.objects.create(
            aci_vlan_pool=cls.aci_vlan_pool,
            vlan_id_from=200,
            vlan_id_to=299,
            role="external",
        )
        ACIVLANPoolRange.objects.create(
            aci_vlan_pool=cls.aci_vlan_pool,
            vlan_id_from=300,
            vlan_id_to=399,
            role="external",
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "aci_vlan_pool": cls.aci_vlan_pool.pk,
            "vlan_id_from": 1000,
            "vlan_id_to": 1099,
            "allocation_mode": "inherit",
            "role": "external",
            "comments": "Form-data VLAN range",
            "tags": [t.pk for t in tags],
        }

        pool = cls.aci_vlan_pool.name
        cls.csv_data = (
            "aci_vlan_pool,vlan_id_from,vlan_id_to,role",
            f"{pool},2000,2099,external",
            f"{pool},2100,2199,external",
            f"{pool},2200,2299,external",
        )

        ranges = list(ACIVLANPoolRange.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,comments",
            f"{ranges[0].pk},Updated range 1",
            f"{ranges[1].pk},Updated range 2",
            f"{ranges[2].pk},Updated range 3",
        )

        cls.bulk_edit_data = {
            "role": "internal",
            "comments": "Bulk-edited range",
        }

    def test_acivlanpool_ranges_tab(self) -> None:
        """Ranges tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acivlanpool",
            "netbox_aci_plugin.view_acivlanpoolrange",
            "netbox_aci_plugin.add_acivlanpoolrange",
        )
        url = get_action_url(
            self.aci_vlan_pool,
            action="vlanpoolranges",
            kwargs={"pk": self.aci_vlan_pool.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACIVLANPoolRange, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={self.aci_vlan_pool.aci_fabric_id}&amp;'
            f"aci_vlan_pool={self.aci_vlan_pool.pk}",
        )
