# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Filterset tests for the ACI Leaf Interface Policy Group model."""

from utilities.testing import ChangeLoggedFilterSetTests

from ....choices import LeafInterfacePolicyGroupTypeChoices
from ....filtersets.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroupFilterSet,
)
from ....models.access_policies.aaep import ACIAttachableAccessEntityProfile
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ...models.base import ACIBaseTestCase


class ACILeafInterfacePolicyGroupFilterSetTestCase(
    ACIBaseTestCase, ChangeLoggedFilterSetTests
):
    """Test case for ACILeafInterfacePolicyGroupFilterSet."""

    queryset = ACILeafInterfacePolicyGroup.objects.all()
    filterset = ACILeafInterfacePolicyGroupFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafInterfacePolicyGroupFilterSet tests."""
        super().setUpTestData()
        cls.aci_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACIFSTestAAEPForLIPG",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_lipg_1 = ACILeafInterfacePolicyGroup.objects.create(
            name="ACIFSTestLIPG1",
            name_alias="ACIFSTestLIPG1Alias",
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            aci_aaep=cls.aci_aaep,
        )
        cls.aci_lipg_2 = ACILeafInterfacePolicyGroup.objects.create(
            name="ACIFSTestLIPG2",
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_PC,
        )
        # A third group, so test_id has more than two objects to filter
        cls.aci_lipg_3 = ACILeafInterfacePolicyGroup.objects.create(
            name="ACIFSTestLIPG3",
            aci_fabric=cls.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_VPC,
        )

    def test_q(self) -> None:
        """Test q search matches the name field."""
        params = {"q": "ACIFSTestLIPG1"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_lipg_1, qs)
        self.assertNotIn(self.aci_lipg_2, qs)

    def test_q_name_alias(self) -> None:
        """Test q search matches the name_alias field."""
        params = {"q": "ACIFSTestLIPG1Alias"}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_lipg_1, qs)
        self.assertNotIn(self.aci_lipg_2, qs)

    def test_search_with_whitespace_only_returns_all(self) -> None:
        """Test search() with whitespace-only returns the full queryset."""
        qs = self.queryset
        fs = self.filterset(queryset=qs)
        result = fs.search(qs, "q", "   ")
        self.assertEqual(result.count(), qs.count())

    def test_group_type(self) -> None:
        """Test filtering by the group type."""
        params = {"group_type": [LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_lipg_1, qs)
        self.assertNotIn(self.aci_lipg_2, qs)

    def test_aci_aaep(self) -> None:
        """Test filtering by the ACI AAEP name."""
        params = {"aci_aaep": [self.aci_aaep.name]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_lipg_1, qs)
        self.assertNotIn(self.aci_lipg_2, qs)

    def test_aci_aaep_id(self) -> None:
        """Test filtering by the ACI AAEP ID."""
        params = {"aci_aaep_id": [self.aci_aaep.pk]}
        qs = self.filterset(params, self.queryset).qs
        self.assertIn(self.aci_lipg_1, qs)
        self.assertNotIn(self.aci_lipg_2, qs)
