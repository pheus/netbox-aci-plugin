# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Convention tests for the ACI API viewset querysets."""

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model, QuerySet
from django.test import SimpleTestCase

from netbox.api.viewsets import NetBoxModelViewSet
from utilities.api import get_prefetches_for_serializer

from ...api import views as aci_api_views

# Past PostgreSQL's geqo_threshold, planning outgrows the round trips saved.
JOIN_CAP = 8


def _iter_aci_viewsets():
    """Yield (name, viewset class) for every ACI API viewset."""
    for attribute_name in dir(aci_api_views):
        viewset = getattr(aci_api_views, attribute_name)
        if (
            isinstance(viewset, type)
            and issubclass(viewset, NetBoxModelViewSet)
            and viewset.__module__ == aci_api_views.__name__
        ):
            yield attribute_name, viewset


def _selected_paths(queryset: QuerySet) -> set[str]:
    """Return the queryset's select_related tree as lookup paths."""

    def walk(node: dict, prefix: str):
        for field_name, subtree in node.items():
            path = f"{prefix}{field_name}"
            yield path
            yield from walk(subtree, f"{path}__")

    tree = queryset.query.select_related
    return set(walk(tree, "")) if isinstance(tree, dict) else set()


def _is_joinable(model: type[Model], path: str) -> bool:
    """Return whether every hop of the path is a forward foreign key."""
    for field_name in path.split("__"):
        try:
            field = model._meta.get_field(field_name)
        except FieldDoesNotExist:
            return False
        if not field.concrete or not (field.many_to_one or field.one_to_one):
            return False
        model = field.related_model
    return True


def _expected_paths(viewset) -> list[str]:
    """Return the joinable serializer paths a viewset should select."""
    queryset = viewset.queryset
    closure = {
        path
        for path in get_prefetches_for_serializer(viewset.serializer_class)
        if _is_joinable(queryset.model, path)
    }
    # Breadth first, so a kept path keeps its own prefixes.
    ordered = sorted(closure, key=lambda path: (path.count("__"), path))
    return ordered[:JOIN_CAP]


class ACIAPIViewSetQuerySetTestCase(SimpleTestCase):
    """Test case for the ACI API viewset queryset conventions."""

    maxDiff = None

    def test_select_related_matches_the_capped_closure(self) -> None:
        """Test each viewset joins the capped set its serializer needs."""
        wrong: dict[str, dict[str, list[str]]] = {}

        for viewset_name, viewset in _iter_aci_viewsets():
            selected = _selected_paths(viewset.queryset)
            expected = set(_expected_paths(viewset))
            if selected != expected:
                wrong[viewset_name] = {
                    "missing": sorted(expected - selected),
                    "unexpected": sorted(selected - expected),
                }

        self.assertEqual(
            wrong,
            {},
            "A viewset does not join the capped set its serializer needs. "
            "Missing paths cost a prefetch query, unexpected ones cost a join.",
        )

    def test_no_viewset_exceeds_the_join_cap(self) -> None:
        """Test no viewset joins more relations than the cap allows."""
        over = {
            viewset_name: len(_selected_paths(viewset.queryset))
            for viewset_name, viewset in _iter_aci_viewsets()
            if len(_selected_paths(viewset.queryset)) > JOIN_CAP
        }

        self.assertEqual(
            over,
            {},
            f"A viewset joins more than {JOIN_CAP} relations. Past PostgreSQL's "
            "geqo_threshold the planner turns genetic and planning time grows "
            "faster than the saved round trips are worth.",
        )
