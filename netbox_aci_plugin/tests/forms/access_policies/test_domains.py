# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from ....forms.access_policies.domains import ACIRoutedDomainEditForm
from ..base import ACIBaseFormTestCase


class ACIRoutedDomainFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIRoutedDomain form."""

    def test_invalid_aci_routed_domain_field_values(self) -> None:
        """Test validation of invalid ACI Routed Domain field values."""
        form = ACIRoutedDomainEditForm(
            data={
                "name": "ACI Routed Domain Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_fabric": self.aci_fabric,
                "security_domains": "Invalid Security Domain",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], [self.name_error_message])
        self.assertEqual(form.errors["name_alias"], [self.name_error_message])
        self.assertEqual(form.errors["description"], [self.description_error_message])
        self.assertIn("security_domains", form.errors)

    def test_valid_aci_routed_domain_field_values(self) -> None:
        """Test validation of valid ACI Routed Domain field values."""
        form = ACIRoutedDomainEditForm(
            data={
                "name": "ACIRoutedDomain1",
                "name_alias": "Testing",
                "description": "ACI Routed Domain for NetBox ACI Plugin",
                "aci_fabric": self.aci_fabric,
                "security_domains": "all,netops",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors.get("name"), None)
        self.assertEqual(form.errors.get("name_alias"), None)
        self.assertEqual(form.errors.get("description"), None)
        self.assertEqual(form.errors.get("security_domains"), None)

    def test_valid_aci_routed_domain_empty_security_domains(self) -> None:
        """Test validation of empty security domains list."""
        form = ACIRoutedDomainEditForm(
            data={
                "name": "ACIRoutedDomain1",
                "aci_fabric": self.aci_fabric,
                "security_domains": "",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors.get("security_domains"), None)

    def test_clean_security_domains_strips_whitespace(self) -> None:
        """Test that clean_security_domains strips whitespace."""
        form = ACIRoutedDomainEditForm(
            data={
                "name": "ACIRoutedDomain1",
                "aci_fabric": self.aci_fabric,
                "security_domains": " all , netops ",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["security_domains"], ["all", "netops"])
