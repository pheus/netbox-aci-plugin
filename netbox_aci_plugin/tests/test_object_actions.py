# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the reusable ACI child-relation object actions."""

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from utilities.views import get_action_url

from ..models.fabric.fabrics import ACIFabric
from ..models.tenant.bridge_domains import ACIBridgeDomain
from ..models.tenant.tenants import ACITenant
from ..models.tenant.vrfs import ACIVRF
from ..object_actions import AddChildObject, add_child_action


class AddChildActionTestCase(TestCase):
    """Tests for ``add_child_action`` / ``AddChildObject``."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for add-child action tests."""
        cls.fabric = ACIFabric.objects.create(
            name="F1", fabric_id=1, infra_vlan_vid=3900
        )
        cls.tenant = ACITenant.objects.create(name="T1", aci_fabric=cls.fabric)
        cls.vrf = ACIVRF.objects.create(name="V1", aci_tenant=cls.tenant)

    def test_factory_returns_addchildobject_subclass(self) -> None:
        action = add_child_action(
            "netbox_aci_plugin.ACIBridgeDomain", "Add a Bridge Domain"
        )
        self.assertTrue(issubclass(action, AddChildObject))
        self.assertEqual(action.label, "Add a Bridge Domain")
        self.assertEqual(action.permissions_required, {"add"})

    def test_get_url_targets_child_model(self) -> None:
        action = add_child_action(
            "netbox_aci_plugin.ACIBridgeDomain", "Add a Bridge Domain"
        )
        # The passed object (the parent VRF) is ignored: the URL targets the
        # child model's add view, not the parent's.
        self.assertEqual(
            action.get_url(self.vrf),
            get_action_url(ACIBridgeDomain, action="add"),
        )
        self.assertNotEqual(
            action.get_url(self.vrf),
            get_action_url(ACIVRF, action="add"),
        )

    def test_get_url_params_resolves_callables_and_return_url(self) -> None:
        action = add_child_action(
            "netbox_aci_plugin.ACIBridgeDomain",
            "Add a Bridge Domain",
            url_params={"aci_vrf": lambda ctx: ctx["object"].pk},
        )
        params = action.get_url_params({"object": self.vrf, "return_url": "/back/"})
        encoded = params.urlencode()
        self.assertIn(f"aci_vrf={self.vrf.pk}", encoded)
        self.assertIn("return_url=%2Fback%2F", encoded)

    def test_get_url_params_omits_none_values(self) -> None:
        action = add_child_action(
            "netbox_aci_plugin.ACIBridgeDomain",
            "Add a Bridge Domain",
            url_params={
                "aci_vrf": lambda ctx: ctx["object"].pk,
                "nb_tenant": lambda ctx: ctx["object"].nb_tenant_id,
            },
        )
        # self.vrf has no nb_tenant, so nb_tenant_id is None and is dropped.
        params = action.get_url_params({"object": self.vrf})
        self.assertIn("aci_vrf", params)
        self.assertNotIn("nb_tenant", params)

    def test_get_child_model_rejects_invalid_label(self) -> None:
        # Neither zero dots nor more than one dot is a valid model label.
        for bad in ("not-a-dotted-label", "too.many.dots"):
            action = add_child_action(bad, "Add Something")
            with self.assertRaises(ImproperlyConfigured):
                action.get_child_model()

    def test_get_child_model_rejects_unknown_model(self) -> None:
        # A well-formed label whose model does not exist raises at lookup.
        action = add_child_action("netbox_aci_plugin.NonexistentModel", "Add X")
        with self.assertRaises(ImproperlyConfigured):
            action.get_child_model()

    def test_get_url_returns_none_without_add_url(self) -> None:
        # A model with no registered "add" view yields a None URL.
        action = add_child_action("contenttypes.ContentType", "Add CT")
        self.assertIsNone(action.get_url(self.vrf))
