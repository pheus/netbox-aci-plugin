# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType

from ....forms.access_policies.aaep import (
    ACIAAEPDomainBindingBulkEditForm,
    ACIAAEPDomainBindingEditForm,
    ACIAAEPDomainBindingImportForm,
    ACIAttachableAccessEntityProfileEditForm,
)
from ....models.access_policies.aaep import ACIAttachableAccessEntityProfile
from ....models.access_policies.domains import ACIPhysicalDomain, ACIRoutedDomain
from ....models.access_policies.vlan_pools import ACIVLANPool
from ..base import ACIBaseFormTestCase


class ACIAttachableAccessEntityProfileFormTestCase(ACIBaseFormTestCase):
    """Test case for the ACIAttachableAccessEntityProfile form."""

    def test_invalid_aci_aaep_field_values(self) -> None:
        """Test validation of invalid ACI AAEP field values."""
        form = ACIAttachableAccessEntityProfileEditForm(
            data={
                "name": "ACI AAEP Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
                "aci_fabric": self.aci_fabric,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], [self.name_error_message])
        self.assertEqual(form.errors["name_alias"], [self.name_error_message])
        self.assertEqual(form.errors["description"], [self.description_error_message])

    def test_valid_aci_aaep_field_values(self) -> None:
        """Test validation of valid ACI AAEP field values."""
        form = ACIAttachableAccessEntityProfileEditForm(
            data={
                "name": "ACIAAEP1",
                "name_alias": "Testing",
                "description": "ACI AAEP for NetBox ACI Plugin",
                "aci_fabric": self.aci_fabric,
            }
        )
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.errors.get("name"))
        self.assertIsNone(form.errors.get("name_alias"))
        self.assertIsNone(form.errors.get("description"))


class ACIAAEPDomainBindingFormTestCase(ACIBaseFormTestCase):
    """Test case for the ACIAAEPDomainBinding forms."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up required objects for ACIAAEPDomainBinding form tests."""
        super().setUpTestData()
        cls.aci_vlan_pool = ACIVLANPool.objects.create(
            name="ACIAAEPFormTestVLANPool",
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_physical_domain = ACIPhysicalDomain.objects.create(
            name="ACIAAEPFormTestPhysicalDomain",
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool,
        )
        cls.aci_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACIAAEPFormTest",
            aci_fabric=cls.aci_fabric,
        )

    def test_edit_form_aci_domain_object_type_unknown(self) -> None:
        """Test the edit form tolerates an unknown ACI domain object type."""
        form = ACIAAEPDomainBindingEditForm(data={"aci_domain_object_type": 99999999})
        self.assertTrue(form.fields["aci_domain_object"].disabled)
        self.assertEqual(form.fields["aci_domain_object"].queryset.count(), 0)

    def test_edit_form_physical_domain_type_configures_field(self) -> None:
        """Test edit form configures aci_domain_object for physical domain."""
        aci_domain_object_type = ContentType.objects.get_for_model(ACIPhysicalDomain)
        form = ACIAAEPDomainBindingEditForm(
            data={"aci_domain_object_type": aci_domain_object_type.pk}
        )
        self.assertEqual(
            form.fields["aci_domain_object"].queryset.model, ACIPhysicalDomain
        )

    def test_edit_form_routed_domain_type_configures_field(self) -> None:
        """Test edit form configures aci_domain_object for routed domain."""
        aci_domain_object_type = ContentType.objects.get_for_model(ACIRoutedDomain)
        form = ACIAAEPDomainBindingEditForm(
            data={"aci_domain_object_type": aci_domain_object_type.pk}
        )
        self.assertEqual(
            form.fields["aci_domain_object"].queryset.model, ACIRoutedDomain
        )

    def test_bulk_edit_form_physical_domain_type_configures_field(self) -> None:
        """Test bulk edit form aci_domain_object for physical domain type."""
        aci_domain_object_type = ContentType.objects.get_for_model(ACIPhysicalDomain)
        form = ACIAAEPDomainBindingBulkEditForm(
            data={"aci_domain_object_type": aci_domain_object_type.pk}
        )
        self.assertEqual(
            form.fields["aci_domain_object"].queryset.model, ACIPhysicalDomain
        )

    def test_bulk_edit_form_aci_domain_object_type_unknown(self) -> None:
        """Test bulk edit form tolerates an unknown ACI domain object type."""
        form = ACIAAEPDomainBindingBulkEditForm(
            data={"aci_domain_object_type": 99999999}
        )
        self.assertTrue(form.fields["aci_domain_object"].disabled)
        self.assertEqual(form.fields["aci_domain_object"].queryset.count(), 0)

    def test_import_form_narrows_aaep_by_fabric(self) -> None:
        """Test the import form narrows ACI AAEP queryset by ACI Fabric."""
        form = ACIAAEPDomainBindingImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_aaep": self.aci_aaep.name,
            }
        )
        aaep_qs = form.fields["aci_aaep"].queryset
        self.assertIn(self.aci_aaep, aaep_qs)
