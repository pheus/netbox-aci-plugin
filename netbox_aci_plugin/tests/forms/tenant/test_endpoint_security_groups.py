# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.test import TestCase

from ....forms.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroupEditForm,
)
from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF


class ACIEndpointSecurityGroupFormTestCase(TestCase):
    """Test case for ACIEndpointSecurityGroup form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are"
        " allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

    @classmethod
    def setUp(cls):
        """Set up required objects for ACIEndpointSecurityGroupForm tests."""
        cls.aci_tenant = ACITenant.objects.create(name="ACITestTenant")
        cls.aci_vrf = ACIVRF.objects.create(
            name="ACITestVRF", aci_tenant=cls.aci_tenant
        )
        cls.aci_app_profile = ACIAppProfile.objects.create(
            name="ACITestAppProfile", aci_tenant=cls.aci_tenant
        )

    def test_invalid_aci_endpoint_security_group_field_values(self) -> None:
        """Test validation of invalid Endpoint Security Group field values."""
        aci_esg_form = ACIEndpointSecurityGroupEditForm(
            data={
                "name": "ACI Endpoint Security Group Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_app_profile": self.aci_app_profile,
                "aci_vrf": self.aci_vrf,
            }
        )
        self.assertEqual(
            aci_esg_form.errors["name"], [self.name_error_message]
        )
        self.assertEqual(
            aci_esg_form.errors["name_alias"], [self.name_error_message]
        )
        self.assertEqual(
            aci_esg_form.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_endpoint_security_group_field_values(self) -> None:
        """Test validation of valid Endpoint Security Group field values."""
        aci_esg_form = ACIEndpointSecurityGroupEditForm(
            data={
                "name": "ACIEndpointSecurityGroup1",
                "name_alias": "Testing",
                "description": "ESG for NetBox ACI Plugin",
                "aci_app_profile": self.aci_app_profile,
                "aci_vrf": self.aci_vrf,
            }
        )
        self.assertEqual(aci_esg_form.errors.get("name"), None)
        self.assertEqual(aci_esg_form.errors.get("name_alias"), None)
        self.assertEqual(aci_esg_form.errors.get("description"), None)
