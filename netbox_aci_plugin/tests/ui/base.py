# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Shared base test case for the declarative UI layer's unit tests."""

from __future__ import annotations

from django.contrib.auth.context_processors import PermWrapper
from django.test import RequestFactory

from netbox.views import generic
from utilities.testing import TestCase

from ... import views


class ACIBaseUITestCase(TestCase):
    """Base test case for panel and action unit tests.

    Builds a template context without a full view round trip, since a
    panel or action renders() from a plain context dict rather than
    through Django's template engine. self.user is created fresh per
    test by utilities.testing.TestCase.setUp(); grant it permissions
    with self.add_permissions(...) before calling get_context().
    """

    factory = RequestFactory()

    def get_context(self, obj, **extra):
        """Return a (request, object, perms) context for a panel or action."""
        request = self.factory.get("/")
        request.user = self.user
        return {
            "request": request,
            "object": obj,
            "perms": PermWrapper(self.user),
            **extra,
        }


def all_object_views():
    """Yield every views/__init__.py ObjectView subclass."""
    for name in views.__all__:
        view_class = getattr(views, name)
        if isinstance(view_class, type) and issubclass(view_class, generic.ObjectView):
            yield view_class


def layout_views(module_prefix: str = ""):
    """Yield every ObjectView subclass declaring a layout."""
    for view_class in all_object_views():
        if view_class.layout is not None and view_class.__module__.startswith(
            module_prefix
        ):
            yield view_class


def layout_panels(view_class):
    """Yield every panel instance in a view's layout, in render order."""
    for row in view_class.layout:
        for column in row:
            yield from column
