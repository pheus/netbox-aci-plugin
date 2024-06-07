# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.test import TestCase

from ..forms.tenant_app_profiles import ACIAppProfileForm, ACIEndpointGroupForm
from ..forms.tenant_networks import (
    ACIBridgeDomainForm,
    ACIBridgeDomainSubnetForm,
    ACIVRFForm,
)
from ..forms.tenants import ACITenantForm


class ACITenantFormTestCase(TestCase):
    """Test case for ACITenant form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are\
        allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are\
        allowed."
    )

    def test_invalid_aci_tenant_field_values(self) -> None:
        """Test validation of invalid ACI Tenant field values."""
        aci_tenant_form = ACITenantForm(
            data={
                "name": "ACI Test Tenant 1",
                "name_alias": "ACI Test Tenant Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(
            aci_tenant_form.errors["name"], [self.name_error_message]
        )
        self.assertEqual(
            aci_tenant_form.errors["name_alias"], [self.name_error_message]
        )
        self.assertEqual(
            aci_tenant_form.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_tenant_field_values(self) -> None:
        """Test validation of valid ACI Tenant field values."""
        aci_tenant_form = ACITenantForm(
            data={
                "name": "ACITestTenant1",
                "name_alias": "TestingTenant",
                "description": "Tenant for NetBox ACI Plugin testing",
            }
        )
        self.assertEqual(aci_tenant_form.errors.get("name"), None)
        self.assertEqual(aci_tenant_form.errors.get("name_alias"), None)
        self.assertEqual(aci_tenant_form.errors.get("description"), None)


class ACIAppProfileFormTestCase(TestCase):
    """Test case for ACIAppProfile form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are\
        allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are\
        allowed."
    )

    def test_invalid_aci_app_profile_field_values(self) -> None:
        """Test validation of invalid ACI AppProfile field values."""
        aci_app_profile_form = ACIAppProfileForm(
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
        aci_app_profile_form = ACIAppProfileForm(
            data={
                "name": "ACIAppProfile1",
                "name_alias": "Testing",
                "description": "Application Profile for NetBox ACI Plugin",
            }
        )
        self.assertEqual(aci_app_profile_form.errors.get("name"), None)
        self.assertEqual(aci_app_profile_form.errors.get("name_alias"), None)
        self.assertEqual(aci_app_profile_form.errors.get("description"), None)


class ACIVRFFormTestCase(TestCase):
    """Test case for ACIVRF form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are\
        allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are\
        allowed."
    )

    def test_invalid_aci_vrf_field_values(self) -> None:
        """Test validation of invalid ACI VRF field values."""
        aci_vrf_form = ACIVRFForm(
            data={
                "name": "ACI VRF Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(
            aci_vrf_form.errors["name"], [self.name_error_message]
        )
        self.assertEqual(
            aci_vrf_form.errors["name_alias"], [self.name_error_message]
        )
        self.assertEqual(
            aci_vrf_form.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_vrf_field_values(self) -> None:
        """Test validation of valid ACI VRF field values."""
        aci_vrf_form = ACIVRFForm(
            data={
                "name": "ACIVRF1",
                "name_alias": "Testing",
                "description": "VRF for NetBox ACI Plugin",
            }
        )
        self.assertEqual(aci_vrf_form.errors.get("name"), None)
        self.assertEqual(aci_vrf_form.errors.get("name_alias"), None)
        self.assertEqual(aci_vrf_form.errors.get("description"), None)


class ACIBridgeDomainFormTestCase(TestCase):
    """Test case for ACIBridgeDomain form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are\
        allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are\
        allowed."
    )

    def test_invalid_aci_bridge_domain_field_values(self) -> None:
        """Test validation of invalid ACI Bridge Domain field values."""
        aci_bd_form = ACIBridgeDomainForm(
            data={
                "name": "ACI BD Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(aci_bd_form.errors["name"], [self.name_error_message])
        self.assertEqual(
            aci_bd_form.errors["name_alias"], [self.name_error_message]
        )
        self.assertEqual(
            aci_bd_form.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_bridge_domain_field_values(self) -> None:
        """Test validation of valid ACI Bridge Domain field values."""
        aci_bd_form = ACIBridgeDomainForm(
            data={
                "name": "ACIBD1",
                "name_alias": "Testing",
                "description": "BD for NetBox ACI Plugin",
            }
        )
        self.assertEqual(aci_bd_form.errors.get("name"), None)
        self.assertEqual(aci_bd_form.errors.get("name_alias"), None)
        self.assertEqual(aci_bd_form.errors.get("description"), None)


class ACIBridgeDomainSubnetFormTestCase(TestCase):
    """Test case for ACIBridgeDomainSubnet form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are\
        allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are\
        allowed."
    )

    def test_invalid_aci_bridge_domain_subnet_field_values(self) -> None:
        """Test validation of invalid ACI Bridge Domain Subnet field values."""
        aci_bd_subnet_form = ACIBridgeDomainSubnetForm(
            data={
                "name": "ACI BDSubnet Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(
            aci_bd_subnet_form.errors["name"], [self.name_error_message]
        )
        self.assertEqual(
            aci_bd_subnet_form.errors["name_alias"], [self.name_error_message]
        )
        self.assertEqual(
            aci_bd_subnet_form.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_bridge_domain_subnet_field_values(self) -> None:
        """Test validation of valid ACI Bridge Domain Subnet field values."""
        aci_bd_subnet_form = ACIBridgeDomainSubnetForm(
            data={
                "name": "ACIBDSubnet1",
                "name_alias": "Testing",
                "description": "BDSubnet for NetBox ACI Plugin",
            }
        )
        self.assertEqual(aci_bd_subnet_form.errors.get("name"), None)
        self.assertEqual(aci_bd_subnet_form.errors.get("name_alias"), None)
        self.assertEqual(aci_bd_subnet_form.errors.get("description"), None)


class ACIEndpointGroupFormTestCase(TestCase):
    """Test case for ACIEndpointGroup form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are\
        allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are\
        allowed."
    )

    def test_invalid_aci_endpoint_group_field_values(self) -> None:
        """Test validation of invalid ACI Endpoint Group field values."""
        aci_epg_form = ACIEndpointGroupForm(
            data={
                "name": "ACI Endpoint Group Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
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
        aci_epg_form = ACIEndpointGroupForm(
            data={
                "name": "ACIEndpointGroup1",
                "name_alias": "Testing",
                "description": "EPG for NetBox ACI Plugin",
            }
        )
        self.assertEqual(aci_epg_form.errors.get("name"), None)
        self.assertEqual(aci_epg_form.errors.get("name_alias"), None)
        self.assertEqual(aci_epg_form.errors.get("description"), None)
