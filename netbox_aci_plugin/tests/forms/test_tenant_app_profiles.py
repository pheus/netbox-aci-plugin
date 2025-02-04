# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.test import TestCase

from ...forms.tenant_app_profiles import (
    ACIAppProfileEditForm,
    ACIEndpointGroupEditForm,
)
from ...models.tenant_app_profiles import ACIAppProfile
from ...models.tenant_networks import ACIVRF, ACIBridgeDomain
from ...models.tenants import ACITenant


class ACIAppProfileFormTestCase(TestCase):
    """Test case for ACIAppProfile form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are"
        " allowed."
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
        self.assertEqual(
            aci_app_profile_form.errors["name"], [self.name_error_message]
        )
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


class ACIEndpointGroupFormTestCase(TestCase):
    """Test case for ACIEndpointGroup form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are"
        " allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

    @classmethod
    def setUp(cls):
        """Set up required objects for ACIBridgeDomainForm tests."""
        cls.aci_tenant = ACITenant.objects.create(name="ACITestTenant")
        cls.aci_vrf = ACIVRF.objects.create(
            name="ACITestVRF", aci_tenant=cls.aci_tenant
        )
        cls.aci_bd = ACIBridgeDomain.objects.create(
            name="ACITestBridgeDomain",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
        )
        cls.aci_app_profile = ACIAppProfile.objects.create(
            name="ACITestAppProfile", aci_tenant=cls.aci_tenant
        )

    def test_invalid_aci_endpoint_group_field_values(self) -> None:
        """Test validation of invalid ACI Endpoint Group field values."""
        aci_epg_form = ACIEndpointGroupEditForm(
            data={
                "name": "ACI Endpoint Group Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_app_profile": self.aci_app_profile,
                "aci_bridge_domain": self.aci_bd,
            }
        )
        self.assertEqual(
            aci_epg_form.errors["name"], [self.name_error_message]
        )
        self.assertEqual(
            aci_epg_form.errors["name_alias"], [self.name_error_message]
        )
        self.assertEqual(
            aci_epg_form.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_endpoint_group_field_values(self) -> None:
        """Test validation of valid ACI Endpoint Group field values."""
        aci_epg_form = ACIEndpointGroupEditForm(
            data={
                "name": "ACIEndpointGroup1",
                "name_alias": "Testing",
                "description": "EPG for NetBox ACI Plugin",
                "aci_app_profile": self.aci_app_profile,
                "aci_bridge_domain": self.aci_bd,
            }
        )
        self.assertEqual(aci_epg_form.errors.get("name"), None)
        self.assertEqual(aci_epg_form.errors.get("name_alias"), None)
        self.assertEqual(aci_epg_form.errors.get("description"), None)
