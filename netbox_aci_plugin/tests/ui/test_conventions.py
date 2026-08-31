# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Convention tests for the declarative UI layer.

Arms itself as each domain is ported: once a view exports through
views/__init__.py and sets layout, these tests hold it to the
branch's conventions. The completeness tests close the branch: every
registered detail view now declares a layout, and the template
directory holds only the surviving partials.
"""

from __future__ import annotations

from pathlib import Path

from django.apps import apps
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.test import TestCase

from netbox.ui.layout import SimpleLayout

from .base import all_object_views, layout_views


def _template_root() -> Path:
    """Return the plugin's netbox_aci_plugin template directory."""
    app_path = Path(apps.get_app_config("netbox_aci_plugin").path)
    return app_path / "templates" / "netbox_aci_plugin"


class UIConventionTestCase(TestCase):
    """Every ported detail view follows the declarative UI conventions."""

    def test_layout_views_use_generic_object_template(self) -> None:
        """Every layout-declaring view renders through generic/object.html."""
        for view_class in layout_views():
            with self.subTest(view=view_class.__name__):
                self.assertEqual(view_class.template_name, "generic/object.html")

    def test_layout_views_use_simple_layout(self) -> None:
        """Every layout is a SimpleLayout, so plugin content survives."""
        for view_class in layout_views():
            with self.subTest(view=view_class.__name__):
                self.assertIsInstance(view_class.layout, SimpleLayout)

    def test_layout_views_have_no_surviving_model_template(self) -> None:
        """The per-model template a layout view once fell back to is gone."""
        for view_class in layout_views():
            model = view_class.queryset.model
            fallback_name = f"{model._meta.app_label}/{model._meta.model_name}.html"
            with (
                self.subTest(view=view_class.__name__),
                self.assertRaises(TemplateDoesNotExist),
            ):
                get_template(fallback_name)


class UIConventionCompletenessTestCase(TestCase):
    """The port is complete: nothing was left on the old template path."""

    def test_every_registered_object_view_declares_a_layout(self) -> None:
        """No registered ObjectView still relies on a per-model template."""
        for view_class in all_object_views():
            with self.subTest(view=view_class.__name__):
                self.assertIsNotNone(view_class.layout)

    def test_template_directory_holds_only_surviving_partials(self) -> None:
        """The template directory holds only the three surviving partials."""
        entries = {entry.name for entry in _template_root().iterdir()}
        self.assertEqual(entries, {"attrs", "buttons", "widgets"})
