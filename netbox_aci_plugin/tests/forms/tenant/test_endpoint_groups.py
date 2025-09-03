# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from ipam.models import IPAddress

from ....forms.tenant.endpoint_groups import (
    ACIEndpointGroupEditForm,
    ACIUSegEndpointGroupEditForm,
    ACIUSegNetworkAttributeEditForm,
)
from ....models.tenant.app_profiles import ACIAppProfile
from ....models.tenant.bridge_domains import ACIBridgeDomain
from ....models.tenant.endpoint_groups import ACIUSegEndpointGroup
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF


class ACIEndpointGroupFormTestCase(TestCase):
    """Test case for ACIEndpointGroup form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are allowed."
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
        self.assertEqual(aci_epg_form.errors["name"], [self.name_error_message])
        self.assertEqual(aci_epg_form.errors["name_alias"], [self.name_error_message])
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


class ACIUSegEndpointGroupFormTestCase(TestCase):
    """Test case for ACIUSegEndpointGroup form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

    @classmethod
    def setUp(cls):
        """Set up required objects for ACIUSegEndpointGroupForm tests."""
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

    def test_invalid_aci_useg_endpoint_group_field_values(self) -> None:
        """Test validation of invalid ACI uSeg Endpoint Group field values."""
        aci_useg_epg_form = ACIUSegEndpointGroupEditForm(
            data={
                "name": "ACI uSeg Endpoint Group Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_app_profile": self.aci_app_profile,
                "aci_bridge_domain": self.aci_bd,
            }
        )
        self.assertEqual(aci_useg_epg_form.errors["name"], [self.name_error_message])
        self.assertEqual(
            aci_useg_epg_form.errors["name_alias"], [self.name_error_message]
        )
        self.assertEqual(
            aci_useg_epg_form.errors["description"],
            [self.description_error_message],
        )

    def test_valid_aci_useg_endpoint_group_field_values(self) -> None:
        """Test validation of valid ACI uSeg Endpoint Group field values."""
        aci_useg_epg_form = ACIUSegEndpointGroupEditForm(
            data={
                "name": "ACIUSegEndpointGroup1",
                "name_alias": "Testing",
                "description": "uSeg EPG for NetBox ACI Plugin",
                "aci_app_profile": self.aci_app_profile,
                "aci_bridge_domain": self.aci_bd,
            }
        )
        self.assertEqual(aci_useg_epg_form.errors.get("name"), None)
        self.assertEqual(aci_useg_epg_form.errors.get("name_alias"), None)
        self.assertEqual(aci_useg_epg_form.errors.get("description"), None)


class ACIUSegNetworkAttributeFormTestCase(TestCase):
    """Test case for ACIUSegNetworkAttribute form."""

    name_error_message: str = (
        "Only alphanumeric characters, hyphens, periods and underscores are allowed."
    )
    description_error_message: str = (
        "Only alphanumeric characters and !#$%()*,-./:;@ _{|}~?&+ are allowed."
    )

    @classmethod
    def setUp(cls):
        """Set up required objects for ACIUSegNetworkAttributeForm tests."""
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
        cls.aci_useg_epg = ACIUSegEndpointGroup.objects.create(
            name="ACIUSegEndpointGroup1",
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.ip_address = IPAddress.objects.create(address="192.168.1.1/32")

    def test_invalid_aci_useg_network_attribute_field_values(self) -> None:
        """Test validation of invalid uSeg Network Attribute field values."""
        aci_useg_network_attr_form = ACIUSegNetworkAttributeEditForm(
            data={
                "name": "ACI uSeg Network Attribute Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_useg_endpoint_group": self.aci_useg_epg,
                "attr_object_type": ContentType.objects.get_for_model(
                    self.aci_bd._meta.model
                ).id,
                "attr_object": self.aci_bd,
            }
        )
        self.assertFalse(aci_useg_network_attr_form.is_valid())
        self.assertEqual(
            aci_useg_network_attr_form.errors["name"],
            [self.name_error_message],
        )
        self.assertEqual(
            aci_useg_network_attr_form.errors["name_alias"],
            [self.name_error_message],
        )
        self.assertEqual(
            aci_useg_network_attr_form.errors["description"],
            [self.description_error_message],
        )
        self.assertIn("attr_object_type", aci_useg_network_attr_form.errors)

    def test_valid_aci_useg_network_attribute_field_values(self) -> None:
        """Test validation of valid ACI uSeg Network Attribute field values."""
        aci_useg_network_attr_form = ACIUSegNetworkAttributeEditForm(
            data={
                "name": "ACIUSegNetworkAttribute1",
                "name_alias": "Testing",
                "description": "uSeg Network Attribute for NetBox ACI Plugin",
                "aci_useg_endpoint_group": self.aci_useg_epg,
                "attr_object_type": ContentType.objects.get_for_model(
                    self.ip_address._meta.model
                ).id,
                "attr_object": self.ip_address,
            }
        )
        self.assertTrue(aci_useg_network_attr_form.is_valid())
        self.assertEqual(aci_useg_network_attr_form.errors.get("name"), None)
        self.assertEqual(aci_useg_network_attr_form.errors.get("name_alias"), None)
        self.assertEqual(aci_useg_network_attr_form.errors.get("description"), None)
        self.assertNotIn("attr_object_type", aci_useg_network_attr_form.errors)
