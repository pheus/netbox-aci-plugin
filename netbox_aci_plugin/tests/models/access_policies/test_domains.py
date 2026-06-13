# SPDX-FileCopyrightText: 2026 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from tenancy.models import Tenant

from ....models.access_policies.domains import ACIRoutedDomain
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

    def test_aci_routed_domain_str_return_value(self) -> None:
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

    def test_constraint_unique_aci_routed_domain_name(self) -> None:
        """Test unique constraint of ACI Routed Domain name."""
        duplicate_domain = ACIRoutedDomain(
            name=self.aci_routed_domain_name,
            aci_fabric=self.aci_fabric,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate_domain.save()
