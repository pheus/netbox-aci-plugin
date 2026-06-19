# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Form tests for tenant L3Out models."""

from django import forms

from ipam.models import Prefix

from ....choices import QualityOfServiceClassChoices, QualityOfServiceDSCPChoices
from ....forms.tenant.l3outs import (
    ACIExternalEndpointGroupEditForm,
    ACIExternalEndpointGroupFilterForm,
    ACIExternalSubnetEditForm,
    ACIExternalSubnetImportForm,
    ACIL3OutEditForm,
    ACIL3OutFilterForm,
)
from ....models.access_policies.domains import ACIRoutedDomain
from ....models.tenant.l3outs import (
    ACIExternalEndpointGroup,
    ACIExternalSubnet,
    ACIL3Out,
)
from ....models.tenant.tenants import ACITenant
from ....models.tenant.vrfs import ACIVRF
from ..base import ACIBaseFormTestCase


class ACIExternalSubnetImportFormCoverageTestCase(ACIBaseFormTestCase):
    """Coverage tests for ACI External Subnet import form."""

    def test_import_form_filters_prefix_by_vrf(self) -> None:
        """Test the import form filters nb_prefix by the provided nb_vrf."""
        form = ACIExternalSubnetImportForm(
            data={"nb_prefix": "10.0.0.0/24", "nb_vrf": self.nb_vrf.name}
        )
        self.assertIn("nb_prefix", form.fields)


