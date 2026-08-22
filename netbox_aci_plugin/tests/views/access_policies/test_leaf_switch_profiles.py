# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the access policies ACI Leaf Switch Profile models."""

from django.db import connection
from django.test.utils import CaptureQueriesContext

from core.models import ObjectType
from extras.models import Tag
from users.models import ObjectPermission
from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....choices import NodeRoleChoices
from ....models.access_policies.leaf_interface_profiles import (
    ACILeafInterfaceProfile,
)
from ....models.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlock,
    ACILeafSelector,
    ACILeafSwitchProfile,
    ACILeafSwitchProfileInterfaceBinding,
)
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ....views.access_policies.leaf_switch_profiles import (
    ACILeafNodeBlockListView,
    ACILeafSelectorListView,
)
from ..base import ACIModelViewTestCase


class ACILeafSwitchProfileViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACILeafSwitchProfile."""

    model = ACILeafSwitchProfile

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafSwitchProfile view tests."""
        super().setUpTestData()

        # 3 ACILeafSwitchProfile instances under the shared base fabric.
        ACILeafSwitchProfile.objects.create(
            name="ACIViewTestProfile1", aci_fabric=cls.aci_fabric
        )
        ACILeafSwitchProfile.objects.create(
            name="ACIViewTestProfile2", aci_fabric=cls.aci_fabric
        )
        ACILeafSwitchProfile.objects.create(
            name="ACIViewTestProfile3", aci_fabric=cls.aci_fabric
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestProfileX",
            "name_alias": "ProfileXAlias",
            "description": "Form-data Leaf Switch Profile",
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

        profiles = list(ACILeafSwitchProfile.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{profiles[0].pk},Updated Leaf Switch Profile 1",
            f"{profiles[1].pk},Updated Leaf Switch Profile 2",
            f"{profiles[2].pk},Updated Leaf Switch Profile 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Leaf Switch Profile"}

    def test_acileafswitchprofile_leafselectors_tab(self) -> None:
        """Selectors tab renders the registered Add button."""
        instance = ACILeafSwitchProfile.objects.first()
        self.add_permissions(
            "netbox_aci_plugin.view_acileafswitchprofile",
            "netbox_aci_plugin.view_acileafselector",
            "netbox_aci_plugin.add_acileafselector",
        )
        url = get_action_url(
            instance, action="leafselectors", kwargs={"pk": instance.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACILeafSelector, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={instance.aci_fabric_id}&amp;'
            f"aci_leaf_switch_profile={instance.pk}",
        )

    def test_acileafswitchprofile_interfaceprofilebindings_tab(self) -> None:
        """Interface Profiles tab lists only Bindings of this Profile."""
        instance = ACILeafSwitchProfile.objects.get(name="ACIViewTestProfile1")
        other_profile = ACILeafSwitchProfile.objects.get(name="ACIViewTestProfile2")
        interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACIViewTestProfileTabInterfaceProfile", aci_fabric=self.aci_fabric
        )
        other_interface_profile = ACILeafInterfaceProfile.objects.create(
            name="ACIViewTestProfileTabForeignInterfaceProfile",
            aci_fabric=self.aci_fabric,
        )
        ACILeafSwitchProfileInterfaceBinding.objects.create(
            aci_leaf_switch_profile=instance,
            aci_leaf_interface_profile=interface_profile,
        )
        ACILeafSwitchProfileInterfaceBinding.objects.create(
            aci_leaf_switch_profile=other_profile,
            aci_leaf_interface_profile=other_interface_profile,
        )
        self.add_permissions(
            "netbox_aci_plugin.view_acileafswitchprofile",
            "netbox_aci_plugin.view_acileafswitchprofileinterfacebinding",
            "netbox_aci_plugin.add_acileafswitchprofileinterfacebinding",
        )
        url = get_action_url(
            instance, action="interfaceprofilebindings", kwargs={"pk": instance.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACILeafSwitchProfileInterfaceBinding, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={instance.aci_fabric_id}&amp;'
            f"aci_leaf_switch_profile={instance.pk}",
        )
        self.assertContains(response, interface_profile.name)
        self.assertNotContains(response, other_interface_profile.name)
        self.assertFalse(
            response.context["table"].columns["aci_leaf_switch_profile"].visible
        )


class ACILeafSelectorViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACILeafSelector."""

    model = ACILeafSelector

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafSelector view tests."""
        super().setUpTestData()

        cls.aci_pod = ACIPod.objects.create(
            name="ACIViewTestSelectorPod", aci_fabric=cls.aci_fabric, pod_id=1
        )
        cls.visible_node = ACINode.objects.create(
            name="ACIViewTestSelectorVisibleNode",
            aci_pod=cls.aci_pod,
            node_id=101,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.hidden_node = ACINode.objects.create(
            name="ACIViewTestSelectorHiddenNode",
            aci_pod=cls.aci_pod,
            node_id=102,
            role=NodeRoleChoices.ROLE_LEAF,
        )

        cls.aci_leaf_switch_profile = ACILeafSwitchProfile.objects.create(
            name="ACIViewTestSelectorProfile", aci_fabric=cls.aci_fabric
        )

        # 3 ACILeafSelector instances under the shared profile.
        cls.aci_leaf_selector1 = ACILeafSelector.objects.create(
            name="ACIViewTestSelector1",
            aci_leaf_switch_profile=cls.aci_leaf_switch_profile,
        )
        cls.aci_leaf_selector2 = ACILeafSelector.objects.create(
            name="ACIViewTestSelector2",
            aci_leaf_switch_profile=cls.aci_leaf_switch_profile,
        )
        cls.aci_leaf_selector3 = ACILeafSelector.objects.create(
            name="ACIViewTestSelector3",
            aci_leaf_switch_profile=cls.aci_leaf_switch_profile,
        )

        # Node Block counts of 2, 1 and 0: deliberately unequal so a
        # count-based sort must reorder the selectors relative to the
        # model's default name ordering. Selector 1's first block spans
        # both ACI Nodes above, so only a permission can filter them apart.
        ACILeafNodeBlock.objects.create(
            name="ACIViewTestSelectorBlock11",
            aci_leaf_selector=cls.aci_leaf_selector1,
            node_id_from=101,
            node_id_to=102,
        )
        ACILeafNodeBlock.objects.create(
            name="ACIViewTestSelectorBlock12",
            aci_leaf_selector=cls.aci_leaf_selector1,
            node_id_from=103,
            node_id_to=103,
        )
        ACILeafNodeBlock.objects.create(
            name="ACIViewTestSelectorBlock21",
            aci_leaf_selector=cls.aci_leaf_selector2,
            node_id_from=104,
            node_id_to=104,
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestSelectorX",
            "name_alias": "SelectorXAlias",
            "description": "Form-data Leaf Selector",
            "aci_leaf_switch_profile": cls.aci_leaf_switch_profile.pk,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        profile = cls.aci_leaf_switch_profile.name
        cls.csv_data = (
            "name,aci_fabric,aci_leaf_switch_profile",
            f"ACIViewTestSelector4,{fabric},{profile}",
            f"ACIViewTestSelector5,{fabric},{profile}",
            f"ACIViewTestSelector6,{fabric},{profile}",
        )

        selectors = list(ACILeafSelector.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{selectors[0].pk},Updated Leaf Selector 1",
            f"{selectors[1].pk},Updated Leaf Selector 2",
            f"{selectors[2].pk},Updated Leaf Selector 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Leaf Selector"}

    def test_acileafselector_leafnodeblocks_tab(self) -> None:
        """Node Blocks tab renders the registered Add button."""
        instance = ACILeafSelector.objects.first()
        self.add_permissions(
            "netbox_aci_plugin.view_acileafselector",
            "netbox_aci_plugin.view_acileafnodeblock",
            "netbox_aci_plugin.add_acileafnodeblock",
        )
        url = get_action_url(
            instance, action="leafnodeblocks", kwargs={"pk": instance.pk}
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACILeafNodeBlock, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={instance.aci_leaf_switch_profile.aci_fabric_id}&amp;'
            f"aci_leaf_switch_profile={instance.aci_leaf_switch_profile_id}&amp;"
            f"aci_leaf_selector={instance.pk}",
        )

    def test_acileafselector_detail_restricts_aci_nodes(self) -> None:
        """The detail page hides ACI Nodes the user cannot view."""
        self.add_permissions("netbox_aci_plugin.view_acileafselector")
        obj_perm = ObjectPermission(
            name="Test view ACINode 101",
            actions=["view"],
            constraints={"node_id": 101},
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(ACINode))

        response = self.client.get(self.aci_leaf_selector1.get_absolute_url())
        self.assertHttpStatus(response, 200)
        self.assertContains(response, self.visible_node.name)
        self.assertNotContains(response, self.hidden_node.name)

    def test_acileafselector_node_block_count_zero_for_empty_selector(self) -> None:
        """A selector holding no Node Blocks annotates the count to 0."""
        annotated = ACILeafSelectorListView.queryset.get(pk=self.aci_leaf_selector3.pk)
        self.assertEqual(annotated.aci_leaf_node_block_count, 0)

    def test_acileafselector_node_block_count_survives_multi_valued_join(self) -> None:
        """A second multi-valued join must not inflate the Node Block count.

        NetBox's own TagFilter is conjoined, so the list view cannot
        currently produce such a join. This pins the annotation against a
        filter that later joins a to-many relation with OR semantics.
        """
        tags = Tag.objects.filter(name__in=("Alpha", "Bravo"))
        self.aci_leaf_selector1.tags.set(tags)

        annotated = (
            ACILeafSelectorListView.queryset.filter(
                tags__slug__in=[t.slug for t in tags]
            )
            .distinct()
            .get(pk=self.aci_leaf_selector1.pk)
        )
        self.assertEqual(annotated.aci_leaf_node_block_count, 2)

    def test_acileafselector_node_block_count_orderable(self) -> None:
        """The node block count column sorts correctly in the list view."""
        self.add_permissions("netbox_aci_plugin.view_acileafselector")
        url = get_action_url(ACILeafSelector, action="list")

        response = self.client.get(url, data={"sort": "aci_leaf_node_block_count"})
        self.assertHttpStatus(response, 200)
        ordered_names = [row.record.name for row in response.context["table"].rows]

        # Counts 0, 1, 2 reverse the model's default name ordering.
        self.assertEqual(
            ordered_names,
            [
                self.aci_leaf_selector3.name,
                self.aci_leaf_selector2.name,
                self.aci_leaf_selector1.name,
            ],
        )


class ACILeafNodeBlockViewTestCase(
    ACIModelViewTestCase, ViewTestCases.PrimaryObjectViewTestCase
):
    """Standard view tests for ACILeafNodeBlock."""

    model = ACILeafNodeBlock

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACILeafNodeBlock view tests."""
        super().setUpTestData()

        cls.aci_pod = ACIPod.objects.create(
            name="ACIViewTestBlockPod", aci_fabric=cls.aci_fabric, pod_id=1
        )
        # Leaf Nodes 101 and 102 fall in block 1, 105 in block 2, none in
        # block 3: unequal coverage so a count-based sort must reorder the
        # blocks relative to the model's default node_id_from ordering.
        cls.visible_node = ACINode.objects.create(
            name="ACIViewTestBlockVisibleNode",
            aci_pod=cls.aci_pod,
            node_id=101,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        cls.hidden_node = ACINode.objects.create(
            name="ACIViewTestBlockHiddenNode",
            aci_pod=cls.aci_pod,
            node_id=102,
            role=NodeRoleChoices.ROLE_LEAF,
        )
        ACINode.objects.create(
            name="ACIViewTestBlockNode105",
            aci_pod=cls.aci_pod,
            node_id=105,
            role=NodeRoleChoices.ROLE_LEAF,
        )

        cls.aci_leaf_switch_profile = ACILeafSwitchProfile.objects.create(
            name="ACIViewTestBlockProfile", aci_fabric=cls.aci_fabric
        )
        cls.aci_leaf_selector = ACILeafSelector.objects.create(
            name="ACIViewTestBlockSelector",
            aci_leaf_switch_profile=cls.aci_leaf_switch_profile,
        )

        # 3 non-overlapping Node Block instances under the shared selector.
        cls.aci_leaf_node_block1 = ACILeafNodeBlock.objects.create(
            name="ACIViewTestBlock1",
            aci_leaf_selector=cls.aci_leaf_selector,
            node_id_from=101,
            node_id_to=104,
        )
        cls.aci_leaf_node_block2 = ACILeafNodeBlock.objects.create(
            name="ACIViewTestBlock2",
            aci_leaf_selector=cls.aci_leaf_selector,
            node_id_from=105,
            node_id_to=108,
        )
        cls.aci_leaf_node_block3 = ACILeafNodeBlock.objects.create(
            name="ACIViewTestBlock3",
            aci_leaf_selector=cls.aci_leaf_selector,
            node_id_from=109,
            node_id_to=112,
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACIViewTestBlockX",
            "name_alias": "BlockXAlias",
            "description": "Form-data Leaf Node Block",
            "aci_leaf_selector": cls.aci_leaf_selector.pk,
            "node_id_from": 200,
            "node_id_to": 210,
            "nb_tenant": cls.nb_tenant.pk,
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        profile = cls.aci_leaf_switch_profile.name
        selector = cls.aci_leaf_selector.name
        cls.csv_data = (
            (
                "name,aci_fabric,aci_leaf_switch_profile,aci_leaf_selector,"
                "node_id_from,node_id_to"
            ),
            f"ACIViewTestBlock4,{fabric},{profile},{selector},301,304",
            f"ACIViewTestBlock5,{fabric},{profile},{selector},305,308",
            f"ACIViewTestBlock6,{fabric},{profile},{selector},309,312",
        )

        blocks = list(ACILeafNodeBlock.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{blocks[0].pk},Updated Leaf Node Block 1",
            f"{blocks[1].pk},Updated Leaf Node Block 2",
            f"{blocks[2].pk},Updated Leaf Node Block 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Leaf Node Block"}

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

    def _add_node_blocks(self, prefix: str, node_id_from: int, count: int) -> None:
        """Create count further ACILeafNodeBlock rows under the selector."""
        for index in range(count):
            ACILeafNodeBlock.objects.create(
                name=f"{prefix}{index}",
                aci_leaf_selector=self.aci_leaf_selector,
                node_id_from=node_id_from + index,
                node_id_to=node_id_from + index,
            )

    def test_acileafnodeblock_detail_restricts_aci_nodes(self) -> None:
        """The detail page hides ACI Nodes the user cannot view."""
        self.add_permissions("netbox_aci_plugin.view_acileafnodeblock")
        obj_perm = ObjectPermission(
            name="Test view ACINode 101",
            actions=["view"],
            constraints={"node_id": 101},
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(ACINode))

        response = self.client.get(self.aci_leaf_node_block1.get_absolute_url())
        self.assertHttpStatus(response, 200)
        self.assertContains(response, self.visible_node.name)
        self.assertNotContains(response, self.hidden_node.name)

    def test_acileafnodeblock_list_query_count_constant(self) -> None:
        """List view query count must not scale with row count (3 vs 6)."""
        self.add_permissions("netbox_aci_plugin.view_acileafnodeblock")
        url = get_action_url(ACILeafNodeBlock, action="list")
        three_rows = self._query_count(url)

        self._add_node_blocks("ACIViewTestBlockListExtra", 3000, 3)
        six_rows = self._query_count(url)

        self.assertEqual(
            three_rows,
            six_rows,
            "Query count grew with row count on the Node Block list view.",
        )

    def test_acileafnodeblock_leafnodeblocks_tab_query_count_constant(self) -> None:
        """Node Blocks tab query count must not scale with row count."""
        self.add_permissions(
            "netbox_aci_plugin.view_acileafselector",
            "netbox_aci_plugin.view_acileafnodeblock",
            "netbox_aci_plugin.add_acileafnodeblock",
        )
        url = get_action_url(
            self.aci_leaf_selector,
            action="leafnodeblocks",
            kwargs={"pk": self.aci_leaf_selector.pk},
        )
        three_rows = self._query_count(url)

        self._add_node_blocks("ACIViewTestBlockTabExtra", 3100, 3)
        six_rows = self._query_count(url)

        self.assertEqual(
            three_rows,
            six_rows,
            "Query count grew with row count on the Node Blocks tab.",
        )

    def test_acileafnodeblock_aci_node_count_zero_for_empty_block(self) -> None:
        """A block covering no ACI Nodes annotates aci_node_count to 0."""
        annotated = ACILeafNodeBlockListView.queryset.get(
            pk=self.aci_leaf_node_block3.pk
        )
        self.assertEqual(annotated.aci_node_count, 0)

    def test_acileafnodeblock_aci_node_count_orderable(self) -> None:
        """The aci_node_count column sorts correctly in the list view."""
        self.add_permissions("netbox_aci_plugin.view_acileafnodeblock")
        url = get_action_url(ACILeafNodeBlock, action="list")

        response = self.client.get(url, data={"sort": "aci_node_count"})
        self.assertHttpStatus(response, 200)
        ordered_names = [row.record.name for row in response.context["table"].rows]

        # Counts 0, 1, 2 reverse the model's default node_id_from ordering.
        self.assertEqual(
            ordered_names,
            [
                self.aci_leaf_node_block3.name,
                self.aci_leaf_node_block2.name,
                self.aci_leaf_node_block1.name,
            ],
        )


class ACILeafSwitchProfileInterfaceBindingViewTestCase(
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
    """Standard view tests for ACILeafSwitchProfileInterfaceBinding.

    ``BulkRenameObjectsViewTestCase`` is intentionally excluded - the
    binding has no ``name`` field.
    """

    model = ACILeafSwitchProfileInterfaceBinding

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACI Profile Binding view tests."""
        super().setUpTestData()

        cls.switch_profiles = [
            ACILeafSwitchProfile.objects.create(
                name=f"ACIViewTestBindingSwitchProfile{i}", aci_fabric=cls.aci_fabric
            )
            for i in range(1, 7)
        ]
        cls.interface_profiles = [
            ACILeafInterfaceProfile.objects.create(
                name=f"ACIViewTestBindingInterfaceProfile{i}", aci_fabric=cls.aci_fabric
            )
            for i in range(1, 7)
        ]

        # 3 existing binding instances for GET / edit / delete / list / bulk
        ACILeafSwitchProfileInterfaceBinding.objects.create(
            aci_leaf_switch_profile=cls.switch_profiles[0],
            aci_leaf_interface_profile=cls.interface_profiles[0],
        )
        ACILeafSwitchProfileInterfaceBinding.objects.create(
            aci_leaf_switch_profile=cls.switch_profiles[1],
            aci_leaf_interface_profile=cls.interface_profiles[1],
        )
        ACILeafSwitchProfileInterfaceBinding.objects.create(
            aci_leaf_switch_profile=cls.switch_profiles[2],
            aci_leaf_interface_profile=cls.interface_profiles[2],
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        # Pair 4 is unused, so create and edit satisfy the unique constraint
        cls.form_data = {
            "aci_leaf_switch_profile": cls.switch_profiles[3].pk,
            "aci_leaf_interface_profile": cls.interface_profiles[3].pk,
            "comments": "Form-data binding",
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        cls.csv_data = (
            "aci_fabric,aci_leaf_switch_profile,aci_leaf_interface_profile",
            (
                f"{fabric},{cls.switch_profiles[3].name},"
                f"{cls.interface_profiles[3].name}"
            ),
            (
                f"{fabric},{cls.switch_profiles[4].name},"
                f"{cls.interface_profiles[4].name}"
            ),
            (
                f"{fabric},{cls.switch_profiles[5].name},"
                f"{cls.interface_profiles[5].name}"
            ),
        )

        bindings = list(ACILeafSwitchProfileInterfaceBinding.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,comments",
            f"{bindings[0].pk},Updated binding 1",
            f"{bindings[1].pk},Updated binding 2",
            f"{bindings[2].pk},Updated binding 3",
        )

        # Setting either FK on all three would collide on the unique pair
        cls.bulk_edit_data = {"comments": "Bulk-edited comment"}
