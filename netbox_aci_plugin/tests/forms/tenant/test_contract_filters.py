# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....forms.tenant.contract_filters import (
    ACIContractFilterEditForm,
    ACIContractFilterEntryEditForm,
    ACIContractFilterEntryImportForm,
)
from ....models.tenant.contract_filters import (
    ACIContractFilter,
    ACIContractFilterEntry,
)
from ..base import ACIBaseFormTestCase


class ACIContractFilterEntryFormCoverageTestCase(ACIBaseFormTestCase):
    """Coverage tests for ACI Contract Filter Entry forms."""

    def test_edit_form_init_with_custom_protocol_and_ports(self) -> None:
        """Test the edit form pre-fills custom protocol and port fields."""
        contract_filter = ACIContractFilter.objects.create(
            name="ACIFormTestCFEntryFilter", aci_tenant=self.aci_tenant
        )
        entry = ACIContractFilterEntry.objects.create(
            name="ACIFormTestCustomEntry",
            aci_contract_filter=contract_filter,
            ip_protocol="200",
            destination_from_port="5000",
            destination_to_port="5001",
            source_from_port="6000",
            source_to_port="6001",
        )
        form = ACIContractFilterEntryEditForm(instance=entry)
        self.assertEqual(form.initial["ip_protocol_custom"], "200")
        self.assertEqual(form.initial["destination_from_port_custom"], "5000")

    def test_edit_form_clean_with_custom_protocol_and_ports(self) -> None:
        """Test the edit form clean resolves custom protocol and ports."""
        contract_filter = ACIContractFilter.objects.create(
            name="ACIFormTestCFEntryFilter2", aci_tenant=self.aci_tenant
        )
        form = ACIContractFilterEntryEditForm(
            data={
                "name": "ACIFormTestCleanEntry",
                "aci_contract_filter": contract_filter.pk,
                "ether_type": "ip",
                "ip_protocol_custom": "200",
                "destination_from_port_custom": "5000",
                "destination_to_port_custom": "5001",
                "source_from_port_custom": "6000",
                "source_to_port_custom": "6001",
            }
        )
        form.is_valid()
        self.assertEqual(str(form.cleaned_data.get("ip_protocol")), "200")

    def test_import_form_clean_field_returns_provided_value(self) -> None:
        """Test the import form clean_* returns a provided field value."""
        form = ACIContractFilterEntryImportForm(data={"ether_type": "ip"})
        form.is_valid()
        self.assertEqual(form.cleaned_data.get("ether_type"), "ip")

    def test_clean_tcp_rules_returns_selected_values(self) -> None:
        """Test clean_tcp_rules returns the selected non-empty values."""
        form = ACIContractFilterEntryImportForm(data={})
        form.cleaned_data = {"tcp_rules": ["ack", "syn"]}
        self.assertEqual(form.clean_tcp_rules(), ["ack", "syn"])


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
