# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from core.choices import ObjectChangeActionChoices

from ....choices import (
    DeploymentImmediacyChoices,
    ResolutionImmediacyChoices,
    VLANAllocationModeChoices,
)
from ....models.access_policies.domains import ACIPhysicalDomain
from ....models.access_policies.vlan_pools import ACIVLANPool
from ....models.fabric.fabrics import ACIFabric
from ....models.tenant.endpoint_group_bindings import (
    ACIEndpointGroupDomainBinding,
)
from ....models.tenant.endpoint_groups import ACIEndpointGroup, ACIUSegEndpointGroup
from ..base import ACIBaseTestCase


class ACIEndpointGroupDomainBindingTestCase(ACIBaseTestCase):
    """Test case for ACIEndpointGroupDomainBinding model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACIEndpointGroupDomainBinding model."""
        super().setUpTestData()

        cls.aci_epg_name = "ACITestEPGForDomainBinding"
        cls.aci_useg_epg_name = "ACITestUSegEPGForDomainBinding"
        cls.aci_physical_domain_name = "ACITestPhysicalDomainForEPGBinding"

        cls.aci_epg = ACIEndpointGroup.objects.create(
            name=cls.aci_epg_name,
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_useg_epg = ACIUSegEndpointGroup.objects.create(
            name=cls.aci_useg_epg_name,
            aci_app_profile=cls.aci_app_profile,
            aci_bridge_domain=cls.aci_bd,
        )
        cls.aci_physical_domain = ACIPhysicalDomain.objects.create(
            name=cls.aci_physical_domain_name,
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool1,
        )

        cls.aci_epg_domain_binding = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_epg,
            aci_domain_object=cls.aci_physical_domain,
        )
        cls.aci_useg_epg_domain_binding = ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=cls.aci_useg_epg,
            aci_domain_object=cls.aci_physical_domain,
        )

    def test_aci_endpoint_group_domain_binding_instance(self) -> None:
        """Test type of created ACI EPG Domain Binding instances."""
        self.assertTrue(
            isinstance(self.aci_epg_domain_binding, ACIEndpointGroupDomainBinding)
        )
        self.assertTrue(
            isinstance(self.aci_useg_epg_domain_binding, ACIEndpointGroupDomainBinding)
        )

    def test_aci_endpoint_group_domain_binding_str(self) -> None:
        """Test string values of created ACI EPG Domain Binding instances."""
        self.assertEqual(
            self.aci_epg_domain_binding.__str__(),
            f"{self.aci_epg_name} - {self.aci_physical_domain_name}",
        )
        self.assertEqual(
            self.aci_useg_epg_domain_binding.__str__(),
            f"{self.aci_useg_epg_name} - {self.aci_physical_domain_name}",
        )

    def test_aci_endpoint_group_domain_binding_aci_epg_object_instance(self) -> None:
        """Test the EPG object instance associated with domain bindings."""
        self.assertTrue(
            isinstance(self.aci_epg_domain_binding.aci_epg_object, ACIEndpointGroup)
        )
        self.assertEqual(
            self.aci_epg_domain_binding.aci_epg_object.name, self.aci_epg_name
        )
        self.assertTrue(
            isinstance(
                self.aci_useg_epg_domain_binding.aci_epg_object, ACIUSegEndpointGroup
            )
        )
        self.assertEqual(
            self.aci_useg_epg_domain_binding.aci_epg_object.name,
            self.aci_useg_epg_name,
        )

    def test_aci_endpoint_group_domain_binding_aci_domain_object_instance(
        self,
    ) -> None:
        """Test the domain object instance associated with domain bindings."""
        self.assertTrue(
            isinstance(self.aci_epg_domain_binding.aci_domain_object, ACIPhysicalDomain)
        )
        self.assertEqual(
            self.aci_epg_domain_binding.aci_domain_object.name,
            self.aci_physical_domain_name,
        )
        self.assertTrue(
            isinstance(
                self.aci_useg_epg_domain_binding.aci_domain_object, ACIPhysicalDomain
            )
        )
        self.assertEqual(
            self.aci_useg_epg_domain_binding.aci_domain_object.name,
            self.aci_physical_domain_name,
        )

    def test_aci_endpoint_group_domain_binding_deployment_immediacy_default(
        self,
    ) -> None:
        """Test the default value of 'deployment_immediacy' is 'lazy'."""
        self.assertEqual(
            self.aci_epg_domain_binding.deployment_immediacy,
            DeploymentImmediacyChoices.IMMEDIACY_LAZY,
        )

    def test_aci_endpoint_group_domain_binding_resolution_immediacy_default(
        self,
    ) -> None:
        """Test the default value of 'resolution_immediacy' is 'lazy'."""
        self.assertEqual(
            self.aci_epg_domain_binding.resolution_immediacy,
            ResolutionImmediacyChoices.IMMEDIACY_LAZY,
        )

    def test_aci_endpoint_group_domain_binding_get_deployment_immediacy_color(
        self,
    ) -> None:
        """Test the 'get_deployment_immediacy_color' method."""
        self.assertEqual(
            self.aci_epg_domain_binding.get_deployment_immediacy_color(),
            DeploymentImmediacyChoices.colors.get(
                DeploymentImmediacyChoices.IMMEDIACY_LAZY
            ),
        )

    def test_aci_endpoint_group_domain_binding_get_resolution_immediacy_color(
        self,
    ) -> None:
        """Test the 'get_resolution_immediacy_color' method."""
        self.assertEqual(
            self.aci_epg_domain_binding.get_resolution_immediacy_color(),
            ResolutionImmediacyChoices.colors.get(
                ResolutionImmediacyChoices.IMMEDIACY_LAZY
            ),
        )

    def test_aci_endpoint_group_domain_binding_cache_related_endpoint_group(
        self,
    ) -> None:
        """Test cache_related_objects populates the EPG cache FK."""
        binding = self.aci_epg_domain_binding
        self.assertEqual(binding._aci_endpoint_group, self.aci_epg)  # noqa: SLF001
        self.assertIsNone(binding._aci_useg_endpoint_group)  # noqa: SLF001
        self.assertEqual(
            binding._aci_physical_domain,  # noqa: SLF001
            self.aci_physical_domain,
        )

    def test_aci_endpoint_group_domain_binding_cache_related_useg_endpoint_group(
        self,
    ) -> None:
        """Test cache_related_objects populates the uSeg EPG cache FK."""
        binding = self.aci_useg_epg_domain_binding
        self.assertEqual(
            binding._aci_useg_endpoint_group,  # noqa: SLF001
            self.aci_useg_epg,
        )
        self.assertIsNone(binding._aci_endpoint_group)  # noqa: SLF001
        self.assertEqual(
            binding._aci_physical_domain,  # noqa: SLF001
            self.aci_physical_domain,
        )

    def test_aci_endpoint_group_domain_binding_to_objectchange(self) -> None:
        """Test to_objectchange sets the EPG object as the related object."""
        objectchange = self.aci_epg_domain_binding.to_objectchange(
            ObjectChangeActionChoices.ACTION_UPDATE
        )
        self.assertEqual(objectchange.related_object, self.aci_epg)

    def test_aci_endpoint_group_domain_binding_parent_object(self) -> None:
        """Test parent object of ACI EPG Domain Binding is the EPG object."""
        self.assertEqual(self.aci_epg_domain_binding.parent_object, self.aci_epg)

    def test_aci_endpoint_group_domain_binding_aci_tenant(self) -> None:
        """Test aci_tenant returns the ACITenant of the related EPG object."""
        self.assertEqual(self.aci_epg_domain_binding.aci_tenant, self.aci_tenant)
        self.assertEqual(self.aci_useg_epg_domain_binding.aci_tenant, self.aci_tenant)

    def test_aci_endpoint_group_domain_binding_aci_fabric(self) -> None:
        """Test aci_fabric returns the ACIFabric of the related EPG object."""
        self.assertEqual(self.aci_epg_domain_binding.aci_fabric, self.aci_fabric)
        self.assertEqual(self.aci_useg_epg_domain_binding.aci_fabric, self.aci_fabric)

    def test_invalid_aci_endpoint_group_domain_binding_epg_object_type_without_object(
        self,
    ) -> None:
        """Test clean requires an EPG object when an object type is set."""
        binding = ACIEndpointGroupDomainBinding(
            aci_domain_object=self.aci_physical_domain,
            aci_epg_object_type=ContentType.objects.get_for_model(ACIEndpointGroup),
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("aci_epg_object", cm.exception.error_dict)

    def test_invalid_aci_endpoint_group_domain_binding_domain_type_without_object(
        self,
    ) -> None:
        """Test clean requires a domain object when an object type is set."""
        binding = ACIEndpointGroupDomainBinding(
            aci_epg_object=self.aci_epg,
            aci_domain_object_type=ContentType.objects.get_for_model(ACIPhysicalDomain),
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("aci_domain_object", cm.exception.error_dict)

    def test_invalid_aci_endpoint_group_domain_binding_cross_fabric_domain(
        self,
    ) -> None:
        """Test clean rejects a domain from a different ACI Fabric."""
        other_fabric = ACIFabric.objects.create(
            name="ACIBaseTestFabricOtherEPGDomainBinding",
            fabric_id=self.aci_fabric_id + 1,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 1,
        )
        other_vlan_pool = ACIVLANPool.objects.create(
            name="VLANPoolOtherEPGDomainBinding",
            aci_fabric=other_fabric,
            allocation_mode=VLANAllocationModeChoices.MODE_STATIC,
        )
        other_physical_domain = ACIPhysicalDomain.objects.create(
            name="ACITestOtherPhysicalDomain",
            aci_fabric=other_fabric,
            aci_vlan_pool=other_vlan_pool,
        )
        binding = ACIEndpointGroupDomainBinding(
            aci_epg_object=self.aci_epg,
            aci_domain_object=other_physical_domain,
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("aci_domain_object", cm.exception.error_dict)

    def test_invalid_aci_endpoint_group_domain_binding_duplicate_epg_domain(
        self,
    ) -> None:
        """Test unique validation rejects a duplicate EPG-domain pair."""
        duplicate_binding = ACIEndpointGroupDomainBinding(
            aci_epg_object=self.aci_epg,
            aci_domain_object=self.aci_physical_domain,
        )
        with self.assertRaises(ValidationError):
            duplicate_binding.full_clean()

    def test_valid_aci_endpoint_group_domain_binding_epg_bound_to_second_domain(
        self,
    ) -> None:
        """Test the same EPG can be bound to a second ACI domain."""
        second_domain = ACIPhysicalDomain.objects.create(
            name="ACITestPhysicalDomainSecond",
            aci_fabric=self.aci_fabric,
            aci_vlan_pool=self.aci_vlan_pool2,
        )
        binding = ACIEndpointGroupDomainBinding(
            aci_epg_object=self.aci_epg,
            aci_domain_object=second_domain,
        )
        binding.full_clean()

    def test_constraint_unique_aci_endpoint_group_domain_binding_per_epg(
        self,
    ) -> None:
        """Test unique constraint of ACI EPG Domain Binding per EPG/domain."""
        duplicate_binding = ACIEndpointGroupDomainBinding(
            aci_epg_object=self.aci_epg,
            aci_domain_object=self.aci_physical_domain,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_binding.save()

    def test_aci_endpoint_group_domain_binding_clone_fields_excludes_object_id(
        self,
    ) -> None:
        """Test clone fields omit the unique generic object ids."""
        self.assertNotIn(
            "aci_epg_object_id", ACIEndpointGroupDomainBinding.clone_fields
        )
        self.assertNotIn(
            "aci_domain_object_id", ACIEndpointGroupDomainBinding.clone_fields
        )
        self.assertIn("aci_epg_object_type", ACIEndpointGroupDomainBinding.clone_fields)
        self.assertIn(
            "aci_domain_object_type", ACIEndpointGroupDomainBinding.clone_fields
        )
