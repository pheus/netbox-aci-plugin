# SPDX-FileCopyrightText: 2025 Martin Hauser
#
# SPDX-License-Identifier: GPL-3.0-or-later

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from ipam.models import VLAN, Prefix
from tenancy.models import Tenant

from ....models.fabric.fabrics import ACIFabric
from ..base import ACIBaseTestCase


class ACIFabricTestCase(ACIBaseTestCase):
    """Test case for ACIFabric model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the ACIFabric model."""
        super().setUpTestData()

        cls.aci_fabric_name = "ACITestFabric"
        cls.aci_fabric_description = "ACI Test Fabric for NetBox ACI Plugin"
        cls.aci_fabric_comments = """
        ACI Fabric for NetBox ACI Plugin testing.
        """
        cls.aci_fabric_id = 100
        cls.aci_fabric_gipo_pool_prefix = "225.0.0.0/15"

        # Create related objects
        cls.infra_vlan = VLAN.objects.create(
            vid=cls.aci_fabric_infra_vlan_vid, name="ACI-Infra-Vlan"
        )
        cls.gipo_pool = Prefix.objects.create(prefix=cls.aci_fabric_gipo_pool_prefix)

        # Create objects
        cls.aci_fabric = ACIFabric.objects.create(
            name=cls.aci_fabric_name,
            description=cls.aci_fabric_description,
            fabric_id=cls.aci_fabric_id,
            infra_vlan_vid=cls.aci_fabric_infra_vlan_vid,
            infra_vlan=cls.infra_vlan,
            gipo_pool=cls.gipo_pool,
            nb_tenant=cls.nb_tenant,
            comments=cls.aci_fabric_comments,
        )

    def test_aci_fabric_instance(self) -> None:
        """Test type of created ACI Fabric."""
        self.assertTrue(isinstance(self.aci_fabric, ACIFabric))

    def test_aci_fabric_str_return_value(self) -> None:
        """Test string value of created ACI Fabric."""
        self.assertEqual(self.aci_fabric.__str__(), self.aci_fabric.name)

    def test_aci_fabric_description(self) -> None:
        """Test description of ACI Fabric."""
        self.assertEqual(self.aci_fabric.description, self.aci_fabric_description)

    def test_aci_fabric_fabric_id(self) -> None:
        """Test fabric ID of ACI Fabric."""
        self.assertEqual(self.aci_fabric.fabric_id, self.aci_fabric_id)

    def test_aci_fabric_infra_vlan_vid(self) -> None:
        """Test infra VLAN ID of ACI Fabric."""
        self.assertEqual(self.aci_fabric.infra_vlan_vid, self.aci_fabric_infra_vlan_vid)

    def test_aci_fabric_infra_vlan(self) -> None:
        """Test the NetBox VLAN associated with ACI Fabric."""
        self.assertTrue(isinstance(self.aci_fabric.infra_vlan, VLAN))
        self.assertEqual(self.aci_fabric.infra_vlan, self.infra_vlan)
        self.assertEqual(self.aci_fabric.infra_vlan.vid, self.aci_fabric_infra_vlan_vid)

    def test_aci_fabric_gipo_pool(self) -> None:
        """Test the NetBox Prefix associated with ACI Fabric."""
        self.assertTrue(isinstance(self.aci_fabric.gipo_pool, Prefix))
        self.assertEqual(self.aci_fabric.gipo_pool, self.gipo_pool)
        self.assertEqual(
            str(self.aci_fabric.gipo_pool.prefix), self.aci_fabric_gipo_pool_prefix
        )

    def test_aci_fabric_nb_tenant_instance(self) -> None:
        """Test the NetBox tenant associated with ACI Fabric."""
        self.assertTrue(isinstance(self.aci_fabric.nb_tenant, Tenant))
        self.assertEqual(self.aci_fabric.nb_tenant.name, self.nb_tenant_name)

    def test_invalid_aci_fabric_name(self) -> None:
        """Test validation of ACI Fabric naming."""
        fabric = ACIFabric(
            name="ACI Test Fabric 1",
            fabric_id=14,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid,
        )
        with self.assertRaises(ValidationError) as cm:
            fabric.full_clean()

        # Check the specific field that failed
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_fabric_name_length(self) -> None:
        """Test validation of ACI Fabric name length."""
        fabric = ACIFabric(
            name="T" * 65,  # Exceeding the maximum length of 64
            fabric_id=14,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid,
        )
        with self.assertRaises(ValidationError) as cm:
            fabric.full_clean()

        # Check the specific field that failed
        self.assertIn("name", cm.exception.error_dict)

    def test_invalid_aci_fabric_description(self) -> None:
        """Test validation of ACI Fabric description."""
        fabric = ACIFabric(
            name="ACITestFabric1",
            description="Invalid Description: ö",
            fabric_id=14,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid,
        )
        with self.assertRaises(ValidationError) as cm:
            fabric.full_clean()

        # Check the specific field that failed
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_fabric_description_length(self) -> None:
        """Test validation of ACI Fabric description length."""
        fabric = ACIFabric(
            name="ACITestFabric1",
            description="T" * 129,  # Exceeding the maximum length of 128
            fabric_id=14,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid,
        )
        with self.assertRaises(ValidationError) as cm:
            fabric.full_clean()

        # Check the specific field that failed
        self.assertIn("description", cm.exception.error_dict)

    def test_invalid_aci_fabric_id(self) -> None:
        """Test validation of ACI Fabric ID value."""
        fabric = ACIFabric(
            name="ACITestFabric1",
            fabric_id=5000,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid,
        )
        with self.assertRaises(ValidationError) as cm:
            fabric.full_clean()

        # Check the specific field that failed
        self.assertIn("fabric_id", cm.exception.error_dict)

    def test_invalid_aci_fabric_infra_vlan_vid(self) -> None:
        """Test validation of ACI Fabric infra VLAN id."""
        fabric = ACIFabric(
            name="ACITestFabric1",
            fabric_id=self.aci_fabric_id,
            infra_vlan_vid=5000,
        )
        with self.assertRaises(ValidationError) as cm:
            fabric.full_clean()

        # Check the specific field that failed
        self.assertIn("infra_vlan_vid", cm.exception.error_dict)

    def test_invalid_aci_fabric_infra_vlan_association(self) -> None:
        """Test validation of ACI Fabric infra VLAN association."""
        invalid_infra_vlan = VLAN.objects.create(vid=100, name="Invalid-Infra-Vlan")
        fabric = ACIFabric(
            name="ACITestFabric1",
            fabric_id=self.aci_fabric_id,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid,
            infra_vlan=invalid_infra_vlan,
        )
        with self.assertRaises(ValidationError) as cm:
            fabric.full_clean()

        # Check the specific field that failed
        self.assertIn("infra_vlan", cm.exception.error_dict)

    def test_invalid_aci_fabric_gipo_pool(self) -> None:
        """Test validation of ACI Fabric GIPo pool prefix."""
        invalid_gipo_pool = Prefix(prefix="192.168.0.0/16")
        invalid_gipo_pool.full_clean()
        invalid_gipo_pool.save()
        fabric = ACIFabric(
            name="ACITestFabric1",
            fabric_id=self.aci_fabric_id,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid,
            gipo_pool=invalid_gipo_pool,
        )
        with self.assertRaises(ValidationError) as cm:
            fabric.full_clean()

        # Check the specific field that failed
        self.assertIn("gipo_pool", cm.exception.error_dict)

    def test_constraint_unique_aci_fabric_name(self) -> None:
        """Test unique constraint of ACI Fabric name."""
        duplicate_fabric = ACIFabric(
            name=self.aci_fabric_name,
            fabric_id=14,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid,
        )
        with self.assertRaises(IntegrityError):
            duplicate_fabric.save()

    def test_constraint_unique_aci_fabric_id(self) -> None:
        """Test unique constraint of ACI Fabric ID."""
        duplicate_fabric = ACIFabric(
            name="ACITestFabric1",
            fabric_id=self.aci_fabric_id,
            infra_vlan_vid=self.aci_fabric_infra_vlan_vid,
        )
        with self.assertRaises(IntegrityError):
            duplicate_fabric.save()
