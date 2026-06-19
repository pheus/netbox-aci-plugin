# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms

from ....forms.tenant.vrfs import ACIVRFEditForm, ACIVRFFilterForm
from ..base import ACIBaseFormTestCase


class ACIVRFFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIVRF form."""

    def test_invalid_aci_vrf_field_values(self) -> None:
        """Test validation of invalid ACI VRF field values."""
        aci_vrf_form = ACIVRFEditForm(
            data={
                "name": "ACI VRF Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(aci_vrf_form.errors["name"], [self.name_error_message])
        self.assertEqual(aci_vrf_form.errors["name_alias"], [self.name_error_message])
        self.assertEqual(
            aci_vrf_form.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_vrf_field_values(self) -> None:
        """Test validation of valid ACI VRF field values."""
        aci_vrf_form = ACIVRFEditForm(
            data={
                "name": "ACIVRF1",
                "name_alias": "Testing",
                "description": "VRF for NetBox ACI Plugin",
            }
        )
        self.assertEqual(aci_vrf_form.errors.get("name"), None)
        self.assertEqual(aci_vrf_form.errors.get("name_alias"), None)
        self.assertEqual(aci_vrf_form.errors.get("description"), None)

    def test_filter_form_choice_fields_accept_multiple(self) -> None:
        """Test the VRF filter form accepts multiple choice values."""
        multi_fields = ("pc_enforcement_direction", "pc_enforcement_preference")
        unbound = ACIVRFFilterForm()
        data = {}
        for name in multi_fields:
            field = unbound.fields[name]
            self.assertIsInstance(field, forms.MultipleChoiceField)
            data[name] = [choice[0] for choice in field.choices if choice[0]][:2]
        form = ACIVRFFilterForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        for name in multi_fields:
            self.assertEqual(form.cleaned_data[name], data[name])
