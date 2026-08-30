# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the fabric ACI Node Interface model."""

from urllib.parse import parse_qs, urlparse

from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext

from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from utilities.testing import ViewTestCases, create_tags
from utilities.views import get_action_url

from ....choices import LeafInterfacePolicyGroupTypeChoices, NodeRoleChoices
from ....models.access_policies.interface_policy_groups import (
    ACILeafInterfacePolicyGroup,
)
from ....models.access_policies.leaf_interface_overrides import (
    ACILeafInterfaceOverride,
)
from ....models.fabric.node_interfaces import ACINodeInterface
from ....models.fabric.nodes import ACINode
from ....models.fabric.pods import ACIPod
from ....ui.panels.fabric.node_interfaces import ACINodeInterfaceOverridePanel
from ....views.fabric.node_interfaces import ACINodeInterfaceChildrenView
from ..base import ACIModelViewTestCase


class ACINodeInterfaceViewTestCase(
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
    """Standard view tests for ACINodeInterface.

    ``BulkRenameObjectsViewTestCase`` is intentionally excluded - the
    model has no ``name`` field.
    """

    model = ACINodeInterface

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACINodeInterface view tests."""
        super().setUpTestData()

        cls.aci_pod = ACIPod.objects.create(
            name="ACIViewTestNodeInterfacePod", aci_fabric=cls.aci_fabric, pod_id=1
        )

        site = Site.objects.create(
            name="ACIViewTestNodeInterfaceSite", slug="acivt-leaf-iface"
        )
        manufacturer = Manufacturer.objects.create(
            name="ACIViewTestNodeInterfaceMfr", slug="acivt-leaf-iface-mfr"
        )
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model="ACIViewTestNodeInterfaceDeviceType",
            slug="acivt-leaf-iface-dt",
        )
        device_role = DeviceRole.objects.create(
            name="ACIViewTestNodeInterfaceRole", slug="acivt-leaf-iface-role"
        )
        cls.device = Device.objects.create(
            name="ACIViewTestNodeInterfaceDevice",
            device_type=device_type,
            role=device_role,
            site=site,
        )

        cls.aci_node = ACINode.objects.create(
            name="ACIViewTestNodeInterfaceNode",
            aci_pod=cls.aci_pod,
            node_id=101,
            node_object=cls.device,
            role="leaf",
            node_type="unknown",
        )
        cls.aci_node_spine = ACINode.objects.create(
            name="ACIViewTestNodeInterfaceNodeSpine",
            aci_pod=cls.aci_pod,
            node_id=201,
            role=NodeRoleChoices.ROLE_SPINE,
            node_type="unknown",
        )
        cls.aci_node_apic = ACINode.objects.create(
            name="ACIViewTestNodeInterfaceNodeApic",
            aci_pod=cls.aci_pod,
            node_id=1,
            role=NodeRoleChoices.ROLE_APIC,
            node_type="unknown",
        )

        interfaces = [
            Interface.objects.create(
                device=cls.device,
                name=f"eth1/{i}",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            )
            for i in range(1, 5)
        ]

        ACINodeInterface.objects.create(
            aci_node=cls.aci_node, module=1, port=1, nb_interface=interfaces[0]
        )
        ACINodeInterface.objects.create(
            aci_node=cls.aci_node, module=1, port=2, nb_interface=interfaces[1]
        )
        ACINodeInterface.objects.create(
            aci_node=cls.aci_node, module=1, port=3, nb_interface=interfaces[2]
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "aci_node": cls.aci_node.pk,
            "nb_interface": interfaces[3].pk,
            "module": 1,
            "port": 4,
            "sub_port": 0,
            "description": "Form-data Node Interface",
            "tags": [t.pk for t in tags],
        }

        fabric = cls.aci_fabric.name
        pod = cls.aci_pod.name
        node = cls.aci_node.name
        cls.csv_data = (
            "aci_fabric,aci_pod,aci_node,module,port,sub_port,description",
            f"{fabric},{pod},{node},1,10,0,CSV Node Interface 1",
            f"{fabric},{pod},{node},1,11,0,CSV Node Interface 2",
            f"{fabric},{pod},{node},1,12,0,CSV Node Interface 3",
        )

        node_interfaces = list(ACINodeInterface.objects.order_by("pk"))
        cls.csv_update_data = (
            "id,description",
            f"{node_interfaces[0].pk},Updated Node Interface 1",
            f"{node_interfaces[1].pk},Updated Node Interface 2",
            f"{node_interfaces[2].pk},Updated Node Interface 3",
        )

        cls.bulk_edit_data = {"description": "Bulk-edited Node Interface"}

    def test_acinode_nodeinterfaces_tab(self) -> None:
        """Node Interfaces tab renders the registered Add button."""
        self.add_permissions(
            "netbox_aci_plugin.view_acinode",
            "netbox_aci_plugin.view_acinodeinterface",
            "netbox_aci_plugin.add_acinodeinterface",
        )
        url = get_action_url(
            self.aci_node,
            action="nodeinterfaces",
            kwargs={"pk": self.aci_node.pk},
        )
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        add_url = get_action_url(ACINodeInterface, action="add")
        self.assertContains(
            response,
            f'href="{add_url}?aci_fabric={self.aci_fabric.pk}&amp;'
            f"aci_pod={self.aci_pod.pk}&amp;"
            f"aci_node={self.aci_node.pk}",
        )

    def test_node_interfaces_tab_visible_for_leaf_node(self) -> None:
        """Node Interfaces tab renders for a Leaf node."""
        self.assertIsNotNone(ACINodeInterfaceChildrenView.tab.render(self.aci_node))

    def test_node_interfaces_tab_hidden_for_spine_node(self) -> None:
        """Node Interfaces tab is hidden for a Spine node."""
        self.assertIsNone(ACINodeInterfaceChildrenView.tab.render(self.aci_node_spine))

    def test_node_interfaces_tab_hidden_for_apic_node(self) -> None:
        """Node Interfaces tab is hidden for an APIC node."""
        self.assertIsNone(ACINodeInterfaceChildrenView.tab.render(self.aci_node_apic))

    def _panel_context(self, obj):
        """Return a (request, object) context for a panel action.

        Deliberately minimal: ACIObjectLinkAction.render()/get_url()
        only read context['request'].user and context['object'].
        """
        request = RequestFactory().get("/")
        request.user = self.user
        return {"request": request, "object": obj}

    def _override_action(self, suffix: str):
        """Return the Override triad action whose view name ends in suffix.

        Selecting by declaration index would silently repoint every
        assertion below if the triad were ever reordered.
        """
        actions = [
            action
            for action in ACINodeInterfaceOverridePanel().actions
            if action.view_name.endswith(f"_{suffix}")
        ]
        self.assertEqual(len(actions), 1)
        return actions[0]

    def test_acinodeinterface_leaf_interface_override_attrs_absent(self) -> None:
        """The Override attrs resolve to None when no Override exists."""
        instance = ACINodeInterface.objects.get(aci_node=self.aci_node, port=1)
        panel = ACINodeInterfaceOverridePanel()
        self.assertIsNone(
            panel._attrs["aci_leaf_interface_override"].get_value(instance)
        )
        self.assertIsNone(
            panel._attrs["aci_leaf_interface_policy_group"].get_value(instance)
        )

    def test_acinodeinterface_leaf_interface_override_attrs_present(self) -> None:
        """The Override attrs resolve to the linked Override and its group."""
        policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACIViewTestNodeInterfaceOverridePolicyGroup",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        instance = ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=1, port=99
        )
        override = ACILeafInterfaceOverride.objects.create(
            aci_node_interface=instance,
            aci_leaf_interface_policy_group=policy_group,
        )
        # Matches the view's queryset: the property reads this cache.
        refetched = ACINodeInterface.objects.select_related(
            "aci_leaf_interface_override",
            "aci_leaf_interface_override__aci_leaf_interface_policy_group",
        ).get(pk=instance.pk)
        panel = ACINodeInterfaceOverridePanel()
        self.assertEqual(
            panel._attrs["aci_leaf_interface_override"].get_value(refetched),
            override,
        )
        self.assertEqual(
            panel._attrs["aci_leaf_interface_policy_group"].get_value(refetched),
            policy_group,
        )

    def test_add_override_action_visible_and_prefilled_when_absent(self) -> None:
        """The Add action's condition holds and prefills all four ancestors."""
        instance = ACINodeInterface.objects.get(aci_node=self.aci_node, port=1)
        self.add_permissions("netbox_aci_plugin.add_acileafinterfaceoverride")
        add_action = self._override_action("add")
        context = self._panel_context(instance)

        self.assertTrue(add_action.condition(context))
        self.assertNotEqual(add_action.render(context), "")
        query = parse_qs(urlparse(add_action.get_url(context)).query)
        self.assertEqual(query["aci_fabric"], [str(self.aci_fabric.pk)])
        self.assertEqual(query["aci_pod"], [str(self.aci_pod.pk)])
        self.assertEqual(query["aci_node"], [str(self.aci_node.pk)])
        self.assertEqual(query["aci_node_interface"], [str(instance.pk)])
        self.assertEqual(query["return_url"], [instance.get_absolute_url()])

    def _override_on_port(self, port: int) -> ACILeafInterfaceOverride:
        """Create and return an Override on a fresh port of the test Node."""
        policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name=f"ACIViewTestNodeInterfaceOverridePolicyGroup{port}",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        interface = ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=1, port=port
        )
        return ACILeafInterfaceOverride.objects.create(
            aci_node_interface=interface,
            aci_leaf_interface_policy_group=policy_group,
        )

    def test_add_override_action_hidden_when_taken(self) -> None:
        """The Add action's condition is False once an Override exists."""
        override = self._override_on_port(97)
        self.add_permissions("netbox_aci_plugin.add_acileafinterfaceoverride")
        add_action = self._override_action("add")
        context = self._panel_context(override.aci_node_interface)

        self.assertFalse(add_action.condition(context))
        self.assertEqual(add_action.render(context), "")

    def test_add_override_action_needs_its_own_permission(self) -> None:
        """The Add action needs the Override add permission, not the port's."""
        instance = ACINodeInterface.objects.get(aci_node=self.aci_node, port=1)
        self.add_permissions("netbox_aci_plugin.add_acinodeinterface")
        add_action = self._override_action("add")
        context = self._panel_context(instance)

        # The condition holds (no Override yet), but render() still gates
        # on the Override model's own add permission.
        self.assertTrue(add_action.condition(context))
        self.assertEqual(add_action.render(context), "")

    def test_edit_delete_actions_visible_when_taken(self) -> None:
        """Edit and Delete resolve to the Override's pk when permitted."""
        override = self._override_on_port(96)
        self.add_permissions(
            "netbox_aci_plugin.change_acileafinterfaceoverride",
            "netbox_aci_plugin.delete_acileafinterfaceoverride",
        )
        edit_action = self._override_action("edit")
        delete_action = self._override_action("delete")
        context = self._panel_context(override.aci_node_interface)

        for action, view_action in ((edit_action, "edit"), (delete_action, "delete")):
            self.assertTrue(action.condition(context))
            self.assertNotEqual(action.render(context), "")
            expected_url = get_action_url(
                ACILeafInterfaceOverride,
                action=view_action,
                kwargs={"pk": override.pk},
            )
            resolved_url = action.get_url(context)
            self.assertTrue(resolved_url.startswith(expected_url))
            # Edit and Delete carry no url_params of their own, so this
            # is the only proof they still return to the port's page.
            query = parse_qs(urlparse(resolved_url).query)
            self.assertEqual(
                query["return_url"],
                [override.aci_node_interface.get_absolute_url()],
            )

    def test_edit_delete_actions_hidden_when_empty(self) -> None:
        """Edit and Delete's condition is False without an Override."""
        instance = ACINodeInterface.objects.get(aci_node=self.aci_node, port=1)
        self.add_permissions(
            "netbox_aci_plugin.change_acileafinterfaceoverride",
            "netbox_aci_plugin.delete_acileafinterfaceoverride",
        )
        edit_action = self._override_action("edit")
        delete_action = self._override_action("delete")
        context = self._panel_context(instance)

        self.assertFalse(edit_action.condition(context))
        self.assertFalse(delete_action.condition(context))
        self.assertEqual(edit_action.render(context), "")
        self.assertEqual(delete_action.render(context), "")

    def test_edit_delete_actions_need_their_own_permission(self) -> None:
        """Edit and Delete each need their own Override permission."""
        override = self._override_on_port(95)
        edit_action = self._override_action("edit")
        delete_action = self._override_action("delete")
        context = self._panel_context(override.aci_node_interface)

        # The condition holds (an Override exists), but render() still
        # gates on each action's own change/delete permission.
        self.assertTrue(edit_action.condition(context))
        self.assertTrue(delete_action.condition(context))
        self.assertEqual(edit_action.render(context), "")
        self.assertEqual(delete_action.render(context), "")

    def _detail_query_count(self, url) -> int:
        """Return the query count of a detail-page GET request to url."""
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        return len(ctx.captured_queries)

    def test_acinodeinterface_detail_query_count_constant_with_override(self) -> None:
        """An existing Override must not add queries to the detail page."""
        self.add_permissions("netbox_aci_plugin.view_acinodeinterface")
        policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACIViewTestNodeInterfaceOverrideQueryCountPolicyGroup",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        without = ACINodeInterface.objects.get(aci_node=self.aci_node, port=1)
        with_override = ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=1, port=98
        )
        ACILeafInterfaceOverride.objects.create(
            aci_node_interface=with_override,
            aci_leaf_interface_policy_group=policy_group,
        )

        # Warm the per-process caches so the measured renders are comparable
        self.client.get(without.get_absolute_url())

        self.assertEqual(
            self._detail_query_count(with_override.get_absolute_url()),
            self._detail_query_count(without.get_absolute_url()),
            "The Override panel costs extra queries, so ACINodeInterfaceView is "
            "missing the reverse one-to-one or its policy group in select_related",
        )
