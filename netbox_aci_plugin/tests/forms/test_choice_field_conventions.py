# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Convention tests for choice fields on ACI edit forms."""

import importlib
import pkgutil

from django import forms
from django.core.exceptions import FieldDoesNotExist
from django.db.models import NOT_PROVIDED
from django.test import SimpleTestCase

from ... import forms as aci_forms


def _iter_edit_form_choice_fields():
    """Yield (form class, field name, form field, model field) to check."""
    for module_info in pkgutil.walk_packages(
        aci_forms.__path__, f"{aci_forms.__name__}."
    ):
        module = importlib.import_module(module_info.name)
        for attribute_name in dir(module):
            form_class = getattr(module, attribute_name)
            if not isinstance(form_class, type) or not issubclass(
                form_class, forms.BaseForm
            ):
                continue
            if form_class.__module__ != module_info.name:
                continue
            if not attribute_name.endswith("EditForm"):
                continue
            if attribute_name.endswith("BulkEditForm"):
                continue
            model = getattr(getattr(form_class, "_meta", None), "model", None)
            if model is None:
                continue
            for field_name, form_field in form_class.base_fields.items():
                if not isinstance(form_field, forms.ChoiceField):
                    continue
                # ModelChoiceField and friends resolve objects, not choice
                # values, and carry their own optionality rules.
                if isinstance(form_field, forms.ModelChoiceField):
                    continue
                # A choice field paired with a "<field>_custom" input may be
                # left blank on purpose: the form's clean() substitutes the
                # custom value (see add_custom_choice in choices.py).
                if f"{field_name}_custom" in form_class.base_fields:
                    continue
                try:
                    model_field = model._meta.get_field(field_name)
                except FieldDoesNotExist:
                    continue
                if model_field.default is NOT_PROVIDED or model_field.blank:
                    continue
                yield form_class, field_name, form_field, model_field


class ACIEditFormChoiceFieldConventionTestCase(SimpleTestCase):
    """Test case for choice field conventions on ACI edit forms."""

    def test_edit_forms_cover_choice_fields(self) -> None:
        """Test the convention checks actually collect edit form fields."""
        collected = list(_iter_edit_form_choice_fields())
        self.assertGreater(len(collected), 20)

    def test_edit_form_choice_fields_are_required(self) -> None:
        """Test defaulted non-blank choice fields stay required."""
        optional = [
            f"{form_class.__name__}.{field_name}"
            for form_class, field_name, form_field, _ in (
                _iter_edit_form_choice_fields()
            )
            if not form_field.required
        ]
        self.assertEqual(
            optional,
            [],
            "Edit form choice fields over a defaulted non-blank model field "
            "must stay required, otherwise an empty submitted value is stored "
            "as an empty string. Drop 'required=False' from: "
            f"{', '.join(optional)}",
        )

    def test_edit_form_choice_fields_offer_no_blank_value(self) -> None:
        """Test defaulted non-blank choice fields omit a blank entry."""
        with_blank = [
            f"{form_class.__name__}.{field_name}"
            for form_class, field_name, form_field, _ in (
                _iter_edit_form_choice_fields()
            )
            # add_blank_choice() renders its placeholder as None, which the
            # browser submits as an empty string.
            if any(value in (None, "") for value, _label in form_field.choices)
        ]
        self.assertEqual(
            with_blank,
            [],
            "Edit form choice fields must not offer a blank value, because "
            "validation rejects it. Drop 'add_blank_choice()' and pair the "
            "ChoiceSet's neutral member with 'initial=' instead in: "
            f"{', '.join(with_blank)}",
        )
