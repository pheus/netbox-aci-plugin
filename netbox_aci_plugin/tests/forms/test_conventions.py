# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.test import SimpleTestCase

import netbox_aci_plugin.forms  # noqa: F401  ensure every form module is imported
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelForm
from netbox.forms.filtersets import NetBoxModelFilterSetForm
from utilities.forms.fields import GenericObjectChoiceField
from utilities.forms.rendering import InlineFields, TabbedGroups

# Fields NetBox auto-renders on bulk-edit forms (Ownership / Tags /
# Comments). The auto-render only fires when `fieldsets` is truthy, and
# `render_fieldset` silently drops a fieldset item the form has no field
# for, so listing these here is dead code.
AUTO_RENDERED_FIELDS = frozenset({"tags", "comments", "owner", "owner_group"})

# Bulk-edit field sets that name `nb_tenant_group` without declaring it. The
# entry renders as nothing today, but the open question is whether bulk edit
# should instead gain the tenant-group cascade its edit form has, so the entry
# is left in place rather than removed. Tracked in todo.md.
PENDING_FIELDSET_ENTRIES = frozenset({"nb_tenant_group"})


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


def _iter_aci_fieldset_forms():
    """Yield every ACI Edit and BulkEdit form class."""
    seen, stack = set(), [NetBoxModelForm, NetBoxModelBulkEditForm]
    while stack:
        for sub in stack.pop().__subclasses__():
            if sub in seen:
                continue
            seen.add(sub)
            stack.append(sub)
            if (
                sub.__module__.startswith("netbox_aci_plugin.")
                and sub.__name__.startswith("ACI")
                and sub.__name__.endswith("EditForm")
            ):
                yield sub


def _iter_aci_all_fieldset_forms():
    """Yield every ACI form carrying field sets, FilterForms included.

    Ordering conventions differ by form kind, so only the rule that a
    field set entry must resolve to a real field uses this wider walk.
    """
    seen, stack = (
        set(),
        [
            NetBoxModelForm,
            NetBoxModelBulkEditForm,
            NetBoxModelFilterSetForm,
        ],
    )
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


class ACIFieldsetDescriptionOrderTests(SimpleTestCase):
    """Guard that `description` follows the FK cascade in form fieldsets."""

    def test_description_follows_aci_fields(self):
        """`description` must follow every `aci_*` field in its FieldSet."""
        offenders = {}
        for form_cls in _iter_aci_fieldset_forms():
            for fieldset in getattr(form_cls, "fieldsets", None) or ():
                names = list(_fieldset_field_names(fieldset))
                if "description" not in names:
                    continue
                desc_idx = names.index("description")
                misplaced = [
                    name for name in names[desc_idx + 1 :] if name.startswith("aci_")
                ]
                if misplaced:
                    offenders[form_cls.__name__] = misplaced
        self.assertEqual(
            offenders,
            {},
            f"`description` must follow aci_* fields in fieldsets: {offenders}",
        )


class ACIFieldsetTargetTests(SimpleTestCase):
    """Guard that fieldset entries and HTMX swap containers resolve."""

    maxDiff = None

    def test_fieldset_items_name_real_fields(self) -> None:
        """Test every field set entry names a field the form declares."""
        unknown = {}
        for form_class in _iter_aci_all_fieldset_forms():
            names = {
                name
                for fieldset in getattr(form_class, "fieldsets", ())
                for name in _fieldset_field_names(fieldset)
            }
            if gaps := sorted(
                names
                - set(form_class.base_fields)
                - AUTO_RENDERED_FIELDS
                - PENDING_FIELDSET_ENTRIES
            ):
                unknown[form_class.__name__] = gaps

        self.assertEqual(
            unknown,
            {},
            "A field set names a field the form does not declare. "
            "render_fieldset skips it silently, so it renders as nothing.",
        )

    def test_swap_containers_hold_only_their_generic_object_field(self) -> None:
        """Test an HTMX swap container carries nothing but its own field."""
        crowded = {}
        for form_class in _iter_aci_fieldset_forms():
            targets = {
                field.hx_target_id: name
                for name, field in form_class.base_fields.items()
                if isinstance(field, GenericObjectChoiceField) and field.hx_target_id
            }
            for fieldset in getattr(form_class, "fieldsets", ()):
                html_id = getattr(fieldset, "html_id", None)
                if html_id not in targets:
                    continue
                extra = sorted(
                    set(_fieldset_field_names(fieldset)) - {targets[html_id]}
                )
                if extra:
                    crowded[f"{form_class.__name__}.{html_id}"] = extra

        self.assertEqual(
            crowded,
            {},
            "An HTMX swap container holds fields besides its generic object "
            "field. hx-swap replaces the container, so those are torn down and "
            "reset on every content type change.",
        )

    def test_generic_object_fields_have_a_swap_container(self) -> None:
        """Test every HTMX swap target has a matching field set html_id."""
        missing = {}
        for form_class in _iter_aci_fieldset_forms():
            html_ids = {
                getattr(fieldset, "html_id", None)
                for fieldset in getattr(form_class, "fieldsets", ())
            }
            for name, field in form_class.base_fields.items():
                if not isinstance(field, GenericObjectChoiceField):
                    continue
                if field.hx_target_id and field.hx_target_id not in html_ids:
                    missing[f"{form_class.__name__}.{name}"] = field.hx_target_id

        self.assertEqual(
            missing,
            {},
            "A generic object field targets an html_id no field set declares. "
            "The HTMX partial swap fails silently.",
        )


class ACIRangePairInlineTests(SimpleTestCase):
    """Guard that `<field>_from` / `<field>_to` pairs render inline."""

    def test_range_pairs_are_inlined(self):
        """A from/to pair in an edit fieldset must be an InlineFields row."""
        offenders = {}
        for form_cls in _iter_aci_fieldset_forms():
            for fieldset in getattr(form_cls, "fieldsets", None) or ():
                bare = {
                    item
                    for item in getattr(fieldset, "items", ())
                    if isinstance(item, str)
                }
                stacked = sorted(
                    name
                    for name in bare
                    if name.endswith("_from") and f"{name[:-5]}_to" in bare
                )
                if stacked:
                    offenders[form_cls.__name__] = stacked
        self.assertEqual(
            offenders,
            {},
            "A from/to pair stacked as two rows reads as two unrelated "
            "inputs. Wrap it in InlineFields with a shared label and "
            f"help text: {offenders}",
        )

    def test_inlined_range_pairs_carry_help_text(self):
        """Every InlineFields row must explain what the pair means."""
        offenders = {}
        for form_cls in _iter_aci_fieldset_forms():
            for fieldset in getattr(form_cls, "fieldsets", None) or ():
                for item in getattr(fieldset, "items", ()):
                    if not isinstance(item, InlineFields):
                        continue
                    if not (item.label and item.help_text):
                        offenders.setdefault(form_cls.__name__, []).append(
                            ", ".join(item.fields)
                        )
        self.assertEqual(
            offenders,
            {},
            f"InlineFields needs both a label and help text: {offenders}",
        )

    def test_range_pairs_are_collected(self):
        """Test the check actually finds the inlined pairs."""
        inlined = [
            item
            for form_cls in _iter_aci_fieldset_forms()
            for fieldset in getattr(form_cls, "fieldsets", None) or ()
            for item in getattr(fieldset, "items", ())
            if isinstance(item, InlineFields)
        ]
        self.assertEqual(len(inlined), 4)
