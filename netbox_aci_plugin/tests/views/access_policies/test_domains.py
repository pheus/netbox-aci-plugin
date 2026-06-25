# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the access policies ACI domain models."""

from utilities.testing import ViewTestCases, create_tags

from ....models.access_policies.domains import ACIPhysicalDomain, ACIRoutedDomain
from ....models.access_policies.vlan_pools import ACIVLANPool
from ..base import ACIModelViewTestCase


class ACIRoutedDomainViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIRoutedDomain."""

    model = ACIRoutedDomain

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIRoutedDomain view tests."""
        super().setUpTestData()

        # 3 ACIRoutedDomain instances under the shared base fabric.
        ACIRoutedDomain.objects.create(
            name="ACIViewTestRoutedDomain1", aci_fabric=cls.aci_fabric
        )
        ACIRoutedDomain.objects.create(
            name="ACIViewTestRoutedDomain2", aci_fabric=cls.aci_fabric
        )
        ACIRoutedDomain.objects.create(
            name="ACIViewTestRoutedDomain3", aci_fabric=cls.aci_fabric
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestRoutedDomainX",
            "name_alias": "RoutedDomainXAlias",
            "description": "Form-data Routed Domain",
            "aci_fabric": cls.aci_fabric.pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        cls.csv_data = (
            "aci_fabric,name,description",
            f"{fabric},ACIViewTestRoutedDomain4,CSV Routed Domain 4",
            f"{fabric},ACIViewTestRoutedDomain5,CSV Routed Domain 5",
            f"{fabric},ACIViewTestRoutedDomain6,CSV Routed Domain 6",
        )

        domains = list(ACIRoutedDomain.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{domains[0].pk},Updated Routed Domain 1",
            f"{domains[1].pk},Updated Routed Domain 2",
            f"{domains[2].pk},Updated Routed Domain 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Routed Domain"}


class ACIPhysicalDomainViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACIPhysicalDomain."""

    model = ACIPhysicalDomain

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIPhysicalDomain view tests."""
        super().setUpTestData()

        cls.aci_vlan_pool = ACIVLANPool.objects.create(
            name="ACIViewTestPhysicalDomainVLANPool",
            aci_fabric=cls.aci_fabric,
        )

        # 3 ACIPhysicalDomain instances under the shared base fabric.
        ACIPhysicalDomain.objects.create(
            name="ACIViewTestPhysicalDomain1",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool,
        )
        ACIPhysicalDomain.objects.create(
            name="ACIViewTestPhysicalDomain2",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool,
        )
        ACIPhysicalDomain.objects.create(
            name="ACIViewTestPhysicalDomain3",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool,
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestPhysicalDomainX",
            "name_alias": "PhysicalDomainXAlias",
            "description": "Form-data Physical Domain",
            "aci_fabric": cls.aci_fabric.pk,
            "aci_vlan_pool": cls.aci_vlan_pool.pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        pool = cls.aci_vlan_pool.name
        cls.csv_data = (
            "aci_fabric,aci_vlan_pool,name,description",
            f"{fabric},{pool},ACIViewTestPhysicalDomain4,CSV Physical Domain 4",
            f"{fabric},{pool},ACIViewTestPhysicalDomain5,CSV Physical Domain 5",
            f"{fabric},{pool},ACIViewTestPhysicalDomain6,CSV Physical Domain 6",
        )

        domains = list(ACIPhysicalDomain.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{domains[0].pk},Updated Physical Domain 1",
            f"{domains[1].pk},Updated Physical Domain 2",
            f"{domains[2].pk},Updated Physical Domain 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Physical Domain"}
