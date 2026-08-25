# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""View tests for the fabric ACI Node Interface model."""

import re

from django.db import connection
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

    def test_acinodeinterface_detail_leaf_interface_override_panel_absent(self) -> None:
        """The Override panel shows the placeholder when no Override exists."""
        instance = ACINodeInterface.objects.get(aci_node=self.aci_node, port=1)
        self.add_permissions("netbox_aci_plugin.view_acinodeinterface")

        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)
        content = response.content.decode()
        placeholder = '<span class="text-muted">&mdash;</span>'
        # Anchored to each row's own header so an unrelated placeholder
        # elsewhere on the page (e.g. the blank Description row) cannot
        # satisfy this assertion in place of the Override panel's own.
        self.assertRegex(
            content,
            r"Leaf Interface Override</th>\s*<td>\s*" + re.escape(placeholder),
        )
        self.assertRegex(
            content,
            r"Leaf Interface Policy Group</th>\s*<td>\s*" + re.escape(placeholder),
        )

    def test_acinodeinterface_detail_leaf_interface_override_panel_present(
        self,
    ) -> None:
        """The Override panel links the Override and its Policy Group."""
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
        self.add_permissions("netbox_aci_plugin.view_acinodeinterface")

        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)
        content = response.content.decode()
        override_link = f'<a href="{override.get_absolute_url()}">'
        policy_group_link = f'<a href="{policy_group.get_absolute_url()}">'
        self.assertRegex(
            content,
            r"Leaf Interface Override</th>\s*<td>\s*" + re.escape(override_link),
        )
        self.assertRegex(
            content,
            r"Leaf Interface Policy Group</th>\s*<td>\s*"
            + re.escape(policy_group_link),
        )

    def test_acinodeinterface_detail_add_override_button_present(self) -> None:
        """The port offers a prefilled Add button while it has no Override."""
        instance = ACINodeInterface.objects.get(aci_node=self.aci_node, port=1)
        self.add_permissions(
            "netbox_aci_plugin.view_acinodeinterface",
            "netbox_aci_plugin.add_acileafinterfaceoverride",
        )

        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)
        content = response.content.decode()
        self.assertIn("Add an Override", content)
        self.assertIn(f"aci_node_interface={instance.pk}", content)
        self.assertIn(f"aci_node={self.aci_node.pk}", content)
        self.assertIn(f"aci_pod={self.aci_pod.pk}", content)
        self.assertIn(f"aci_fabric={self.aci_fabric.pk}", content)

    def test_acinodeinterface_detail_add_override_button_hidden_when_taken(
        self,
    ) -> None:
        """A port that already has an Override offers no Add button."""
        policy_group = ACILeafInterfacePolicyGroup.objects.create(
            name="ACIViewTestNodeInterfaceOverrideButtonPolicyGroup",
            aci_fabric=self.aci_fabric,
            group_type=LeafInterfacePolicyGroupTypeChoices.TYPE_ACCESS,
        )
        instance = ACINodeInterface.objects.create(
            aci_node=self.aci_node, module=1, port=97
        )
        ACILeafInterfaceOverride.objects.create(
            aci_node_interface=instance,
            aci_leaf_interface_policy_group=policy_group,
        )
        self.add_permissions(
            "netbox_aci_plugin.view_acinodeinterface",
            "netbox_aci_plugin.add_acileafinterfaceoverride",
        )

        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)
        self.assertNotIn("Add an Override", response.content.decode())

    def test_acinodeinterface_detail_add_override_button_needs_permission(
        self,
    ) -> None:
        """The Add button needs the Override add permission, not the port's."""
        instance = ACINodeInterface.objects.get(aci_node=self.aci_node, port=1)
        self.add_permissions(
            "netbox_aci_plugin.view_acinodeinterface",
            "netbox_aci_plugin.add_acinodeinterface",
        )

        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)
        self.assertNotIn("Add an Override", response.content.decode())

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

    def test_acinodeinterface_detail_edit_delete_buttons_present_when_taken(
        self,
    ) -> None:
        """A port with an Override offers Edit and Delete in the panel."""
        override = self._override_on_port(96)
        self.add_permissions(
            "netbox_aci_plugin.view_acinodeinterface",
            "netbox_aci_plugin.change_acileafinterfaceoverride",
            "netbox_aci_plugin.delete_acileafinterfaceoverride",
        )

        response = self.client.get(override.aci_node_interface.get_absolute_url())
        self.assertHttpStatus(response, 200)
        content = response.content.decode()
        for action in ("edit", "delete"):
            self.assertIn(
                get_action_url(
                    ACILeafInterfaceOverride,
                    action=action,
                    kwargs={"pk": override.pk},
                ),
                content,
            )

    def test_acinodeinterface_detail_edit_delete_buttons_absent_when_empty(
        self,
    ) -> None:
        """A port without an Override offers neither Edit nor Delete."""
        instance = ACINodeInterface.objects.get(aci_node=self.aci_node, port=1)
        self.add_permissions(
            "netbox_aci_plugin.view_acinodeinterface",
            "netbox_aci_plugin.change_acileafinterfaceoverride",
            "netbox_aci_plugin.delete_acileafinterfaceoverride",
        )

        response = self.client.get(instance.get_absolute_url())
        self.assertHttpStatus(response, 200)
        content = response.content.decode()
        self.assertNotIn("mdi-pencil", content)
        self.assertNotIn("mdi-trash-can-outline", content)

    def test_acinodeinterface_detail_edit_delete_buttons_need_permission(
        self,
    ) -> None:
        """Edit and Delete each need their own Override permission."""
        override = self._override_on_port(95)
        self.add_permissions("netbox_aci_plugin.view_acinodeinterface")

        response = self.client.get(override.aci_node_interface.get_absolute_url())
        self.assertHttpStatus(response, 200)
        content = response.content.decode()
        self.assertNotIn("mdi-pencil", content)
        self.assertNotIn("mdi-trash-can-outline", content)

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