class ACIL3OutFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIL3Out form."""

    @classmethod
    def setUpTestData(cls):
        """Set up required objects for ACIL3Out form tests."""
        super().setUpTestData()
        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIBaseFormTestRoutedDomain",
            aci_fabric=cls.aci_fabric,
        )
        cls.infra_tenant = ACITenant.objects.create(
            name="infra",
            aci_fabric=cls.aci_fabric,
        )
        cls.infra_vrf = ACIVRF.objects.create(
            name="ACIBaseFormTestInfraVRF",
            aci_tenant=cls.infra_tenant,
        )

    def test_invalid_aci_l3out_field_values(self) -> None:
        """Test validation of invalid ACI L3Out field values."""
        form = ACIL3OutEditForm(
            data={
                "name": "ACI L3Out Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_tenant": self.aci_tenant,
                "aci_vrf": self.aci_vrf,
                "aci_routed_domain": self.aci_routed_domain,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], [self.name_error_message])
        self.assertEqual(form.errors["name_alias"], [self.name_error_message])
        self.assertEqual(form.errors["description"], [self.description_error_message])

    def test_valid_aci_l3out_field_values(self) -> None:
        """Test validation of valid ACI L3Out field values."""
        form = ACIL3OutEditForm(
            data={
                "name": "ACIL3Out1",
                "name_alias": "Testing",
                "description": "L3Out for NetBox ACI Plugin",
                "aci_tenant": self.aci_tenant,
                "aci_vrf": self.aci_vrf,
                "aci_routed_domain": self.aci_routed_domain,
                "target_dscp": QualityOfServiceDSCPChoices.DSCP_AF11,
                "bgp_enabled": True,
                "ospf_enabled": False,
                "eigrp_enabled": False,
                "multipod_enabled": False,
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors.get("name"), None)
        self.assertEqual(form.errors.get("name_alias"), None)
        self.assertEqual(form.errors.get("description"), None)
        self.assertEqual(form.errors.get("multipod_enabled"), None)

    def test_invalid_aci_l3out_multipod_enabled_tenant(self) -> None:
        """Test Multi-Pod validation of invalid ACI L3Out tenant."""
        form = ACIL3OutEditForm(
            data={
                "name": "ACIL3OutMultiPod1",
                "name_alias": "Testing",
                "description": "L3Out for NetBox ACI Plugin",
                "aci_tenant": self.aci_tenant,
                "aci_vrf": self.aci_vrf,
                "aci_routed_domain": self.aci_routed_domain,
                "multipod_enabled": True,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("multipod_enabled", form.errors)

    def test_valid_aci_l3out_multipod_enabled_tenant(self) -> None:
        """Test Multi-Pod validation of valid ACI L3Out tenant."""
        form = ACIL3OutEditForm(
            data={
                "name": "ACIL3OutMultiPod2",
                "name_alias": "Testing",
                "description": "L3Out for NetBox ACI Plugin",
                "aci_tenant": self.infra_tenant,
                "aci_vrf": self.infra_vrf,
                "aci_routed_domain": self.aci_routed_domain,
                "multipod_enabled": True,
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors.get("multipod_enabled"), None)

    def test_aci_l3out_export_route_control_enforcement_disabled_field(
        self,
    ) -> None:
        """Test that the export route control enforcement field is disabled."""
        form = ACIL3OutEditForm()
        field = form.fields["export_route_control_enforcement_enabled"]
        self.assertTrue(field.disabled)
        self.assertTrue(field.initial)

    def test_filter_form_target_dscp_accepts_multiple(self) -> None:
        """Test the L3Out filter accepts multiple target DSCP values."""
        unbound = ACIL3OutFilterForm()
        field = unbound.fields["target_dscp"]
        self.assertIsInstance(field, forms.MultipleChoiceField)
        values = [choice[0] for choice in field.choices if choice[0]][:2]
        form = ACIL3OutFilterForm(data={"target_dscp": values})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["target_dscp"], values)


class ACIExternalEndpointGroupFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIExternalEndpointGroup form."""

    @classmethod
    def setUpTestData(cls):
        """Set up required objects for ACIExternalEndpointGroup form tests."""
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

    def test_invalid_aci_external_endpoint_group_field_values(self) -> None:
        """Test validation of invalid ACI External EPG field values."""
        form = ACIExternalEndpointGroupEditForm(
            data={
                "name": "ACI External Endpoint Group Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_l3out": self.aci_l3out,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], [self.name_error_message])
        self.assertEqual(form.errors["name_alias"], [self.name_error_message])
        self.assertEqual(form.errors["description"], [self.description_error_message])

    def test_valid_aci_external_endpoint_group_field_values(self) -> None:
        """Test validation of valid ACI External EPG field values."""
        form = ACIExternalEndpointGroupEditForm(
            data={
                "name": "ACIExternalEndpointGroup1",
                "name_alias": "Testing",
                "description": "External EPG for NetBox ACI Plugin",
                "aci_l3out": self.aci_l3out,
                "preferred_group_member_enabled": True,
                "qos_class": QualityOfServiceClassChoices.CLASS_LEVEL_1,
                "target_dscp": QualityOfServiceDSCPChoices.DSCP_AF11,
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors.get("name"), None)
        self.assertEqual(form.errors.get("name_alias"), None)
        self.assertEqual(form.errors.get("description"), None)

    def test_filter_form_choice_fields_accept_multiple(self) -> None:
        """Test the External EPG filter accepts multiple choice values."""
        multi_fields = ("target_dscp", "qos_class")
        unbound = ACIExternalEndpointGroupFilterForm()
        data = {}
        for name in multi_fields:
            field = unbound.fields[name]
            self.assertIsInstance(field, forms.MultipleChoiceField)
            data[name] = [choice[0] for choice in field.choices if choice[0]][:2]
        form = ACIExternalEndpointGroupFilterForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        for name in multi_fields:
            self.assertEqual(form.cleaned_data[name], data[name])


class ACIExternalSubnetFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIExternalSubnet form."""

    @classmethod
    def setUpTestData(cls):
        """Set up required objects for ACIExternalSubnet form tests."""
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
        cls.aci_external_epg = ACIExternalEndpointGroup.objects.create(
            name="ACIBaseFormTestExternalEPG",
            aci_l3out=cls.aci_l3out,
        )
        cls.prefix = Prefix.objects.create(prefix="10.0.0.0/24")

    def test_invalid_aci_external_subnet_field_values(self) -> None:
        """Test validation of invalid ACI External Subnet field values."""
        form = ACIExternalSubnetEditForm(
            data={
                "name": "ACI External Subnet Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_external_endpoint_group": self.aci_external_epg,
                "prefix": self.prefix,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], [self.name_error_message])
        self.assertEqual(form.errors["name_alias"], [self.name_error_message])
        self.assertEqual(form.errors["description"], [self.description_error_message])

    def test_valid_aci_external_subnet_field_values(self) -> None:
        """Test validation of valid ACI External Subnet field values."""
        form = ACIExternalSubnetEditForm(
            data={
                "name": "ACIExternalSubnet1",
                "name_alias": "Testing",
                "description": "External Subnet for NetBox ACI Plugin",
                "aci_external_endpoint_group": self.aci_external_epg,
                "matched_prefix": str(self.prefix.prefix),
                "import_route_control_enabled": False,
                "export_route_control_enabled": False,
                "shared_route_control_enabled": False,
                "import_security_enabled": True,
                "shared_security_enabled": False,
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors.get("name"), None)
        self.assertEqual(form.errors.get("name_alias"), None)
        self.assertEqual(form.errors.get("description"), None)
        self.assertEqual(form.errors.get("matched_prefix"), None)


class ACIExternalSubnetEditFormInitTestCase(ACIBaseFormTestCase):
    """Test case for ACIExternalSubnetEditForm matched_prefix clearing."""

    @classmethod
    def setUpTestData(cls):
        """Set up objects for ACIExternalSubnetEditForm __init__ tests."""
        super().setUpTestData()
        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name="ACIBaseFormTestRoutedDomainSubnetEdit",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_l3out = ACIL3Out.objects.create(
            name="ACIBaseFormTestL3OutSubnetEdit",
            aci_tenant=cls.aci_tenant,
            aci_vrf=cls.aci_vrf,
            aci_routed_domain=cls.aci_routed_domain,
        )
        cls.aci_epg = ACIExternalEndpointGroup.objects.create(
            name="ACIBaseFormTestEPGSubnetEdit",
            aci_l3out=cls.aci_l3out,
        )
        cls.prefix = Prefix.objects.create(prefix="10.50.0.0/24")
        cls.subnet_with_nb_prefix = ACIExternalSubnet.objects.create(
            name="ACIBaseFormTestSubnetWithNBPrefix",
            aci_external_endpoint_group=cls.aci_epg,
            nb_prefix=cls.prefix,
        )

    def test_edit_form_clears_matched_prefix_when_nb_prefix_set(self) -> None:
        """Test matched_prefix is cleared in initial when nb_prefix is set."""
        form = ACIExternalSubnetEditForm(instance=self.subnet_with_nb_prefix)
        self.assertEqual(form.initial.get("matched_prefix"), "")

    def test_edit_form_does_not_clear_matched_prefix_for_new_instance(
        self,
    ) -> None:
        """Test matched_prefix is not cleared for a new (unsaved) instance."""
        form = ACIExternalSubnetEditForm()
        self.assertNotEqual(form.initial.get("matched_prefix"), "")
