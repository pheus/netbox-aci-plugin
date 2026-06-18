# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType

from ipam.models import IPAddress

from ....choices import QualityOfServiceClassChoices
from ....forms.tenant.endpoint_groups import (
    ACIEndpointGroupEditForm,
    ACIEndpointGroupFilterForm,
    ACIEndpointGroupImportForm,
    ACIUSegEndpointGroupEditForm,
    ACIUSegEndpointGroupFilterForm,
    ACIUSegEndpointGroupImportForm,
    ACIUSegNetworkAttributeBulkEditForm,
    ACIUSegNetworkAttributeEditForm,
)
from ....models.tenant.endpoint_groups import ACIUSegEndpointGroup
from ..base import ACIBaseFormTestCase


class ACIEndpointGroupFormCoverageTestCase(ACIBaseFormTestCase):
    """Coverage tests for ACI EPG import and uSeg attribute forms."""

    def test_epg_import_form_bridge_domain_in_common(self) -> None:
        """Test the EPG import form narrows the BD queryset to 'common'."""
        form = ACIEndpointGroupImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_tenant": self.aci_tenant.name,
                "is_aci_bd_in_common": "true",
            }
        )
        self.assertIn("aci_bridge_domain", form.fields)

    def test_useg_epg_import_form_bridge_domain_in_common(self) -> None:
        """Test the uSeg EPG import form narrows the BD to 'common'."""
        form = ACIUSegEndpointGroupImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_tenant": self.aci_tenant.name,
                "is_aci_bd_in_common": "true",
            }
        )
        self.assertIn("aci_bridge_domain", form.fields)

    def test_useg_attr_edit_form_object_type_unknown(self) -> None:
        """Test the uSeg attribute edit form tolerates an unknown type."""
        form = ACIUSegNetworkAttributeEditForm(data={"attr_object_type": 99999999})
        self.assertIn("attr_object", form.fields)

    def test_useg_attr_bulk_edit_form_configures_field(self) -> None:
        """Test the uSeg attribute bulk edit form configures attr_object."""
        attr_object_type = ContentType.objects.get_for_model(IPAddress)
        form = ACIUSegNetworkAttributeBulkEditForm(
            data={"attr_object_type": attr_object_type.pk}
        )
        self.assertEqual(form.fields["attr_object"].queryset.model, IPAddress)

    def test_useg_attr_bulk_edit_form_object_type_unknown(self) -> None:
        """Test the uSeg attribute bulk edit form tolerates an unknown type."""
        form = ACIUSegNetworkAttributeBulkEditForm(data={"attr_object_type": 99999999})
        self.assertIn("attr_object", form.fields)

    def test_epg_filter_form_qos_class_accepts_multiple(self) -> None:
        """Test the EPG filter form accepts multiple QoS class values."""
        form = ACIEndpointGroupFilterForm(
            data={
                "qos_class": [
                    QualityOfServiceClassChoices.CLASS_LEVEL_1,
                    QualityOfServiceClassChoices.CLASS_LEVEL_2,
                ]
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["qos_class"],
            [
                QualityOfServiceClassChoices.CLASS_LEVEL_1,
                QualityOfServiceClassChoices.CLASS_LEVEL_2,
            ],
        )

    def test_useg_epg_filter_form_qos_class_accepts_multiple(self) -> None:
        """Test the uSeg EPG filter form accepts multiple QoS values."""
        form = ACIUSegEndpointGroupFilterForm(
            data={
                "qos_class": [
                    QualityOfServiceClassChoices.CLASS_LEVEL_1,
                    QualityOfServiceClassChoices.CLASS_LEVEL_2,
                ]
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["qos_class"],
            [
                QualityOfServiceClassChoices.CLASS_LEVEL_1,
                QualityOfServiceClassChoices.CLASS_LEVEL_2,
            ],
        )


class ACIEndpointGroupFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIEndpointGroup form."""

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


class ACIUSegEndpointGroupFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIUSegEndpointGroup form."""

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


class ACIUSegNetworkAttributeFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIUSegNetworkAttribute form."""

    @classmethod
    def setUpTestData(cls):
        """Set up required objects for ACIUSegNetworkAttributeForm tests."""
        super().setUpTestData()

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
