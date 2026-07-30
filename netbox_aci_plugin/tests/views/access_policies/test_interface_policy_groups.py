# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the access policies ACI Leaf Interface Policy Group model."""

from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....choices import LeafInterfacePolicyGroupTypeChoices
from ....models.access_policies.aaep import ACIAttachableAccessEntityProfile
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ..base import ACIModelViewTestCase


class ACILeafInterfacePolicyGroupViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACILeafInterfacePolicyGroup."""

    model = ACILeafInterfacePolicyGroup

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafInterfacePolicyGroup view tests."""
        super().setUpTestData()

        cls.aci_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACIViewTestPolicyGroupAAEP", aci_fabric=cls.aci_fabric
        )

        ACILeafInterfacePolicyGroup.objects.create(
            name="ACIViewTestPolicyGroup1",
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            aci_aaep=cls.aci_aaep,
        )
        ACILeafInterfacePolicyGroup.objects.create(
            name="ACIViewTestPolicyGroup2",
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        ACILeafInterfacePolicyGroup.objects.create(
            name="ACIViewTestPolicyGroup3",
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestPolicyGroupX",
            "name_alias": "PolicyGroupXAlias",
            "description": "Form-data Policy Group",
            "aci_fabric": cls.aci_fabric.pk,
            "group_type": LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            "aci_aaep": cls.aci_aaep.pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        cls.csv_data = (
            "name,aci_fabric,group_type,description",
            f"ACIViewTestPolicyGroup4,{fabric},access,CSV Policy Group 4",
            f"ACIViewTestPolicyGroup5,{fabric},pc,CSV Policy Group 5",
            f"ACIViewTestPolicyGroup6,{fabric},vpc,CSV Policy Group 6",
        )

        policy_groups = list(ACILeafInterfacePolicyGroup.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{policy_groups[0].pk},Updated Policy Group 1",
            f"{policy_groups[1].pk},Updated Policy Group 2",
            f"{policy_groups[2].pk},Updated Policy Group 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Policy Group"}

    def test_aciaaep_policygroups_tab(self) -> None:
        """Policy Groups tab on the AAEP detail renders the Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_aciattachableaccessentityprofile",
            "netbox_aci_plugin.view_acileafinterfacepolicygroup",
            "netbox_aci_plugin.add_acileafinterfacepolicygroup",
        )
        url = get_action_url(
            self.aci_aaep,
            action="policygroups",
            kwargs={"pk": self.aci_aaep.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACILeafInterfacePolicyGroup, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={self.aci_fabric.pk}&amp;'
            f"aci_aaep={self.aci_aaep.pk}",
        )
