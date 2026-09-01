# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for the declarative UI layer's panel-action classes."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from django.urls import reverse

from ...models.fabric.fabrics import ACIFabric
from ...models.fabric.pods import ACIPod
from ...ui.actions import ACIObjectLinkAction
from .base import ACIBaseUITestCase


class ACIObjectLinkActionTestCase(ACIBaseUITestCase):
    """Unit tests for ACIObjectLinkAction."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for ACIObjectLinkAction tests."""
        cls.aci_fabric = ACIFabric.objects.create(
            name="ACIUITestActionFabric", fabric_id=1, infra_vlan_vid=100
        )
        cls.aci_pod = ACIPod.objects.create(
            name="ACIUITestActionPod", aci_fabric=cls.aci_fabric, pod_id=1
        )

    def test_get_url_with_static_view_kwargs(self) -> None:
        """A static view_kwargs value resolves without a context lookup."""
        action = ACIObjectLinkAction(
            "plugins:netbox_aci_plugin:acipod_edit",
            label="Edit",
            view_kwargs={"pk": self.aci_pod.pk},
        )
        expected_path = reverse(
            "plugins:netbox_aci_plugin:acipod_edit", kwargs={"pk": self.aci_pod.pk}
        )
        url = action.get_url(self.get_context(self.aci_pod))
        self.assertTrue(url.startswith(expected_path))

    def test_get_url_with_callable_view_kwargs(self) -> None:
        """A callable view_kwargs value is resolved against the context."""
        action = ACIObjectLinkAction(
            "plugins:netbox_aci_plugin:acipod_edit",
            label="Edit",
            view_kwargs={"pk": lambda ctx: ctx["object"].pk},
        )
        expected_path = reverse(
            "plugins:netbox_aci_plugin:acipod_edit", kwargs={"pk": self.aci_pod.pk}
        )
        url = action.get_url(self.get_context(self.aci_pod))
        self.assertTrue(url.startswith(expected_path))

    def test_get_url_resolves_callable_url_params(self) -> None:
        """A callable url_params value is resolved against the context."""
        action = ACIObjectLinkAction(
            "plugins:netbox_aci_plugin:acipod_add",
            label="Add",
            url_params={"aci_fabric": lambda ctx: ctx["object"].pk},
        )
        url = action.get_url(self.get_context(self.aci_fabric))
        query = parse_qs(urlparse(url).query)
        self.assertEqual(query["aci_fabric"], [str(self.aci_fabric.pk)])

    def test_get_url_appends_return_url_automatically(self) -> None:
        """get_url() appends return_url alongside other resolved url_params."""
        action = ACIObjectLinkAction(
            "plugins:netbox_aci_plugin:acipod_add",
            label="Add",
            url_params={"aci_fabric": lambda ctx: ctx["object"].pk},
        )
        url = action.get_url(self.get_context(self.aci_pod))
        query = parse_qs(urlparse(url).query)
        self.assertEqual(query["return_url"], [self.aci_pod.get_absolute_url()])

    def test_get_url_appends_return_url_with_no_other_url_params(self) -> None:
        """get_url() appends return_url with no other url_params set.

        The Override triad's Edit and Delete actions carry only
        view_kwargs, so this is the path they rely on to return to
        the port they came from.
        """
        action = ACIObjectLinkAction(
            "plugins:netbox_aci_plugin:acipod_edit",
            label="Edit",
            view_kwargs={"pk": self.aci_pod.pk},
        )
        url = action.get_url(self.get_context(self.aci_pod))
        query = parse_qs(urlparse(url).query)
        self.assertEqual(query["return_url"], [self.aci_pod.get_absolute_url()])

    def test_render_visible_with_no_condition_set(self) -> None:
        """A None condition (the default) never hides the action."""
        action = ACIObjectLinkAction(
            "plugins:netbox_aci_plugin:acipod_add", label="Add"
        )
        self.assertNotEqual(action.render(self.get_context(self.aci_fabric)), "")

    def test_render_hidden_when_condition_false(self) -> None:
        """A False condition hides the action regardless of permissions."""
        action = ACIObjectLinkAction(
            "plugins:netbox_aci_plugin:acipod_add",
            label="Add",
            condition=lambda ctx: False,
        )
        self.add_permissions("netbox_aci_plugin.add_acipod")
        self.assertEqual(action.render(self.get_context(self.aci_fabric)), "")

    def test_render_visible_when_condition_true(self) -> None:
        """A True condition lets the action render, subject to permissions."""
        action = ACIObjectLinkAction(
            "plugins:netbox_aci_plugin:acipod_add",
            label="Add",
            condition=lambda ctx: True,
        )
        self.add_permissions("netbox_aci_plugin.add_acipod")
        self.assertNotEqual(action.render(self.get_context(self.aci_fabric)), "")

    def test_render_hidden_without_permission(self) -> None:
        """The stock permission gate still applies on top of condition."""
        action = ACIObjectLinkAction(
            "plugins:netbox_aci_plugin:acipod_add",
            label="Add",
            permissions=["netbox_aci_plugin.add_acipod"],
        )
        self.assertEqual(action.render(self.get_context(self.aci_fabric)), "")

    def test_render_visible_with_permission(self) -> None:
        """The action renders once both condition and permission pass."""
        action = ACIObjectLinkAction(
            "plugins:netbox_aci_plugin:acipod_add",
            label="Add",
            condition=lambda ctx: True,
            permissions=["netbox_aci_plugin.add_acipod"],
        )
        self.add_permissions("netbox_aci_plugin.add_acipod")
        self.assertNotEqual(action.render(self.get_context(self.aci_fabric)), "")

    def test_condition_is_keyword_only(self) -> None:
        """A positional second argument must not bind to condition."""
        with self.assertRaises(TypeError):
            ACIObjectLinkAction(
                "plugins:netbox_aci_plugin:acipod_edit",
                {"pk": self.aci_pod.pk},
                label="Edit",
            )
