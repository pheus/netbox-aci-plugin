# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.test import TestCase

from ....forms.tenant.app_profiles import ACIAppProfileEditForm


class ACIAppProfileFormTestCase(TestCase):
    """Test case for ACIAppProfile form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

    def test_invalid_aci_app_profile_field_values(self) -> None:
        """Test validation of invalid ACI AppProfile field values."""
        aci_app_profile_form = ACIAppProfileEditForm(
            data={
                "name": "ACI App Profile Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(aci_app_profile_form.errors["name"], [self.name_error_message])
        self.assertEqual(
            aci_app_profile_form.errors["name_alias"],
            [self.name_error_message],
        )
        self.assertEqual(
            aci_app_profile_form.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_app_profile_field_values(self) -> None:
        """Test validation of valid ACI AppProfile field values."""
        aci_app_profile_form = ACIAppProfileEditForm(
            data={
                "name": "ACIAppProfile1",
                "name_alias": "Testing",
                "description": "Application Profile for NetBox ACI Plugin",
            }
        )
        self.assertEqual(aci_app_profile_form.errors.get("name"), None)
        self.assertEqual(aci_app_profile_form.errors.get("name_alias"), None)
        self.assertEqual(aci_app_profile_form.errors.get("description"), None)
