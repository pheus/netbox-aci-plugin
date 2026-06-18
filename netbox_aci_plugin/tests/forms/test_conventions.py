# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.test import SimpleTestCase

import netbox_aci_plugin.forms  # noqa: F401  ensure every form module is imported
from netbox.forms import NetBoxModelBulkEditForm
from utilities.forms.rendering import InlineFields, TabbedGroups

# Fields NetBox auto-renders on bulk-edit forms (Ownership / Tags /
# Comments). The auto-render only fires when `fieldsets` is truthy, and
# `render_fieldset` silently drops a fieldset item the form has no field
# for, so listing these here is dead code.
AUTO_RENDERED_FIELDS = frozenset({"tags", "comments", "owner", "owner_group"})


def _iter_aci_bulk_edit_forms():
    """Yield every ACI plugin NetBoxModelBulkEditForm subclass."""
    seen, stack = set(), [NetBoxModelBulkEditForm]
    while stack:
        for sub in stack.pop().__subclasses__():
            if sub in seen:
                continue
            seen.add(sub)
            stack.append(sub)
            if sub.__module__.startswith(
                "netbox_aci_plugin."
            ) and sub.__name__.startswith("ACI"):
                yield sub


def _fieldset_field_names(fieldset):
    """Yield field names in a FieldSet, flattening Inline/Tabbed groups."""
    for item in getattr(fieldset, "items", ()):
        if isinstance(item, str):
            yield item
        elif isinstance(item, InlineFields):
            yield from item.fields
        elif isinstance(item, TabbedGroups):
            for group in item.groups:
                yield from _fieldset_field_names(group)


class ACIBulkEditFieldsetConventionTests(SimpleTestCase):
    """Guard the bulk-edit fieldset convention against regression."""

    def test_fieldsets_omit_auto_rendered_fields(self):
        """Bulk-edit fieldsets must not list tags/comments/owner fields."""
        offenders = {}
        for form_cls in _iter_aci_bulk_edit_forms():
            referenced = {
                name
                for fieldset in (form_cls.fieldsets or ())
                for name in _fieldset_field_names(fieldset)
            }
            if bad := referenced & AUTO_RENDERED_FIELDS:
                offenders[form_cls.__name__] = sorted(bad)
        self.assertEqual(
            offenders,
            {},
            f"Bulk-edit fieldsets must omit auto-rendered fields: {offenders}",
        )

    def test_fieldsets_are_non_empty(self):
        """A truthy `fieldsets` is required for the auto-render sections."""
        empty = [
            form_cls.__name__
            for form_cls in _iter_aci_bulk_edit_forms()
            if not getattr(form_cls, "fieldsets", None)
        ]
        self.assertEqual(
            empty, [], f"Bulk-edit forms need a non-empty fieldsets: {empty}"
        )
