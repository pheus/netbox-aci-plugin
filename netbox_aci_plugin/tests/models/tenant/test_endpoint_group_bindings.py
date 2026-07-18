# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.backends.postgresql.psycopg_any import NumericRange

from core.choices import ObjectChangeActionChoices
from ipam.models import VLAN, VLANGroup

from ....choices import (
    DeploymentImmediacyChoices,
    PortModeChoices,
    ResolutionImmediacyChoices,
    VLANAllocationModeChoices,
)
from ....models.access_policies.aaep import (
    ACIAAEPDomainBinding,
    ACIAttachableAccessEntityProfile,
)
from ....models.access_policies.domains import ACIPhysicalDomain
from ....models.access_policies.vlan_pools import ACIVLANPool, ACIVLANPoolRange
from ....models.fabric.fabrics import ACIFabric
from ....models.tenant.endpoint_group_bindings import (
    ACIEndpointGroupAAEPBinding,
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


class ACIEndpointGroupAAEPBindingTestCase(ACIBaseTestCase):
    """Test case for ACIEndpointGroupAAEPBinding model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACIEndpointGroupAAEPBinding model."""
        super().setUpTestData()

        cls.aci_epg_name = "ACITestEPGForAAEPBinding"
        cls.aci_physical_domain_name = "ACITestPhysicalDomainForAAEPBinding"
        cls.aci_aaep_name = "ACITestAAEPForEPGAAEPBinding"

        # aci_vlan_pool1 (from the base fixture) covers 100-199 and 200-299
        cls.aci_epg = ACIEndpointGroup.objects.create(
            name=cls.aci_epg_name,
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
        cls.aci_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name=cls.aci_aaep_name,
            aci_fabric=cls.aci_fabric,
        )
        cls.aci_aaep_domain_binding = ACIAAEPDomainBinding.objects.create(
            aci_aaep=cls.aci_aaep,
            aci_domain_object=cls.aci_physical_domain,
        )
        cls.nb_vlan = VLAN.objects.create(vid=150, name="VLANForAAEPBinding")

        cls.aci_epg_aaep_binding = ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=cls.aci_epg,
            aci_aaep=cls.aci_aaep,
            nb_vlan=cls.nb_vlan,
        )

    def test_aci_endpoint_group_aaep_binding_instance(self) -> None:
        """Test type of created ACI EPG AAEP Binding instance."""
        self.assertTrue(
            isinstance(self.aci_epg_aaep_binding, ACIEndpointGroupAAEPBinding)
        )

    def test_aci_endpoint_group_aaep_binding_str(self) -> None:
        """Test string value of created ACI EPG AAEP Binding instance."""
        self.assertEqual(
            self.aci_epg_aaep_binding.__str__(),
            f"{self.aci_epg} - {self.aci_aaep_name}",
        )

    def test_aci_endpoint_group_aaep_binding_create_with_nb_vlan_snapshots_encap(
        self,
    ) -> None:
        """Test creating with nb_vlan snapshots the encap VLAN ID on save."""
        self.assertEqual(self.aci_epg_aaep_binding.encap_vlan_id, 150)

    def test_aci_endpoint_group_aaep_binding_create_with_encap_vlan_id_only(
        self,
    ) -> None:
        """Test creating with only an encap VLAN ID is valid."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingEncapOnly",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=180,
        )
        binding.full_clean()
        binding.save()
        self.assertIsNone(binding.nb_vlan_id)
        self.assertEqual(binding.encap_vlan_id, 180)

    def test_aci_endpoint_group_aaep_binding_create_with_matching_pair(self) -> None:
        """Test creating with a matching nb_vlan and encap VLAN ID is valid."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingMatchingPair",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        vlan = VLAN.objects.create(vid=185, name="VLANMatchingPairTest")
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            nb_vlan=vlan,
            encap_vlan_id=185,
        )
        binding.full_clean()  # matching pair -> no error

    def test_invalid_aci_endpoint_group_aaep_binding_mismatched_pair(self) -> None:
        """Test clean rejects a mismatched nb_vlan/encap VLAN ID pair."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingMismatchedPair",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        vlan = VLAN.objects.create(vid=151, name="VLANMismatchedPairTest")
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            nb_vlan=vlan,
            encap_vlan_id=152,
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("encap_vlan_id", cm.exception.error_dict)

    def test_invalid_aci_endpoint_group_aaep_binding_primary_mismatched_pair(
        self,
    ) -> None:
        """Test clean rejects a mismatched primary_nb_vlan/encap VLAN pair."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingPrimaryMismatchedPair",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        primary_vlan = VLAN.objects.create(
            vid=145, name="VLANPrimaryMismatchedPairTest"
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=140,
            primary_nb_vlan=primary_vlan,
            primary_encap_vlan_id=146,
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("primary_encap_vlan_id", cm.exception.error_dict)
        self.assertIn(
            "re-sync",
            cm.exception.message_dict["primary_encap_vlan_id"][0],
        )

    def test_aci_endpoint_group_aaep_binding_repoint_nb_vlan_snapshot_handling(
        self,
    ) -> None:
        """Test re-pointing nb_vlan with a stale snapshot, then re-syncing."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingRepoint",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        vlan_a = VLAN.objects.create(vid=160, name="VLANRepointA")
        vlan_b = VLAN.objects.create(vid=161, name="VLANRepointB")
        binding = ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            nb_vlan=vlan_a,
        )
        self.assertEqual(binding.encap_vlan_id, 160)

        # Re-pointing to a different VLAN without clearing the stale
        # snapshot is rejected
        binding.nb_vlan = vlan_b
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("encap_vlan_id", cm.exception.error_dict)

        # Clearing the stale snapshot re-syncs the new VLAN's ID on save
        binding.encap_vlan_id = None
        binding.full_clean()
        binding.save()
        self.assertEqual(binding.encap_vlan_id, 161)

    def test_invalid_aci_endpoint_group_aaep_binding_missing_encap(self) -> None:
        """Test clean rejects a binding without any encapsulation."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingMissingEncap",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("encap_vlan_id", cm.exception.error_dict)

    def test_invalid_aci_endpoint_group_aaep_binding_primary_without_main(
        self,
    ) -> None:
        """Test clean rejects a primary encap without a main encap."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingPrimaryWithoutMain",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            primary_encap_vlan_id=110,
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("primary_encap_vlan_id", cm.exception.error_dict)

    def test_invalid_aci_endpoint_group_aaep_binding_primary_equals_main(
        self,
    ) -> None:
        """Test clean rejects a primary encap equal to the main encap."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingPrimaryEqualsMain",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=120,
            primary_encap_vlan_id=120,
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("primary_encap_vlan_id", cm.exception.error_dict)

    def test_invalid_aci_endpoint_group_aaep_binding_out_of_pool_range(self) -> None:
        """Test clean rejects an encap VLAN ID outside the ACI VLAN Pool."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingOutOfPoolRange",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=500,
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("encap_vlan_id", cm.exception.error_dict)

    def test_invalid_aci_endpoint_group_aaep_binding_primary_out_of_pool_range(
        self,
    ) -> None:
        """Test clean rejects a primary encap VLAN ID outside the pool."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingPrimaryOutOfPoolRange",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=140,
            primary_encap_vlan_id=500,
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("primary_encap_vlan_id", cm.exception.error_dict)
        self.assertIn(
            "ACI VLAN Pool",
            cm.exception.message_dict["primary_encap_vlan_id"][0],
        )

    def test_invalid_aci_endpoint_group_aaep_binding_wrong_nb_vlan_group(
        self,
    ) -> None:
        """Test clean rejects a NetBox VLAN outside the pool's VLAN group."""
        group = VLANGroup.objects.create(
            name="VLANGroupForAAEPBindingRule6",
            slug="vlan-group-for-aaep-binding-rule6",
            vid_ranges=[NumericRange(700, 799)],
        )
        pool = ACIVLANPool.objects.create(
            name="VLANPoolGroupedForAAEPBinding",
            aci_fabric=self.aci_fabric,
            nb_vlan_group=group,
        )
        ACIVLANPoolRange.objects.create(
            aci_vlan_pool=pool, vlan_id_from=700, vlan_id_to=799
        )
        physical_domain = ACIPhysicalDomain.objects.create(
            name="ACIPhysicalDomainGroupedForAAEPBinding",
            aci_fabric=self.aci_fabric,
            aci_vlan_pool=pool,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=self.aci_epg,
            aci_domain_object=physical_domain,
        )
        ACIAAEPDomainBinding.objects.create(
            aci_aaep=self.aci_aaep, aci_domain_object=physical_domain
        )
        nb_vlan_outside_group = VLAN.objects.create(vid=750, name="VLANOutsideGroup")
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=self.aci_epg,
            aci_aaep=self.aci_aaep,
            nb_vlan=nb_vlan_outside_group,
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("nb_vlan", cm.exception.error_dict)

    def test_aci_endpoint_group_aaep_binding_effective_props_fallback(self) -> None:
        """Test effective props prefer the live vid, else the snapshot."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingEffectiveProps",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        main_vlan = VLAN.objects.create(vid=171, name="VLANMainForFallback")
        primary_vlan = VLAN.objects.create(vid=172, name="VLANPrimaryForFallback")
        binding = ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            nb_vlan=main_vlan,
            primary_nb_vlan=primary_vlan,
        )
        self.assertEqual(binding.effective_encap_vlan_id, 171)
        self.assertEqual(binding.effective_primary_encap_vlan_id, 172)

        main_vlan.delete()
        primary_vlan.delete()
        binding.refresh_from_db()

        self.assertIsNone(binding.nb_vlan_id)
        self.assertIsNone(binding.primary_nb_vlan_id)
        self.assertEqual(binding.effective_encap_vlan_id, 171)
        self.assertEqual(binding.effective_primary_encap_vlan_id, 172)

    def test_aci_endpoint_group_aaep_binding_save_update_fields_widening(
        self,
    ) -> None:
        """Test save() widens update_fields to include synced encap IDs.

        Regression test for the save() branch that unions the synced
        encap_vlan_id/primary_encap_vlan_id field names into an explicit
        update_fields argument, so a caller naming only an unrelated field
        does not silently exclude the synced columns from the UPDATE.
        """
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingUpdateFieldsWidening",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        main_vlan = VLAN.objects.create(vid=190, name="VLANMainForUpdateFieldsWidening")
        primary_vlan = VLAN.objects.create(
            vid=191, name="VLANPrimaryForUpdateFieldsWidening"
        )
        binding = ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            nb_vlan=main_vlan,
            primary_nb_vlan=primary_vlan,
        )
        self.assertEqual(binding.encap_vlan_id, 190)
        self.assertEqual(binding.primary_encap_vlan_id, 191)

        # Move the live VLAN IDs WITHOUT re-saving the binding, so the DB
        # snapshots (190/191) are now stale relative to the live VLANs.
        main_vlan.vid = 192
        main_vlan.save(update_fields=("vid",))
        primary_vlan.vid = 193
        primary_vlan.save(update_fields=("vid",))

        # Save naming only "mode": save() must re-sync the encap columns
        # from the live VLANs AND widen update_fields to persist them; a
        # non-widening save() would drop 192/193 and leave 190/191.
        binding.nb_vlan = main_vlan
        binding.primary_nb_vlan = primary_vlan
        binding.mode = PortModeChoices.MODE_NATIVE
        binding.save(update_fields={"mode"})

        binding.refresh_from_db()
        self.assertEqual(binding.mode, PortModeChoices.MODE_NATIVE)
        self.assertEqual(binding.encap_vlan_id, 192)
        self.assertEqual(binding.primary_encap_vlan_id, 193)

    def test_invalid_aci_endpoint_group_aaep_binding_duplicate_epg_aaep(
        self,
    ) -> None:
        """Test unique validation rejects a duplicate EPG/AAEP pair."""
        duplicate_binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=self.aci_epg,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=150,
        )
        with self.assertRaises(ValidationError):
            duplicate_binding.full_clean()

    def test_constraint_unique_aci_endpoint_group_aaep_binding_per_epg(
        self,
    ) -> None:
        """Test unique constraint of ACI EPG AAEP Binding per EPG and AAEP."""
        duplicate_binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=self.aci_epg,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=150,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_binding.save()

    def test_invalid_aci_endpoint_group_aaep_binding_cross_fabric_aaep(self) -> None:
        """Test clean rejects an AAEP from a different ACI Fabric."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingCrossFabric",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        other_fabric = ACIFabric.objects.create(
            name="ACIBaseTestFabricOtherAAEPBinding",
            fabric_id=self.aci_fabric_id + 1,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid + 1,
        )
        other_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACITestAAEPOtherFabricForEPGBinding",
            aci_fabric=other_fabric,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=other_aaep,
            encap_vlan_id=150,
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("aci_aaep", cm.exception.error_dict)

    def test_invalid_aci_endpoint_group_aaep_binding_missing_f0467_chain(
        self,
    ) -> None:
        """Test clean rejects an AAEP not bound to the EPG's ACI domain."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingMissingF0467",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        aaep_without_domain = ACIAttachableAccessEntityProfile.objects.create(
            name="ACITestAAEPWithoutDomainBindingForEPG",
            aci_fabric=self.aci_fabric,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=aaep_without_domain,
            encap_vlan_id=150,
        )
        with self.assertRaises(ValidationError) as cm:
            binding.full_clean()
        self.assertIn("aci_aaep", cm.exception.error_dict)

    def test_valid_aci_endpoint_group_aaep_binding_f0467_chain_satisfied(
        self,
    ) -> None:
        """Test clean accepts an AAEP bound to the EPG's ACI domain."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingF0467Satisfied",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        aaep_with_domain = ACIAttachableAccessEntityProfile.objects.create(
            name="ACITestAAEPWithDomainBindingForEPG",
            aci_fabric=self.aci_fabric,
        )
        ACIAAEPDomainBinding.objects.create(
            aci_aaep=aaep_with_domain,
            aci_domain_object=self.aci_physical_domain,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=aaep_with_domain,
            encap_vlan_id=150,
        )
        binding.full_clean()  # F0467 chain satisfied -> no error

    def test_invalid_aci_endpoint_group_aaep_binding_epg_without_domain(
        self,
    ) -> None:
        """Test validation of a binding for an EPG without domain bindings."""
        epg_unbound = ACIEndpointGroup.objects.create(
            name="ACITestEPGWithoutDomain",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg_unbound,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=150,
        )
        with self.assertRaises(ValidationError) as context:
            binding.full_clean()
        self.assertIn("aci_aaep", context.exception.error_dict)

    def test_aci_endpoint_group_aaep_binding_encap_in_second_shared_pool(
        self,
    ) -> None:
        """Test encap validation across multiple shared domain pools.

        Uses a fresh EPG (rather than the shared ``self.aci_epg``) bound to
        both the setUpTestData physical domain and a second one, so the
        new binding does not collide with the unique ``setUpTestData``
        binding's (endpoint group, AAEP) pair.
        """
        # Second pool covering 500-599, second shared physical domain
        vlan_pool = ACIVLANPool.objects.create(
            name="ACITestPool2ForAAEPBinding", aci_fabric=self.aci_fabric
        )
        ACIVLANPoolRange.objects.create(
            aci_vlan_pool=vlan_pool, vlan_id_from=500, vlan_id_to=599
        )
        physical_domain = ACIPhysicalDomain.objects.create(
            name="ACITestPhysDom2ForAAEPBinding",
            aci_fabric=self.aci_fabric,
            aci_vlan_pool=vlan_pool,
        )
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGSecondPoolForAAEPBinding",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=physical_domain,
        )
        ACIAAEPDomainBinding.objects.create(
            aci_aaep=self.aci_aaep,
            aci_domain_object=physical_domain,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=550,
        )
        binding.full_clean()  # valid: covered by the second shared pool

    def test_invalid_aci_endpoint_group_aaep_binding_encap_primary_split_domains(
        self,
    ) -> None:
        """Test encap and primary must be covered by ONE shared pool."""
        # Two single-range pools/domains: X covers 100-199, Y covers 200-299
        pool_x = ACIVLANPool.objects.create(
            name="ACITestPoolXForAAEPBinding", aci_fabric=self.aci_fabric
        )
        ACIVLANPoolRange.objects.create(
            aci_vlan_pool=pool_x, vlan_id_from=100, vlan_id_to=199
        )
        pool_y = ACIVLANPool.objects.create(
            name="ACITestPoolYForAAEPBinding", aci_fabric=self.aci_fabric
        )
        ACIVLANPoolRange.objects.create(
            aci_vlan_pool=pool_y, vlan_id_from=200, vlan_id_to=299
        )
        domain_x = ACIPhysicalDomain.objects.create(
            name="ACITestDomXForAAEPBinding",
            aci_fabric=self.aci_fabric,
            aci_vlan_pool=pool_x,
        )
        domain_y = ACIPhysicalDomain.objects.create(
            name="ACITestDomYForAAEPBinding",
            aci_fabric=self.aci_fabric,
            aci_vlan_pool=pool_y,
        )
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGSplitForAAEPBinding",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACITestAAEPSplitForAAEPBinding", aci_fabric=self.aci_fabric
        )
        for domain in (domain_x, domain_y):
            ACIEndpointGroupDomainBinding.objects.create(
                aci_epg_object=epg, aci_domain_object=domain
            )
            ACIAAEPDomainBinding.objects.create(aci_aaep=aaep, aci_domain_object=domain)
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=aaep,
            encap_vlan_id=150,  # only pool_x
            primary_encap_vlan_id=250,  # only pool_y
        )
        with self.assertRaises(ValidationError) as context:
            binding.full_clean()
        self.assertIn("primary_encap_vlan_id", context.exception.error_dict)

    def test_aci_endpoint_group_aaep_binding_survives_nb_vlan_deletion(
        self,
    ) -> None:
        """Test the encap snapshots survive NetBox VLAN deletion.

        Uses a fresh EPG (rather than the shared ``self.aci_epg``) so the
        new binding does not collide with the unique ``setUpTestData``
        binding's (endpoint group, AAEP) pair, and a dedicated main
        NetBox VLAN (rather than the shared ``self.nb_vlan``) so the
        encap VLAN ID does not collide with the fixture binding's encap
        on the same AAEP.
        """
        # 151 and 175 both fall in aci_vlan_pool1 (100-199)
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGSurvivesDeletionForAAEPBinding",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        main_vlan = VLAN.objects.create(vid=151, name="MainVLANForAAEPBinding")
        primary_vlan = VLAN.objects.create(vid=175, name="PrimaryVLANForAAEPBinding")
        binding = ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            nb_vlan=main_vlan,
            primary_nb_vlan=primary_vlan,
        )
        self.assertEqual(binding.encap_vlan_id, 151)
        self.assertEqual(binding.primary_encap_vlan_id, 175)
        main_vlan.delete()
        primary_vlan.delete()
        binding.refresh_from_db()
        self.assertIsNone(binding.nb_vlan_id)
        self.assertIsNone(binding.primary_nb_vlan_id)
        self.assertEqual(binding.encap_vlan_id, 151)
        self.assertEqual(binding.primary_encap_vlan_id, 175)
        binding.full_clean()  # snapshots remain usable as effective encaps
        self.assertEqual(str(binding), f"{epg} - {self.aci_aaep.name}")

    def test_invalid_aci_endpoint_group_aaep_binding_split_vlan_groups(
        self,
    ) -> None:
        """Test one pool must admit BOTH NetBox VLAN groups."""
        # Two pools, each covering 150 and 175, bound to different groups
        group_a = VLANGroup.objects.create(
            name="VLANGroupAForAAEP", slug="vlan-group-a-aaep"
        )
        group_b = VLANGroup.objects.create(
            name="VLANGroupBForAAEP", slug="vlan-group-b-aaep"
        )
        pool_a = ACIVLANPool.objects.create(
            name="ACITestPoolGroupAForAAEP",
            aci_fabric=self.aci_fabric,
            nb_vlan_group=group_a,
        )
        pool_b = ACIVLANPool.objects.create(
            name="ACITestPoolGroupBForAAEP",
            aci_fabric=self.aci_fabric,
            nb_vlan_group=group_b,
        )
        for pool in (pool_a, pool_b):
            ACIVLANPoolRange.objects.create(
                aci_vlan_pool=pool, vlan_id_from=100, vlan_id_to=199
            )
        domain_a = ACIPhysicalDomain.objects.create(
            name="ACITestDomGroupAForAAEP",
            aci_fabric=self.aci_fabric,
            aci_vlan_pool=pool_a,
        )
        domain_b = ACIPhysicalDomain.objects.create(
            name="ACITestDomGroupBForAAEP",
            aci_fabric=self.aci_fabric,
            aci_vlan_pool=pool_b,
        )
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGGroupsForAAEP",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACITestAAEPGroupsForAAEP", aci_fabric=self.aci_fabric
        )
        for domain in (domain_a, domain_b):
            ACIEndpointGroupDomainBinding.objects.create(
                aci_epg_object=epg, aci_domain_object=domain
            )
            ACIAAEPDomainBinding.objects.create(aci_aaep=aaep, aci_domain_object=domain)
        main_vlan = VLAN.objects.create(
            vid=150, name="MainVLANGroupsAAEP", group=group_a
        )
        primary_vlan = VLAN.objects.create(
            vid=175, name="PrimaryVLANGroupsAAEP", group=group_b
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=aaep,
            nb_vlan=main_vlan,  # group A -> only pool_a
            primary_nb_vlan=primary_vlan,  # group B -> only pool_b
        )
        # main VLAN narrows candidates to pool_a; pool_a rejects group B
        with self.assertRaises(ValidationError) as context:
            binding.full_clean()
        self.assertIn("primary_nb_vlan", context.exception.error_dict)

    def test_aci_endpoint_group_aaep_binding_prerequisite_removal(
        self,
    ) -> None:
        """Test point-in-time validation after a prerequisite is removed.

        Reuses the setUpTestData binding directly (rather than creating a
        second one for the same endpoint group/AAEP pair, which would
        collide with the unique constraint).
        """
        binding = self.aci_epg_aaep_binding
        binding.full_clean()  # valid while the shared domain exists
        # Remove the EPG's only shared physical-domain binding
        self.aci_epg_domain_binding.delete()
        binding.refresh_from_db()  # binding row survives - no cascade
        with self.assertRaises(ValidationError) as context:
            binding.full_clean()
        self.assertIn("aci_aaep", context.exception.error_dict)

    def test_aci_endpoint_group_aaep_binding_get_mode_color(self) -> None:
        """Test the 'get_mode_color' method."""
        self.assertEqual(
            self.aci_epg_aaep_binding.get_mode_color(),
            PortModeChoices.colors.get(PortModeChoices.MODE_REGULAR),
        )

    def test_aci_endpoint_group_aaep_binding_get_deployment_immediacy_color(
        self,
    ) -> None:
        """Test the 'get_deployment_immediacy_color' method."""
        self.assertEqual(
            self.aci_epg_aaep_binding.get_deployment_immediacy_color(),
            DeploymentImmediacyChoices.colors.get(
                DeploymentImmediacyChoices.IMMEDIACY_LAZY
            ),
        )

    def test_aci_endpoint_group_aaep_binding_to_objectchange(self) -> None:
        """Test to_objectchange sets the AAEP as the related object."""
        objectchange = self.aci_epg_aaep_binding.to_objectchange(
            ObjectChangeActionChoices.ACTION_UPDATE
        )
        self.assertEqual(objectchange.related_object, self.aci_aaep)

    def test_aci_endpoint_group_aaep_binding_parent_object(self) -> None:
        """Test parent object of ACI EPG AAEP Binding is the AAEP object."""
        self.assertEqual(self.aci_epg_aaep_binding.parent_object, self.aci_aaep)

    def test_aci_endpoint_group_aaep_binding_aci_tenant(self) -> None:
        """Test aci_tenant returns the ACITenant of the related EPG."""
        self.assertEqual(self.aci_epg_aaep_binding.aci_tenant, self.aci_tenant)

    def test_aci_endpoint_group_aaep_binding_aci_fabric(self) -> None:
        """Test aci_fabric returns the related ACIFabric."""
        self.assertEqual(self.aci_epg_aaep_binding.aci_fabric, self.aci_fabric)

    def test_default_ordering_queryset_evaluates(self) -> None:
        """Test that the default-ordered queryset evaluates without error."""
        self.assertIsNotNone(list(ACIEndpointGroupAAEPBinding.objects.all()))

    def test_invalid_aci_endpoint_group_aaep_binding_duplicate_encap(
        self,
    ) -> None:
        """Test clean rejects an encap VLAN ID already used on the AAEP."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingDuplicateEncap",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=150,  # collides with the fixture binding's encap
        )
        with self.assertRaises(ValidationError) as context:
            binding.full_clean()
        self.assertIn("encap_vlan_id", context.exception.error_dict)

    def test_invalid_aci_endpoint_group_aaep_binding_primary_collides_main(
        self,
    ) -> None:
        """Test clean rejects a primary encap equal to a sibling's encap."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingPrimaryCollidesMain",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=160,
            primary_encap_vlan_id=150,  # collides with the fixture's encap
        )
        with self.assertRaises(ValidationError) as context:
            binding.full_clean()
        self.assertIn("primary_encap_vlan_id", context.exception.error_dict)

    def test_invalid_aci_endpoint_group_aaep_binding_main_collides_primary(
        self,
    ) -> None:
        """Test clean rejects an encap equal to a sibling's primary encap."""
        epg_with_primary = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingSiblingWithPrimary",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg_with_primary,
            aci_domain_object=self.aci_physical_domain,
        )
        ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=epg_with_primary,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=161,
            primary_encap_vlan_id=162,
        )
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingMainCollidesPrimary",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=162,  # collides with the sibling's primary encap
        )
        with self.assertRaises(ValidationError) as context:
            binding.full_clean()
        self.assertIn("encap_vlan_id", context.exception.error_dict)

    def test_invalid_aci_endpoint_group_aaep_binding_untagged_not_alone(
        self,
    ) -> None:
        """Test clean rejects an untagged binding joining a used AAEP."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingUntaggedNotAlone",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=160,
            mode=PortModeChoices.MODE_UNTAGGED,
        )
        with self.assertRaises(ValidationError) as context:
            binding.full_clean()
        self.assertIn("mode", context.exception.error_dict)

    def test_invalid_aci_endpoint_group_aaep_binding_join_untagged_aaep(
        self,
    ) -> None:
        """Test clean rejects any binding joining an untagged AAEP."""
        second_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACITestAAEPSecondForUntaggedConflict",
            aci_fabric=self.aci_fabric,
        )
        ACIAAEPDomainBinding.objects.create(
            aci_aaep=second_aaep,
            aci_domain_object=self.aci_physical_domain,
        )
        epg_untagged = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingUntaggedSibling",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg_untagged,
            aci_domain_object=self.aci_physical_domain,
        )
        ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=epg_untagged,
            aci_aaep=second_aaep,
            encap_vlan_id=170,
            mode=PortModeChoices.MODE_UNTAGGED,
        )
        epg_regular = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingAfterUntagged",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg_regular,
            aci_domain_object=self.aci_physical_domain,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg_regular,
            aci_aaep=second_aaep,
            encap_vlan_id=171,
        )
        with self.assertRaises(ValidationError) as context:
            binding.full_clean()
        self.assertIn("mode", context.exception.error_dict)

    def test_invalid_aci_endpoint_group_aaep_binding_second_native(
        self,
    ) -> None:
        """Test clean rejects a second native mode binding on the AAEP."""
        epg_native1 = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingFirstNative",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg_native1,
            aci_domain_object=self.aci_physical_domain,
        )
        ACIEndpointGroupAAEPBinding.objects.create(
            aci_endpoint_group=epg_native1,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=165,
            mode=PortModeChoices.MODE_NATIVE,
        )
        epg_native2 = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingSecondNative",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg_native2,
            aci_domain_object=self.aci_physical_domain,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg_native2,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=166,
            mode=PortModeChoices.MODE_NATIVE,
        )
        with self.assertRaises(ValidationError) as context:
            binding.full_clean()
        self.assertIn("mode", context.exception.error_dict)

    def test_valid_aci_endpoint_group_aaep_binding_native_with_regular(
        self,
    ) -> None:
        """Test a native mode binding coexists with a regular sibling."""
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingNativeCoexist",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=self.aci_aaep,
            encap_vlan_id=167,
            mode=PortModeChoices.MODE_NATIVE,
        )
        binding.full_clean()  # native plus the fixture's regular binding

    def test_valid_aci_endpoint_group_aaep_binding_same_encap_other_aaep(
        self,
    ) -> None:
        """Test the same encap VLAN ID is valid on a different AAEP."""
        other_aaep = ACIAttachableAccessEntityProfile.objects.create(
            name="ACITestAAEPOtherForSameEncap",
            aci_fabric=self.aci_fabric,
        )
        ACIAAEPDomainBinding.objects.create(
            aci_aaep=other_aaep,
            aci_domain_object=self.aci_physical_domain,
        )
        epg = ACIEndpointGroup.objects.create(
            name="ACITestEPGForAAEPBindingSameEncapOtherAAEP",
            aci_app_profile=self.aci_app_profile,
            aci_bridge_domain=self.aci_bd,
        )
        ACIEndpointGroupDomainBinding.objects.create(
            aci_epg_object=epg,
            aci_domain_object=self.aci_physical_domain,
        )
        binding = ACIEndpointGroupAAEPBinding(
            aci_endpoint_group=epg,
            aci_aaep=other_aaep,
            encap_vlan_id=150,  # same VID as the fixture, different AAEP
        )
        binding.full_clean()  # different AAEP scope raises no error

    def test_valid_aci_endpoint_group_aaep_binding_self_exclusion(
        self,
    ) -> None:
        """Test re-validating a persisted binding excludes itself."""
        # Without pk exclusion, the binding's own encap VLAN ID 150
        # in the database would collide with itself.
        self.aci_epg_aaep_binding.full_clean()
