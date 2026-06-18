# SPDX-FileCopyrightText: 2024 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType

from ....choices import (
    ContractSubjectFilterApplyDirectionChoices,
    ContractSubjectFilterPriorityChoices,
    QualityOfServiceClassChoices,
)
from ....forms.tenant.contracts import (
    ACIContractEditForm,
    ACIContractImportForm,
    ACIContractRelationBulkEditForm,
    ACIContractRelationEditForm,
    ACIContractRelationImportForm,
    ACIContractSubjectEditForm,
    ACIContractSubjectFilterImportForm,
    ACIContractSubjectImportForm,
)
from ....models.tenant.contracts import ACIContract, ACIContractSubject
from ....models.tenant.endpoint_groups import ACIEndpointGroup
from ..base import ACIBaseFormTestCase


class ACIContractFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIContract form."""

    def test_invalid_aci_contract_field_values(self) -> None:
        """Test validation of invalid ACI Contract field values."""
        aci_contract = ACIContractEditForm(
            data={
                "name": "ACI Contract Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(aci_contract.errors["name"], [self.name_error_message])
        self.assertEqual(aci_contract.errors["name_alias"], [self.name_error_message])
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


class ACIContractSubjectFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIContractSubject form."""

    def test_invalid_aci_contract_subject_field_values(self) -> None:
        """Test validation of invalid ACI Contract Subject field values."""
        aci_contract_subject = ACIContractSubjectEditForm(
            data={
                "name": "ACI Contract Subject Test 1",
                "name_alias": "ACI Test Alias 1",
                "description": "Invalid Description: ö",
            }
        )
        self.assertEqual(aci_contract_subject.errors["name"], [self.name_error_message])
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


class ACIContractRelationFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIContractRelation forms."""

    def test_edit_form_aci_object_type_unknown(self) -> None:
        """Test the edit form tolerates an unknown ACI object type."""
        form = ACIContractRelationEditForm(data={"aci_object_type": 99999999})
        self.assertIn("aci_object", form.fields)

    def test_bulk_edit_form_aci_object_type_configures_field(self) -> None:
        """Test the bulk edit form configures aci_object for a valid type."""
        aci_object_type = ContentType.objects.get_for_model(ACIEndpointGroup)
        form = ACIContractRelationBulkEditForm(
            data={"aci_object_type": aci_object_type.pk}
        )
        self.assertEqual(form.fields["aci_object"].queryset.model, ACIEndpointGroup)

    def test_bulk_edit_form_aci_object_type_unknown(self) -> None:
        """Test the bulk edit form tolerates an unknown ACI object type."""
        form = ACIContractRelationBulkEditForm(data={"aci_object_type": 99999999})
        self.assertIn("aci_object", form.fields)


class ACIContractSubjectFilterImportFormTestCase(ACIBaseFormTestCase):
    """Test case for ACIContractSubjectFilter import form."""

    def test_clean_apply_direction_returns_value(self) -> None:
        """Test clean_apply_direction returns a provided value unchanged."""
        form = ACIContractSubjectFilterImportForm(
            data={
                "apply_direction": ContractSubjectFilterApplyDirectionChoices.DIR_BOTH
            }
        )
        form.is_valid()
        self.assertEqual(
            form.cleaned_data.get("apply_direction"),
            ContractSubjectFilterApplyDirectionChoices.DIR_BOTH,
        )

    def test_clean_priority_returns_value(self) -> None:
        """Test clean_priority returns a provided value unchanged."""
        form = ACIContractSubjectFilterImportForm(
            data={"priority": ContractSubjectFilterPriorityChoices.CLASS_LEVEL_1}
        )
        form.is_valid()
        self.assertEqual(
            form.cleaned_data.get("priority"),
            ContractSubjectFilterPriorityChoices.CLASS_LEVEL_1,
        )


class ACIContractImportFormCoverageTestCase(ACIBaseFormTestCase):
    """Coverage tests for ACI Contract import and subject forms."""

    def test_contract_import_form_clean_qos_class_returns_value(self) -> None:
        """Test the Contract import form clean_qos_class returns the value."""
        form = ACIContractImportForm(
            data={"qos_class": QualityOfServiceClassChoices.CLASS_LEVEL_3}
        )
        form.is_valid()
        self.assertEqual(
            form.cleaned_data.get("qos_class"),
            QualityOfServiceClassChoices.CLASS_LEVEL_3,
        )

    def test_contract_relation_import_form_contract_in_common(self) -> None:
        """Test the relation import form narrows the contract to 'common'."""
        form = ACIContractRelationImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_tenant": self.aci_tenant.name,
                "is_aci_contract_in_common": "true",
            }
        )
        self.assertIn("aci_contract", form.fields)

    def test_contract_subject_import_form_clean_qos_class_returns_value(self) -> None:
        """Test the Subject import form clean_qos_class returns the value."""
        form = ACIContractSubjectImportForm(
            data={"qos_class": QualityOfServiceClassChoices.CLASS_LEVEL_3}
        )
        form.is_valid()
        self.assertEqual(
            form.cleaned_data.get("qos_class"),
            QualityOfServiceClassChoices.CLASS_LEVEL_3,
        )

    def test_contract_subject_filter_import_form_filter_in_common(self) -> None:
        """Test the Subject Filter import narrows the filter to 'common'."""
        form = ACIContractSubjectFilterImportForm(
            data={
                "aci_fabric": self.aci_fabric.name,
                "aci_tenant": self.aci_tenant.name,
                "aci_contract": "ACITestContract",
                "is_aci_contract_filter_in_common": "true",
            }
        )
        self.assertIn("aci_contract_filter", form.fields)

    def test_contract_subject_edit_form_init_separated_directions(self) -> None:
        """Test the Subject edit form selects the separated-directions tab."""
        contract = ACIContract.objects.create(
            name="ACIFormTestSubjectContract", aci_tenant=self.aci_tenant
        )
        subject = ACIContractSubject.objects.create(
            name="ACIFormTestSeparatedSubject",
            aci_contract=contract,
            apply_both_directions_enabled=False,
        )
        form = ACIContractSubjectEditForm(instance=subject)
        self.assertIsNone(form.initial["qos_class"])
