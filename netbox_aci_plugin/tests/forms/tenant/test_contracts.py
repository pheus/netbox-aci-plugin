# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.test import TestCase

from ....forms.tenant.contracts import (
    ACIContractEditForm,
    ACIContractSubjectEditForm,
)


class ACIContractFormTestCase(TestCase):
    """Test case for ACIContract form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

    def test_invalid_aci_contract_field_values(self) -> None:
        """Test validation of invalid ACI Contract field values."""
        aci_contract = ACIContractEditForm(
            data={
                "name": "ACI Contract Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(aci_contract.errors["name"], [self.name_error_message])
        self.assertEqual(aci_contract.errors["name_alias"], [self.name_error_message])
        self.assertEqual(
            aci_contract.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_contract_field_values(self) -> None:
        """Test validation of valid ACI Contract field values."""
        aci_contract = ACIContractEditForm(
            data={
                "name": "ACIContract1",
                "name_alias": "Testing",
                "description": "Contract for NetBox ACI Plugin",
            }
        )
        self.assertEqual(aci_contract.errors.get("name"), None)
        self.assertEqual(aci_contract.errors.get("name_alias"), None)
        self.assertEqual(aci_contract.errors.get("description"), None)


class ACIContractSubjectFormTestCase(TestCase):
    """Test case for ACIContractSubject form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

    def test_invalid_aci_contract_subject_field_values(self) -> None:
        """Test validation of invalid ACI Contract Subject field values."""
        aci_contract_subject = ACIContractSubjectEditForm(
            data={
                "name": "ACI Contract Subject Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(aci_contract_subject.errors["name"], [self.name_error_message])
        self.assertEqual(
            aci_contract_subject.errors["name_alias"],
            [self.name_error_message],
        )
        self.assertEqual(
            aci_contract_subject.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_contract_subject_field_values(self) -> None:
        """Test validation of valid ACI Contract Subject field values."""
        aci_contract_subject = ACIContractSubjectEditForm(
            data={
                "name": "ACIContractSubject1",
                "name_alias": "Testing",
                "description": "Contract Subject for NetBox ACI Plugin",
            }
        )
        self.assertEqual(aci_contract_subject.errors.get("name"), None)
        self.assertEqual(aci_contract_subject.errors.get("name_alias"), None)
        self.assertEqual(aci_contract_subject.errors.get("description"), None)
