# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from tenancy.models import Tenant

from ....models.access_policies.domains import (
    ACIPhysicalDomain,
    ACIRoutedDomain,
)
from ....models.access_policies.vlan_pools import ACIVLANPool
from ....models.fabric.fabrics import ACIFabric
from ..base import ACIBaseTestCase


class ACIRoutedDomainTestCase(ACIBaseTestCase):
    """Test case for ACIRoutedDomain model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACIRoutedDomain model."""
        super().setUpTestData()

        cls.aci_routed_domain_name = "ACITestRoutedDomain"
        cls.aci_routed_domain_alias = "ACITestRoutedDomainAlias"
        cls.aci_routed_domain_description = "ACI Test Routed Domain"
        cls.aci_routed_domain_security_domains = ["all", "netops"]
        cls.aci_routed_domain_comments = "ACI Routed Domain for testing."

        cls.aci_routed_domain = ACIRoutedDomain.objects.create(
            name=cls.aci_routed_domain_name,
            name_alias=cls.aci_routed_domain_alias,
            description=cls.aci_routed_domain_description,
            aci_fabric=cls.aci_fabric,
            security_domains=cls.aci_routed_domain_security_domains,
            nb_tenant=cls.nb_tenant,
            comments=cls.aci_routed_domain_comments,
        )

    def test_aci_routed_domain_instance(self) -> None:
        """Test type of created ACI Routed Domain."""
        self.assertTrue(isinstance(self.aci_routed_domain, ACIRoutedDomain))

    def test_aci_routed_domain_str(self) -> None:
        """Test string value of created ACI Routed Domain."""
        self.assertEqual(
            self.aci_routed_domain.__str__(),
            self.aci_routed_domain.name,
        )

    def test_aci_routed_domain_alias(self) -> None:
        """Test alias of ACI Routed Domain."""
        self.assertEqual(
            self.aci_routed_domain.name_alias,
            self.aci_routed_domain_alias,
        )

    def test_aci_routed_domain_description(self) -> None:
        """Test description of ACI Routed Domain."""
        self.assertEqual(
            self.aci_routed_domain.description,
            self.aci_routed_domain_description,
        )

    def test_aci_routed_domain_aci_fabric_instance(self) -> None:
        """Test the ACI Fabric instance associated with ACI Routed Domain."""
        self.assertTrue(isinstance(self.aci_routed_domain.aci_fabric, ACIFabric))
        self.assertEqual(self.aci_routed_domain.aci_fabric.name, self.aci_fabric_name)

    def test_aci_routed_domain_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant associated with ACI Routed Domain."""
        self.assertTrue(isinstance(self.aci_routed_domain.nb_tenant, Tenant))
        self.assertEqual(self.aci_routed_domain.nb_tenant.name, self.nb_tenant_name)

    def test_aci_routed_domain_parent_object(self) -> None:
        """Test parent object of ACI Routed Domain."""
        self.assertEqual(self.aci_routed_domain.parent_object, self.aci_fabric)

    def test_aci_routed_domain_security_domains(self) -> None:
        """Test security domains of ACI Routed Domain."""
        self.assertEqual(
            self.aci_routed_domain.security_domains,
            self.aci_routed_domain_security_domains,
        )

    def test_invalid_aci_routed_domain_name(self) -> None:
        """Test validation of ACI Routed Domain naming."""
        domain = ACIRoutedDomain(
            name="ACI Test Routed Domain 1",
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(ValidationError) as cm:
            domain.full_clean()
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_routed_domain_name_length(self) -> None:
        """Test validation of ACI Routed Domain name length."""
        domain = ACIRoutedDomain(
            name="T" * 65,
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(ValidationError) as cm:
            domain.full_clean()
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_routed_domain_name_alias(self) -> None:
        """Test validation of ACI Routed Domain aliasing."""
        domain = ACIRoutedDomain(
            name="ACIRoutedDomainTest1",
            name_alias="Invalid Alias",
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(ValidationError) as cm:
            domain.full_clean()
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_routed_domain_description(self) -> None:
        """Test validation of ACI Routed Domain description."""
        domain = ACIRoutedDomain(
            name="ACIRoutedDomainTest1",
            description="Invalid Description: ö",
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(ValidationError) as cm:
            domain.full_clean()
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_routed_domain_security_domain(self) -> None:
        """Test validation of ACI Routed Domain security domain names."""
        domain = ACIRoutedDomain(
            name="ACIRoutedDomainTest1",
            aci_fabric=self.aci_fabric,
            security_domains=["Invalid Security Domain"],
        )
        with self.assertRaises(ValidationError) as cm:
            domain.full_clean()
        self.assertIn("security_domains", cm.exception.error_dict)

    def test_invalid_aci_routed_domain_duplicate_security_domains(self) -> None:
        """Test validation rejects duplicate security domain names."""
        domain = ACIRoutedDomain(
            name="ACIRoutedDomainTest1",
            aci_fabric=self.aci_fabric,
            security_domains=["netops", "netops"],
        )
        with self.assertRaises(ValidationError) as cm:
            domain.full_clean()
        self.assertIn("security_domains", cm.exception.error_dict)

    def test_constraint_unique_aci_routed_domain_name(self) -> None:
        """Test unique constraint of ACI Routed Domain name."""
        duplicate_domain = ACIRoutedDomain(
            name=self.aci_routed_domain_name,
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_domain.save()

    def test_aci_routed_domain_aci_vlan_pool(self) -> None:
        """Test assigning a same-fabric VLAN pool to ACI Routed Domain."""
        self.aci_routed_domain.aci_vlan_pool = self.aci_vlan_pool1
        self.aci_routed_domain.full_clean()
        self.assertTrue(isinstance(self.aci_routed_domain.aci_vlan_pool, ACIVLANPool))
        self.assertEqual(
            self.aci_routed_domain.aci_vlan_pool,
            self.aci_vlan_pool1,
        )

    def test_clean_rejects_vlan_pool_in_other_fabric(self) -> None:
        """Test validation rejects a VLAN pool from another ACI Fabric."""
        other_fabric = ACIFabric.objects.create(
            name="ACITestRoutedDomainOtherFabric",
            fabric_id=128,
            infra_vlan_vid=3901,
        )
        other_vlan_pool = ACIVLANPool.objects.create(
            name="ACITestRoutedDomainOtherPool",
            aci_fabric=other_fabric,
        )
        self.aci_routed_domain.aci_vlan_pool = other_vlan_pool
        with self.assertRaises(ValidationError) as cm:
            self.aci_routed_domain.full_clean()
        self.assertIn("aci_vlan_pool", cm.exception.message_dict)


class ACIPhysicalDomainTestCase(ACIBaseTestCase):
    """Test case for ACIPhysicalDomain model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACIPhysicalDomain model."""
        super().setUpTestData()

        cls.aci_physical_domain_name = "ACITestPhysicalDomain"
        cls.aci_physical_domain_alias = "ACITestPhysicalDomainAlias"
        cls.aci_physical_domain_description = "ACI Test Physical Domain"
        cls.aci_physical_domain_security_domains = ["all", "netops"]
        cls.aci_physical_domain_comments = "ACI Physical Domain for testing."

        cls.aci_physical_domain = ACIPhysicalDomain.objects.create(
            name=cls.aci_physical_domain_name,
            name_alias=cls.aci_physical_domain_alias,
            description=cls.aci_physical_domain_description,
            aci_fabric=cls.aci_fabric,
            aci_vlan_pool=cls.aci_vlan_pool1,
            security_domains=cls.aci_physical_domain_security_domains,
            nb_tenant=cls.nb_tenant,
            comments=cls.aci_physical_domain_comments,
        )

    def test_aci_physical_domain_instance(self) -> None:
        """Test type of created ACI Physical Domain."""
        self.assertTrue(isinstance(self.aci_physical_domain, ACIPhysicalDomain))

    def test_aci_physical_domain_str(self) -> None:
        """Test string value of created ACI Physical Domain."""
        self.assertEqual(
            self.aci_physical_domain.__str__(),
            self.aci_physical_domain.name,
        )

    def test_aci_physical_domain_alias(self) -> None:
        """Test alias of ACI Physical Domain."""
        self.assertEqual(
            self.aci_physical_domain.name_alias,
            self.aci_physical_domain_alias,
        )

    def test_aci_physical_domain_description(self) -> None:
        """Test description of ACI Physical Domain."""
        self.assertEqual(
            self.aci_physical_domain.description,
            self.aci_physical_domain_description,
        )

    def test_aci_physical_domain_aci_fabric_instance(self) -> None:
        """Test the ACI Fabric instance associated with ACI Physical Domain."""
        self.assertTrue(isinstance(self.aci_physical_domain.aci_fabric, ACIFabric))
        self.assertEqual(self.aci_physical_domain.aci_fabric.name, self.aci_fabric_name)

    def test_aci_physical_domain_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant associated with ACI Physical Domain."""
        self.assertTrue(isinstance(self.aci_physical_domain.nb_tenant, Tenant))
        self.assertEqual(self.aci_physical_domain.nb_tenant.name, self.nb_tenant_name)

    def test_aci_physical_domain_parent_object(self) -> None:
        """Test parent object of ACI Physical Domain."""
        self.assertEqual(self.aci_physical_domain.parent_object, self.aci_fabric)

    def test_aci_physical_domain_security_domains(self) -> None:
        """Test security domains of ACI Physical Domain."""
        self.assertEqual(
            self.aci_physical_domain.security_domains,
            self.aci_physical_domain_security_domains,
        )

    def test_invalid_aci_physical_domain_name(self) -> None:
        """Test validation of ACI Physical Domain naming."""
        domain = ACIPhysicalDomain(
            name="ACI Test Physical Domain 1",
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(ValidationError) as cm:
            domain.full_clean()
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_physical_domain_name_length(self) -> None:
        """Test validation of ACI Physical Domain name length."""
        domain = ACIPhysicalDomain(
            name="T" * 65,
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(ValidationError) as cm:
            domain.full_clean()
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_physical_domain_name_alias(self) -> None:
        """Test validation of ACI Physical Domain aliasing."""
        domain = ACIPhysicalDomain(
            name="ACIPhysicalDomainTest1",
            name_alias="Invalid Alias",
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(ValidationError) as cm:
            domain.full_clean()
        self.assertIn("name_alias", cm.exception.error_dict)

    def test_invalid_aci_physical_domain_description(self) -> None:
        """Test validation of ACI Physical Domain description."""
        domain = ACIPhysicalDomain(
            name="ACIPhysicalDomainTest1",
            description="Invalid Description: ö",
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(ValidationError) as cm:
            domain.full_clean()
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_physical_domain_security_domain(self) -> None:
        """Test validation of ACI Physical Domain security domain names."""
        domain = ACIPhysicalDomain(
            name="ACIPhysicalDomainTest1",
            aci_fabric=self.aci_fabric,
            security_domains=["Invalid Security Domain"],
        )
        with self.assertRaises(ValidationError) as cm:
            domain.full_clean()
        self.assertIn("security_domains", cm.exception.error_dict)

    def test_invalid_aci_physical_domain_duplicate_security_domains(self) -> None:
        """Test validation rejects duplicate security domain names."""
        domain = ACIPhysicalDomain(
            name="ACIPhysicalDomainTest1",
            aci_fabric=self.aci_fabric,
            security_domains=["netops", "netops"],
        )
        with self.assertRaises(ValidationError) as cm:
            domain.full_clean()
        self.assertIn("security_domains", cm.exception.error_dict)

    def test_constraint_unique_aci_physical_domain_name(self) -> None:
        """Test unique constraint of ACI Physical Domain name."""
        duplicate_domain = ACIPhysicalDomain(
            name=self.aci_physical_domain_name,
            aci_fabric=self.aci_fabric,
            aci_vlan_pool=self.aci_vlan_pool1,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_domain.save()

    def test_aci_physical_domain_aci_vlan_pool(self) -> None:
        """Test assigning a same-fabric VLAN pool to ACI Physical Domain."""
        self.aci_physical_domain.aci_vlan_pool = self.aci_vlan_pool1
        self.aci_physical_domain.full_clean()
        self.assertTrue(isinstance(self.aci_physical_domain.aci_vlan_pool, ACIVLANPool))
        self.assertEqual(
            self.aci_physical_domain.aci_vlan_pool,
            self.aci_vlan_pool1,
        )

    def test_clean_rejects_vlan_pool_in_other_fabric(self) -> None:
        """Test validation rejects a VLAN pool from another ACI Fabric."""
        other_fabric = ACIFabric.objects.create(
            name="ACITestPhysicalDomainOtherFabric",
            fabric_id=128,
            infra_vlan_vid=3901,
        )
        other_vlan_pool = ACIVLANPool.objects.create(
            name="ACITestPhysicalDomainOtherPool",
            aci_fabric=other_fabric,
        )
        self.aci_physical_domain.aci_vlan_pool = other_vlan_pool
        with self.assertRaises(ValidationError) as cm:
            self.aci_physical_domain.full_clean()
        self.assertIn("aci_vlan_pool", cm.exception.message_dict)
