# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Convention tests for the declarative UI layer.

Vacuously green until a view declares a layout. Arms itself as each
domain is ported: once a view exports through views/__init__.py and
sets layout, these tests hold it to the branch's conventions.
"""

from __future__ import annotations

from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.test import TestCase

from netbox.ui.layout import SimpleLayout

from .base import layout_views


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
