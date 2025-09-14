# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....forms.tenant.contract_filters import (
    ACIContractFilterEditForm,
    ACIContractFilterEntryEditForm,
)
from ..base import ACIBaseFormTestCase


class ACIContractFilterFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIContractFilter form."""

    def test_invalid_aci_contract_filter_field_values(self) -> None:
        """Test validation of invalid ACI Contract Filter field values."""
        aci_contract_filter = ACIContractFilterEditForm(
            data={
                "name": "ACI Contract Filter Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(aci_contract_filter.errors["name"], [self.name_error_message])
        self.assertEqual(
            aci_contract_filter.errors["name_alias"], [self.name_error_message]
        )
        self.assertEqual(
            aci_contract_filter.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_contract_filter_field_values(self) -> None:
        """Test validation of valid ACI Contract Filter field values."""
        aci_contract_filter = ACIContractFilterEditForm(
            data={
                "name": "ACIContractFilter1",
                "name_alias": "Testing",
                "description": "Contract Filter for NetBox ACI Plugin",
            }
        )
        self.assertEqual(aci_contract_filter.errors.get("name"), None)
        self.assertEqual(aci_contract_filter.errors.get("name_alias"), None)
        self.assertEqual(aci_contract_filter.errors.get("description"), None)


class ACIContractFilterEntryFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIContractFilterEntry form."""

    def test_invalid_aci_contract_filter_entry_field_values(self) -> None:
        """Test validation of invalid Contract Filter Entry field values."""
        aci_contract_filter_entry = ACIContractFilterEntryEditForm(
            data={
                "name": "ACI Contract Filter Entry Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(
            aci_contract_filter_entry.errors["name"], [self.name_error_message]
        )
        self.assertEqual(
            aci_contract_filter_entry.errors["name_alias"],
            [self.name_error_message],
        )
        self.assertEqual(
            aci_contract_filter_entry.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_contract_filter_entry_field_values(self) -> None:
        """Test validation of valid Contract Filter Entry field values."""
        aci_contract_filter_entry = ACIContractFilterEntryEditForm(
            data={
                "name": "ACIContractFilterEntry1",
                "name_alias": "Testing",
                "description": "Contract Filter Entry for NetBox ACI Plugin",
            }
        )
        self.assertEqual(aci_contract_filter_entry.errors.get("name"), None)
        self.assertEqual(aci_contract_filter_entry.errors.get("name_alias"), None)
        self.assertEqual(aci_contract_filter_entry.errors.get("description"), None)
