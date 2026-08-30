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

from utilities.choices import Choice, ChoiceSet
from utilities.forms.fields import TagFilterField
from utilities.forms.fields.choices import AttrChoiceMixin
from utilities.forms.fields.csv import CSVChoicesMixin

from ... import choices as aci_choices
from ... import forms as aci_forms
from ...choices import (
    BDMultiDestinationFloodingChoices,
    QualityOfServiceDSCPChoices,
)
from ...forms.tenant.bridge_domains import ACIBridgeDomainEditForm
from ...forms.tenant.contracts import ACIContractEditForm


def _iter_aci_choice_sets():
    """Yield (name, ChoiceSet subclass) for every ACI choice set."""
    for attribute_name in dir(aci_choices):
        candidate = getattr(aci_choices, attribute_name)
        if (
            isinstance(candidate, type)
            and issubclass(candidate, ChoiceSet)
            and candidate is not ChoiceSet
        ):
            yield attribute_name, candidate


def _iter_rendered_choice_fields():
    """Yield (form class, field name, field) for rendered choice fields."""
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
            for field_name, form_field in form_class.base_fields.items():
                if not isinstance(form_field, forms.ChoiceField):
                    continue
                # Object pickers resolve rows, CSV fields never render a
                # dropdown, and a tag filter's choices are queried lazily
                # rather than declared in a choice set, so none of the three
                # can carry option descriptions.
                if isinstance(
                    form_field,
                    (forms.ModelChoiceField, CSVChoicesMixin, TagFilterField),
                ):
                    continue
                yield form_class, field_name, form_field


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


class ACIChoiceDescriptionTestCase(SimpleTestCase):
    """Test case for choice descriptions reaching the rendered widget."""

    def test_choice_sets_use_choice_objects(self) -> None:
        """Test every choice set member is a Choice, not a plain tuple."""
        plain = [
            f"{set_name}.{entry[0]}"
            for set_name, choice_set in _iter_aci_choice_sets()
            for entry in choice_set.CHOICES
            if not isinstance(entry, Choice)
        ]
        self.assertEqual(
            plain,
            [],
            "Choice set members must be Choice objects so they can carry a "
            "color and a description. Convert: " + ", ".join(plain),
        )

    def test_rendered_choice_fields_are_description_aware(self) -> None:
        """Test rendered choice fields use the description-aware class."""
        plain = [
            f"{form_class.__name__}.{field_name}"
            for form_class, field_name, form_field in _iter_rendered_choice_fields()
            if not isinstance(form_field, AttrChoiceMixin)
        ]
        self.assertEqual(
            plain,
            [],
            "Django's forms.ChoiceField drops the description a Choice "
            "carries, so no option subtitle renders. Import ChoiceField and "
            "MultipleChoiceField from utilities.forms.fields in: " + ", ".join(plain),
        )

    def test_rendered_choice_fields_are_collected(self) -> None:
        """Test the convention check actually collects choice fields."""
        self.assertGreater(len(list(_iter_rendered_choice_fields())), 100)

    def test_dscp_labels_are_bare_code_points(self) -> None:
        """Test the DSCP labels carry no inline description."""
        embedded = [
            str(entry.label)
            for entry in QualityOfServiceDSCPChoices.CHOICES
            if "(" in str(entry.label)
        ]
        self.assertEqual(
            embedded,
            [],
            "A DSCP label is the code point alone. Its meaning belongs in the "
            "Choice description, where it renders as an option subtitle: "
            + ", ".join(embedded),
        )

    def test_choice_descriptions_reach_the_widget(self) -> None:
        """Test a described choice set renders its descriptions."""
        form_field = ACIBridgeDomainEditForm.base_fields["multi_destination_flooding"]
        self.assertEqual(
            form_field.widget.descriptions[BDMultiDestinationFloodingChoices.FLOOD_BD],
            "Flood in the Bridge Domain",
        )

    def test_split_descriptions_reach_the_widget(self) -> None:
        """Test a label split into code and description renders both."""
        form_field = ACIContractEditForm.base_fields["target_dscp"]
        self.assertEqual(
            dict(form_field.choices)[QualityOfServiceDSCPChoices.DSCP_CS4],
            "CS4",
        )
        self.assertEqual(
            form_field.widget.descriptions[QualityOfServiceDSCPChoices.DSCP_CS4],
            "Class Selector 4, policy plane and priority queue",
        )
