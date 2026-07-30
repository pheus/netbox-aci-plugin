# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""API tests for access-policy Leaf Interface Policy Group models."""

from tenancy.models import Tenant
from utilities.testing import APIViewTestCases

from ....api.urls import app_name
from ....choices import LeafInterfacePolicyGroupTypeChoices
from ....models.access_policies.aaep import ACIAttachableAccessEntityProfile
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ....models.fabric.fabrics import ACIFabric


class ACILeafInterfacePolicyGroupAPIViewTestCase(APIViewTestCases.APIViewTestCase):
    """API view test case for ACI Leaf Interface Policy Group."""

    model = ACILeafInterfacePolicyGroup
    view_namespace: str = f"plugins-api:{app_name}"
    brief_fields: list[str] = [
        "aci_fabric",
        "description",
        "display",
        "group_type",
        "id",
        "name",
        "name_alias",
        "nb_tenant",
        "url",
    ]
    user_permissions = (
        "netbox_aci_plugin.view_aciattachableaccessentityprofile",
        "netbox_aci_plugin.view_acifabric",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up ACI Leaf Interface Policy Group for API view testing."""
        nb_tenant1 = Tenant.objects.create(
            name="NetBox Tenant API 1", slug="netbox-tenant-api-1"
        )
        nb_tenant2 = Tenant.objects.create(
            name="NetBox Tenant API 2", slug="netbox-tenant-api-2"
        )
        aci_fabric = ACIFabric.objects.create(
            name="ACITestFabricAPI", fabric_id=115, infra_vlan_vid=3900
        )
        aci_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACIPolicyGroupTestAPIAAEP", aci_fabric=aci_fabric
        )

        policy_groups: tuple = (
            ACILeafInterfacePolicyGroup(
                name="ACILeafInterfacePolicyGroupTestAPI1",
                name_alias="Testing",
                description="First ACI Test",
                aci_fabric=aci_fabric,
                group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
                aci_aaep=aci_aaep,
                nb_tenant=nb_tenant1,
                comments="# ACI Test 1",
            ),
            ACILeafInterfacePolicyGroup(
                name="ACILeafInterfacePolicyGroupTestAPI2",
                name_alias="Testing",
                description="Second ACI Test",
                aci_fabric=aci_fabric,
                group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_PC,
                nb_tenant=nb_tenant2,
                comments="# ACI Test 2",
            ),
            ACILeafInterfacePolicyGroup(
                name="ACILeafInterfacePolicyGroupTestAPI3",
                name_alias="Testing",
                description="Third ACI Test",
                aci_fabric=aci_fabric,
                group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_VPC,
                aci_aaep=aci_aaep,
                nb_tenant=nb_tenant2,
                comments="# ACI Test 3",
            ),
        )
        ACILeafInterfacePolicyGroup.objects.bulk_create(policy_groups)

        cls.create_data: list[dict] = [
            {
                "name": "ACILeafInterfacePolicyGroupTestAPI4",
                "name_alias": "Testing",
                "description": "Fourth ACI Test",
                "aci_fabric": aci_fabric.id,
                "group_type": LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
                "nb_tenant": nb_tenant1.id,
                "comments": "# ACI Test 4",
            },
            {
                "name": "ACILeafInterfacePolicyGroupTestAPI5",
                "name_alias": "Testing",
                "description": "Fifth ACI Test",
                "aci_fabric": aci_fabric.id,
                "group_type": LeafInterfacePolicyGroupTypeChoices.TYPE_PC,
                "aci_aaep": aci_aaep.id,
                "nb_tenant": nb_tenant2.id,
                "comments": "# ACI Test 5",
            },
            {
                "name": "ACILeafInterfacePolicyGroupTestAPI6",
                "name_alias": "Testing",
                "description": "Sixth ACI Test",
                "aci_fabric": aci_fabric.id,
                "group_type": LeafInterfacePolicyGroupTypeChoices.TYPE_VPC,
                "aci_aaep": aci_aaep.id,
                "nb_tenant": nb_tenant2.id,
                "comments": "# ACI Test 6",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }
