# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django import forms

from ....forms.tenant.bridge_domains import (
    ACIBridgeDomainEditForm,
    ACIBridgeDomainFilterForm,
    ACIBridgeDomainImportForm,
    ACIBridgeDomainL3OutBindingEditForm,
    ACIBridgeDomainL3OutBindingImportForm,
    ACIBridgeDomainSubnetEditForm,
)
from ....models.access_policies.domains import ACIRoutedDomain
from ....models.tenant.l3outs import ACIL3Out
from ....models.tenant.vrfs import ACIVRF
from ..base import ACIBaseFormTestCase


class ACIBridgeDomainImportFormCoverageTestCase(ACIBaseFormTestCase):
    """Coverage tests for ACI Bridge Domain import forms."""

    def test_bd_import_form_vrf_in_common(self) -> None:
        """Test the BD import form narrows the VRF queryset to 'common'."""
        form = ACIBridgeDomainImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_tenant": self.aci_tenant.name,
                "is_aci_vrf_in_common": "true",
            }
        )
        self.assertIn("aci_vrf", form.fields)

    def test_bd_l3out_binding_import_form_filters_bd_by_vrf(self) -> None:
        """Test the BD-L3Out binding import form filters BD by VRF."""
        form = ACIBridgeDomainL3OutBindingImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_tenant": self.aci_tenant.name,
                "aci_vrf": self.aci_vrf.name,
            }
        )
        self.assertIn("aci_bridge_domain", form.fields)


class ACIBridgeDomainFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIBridgeDomain form."""

    def test_filter_form_choice_fields_accept_multiple(self) -> None:
        """Test the BD filter form accepts multiple choice values."""
        multi_fields = (
            "multi_destination_flooding",
            "unknown_ipv4_multicast",
            "unknown_ipv6_multicast",
            "unknown_unicast",
        )
        unbound = ACIBridgeDomainFilterForm()
        data = {}
        for name in multi_fields:
            field = unbound.fields[name]
            self.assertIsInstance(field, forms.MultipleChoiceField)
            data[name] = [choice[0] for choice in field.choices if choice[0]][:2]
        form = ACIBridgeDomainFilterForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        for name in multi_fields:
            self.assertEqual(form.cleaned_data[name], data[name])

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
        self.assertEqual(aci_bd_form.errors["name_alias"], [self.name_error_message])
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


class ACIBridgeDomainSubnetFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIBridgeDomainSubnet form."""

    def test_invalid_aci_bridge_domain_subnet_field_values(self) -> None:
        """Test validation of invalid ACI Bridge Domain Subnet field values."""
        aci_bd_subnet_form = ACIBridgeDomainSubnetEditForm(
            data={
                "name": "ACI BDSubnet Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(aci_bd_subnet_form.errors["name"], [self.name_error_message])
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


class ACIBridgeDomainL3OutBindingFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIBridgeDomainL3OutBinding form."""

    @classmethod
    def setUpTestData(cls):
        """Set up required objects for BD L3Out Relation form tests."""
        super().setUpTestData()
        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIBaseFormTestRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_l3out = ACIL3Out.objects.create(
            name="ACIBaseFormTestL3Out",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.aci_vrf2 = ACIVRF.objects.create(
            name="ACIBaseFormTestVRF2",
            aci_tenant=cls.aci_tenant,
        )
        cls.aci_l3out_vrf2 = ACIL3Out.objects.create(
            name="ACIBaseFormTestL3OutVRF2",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf2,
            aci_routed_domain=cls.aci_routed_domain,
        )

    def test_invalid_aci_bridge_domain_l3out_binding_values(self) -> None:
        """Test validation of invalid ACI BD L3Out Relation values."""
        form = ACIBridgeDomainL3OutBindingEditForm(
            data={
                "aci_bridge_domain": self.aci_bd,
                "aci_l3out": self.aci_l3out_vrf2,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("aci_l3out", form.errors)

    def test_valid_aci_bridge_domain_l3out_binding_values(self) -> None:
        """Test validation of valid ACI Bridge Domain L3Out Relation values."""
        form = ACIBridgeDomainL3OutBindingEditForm(
            data={
                "aci_bridge_domain": self.aci_bd,
                "aci_l3out": self.aci_l3out,
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors.get("aci_bridge_domain"), None)
        self.assertEqual(form.errors.get("aci_l3out"), None)
