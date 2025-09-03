# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from ipam.models import IPAddress

from ....forms.tenant.endpoint_security_groups import (
    ACIEndpointSecurityGroupEditForm,
    ACIEsgEndpointGroupSelectorEditForm,
    ACIEsgEndpointSelectorEditForm,
)
from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.bridge_domains import ACIBridgeDomain
from ....models.tenant.endpoint_groups import ACIEndpointGroup
from ....models.tenant.endpoint_security_groups import ACIEndpointSecurityGroup
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF


class ACIEndpointSecurityGroupFormTestCase(TestCase):
    """Test case for ACIEndpointSecurityGroup form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are allowed."
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
        self.assertEqual(aci_esg_form.errors["name"], [self.name_error_message])
        self.assertEqual(aci_esg_form.errors["name_alias"], [self.name_error_message])
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


class ACIEsgEndpointGroupSelectorFormTestCase(TestCase):
    """Test case for ACIEsgEndpointGroupSelector form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

    @classmethod
    def setUp(cls):
        """Set up required objects for ACIEsgEndpointGroupSelector tests."""
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
        cls.aci_esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIEndpointSecurityGroup1",
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
        )
        cls.aci_epg = ACIEndpointGroup.objects.create(
            name="ACIEndpointGroup1",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )

    def test_invalid_aci_esg_epg_selector_field_values(self) -> None:
        """Test validation of invalid ACI ESG EPG Selector field values."""
        aci_esg_epg_selector_form = ACIEsgEndpointGroupSelectorEditForm(
            data={
                "name": "ACI ESG Endpoint Group Selector Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_endpoint_security_group": self.aci_esg,
                "aci_epg_object_type": ContentType.objects.get_for_model(
                    self.aci_bd._meta.model
                ).id,
                "aci_epg_object": self.aci_bd,
            }
        )
        self.assertFalse(aci_esg_epg_selector_form.is_valid())
        self.assertEqual(
            aci_esg_epg_selector_form.errors["name"],
            [self.name_error_message],
        )
        self.assertEqual(
            aci_esg_epg_selector_form.errors["name_alias"],
            [self.name_error_message],
        )
        self.assertEqual(
            aci_esg_epg_selector_form.errors["description"],
            [self.description_error_message],
        )
        self.assertIn("aci_epg_object_type", aci_esg_epg_selector_form.errors)

    def test_valid_aci_esg_epg_selector_field_values(self) -> None:
        """Test validation of valid ACI ESG EPG Selector field values."""
        aci_esg_epg_selector_form = ACIEsgEndpointGroupSelectorEditForm(
            data={
                "name": "ACIEsgEndpointGroupSelector1",
                "name_alias": "Testing",
                "description": "ESG Endpoint Group Selector for NetBox ACI Plugin",
                "aci_endpoint_security_group": self.aci_esg,
                "aci_epg_object_type": ContentType.objects.get_for_model(
                    self.aci_epg._meta.model
                ).id,
                "aci_epg_object": self.aci_epg,
            }
        )
        self.assertTrue(aci_esg_epg_selector_form.is_valid())
        self.assertEqual(aci_esg_epg_selector_form.errors.get("name"), None)
        self.assertEqual(aci_esg_epg_selector_form.errors.get("name_alias"), None)
        self.assertEqual(aci_esg_epg_selector_form.errors.get("description"), None)
        self.assertNotIn("aci_epg_object_type", aci_esg_epg_selector_form.errors)


class ACIEsgEndpointSelectorFormTestCase(TestCase):
    """Test case for ACIEsgEndpointSelector form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

    @classmethod
    def setUp(cls):
        """Set up required objects for ACIEsgEndpointSelector tests."""
        cls.aci_tenant = ACITenant.objects.create(name="ACITestTenant")
        cls.aci_vrf = ACIVRF.objects.create(
            name="ACITestVRF", aci_tenant=cls.aci_tenant
        )
        cls.aci_app_profile = ACIAppProfile.objects.create(
            name="ACITestAppProfile", aci_tenant=cls.aci_tenant
        )
        cls.aci_esg = ACIEndpointSecurityGroup.objects.create(
            name="ACIEndpointSecurityGroup1",
            aci_app_profile=cls.aci_app_profile,
            aci_vrf=cls.aci_vrf,
        )
        cls.ip_address = IPAddress.objects.create(address="192.168.1.1/32")

    def test_invalid_aci_endpoint_selector_field_values(self) -> None:
        """Test validation of invalid ESG Endpoint Selector field values."""
        aci_esg_ep_selector_form = ACIEsgEndpointSelectorEditForm(
            data={
                "name": "ACI ESG Endpoint Selector Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_endpoint_security_group": self.aci_esg,
                "ep_object_type": ContentType.objects.get_for_model(
                    self.aci_vrf._meta.model
                ).id,
                "ep_object": self.aci_vrf,
            }
        )
        self.assertFalse(aci_esg_ep_selector_form.is_valid())
        self.assertEqual(
            aci_esg_ep_selector_form.errors["name"],
            [self.name_error_message],
        )
        self.assertEqual(
            aci_esg_ep_selector_form.errors["name_alias"],
            [self.name_error_message],
        )
        self.assertEqual(
            aci_esg_ep_selector_form.errors["description"],
            [self.description_error_message],
        )
        self.assertIn("ep_object_type", aci_esg_ep_selector_form.errors)

    def test_valid_aci_endpoint_selector_field_values(self) -> None:
        """Test validation of valid ESG Endpoint Selector field values."""
        aci_esg_ep_selector_form = ACIEsgEndpointSelectorEditForm(
            data={
                "name": "ACIEsgEndpointSelector1",
                "name_alias": "Testing",
                "description": "ESG Endpoint Selector for NetBox ACI Plugin",
                "aci_endpoint_security_group": self.aci_esg,
                "ep_object_type": ContentType.objects.get_for_model(
                    self.ip_address._meta.model
                ).id,
                "ep_object": self.ip_address,
            }
        )
        self.assertTrue(aci_esg_ep_selector_form.is_valid())
        self.assertEqual(aci_esg_ep_selector_form.errors.get("name"), None)
        self.assertEqual(aci_esg_ep_selector_form.errors.get("name_alias"), None)
        self.assertEqual(aci_esg_ep_selector_form.errors.get("description"), None)
        self.assertNotIn("ep_object_type", aci_esg_ep_selector_form.errors)
