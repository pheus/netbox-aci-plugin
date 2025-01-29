# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.test import TestCase

from ..forms.tenant_app_profiles import (
    ACIAppProfileEditForm,
    ACIEndpointGroupEditForm,
)
from ..forms.tenant_contract_filters import (
    ACIContractFilterEditForm,
    ACIContractFilterEntryEditForm,
)
from ..forms.tenant_contracts import (
    ACIContractEditForm,
    ACIContractSubjectEditForm,
)
from ..forms.tenant_networks import (
    ACIBridgeDomainEditForm,
    ACIBridgeDomainSubnetEditForm,
    ACIVRFEditForm,
)
from ..forms.tenants import ACITenantEditForm
from ..models.tenant_app_profiles import ACIAppProfile
from ..models.tenant_networks import ACIVRF, ACIBridgeDomain
from ..models.tenants import ACITenant


class ACITenantFormTestCase(TestCase):
    """Test case for ACITenant form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are"
        " allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

    def test_invalid_aci_tenant_field_values(self) -> None:
        """Test validation of invalid ACI Tenant field values."""
        aci_tenant_form = ACITenantEditForm(
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
        aci_tenant_form = ACITenantEditForm(
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


class ACIVRFFormTestCase(TestCase):
    """Test case for ACIVRF form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are"
        " allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

    def test_invalid_aci_vrf_field_values(self) -> None:
        """Test validation of invalid ACI VRF field values."""
        aci_vrf_form = ACIVRFEditForm(
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


class ACIBridgeDomainFormTestCase(TestCase):
    """Test case for ACIBridgeDomain form."""

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

    def test_invalid_aci_bridge_domain_field_values(self) -> None:
        """Test validation of invalid ACI Bridge Domain field values."""
        aci_bd_form = ACIBridgeDomainEditForm(
            data={
                "name": "ACI BD Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_tenant": self.aci_tenant,
                "aci_vrf": self.aci_vrf,
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
        aci_bd_form = ACIBridgeDomainEditForm(
            data={
                "name": "ACIBD1",
                "name_alias": "Testing",
                "description": "BD for NetBox ACI Plugin",
                "aci_tenant": self.aci_tenant,
                "aci_vrf": self.aci_vrf,
            }
        )
        self.assertEqual(aci_bd_form.errors.get("name"), None)
        self.assertEqual(aci_bd_form.errors.get("name_alias"), None)
        self.assertEqual(aci_bd_form.errors.get("description"), None)


class ACIBridgeDomainSubnetFormTestCase(TestCase):
    """Test case for ACIBridgeDomainSubnet form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are"
        " allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

    def test_invalid_aci_bridge_domain_subnet_field_values(self) -> None:
        """Test validation of invalid ACI Bridge Domain Subnet field values."""
        aci_bd_subnet_form = ACIBridgeDomainSubnetEditForm(
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
        aci_bd_subnet_form = ACIBridgeDomainSubnetEditForm(
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


class ACIContractFilterFormTestCase(TestCase):
    """Test case for ACIContractFilter form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are"
        " allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

    def test_invalid_aci_contract_filter_field_values(self) -> None:
        """Test validation of invalid ACI Contract Filter field values."""
        aci_contract_filter = ACIContractFilterEditForm(
            data={
                "name": "ACI Contract Filter Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(
            aci_contract_filter.errors["name"], [self.name_error_message]
        )
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


class ACIContractFilterEntryFormTestCase(TestCase):
    """Test case for ACIContractFilterEntry form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are"
        " allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

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
        self.assertEqual(
            aci_contract_filter_entry.errors.get("name_alias"), None
        )
        self.assertEqual(
            aci_contract_filter_entry.errors.get("description"), None
        )


class ACIContractFormTestCase(TestCase):
    """Test case for ACIContract form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are"
        " allowed."
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
        self.assertEqual(
            aci_contract.errors["name"], [self.name_error_message]
        )
        self.assertEqual(
            aci_contract.errors["name_alias"], [self.name_error_message]
        )
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
        "Only alphanumeric characters, hyphens, periods and underscores are"
        " allowed."
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
        self.assertEqual(
            aci_contract_subject.errors["name"], [self.name_error_message]
        )
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
