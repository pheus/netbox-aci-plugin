# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from core.choices import ObjectChangeActionChoices

from ....models.access_policies.aaep import (
    ACIAAEPDomainBinding,
    ACIAttachableAccessEntityProfile,
)
from ....models.access_policies.domains import (
    ACIPhysicalDomain,
    ACIRoutedDomain,
)
from ....models.fabric.fabrics import ACIFabric
from ..base import ACIBaseTestCase


class ACIAttachableAccessEntityProfileTestCase(ACIBaseTestCase):
    """Test case for ACIAttachableAccessEntityProfile model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACIAttachableAccessEntityProfile model."""
        super().setUpTestData()

        cls.aci_aaep_name = "ACITestAAEP"
        cls.aci_aaep_alias = "ACITestAAEPAlias"
        cls.aci_aaep_description = "ACI Test AAEP for NetBox ACI Plugin"
        cls.aci_aaep_comments = "ACI AAEP for NetBox ACI Plugin testing."
        cls.aci_aaep_infra_vlan = True

        cls.aci_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name=cls.aci_aaep_name,
            name_alias=cls.aci_aaep_alias,
            description=cls.aci_aaep_description,
            comments=cls.aci_aaep_comments,
            aci_fabric=cls.aci_fabric,
            nb_tenant=cls.nb_tenant,
            infra_vlan=cls.aci_aaep_infra_vlan,
        )

    def test_aci_attachable_access_entity_profile_instance(self) -> None:
        """Test type of created ACI Attachable Access Entity Profile."""
        self.assertTrue(isinstance(self.aci_aaep, ACIAttachableAccessEntityProfile))

    def test_aci_attachable_access_entity_profile_str(self) -> None:
        """Test string value of created ACI AAEP."""
        self.assertEqual(self.aci_aaep.__str__(), self.aci_aaep_name)

    def test_aci_attachable_access_entity_profile_alias(self) -> None:
        """Test alias of ACI Attachable Access Entity Profile."""
        self.assertEqual(self.aci_aaep.name_alias, self.aci_aaep_alias)

    def test_aci_attachable_access_entity_profile_description(self) -> None:
        """Test description of ACI Attachable Access Entity Profile."""
        self.assertEqual(self.aci_aaep.description, self.aci_aaep_description)

    def test_aci_attachable_access_entity_profile_aci_fabric_instance(
        self,
    ) -> None:
        """Test the ACI Fabric instance associated with ACI AAEP."""
        self.assertTrue(isinstance(self.aci_aaep.aci_fabric, ACIFabric))
        self.assertEqual(self.aci_aaep.aci_fabric.name, self.aci_fabric_name)

    def test_aci_attachable_access_entity_profile_infra_vlan(self) -> None:
        """Test the 'infra_vlan' option of ACI AAEP."""
        self.assertEqual(self.aci_aaep.infra_vlan, self.aci_aaep_infra_vlan)

    def test_aci_attachable_access_entity_profile_infra_vlan_default(
        self,
    ) -> None:
        """Test the default value of 'infra_vlan' is False."""
        aaep_defaults = ACIAttachableAccessEntityProfile.objects.create(
            name="ACITestAAEPDefaults",
            aci_fabric=self.aci_fabric,
        )
        self.assertFalse(aaep_defaults.infra_vlan)

    def test_aci_attachable_access_entity_profile_parent_object(self) -> None:
        """Test parent object of ACI AAEP is the ACI Fabric."""
        self.assertEqual(self.aci_aaep.parent_object, self.aci_fabric)

    def test_invalid_aci_attachable_access_entity_profile_name(self) -> None:
        """Test validation of ACI AAEP naming."""
        aaep = ACIAttachableAccessEntityProfile(name="Invalid Name With Spaces")
        with self.assertRaises(ValidationError):
            aaep.full_clean()

    def test_invalid_aci_attachable_access_entity_profile_name_length(
        self,
    ) -> None:
        """Test validation of ACI AAEP name length."""
        aaep = ACIAttachableAccessEntityProfile(
            name="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            aaep.full_clean()

    def test_invalid_aci_attachable_access_entity_profile_name_alias(
        self,
    ) -> None:
        """Test validation of ACI AAEP name alias."""
        aaep = ACIAttachableAccessEntityProfile(
            name="ACIAAEPTest1",
            name_alias="Invalid Alias",
        )
        with self.assertRaises(ValidationError):
            aaep.full_clean()

    def test_invalid_aci_attachable_access_entity_profile_name_alias_length(
        self,
    ) -> None:
        """Test validation of ACI AAEP name alias length."""
        aaep = ACIAttachableAccessEntityProfile(
            name="ACIAAEPTest1",
            name_alias="A" * 65,  # Exceeding the maximum length of 64
        )
        with self.assertRaises(ValidationError):
            aaep.full_clean()

    def test_invalid_aci_attachable_access_entity_profile_description(
        self,
    ) -> None:
        """Test validation of ACI AAEP description."""
        aaep = ACIAttachableAccessEntityProfile(
            name="ACIAAEPTest1",
            description="Invalid Description: ö",
        )
        with self.assertRaises(ValidationError):
            aaep.full_clean()

    def test_invalid_aci_attachable_access_entity_profile_description_length(
        self,
    ) -> None:
        """Test validation of ACI AAEP description length."""
        aaep = ACIAttachableAccessEntityProfile(
            name="ACIAAEPTest1",
            description="A" * 129,  # Exceeding the maximum length of 128
        )
        with self.assertRaises(ValidationError):
            aaep.full_clean()

    def test_constraint_unique_aci_aaep_name_per_aci_fabric(self) -> None:
        """Test unique constraint of ACI AAEP name per ACI Fabric."""
        duplicate_aaep = ACIAttachableAccessEntityProfile(
            name=self.aci_aaep_name,
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_aaep.save()


class ACIAAEPDomainBindingTestCase(ACIBaseTestCase):
    """Test case for ACIAAEPDomainBinding model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACIAAEPDomainBinding model."""
        super().setUpTestData()

        cls.aci_aaep_name = "ACITestAAEP"
        cls.aci_physical_domain_name = "ACITestPhysicalDomain"
        cls.aci_routed_domain_name = "ACITestRoutedDomain"

        cls.aci_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name=cls.aci_aaep_name,
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_physical_domain = ACIPhysicalDomain.objects.create(
            name=cls.aci_physical_domain_name,
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool1,
        )
        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name=cls.aci_routed_domain_name,
            aci_fabric=cls.aci_fabric,
        )

        cls.aci_aaep_domain_binding_physical = ACIAAEPDomainBinding.objects.create(
            aci_aaep=cls.aci_aaep,
            aci_domain_object=cls.aci_physical_domain,
        )
        cls.aci_aaep_domain_binding_routed = ACIAAEPDomainBinding.objects.create(
            aci_aaep=cls.aci_aaep,
            aci_domain_object=cls.aci_routed_domain,
        )

    def test_aci_aaep_domain_binding_instance(self) -> None:
        """Test type of created ACI AAEP Domain Binding instances."""
        self.assertTrue(
            isinstance(self.aci_aaep_domain_binding_physical, ACIAAEPDomainBinding)
        )
        self.assertTrue(
            isinstance(self.aci_aaep_domain_binding_routed, ACIAAEPDomainBinding)
        )

    def test_aci_aaep_domain_binding_str(self) -> None:
        """Test string values of created ACI AAEP Domain Binding instances."""
        self.assertEqual(
            self.aci_aaep_domain_binding_physical.__str__(),
            f"{self.aci_aaep_name} - {self.aci_physical_domain_name}",
        )
        self.assertEqual(
            self.aci_aaep_domain_binding_routed.__str__(),
            f"{self.aci_aaep_name} - {self.aci_routed_domain_name}",
        )

    def test_aci_aaep_domain_binding_aci_aaep_instance(self) -> None:
        """Test the ACI AAEP instance associated with domain bindings."""
        self.assertTrue(
            isinstance(
                self.aci_aaep_domain_binding_physical.aci_aaep,
                ACIAttachableAccessEntityProfile,
            )
        )
        self.assertEqual(
            self.aci_aaep_domain_binding_physical.aci_aaep.name,
            self.aci_aaep_name,
        )

    def test_aci_aaep_domain_binding_physical_domain_object(self) -> None:
        """Test the domain object instance of a physical domain binding."""
        self.assertTrue(
            isinstance(
                self.aci_aaep_domain_binding_physical.aci_domain_object,
                ACIPhysicalDomain,
            )
        )
        self.assertEqual(
            self.aci_aaep_domain_binding_physical.aci_domain_object.name,
            self.aci_physical_domain_name,
        )

    def test_aci_aaep_domain_binding_routed_domain_object(self) -> None:
        """Test the domain object instance of a routed domain binding."""
        self.assertTrue(
            isinstance(
                self.aci_aaep_domain_binding_routed.aci_domain_object,
                ACIRoutedDomain,
            )
        )
        self.assertEqual(
            self.aci_aaep_domain_binding_routed.aci_domain_object.name,
            self.aci_routed_domain_name,
        )

    def test_aci_aaep_domain_binding_cache_related_physical(self) -> None:
        """Test cache_related_objects populates physical domain cache FK."""
        binding = self.aci_aaep_domain_binding_physical
        self.assertEqual(binding._aci_physical_domain, self.aci_physical_domain)  # noqa: SLF001
        self.assertIsNone(binding._aci_routed_domain)  # noqa: SLF001

    def test_aci_aaep_domain_binding_cache_related_routed(self) -> None:
        """Test cache_related_objects populates routed domain cache FK."""
        binding = self.aci_aaep_domain_binding_routed
        self.assertEqual(binding._aci_routed_domain, self.aci_routed_domain)  # noqa: SLF001
        self.assertIsNone(binding._aci_physical_domain)  # noqa: SLF001

    def test_aci_aaep_domain_binding_to_objectchange(self) -> None:
        """Test to_objectchange sets the ACI AAEP as the related object."""
        objectchange = self.aci_aaep_domain_binding_physical.to_objectchange(
            ObjectChangeActionChoices.ACTION_UPDATE
        )
        self.assertEqual(objectchange.related_object, self.aci_aaep)

    def test_aci_aaep_domain_binding_parent_object(self) -> None:
        """Test parent object of ACI AAEP Domain Binding is the ACI AAEP."""
        self.assertEqual(
            self.aci_aaep_domain_binding_physical.parent_object, self.aci_aaep
        )

    def test_aci_aaep_domain_binding_aci_fabric(self) -> None:
        """Test aci_fabric of ACI AAEP Domain Binding is the ACI Fabric."""
        self.assertEqual(
            self.aci_aaep_domain_binding_physical.aci_fabric, self.aci_fabric
        )

    def test_invalid_aci_aaep_domain_binding_missing_aaep(
        self,
    ) -> None:
        """Test missing aci_aaep raises ValidationError, not DoesNotExist."""
        binding = ACIAAEPDomainBinding(
            aci_domain_object=self.aci_physical_domain,
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("aci_aaep", cm.exception.error_dict)

    def test_invalid_aci_aaep_domain_binding_object_type_without_object(
        self,
    ) -> None:
        """Test clean requires a domain object when an object type is set."""
        binding = ACIAAEPDomainBinding(
            aci_aaep=self.aci_aaep,
            aci_domain_object_type=ContentType.objects.get_for_model(ACIPhysicalDomain),
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("aci_domain_object", cm.exception.error_dict)

    def test_invalid_aci_aaep_domain_binding_cross_fabric_domain(
        self,
    ) -> None:
        """Test clean rejects a domain from a different ACI Fabric."""
        other_fabric = ACIFabric.objects.create(
            name="ACIBaseTestFabricOther",
            fabric_id=self.aci_fabric_id + 1,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 1,
        )
        other_routed_domain = ACIRoutedDomain.objects.create(
            name="ACITestOtherRoutedDomain",
            aci_fabric=other_fabric,
        )
        aaep_other = ACIAttachableAccessEntityProfile.objects.create(
            name="ACITestAAEPOther",
            aci_fabric=self.aci_fabric,
        )
        binding = ACIAAEPDomainBinding(
            aci_aaep=aaep_other,
            aci_domain_object=other_routed_domain,
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("aci_domain_object", cm.exception.error_dict)

    def test_invalid_aci_aaep_domain_binding_duplicate_domain_per_aaep(
        self,
    ) -> None:
        """Test unique validation rejects duplicate domain per ACI AAEP."""
        duplicate_binding = ACIAAEPDomainBinding(
            aci_aaep=self.aci_aaep,
            aci_domain_object=self.aci_physical_domain,
        )
        with self.assertRaises(ValidationError):
            duplicate_binding.full_clean()

    def test_constraint_unique_aci_aaep_domain_binding_per_aaep(self) -> None:
        """Test unique constraint of ACI AAEP Domain Binding per ACI AAEP."""
        duplicate_binding = ACIAAEPDomainBinding(
            aci_aaep=self.aci_aaep,
            aci_domain_object=self.aci_physical_domain,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_binding.save()

    def test_aci_aaep_domain_binding_clone_fields_excludes_object_id(
        self,
    ) -> None:
        """Test clone fields omit the unique generic object id."""
        self.assertNotIn("aci_domain_object_id", ACIAAEPDomainBinding.clone_fields)
        self.assertIn("aci_domain_object_type", ACIAAEPDomainBinding.clone_fields)
