# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the access policies ACI Leaf Interface Profile models."""

from django.db import connection
from django.test.utils import CaptureQueriesContext

from extras.models import Tag
from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....choices import LeafInterfacePolicyGroupTypeChoices
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ....models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
    ACILeafInterfaceSelector,
    ACILeafPortBlock,
)
from ....models.access_policies.leaf_switch_profiles import (
    ACILeafSwitchProfile,
    ACILeafSwitchProfileInterfaceBinding,
)
from ....views.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceSelectorListView,
)
from ..base import ACIModelViewTestCase


class ACILeafInterfaceProfileViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACILeafInterfaceProfile."""

    model = ACILeafInterfaceProfile

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafInterfaceProfile view tests."""
        super().setUpTestData()

        # 3 ACILeafInterfaceProfile instances under the shared base fabric.
        ACILeafInterfaceProfile.objects.create(
            name="ACIViewTestProfile1", aci_fabric=cls.aci_fabric
        )
        ACILeafInterfaceProfile.objects.create(
            name="ACIViewTestProfile2", aci_fabric=cls.aci_fabric
        )
        ACILeafInterfaceProfile.objects.create(
            name="ACIViewTestProfile3", aci_fabric=cls.aci_fabric
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestProfileX",
            "name_alias": "ProfileXAlias",
            "description": "Form-data Leaf Interface Profile",
            "aci_fabric": cls.aci_fabric.pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        cls.csv_data = (
            "name,aci_fabric",
            f"ACIViewTestProfile4,{fabric}",
            f"ACIViewTestProfile5,{fabric}",
            f"ACIViewTestProfile6,{fabric}",
        )

        profiles = list(ACILeafInterfaceProfile.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{profiles[0].pk},Updated Leaf Interface Profile 1",
            f"{profiles[1].pk},Updated Leaf Interface Profile 2",
            f"{profiles[2].pk},Updated Leaf Interface Profile 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Leaf Interface Profile"}

    def test_acileafinterfaceprofile_leafinterfaceselectors_tab(self) -> None:
        """Selectors tab renders the registered Add button."""
        instance = ACILeafInterfaceProfile.objects.first()
        self.add_permissions(
            "netbox_aci_plugin.view_acileafinterfaceprofile",
            "netbox_aci_plugin.view_acileafinterfaceselector",
            "netbox_aci_plugin.add_acileafinterfaceselector",
        )
        url = get_action_url(
            instance, action="leafinterfaceselectors", kwargs={"pk": instance.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACILeafInterfaceSelector, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={instance.aci_fabric_id}&amp;'
            f"aci_leaf_interface_profile={instance.pk}",
        )

    def test_acileafinterfaceprofile_switchprofilebindings_tab(self) -> None:
        """Switch Profiles tab lists only Bindings of this Profile."""
        instance = ACILeafInterfaceProfile.objects.get(name="ACIViewTestProfile1")
        other_profile = ACILeafInterfaceProfile.objects.get(name="ACIViewTestProfile2")
        switch_profile = ACILeafSwitchProfile.objects.create(
            name="ACIViewTestProfileTabSwitchProfile", aci_fabric=self.aci_fabric
        )
        other_switch_profile = ACILeafSwitchProfile.objects.create(
            name="ACIViewTestProfileTabForeignSwitchProfile",
            aci_fabric=self.aci_fabric,
        )
        ACILeafSwitchProfileInterfaceBinding.objects.create(
            aci_leaf_switch_profile=switch_profile,
            aci_leaf_interface_profile=instance,
        )
        ACILeafSwitchProfileInterfaceBinding.objects.create(
            aci_leaf_switch_profile=other_switch_profile,
            aci_leaf_interface_profile=other_profile,
        )
        self.add_permissions(
            "netbox_aci_plugin.view_acileafinterfaceprofile",
            "netbox_aci_plugin.view_acileafswitchprofileinterfacebinding",
            "netbox_aci_plugin.add_acileafswitchprofileinterfacebinding",
        )
        url = get_action_url(
            instance, action="switchprofilebindings", kwargs={"pk": instance.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACILeafSwitchProfileInterfaceBinding, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={instance.aci_fabric_id}&amp;'
            f"aci_leaf_interface_profile={instance.pk}",
        )
        self.assertContains(response, switch_profile.name)
        self.assertNotContains(response, other_switch_profile.name)
        self.assertFalse(
            response.context["table"].columns["aci_leaf_interface_profile"].visible
        )


class ACILeafInterfaceSelectorViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACILeafInterfaceSelector."""

    model = ACILeafInterfaceSelector

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafInterfaceSelector view tests."""
        super().setUpTestData()

        cls.aci_leaf_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACIViewTestSelectorProfile", aci_fabric=cls.aci_fabric
        )
        cls.aci_leaf_interface_policy_group = (
            ACILeafInterfacePolicyGroup.objects.create(
                name="ACIViewTestSelectorPolicyGroup",
                aci_fabric=cls.aci_fabric,
                group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
            )
        )

        # 3 ACILeafInterfaceSelector instances under the shared profile.
        cls.aci_leaf_interface_selector1 = ACILeafInterfaceSelector.objects.create(
            name="ACIViewTestSelector1",
            aci_leaf_interface_profile=cls.aci_leaf_interface_profile,
        )
        cls.aci_leaf_interface_selector2 = ACILeafInterfaceSelector.objects.create(
            name="ACIViewTestSelector2",
            aci_leaf_interface_profile=cls.aci_leaf_interface_profile,
        )
        cls.aci_leaf_interface_selector3 = ACILeafInterfaceSelector.objects.create(
            name="ACIViewTestSelector3",
            aci_leaf_interface_profile=cls.aci_leaf_interface_profile,
        )

        # Port Block counts of 2, 1 and 0: deliberately unequal so a
        # count-based sort must reorder the selectors relative to the
        # model's default name ordering.
        ACILeafPortBlock.objects.create(
            name="ACIViewTestSelectorBlock11",
            aci_leaf_interface_selector=cls.aci_leaf_interface_selector1,
            module_from=1,
            module_to=1,
            port_from=1,
            port_to=1,
        )
        ACILeafPortBlock.objects.create(
            name="ACIViewTestSelectorBlock12",
            aci_leaf_interface_selector=cls.aci_leaf_interface_selector1,
            module_from=1,
            module_to=1,
            port_from=2,
            port_to=2,
        )
        ACILeafPortBlock.objects.create(
            name="ACIViewTestSelectorBlock21",
            aci_leaf_interface_selector=cls.aci_leaf_interface_selector2,
            module_from=1,
            module_to=1,
            port_from=1,
            port_to=1,
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestSelectorX",
            "name_alias": "SelectorXAlias",
            "description": "Form-data Leaf Interface Selector",
            "aci_leaf_interface_profile": cls.aci_leaf_interface_profile.pk,
            "aci_leaf_interface_policy_group": cls.aci_leaf_interface_policy_group.pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        profile = cls.aci_leaf_interface_profile.name
        cls.csv_data = (
            "name,aci_fabric,aci_leaf_interface_profile",
            f"ACIViewTestSelector4,{fabric},{profile}",
            f"ACIViewTestSelector5,{fabric},{profile}",
            f"ACIViewTestSelector6,{fabric},{profile}",
        )

        selectors = list(ACILeafInterfaceSelector.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{selectors[0].pk},Updated Leaf Interface Selector 1",
            f"{selectors[1].pk},Updated Leaf Interface Selector 2",
            f"{selectors[2].pk},Updated Leaf Interface Selector 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Leaf Interface Selector"}

    def test_acileafinterfaceselector_leafportblocks_tab(self) -> None:
        """Port Blocks tab renders the registered Add button."""
        instance = ACILeafInterfaceSelector.objects.first()
        self.add_permissions(
            "netbox_aci_plugin.view_acileafinterfaceselector",
            "netbox_aci_plugin.view_acileafportblock",
            "netbox_aci_plugin.add_acileafportblock",
        )
        url = get_action_url(
            instance, action="leafportblocks", kwargs={"pk": instance.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACILeafPortBlock, action="add")
        fabric_id = instance.aci_leaf_interface_profile.aci_fabric_id
        profile_id = instance.aci_leaf_interface_profile_id
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={fabric_id}&amp;'
            f"aci_leaf_interface_profile={profile_id}&amp;"
            f"aci_leaf_interface_selector={instance.pk}",
        )

    def test_acileafinterfaceselector_port_block_count_zero_for_empty_selector(
        self,
    ) -> None:
        """A selector holding no Port Blocks annotates the count to 0."""
        annotated = ACILeafInterfaceSelectorListView.queryset.get(
            pk=self.aci_leaf_interface_selector3.pk
        )
        self.assertEqual(annotated.aci_leaf_port_block_count, 0)

    def test_acileafinterfaceselector_port_block_count_survives_multi_valued_join(
        self,
    ) -> None:
        """A second multi-valued join must not inflate the Port Block count.

        NetBox's own TagFilter is conjoined, so the list view cannot
        currently produce such a join. This pins the annotation against a
        filter that later joins a to-many relation with OR semantics.
        """
        tags = Tag.objects.filter(name__in=("Alpha", "Bravo"))
        self.aci_leaf_interface_selector1.tags.set(tags)

        annotated = (
            ACILeafInterfaceSelectorListView.queryset.filter(
                tags__slug__in=[t.slug for t in tags]
            )
            .distinct()
            .get(pk=self.aci_leaf_interface_selector1.pk)
        )
        self.assertEqual(annotated.aci_leaf_port_block_count, 2)

    def test_acileafinterfaceselector_port_block_count_orderable(self) -> None:
        """The port block count column sorts correctly in the list view."""
        self.add_permissions("netbox_aci_plugin.view_acileafinterfaceselector")
        url = get_action_url(ACILeafInterfaceSelector, action="list")

        response = self.client.get(url, data={"sort": "aci_leaf_port_block_count"})
        self.assertHttpStatus(response, 200)
        ordered_names = [row.record.name for row in response.context["table"].rows]

        # Counts 0, 1, 2 reverse the model's default name ordering.
        self.assertEqual(
            ordered_names,
            [
                self.aci_leaf_interface_selector3.name,
                self.aci_leaf_interface_selector2.name,
                self.aci_leaf_interface_selector1.name,
            ],
        )


class ACILeafPortBlockViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACILeafPortBlock."""

    model = ACILeafPortBlock

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafPortBlock view tests."""
        super().setUpTestData()

        cls.aci_leaf_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACIViewTestBlockProfile", aci_fabric=cls.aci_fabric
        )
        cls.aci_leaf_interface_selector = ACILeafInterfaceSelector.objects.create(
            name="ACIViewTestBlockSelector",
            aci_leaf_interface_profile=cls.aci_leaf_interface_profile,
        )

        # 3 Leaf Port Block instances under the shared selector.
        cls.aci_leaf_port_block1 = ACILeafPortBlock.objects.create(
            name="ACIViewTestBlock1",
            aci_leaf_interface_selector=cls.aci_leaf_interface_selector,
            module_from=1,
            module_to=1,
            port_from=1,
            port_to=4,
        )
        cls.aci_leaf_port_block2 = ACILeafPortBlock.objects.create(
            name="ACIViewTestBlock2",
            aci_leaf_interface_selector=cls.aci_leaf_interface_selector,
            module_from=1,
            module_to=1,
            port_from=5,
            port_to=8,
        )
        cls.aci_leaf_port_block3 = ACILeafPortBlock.objects.create(
            name="ACIViewTestBlock3",
            aci_leaf_interface_selector=cls.aci_leaf_interface_selector,
            module_from=1,
            module_to=1,
            port_from=9,
            port_to=12,
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestBlockX",
            "name_alias": "BlockXAlias",
            "description": "Form-data Leaf Port Block",
            "aci_leaf_interface_selector": cls.aci_leaf_interface_selector.pk,
            "module_from": 2,
            "module_to": 2,
            "port_from": 1,
            "port_to": 10,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        profile = cls.aci_leaf_interface_profile.name
        selector = cls.aci_leaf_interface_selector.name
        cls.csv_data = (
            (
                "name,aci_fabric,aci_leaf_interface_profile,"
                "aci_leaf_interface_selector,module_from,module_to,"
                "port_from,port_to"
            ),
            f"ACIViewTestBlock4,{fabric},{profile},{selector},1,1,13,16",
            f"ACIViewTestBlock5,{fabric},{profile},{selector},1,1,17,20",
            f"ACIViewTestBlock6,{fabric},{profile},{selector},1,1,21,24",
        )

        blocks = list(ACILeafPortBlock.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{blocks[0].pk},Updated Leaf Port Block 1",
            f"{blocks[1].pk},Updated Leaf Port Block 2",
            f"{blocks[2].pk},Updated Leaf Port Block 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Leaf Port Block"}

    def _query_count(self, url) -> int:
        """Return the query count of a table-only GET request to url.

        The htmx partial path, the same one a real sort or pagination
        click uses, renders the table without the surrounding page. A
        full-page render also counts chrome queries, which vary with
        per-process caching and make the measurement order-sensitive.
        """
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url, headers={"HX-Request": "true"})
        self.assertHttpStatus(response, 200)
        return len(ctx.captured_queries)

    def _add_port_blocks(self, prefix: str, count: int) -> None:
        """Create count further ACILeafPortBlock rows under the selector."""
        for index in range(count):
            ACILeafPortBlock.objects.create(
                name=f"{prefix}{index}",
                aci_leaf_interface_selector=self.aci_leaf_interface_selector,
                module_from=1,
                module_to=1,
                port_from=1,
                port_to=1,
            )

    def test_acileafportblock_list_query_count_constant(self) -> None:
        """List view query count must not scale with row count (3 vs 6)."""
        self.add_permissions("netbox_aci_plugin.view_acileafportblock")
        url = get_action_url(ACILeafPortBlock, action="list")
        three_rows = self._query_count(url)

        self._add_port_blocks("ACIViewTestBlockListExtra", 3)
        six_rows = self._query_count(url)

        self.assertEqual(
            three_rows,
            six_rows,
            "Query count grew with row count on the Port Block list view.",
        )

    def test_acileafportblock_leafportblocks_tab_query_count_constant(self) -> None:
        """Port Blocks tab query count must not scale with row count."""
        self.add_permissions(
            "netbox_aci_plugin.view_acileafinterfaceselector",
            "netbox_aci_plugin.view_acileafportblock",
            "netbox_aci_plugin.add_acileafportblock",
        )
        url = get_action_url(
            self.aci_leaf_interface_selector,
            action="leafportblocks",
            kwargs={"pk": self.aci_leaf_interface_selector.pk},
        )
        three_rows = self._query_count(url)

        self._add_port_blocks("ACIViewTestBlockTabExtra", 3)
        six_rows = self._query_count(url)

        self.assertEqual(
            three_rows,
            six_rows,
            "Query count grew with row count on the Port Blocks tab.",
        )
